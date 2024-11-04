from fastapi import APIRouter,HTTPException,UploadFile,Response,Depends,Query
from fastapi.responses import JSONResponse
from sqlmodel import select
from ..models import SessionDep,File
from llama_index.core.schema import Document
from .auth import get_current_user
from ..models import User
from typing import Annotated, Union
from ..IndexBuilder import index
from ..utils import add_texts_to_documents
import os
import pymupdf
from fastapi_limiter.depends import RateLimiter

fileRouter = APIRouter()


@fileRouter.post("/upload/",dependencies=[Depends(RateLimiter(times=5,seconds=60))])
async def upload_file(file: UploadFile,user:Annotated[User,Depends(get_current_user)],session: SessionDep):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Please upload a PDF file!!")
    user_uploaded_file = session.exec(select(File).where(File.filename==file.filename,File.userid==user.id)).first()
    if user_uploaded_file:
        raise HTTPException(status_code=409,detail=f"Resource '{file.filename}' already exists for user {user.username}")

    file_location = f"data/pdf/{file.filename}"
    text = "output.txt"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    try:
        with open(file_location, "wb") as f:
            content = await file.read()  # Read the file content
            f.write(content)  # Write the content to the file
        doc = pymupdf.open(stream=content)
        document: list[Document] = []
        texts = ""
        for page in doc: # iterate the document pages
            text = page.get_text()
            texts += text
        document = add_texts_to_documents(document,texts,{"filename":file.filename.strip()},chunk_size=1024)
        fileObj = File(filename=file.filename,file_location=file_location,content=texts)
        fileObj.userid = user.id
        session.add(fileObj)
        if not os.path.exists(file_location):
            for x in document:
                index.insert(x)
        print("doc uploading and indexing done")
        session.commit()
        return JSONResponse(content={
        "message":"file uploaded and index created",
        "pdf_name": file.filename,
        },status_code=201)
       
    except Exception as e:
        if e:
           raise HTTPException(status_code=400,detail=f"{e} as exception")
        
@fileRouter.get("/files/{page}")
async def getAllFiles(session:SessionDep,page:int,limit:Union[int,None]=1):
    offset = (page - 1) * limit
    files = session.exec(select(File.filename,User.username).join(File.user).offset(offset).limit(limit)).all()
    allfiles = []
    for (file,user) in files:
        allfiles.append({"filename":file,"username":user})

    return {
        "files":allfiles
    }
