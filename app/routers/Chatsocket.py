from fastapi import WebSocket,WebSocketDisconnect,APIRouter,WebSocketException
from fastapi_limiter.depends import WebSocketRateLimiter
import uuid
from ..utils import llm
from .auth import oauth2_scheme
from typing import List,Dict
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.storage.chat_store.redis import RedisChatStore
from llama_index.core.memory import ChatMemoryBuffer
from ..IndexBuilder import index,buildfilter
import os
from llama_index.core import PromptTemplate

text_qa_template_str = (
    "Context information is"
    " below.\n---------------------\n{context_str}\n---------------------\nUsing"
    " both the context information and also using your own knowledge, answer"
    " the question: {query_str}\nIf the context isn't helpful, you can also"
    " answer the question on your own.\n"
)
text_qa_template = PromptTemplate(text_qa_template_str)

chat_store = RedisChatStore(redis_url=os.getenv("REDIS_URL"))

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str,WebSocket] = {}
        self.chat_engines: Dict[str,BaseChatEngine] = {}
        self.memories: Dict[str,ChatMemoryBuffer] = {}


    async def connect(self, websocket: WebSocket,sockid:str):
        await websocket.accept()
        self.active_connections[sockid] = websocket

    def disconnect(self,sockid:str):
        self.active_connections.pop(sockid,None)
        self.chat_engines.pop(sockid,None)
        self.memories.pop(sockid,None)
        chat_store.delete_messages(sockid)
        print("disconnected and memory removed")
    
    def buildchatEngine(self,sockid:str,filename:str):
        chat_memory = ChatMemoryBuffer.from_defaults(
        token_limit=4096,
        chat_store=chat_store,
        chat_store_key=sockid,
        )
        filters = buildfilter(filename)
        self.memories[sockid]= chat_memory
        self.chat_engines[sockid]= index.as_chat_engine(chat_mode="context",
        memory=chat_memory,
        text_qa_template=text_qa_template,
        llm=llm,filters=filters)




chatRouter = APIRouter()
connections = ConnectionManager()


# ,username:str,filename:str
@chatRouter.websocket("/ws/{filename}")
async def ChatEndpoint(socket:WebSocket,filename:str):
    # ratelimit = WebSocketRateLimiter(times=1, seconds=5)
    sockid = f"{uuid.uuid4()}_{filename}"
    await connections.connect(socket,sockid)
    connections.buildchatEngine(sockid=sockid,filename=filename)
    ratelimit = WebSocketRateLimiter(times=1, seconds=20)
    while True:
        try:
            data = await socket.receive_text()
            await ratelimit(socket, context_key=data)
            res = connections.chat_engines[sockid].stream_chat(data).response_gen
            for idx,chunk in enumerate(res,start=1):
                if chunk == "Empty Response" and idx < 2:
                    await socket.send_text("There was no context to answer the Question so model sent an empty response there might be a error in server or pdf doesn't exist on the server")
                else:    
                    await socket.send_text(chunk)   
        except WebSocketDisconnect:
            connections.disconnect(sockid=sockid)
            break
        except Exception as e:
            await socket.send_text("Too Many Requests") # Thrown when rate limit exceeded.
            connections.disconnect(sockid=sockid)
            await socket.close(reason="too many requests")
            break
          # context_key is optional
        
        




