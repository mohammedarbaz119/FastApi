from fastapi import APIRouter,HTTPException,Response,Depends,status
from fastapi.responses import JSONResponse
from ..models.User import User,UserForm,Form,TokenData,Token
from ..models import SessionDep
from sqlmodel import select
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



authRouter = APIRouter()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password:str):
    return pwd_context.hash(password)

def get_user(db:SessionDep, username: str):
     existing_user = db.exec(
            statement=select(User).where((User.username == username))
        ).first()
     return existing_user
    
def authenticate_user(db:SessionDep, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],db:SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@authRouter.post("/login",dependencies=[Depends(RateLimiter(times=10,seconds=60))])
async def login_for_access_token(
    form_data: Annotated[Form,"form for user login"],session:SessionDep
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect username or password {user}" ,
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@authRouter.post("/register/",dependencies=[Depends(RateLimiter(times=10,seconds=60))])
async def register_user(user: UserForm,session:SessionDep):
    # Check if the username or email is already taken
        existing_user = session.exec(
            select(User).where((User.username == user.username) | (User.email == user.email))
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already registered")
        new_user = User(username=user.username,email=user.email) 

        # Hash the password
        new_user.hashed_password = get_password_hash(password=user.password)
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return JSONResponse(content={"message":"user created,Now you can login"},status_code=201)


