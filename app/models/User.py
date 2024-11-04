from typing import Optional
from sqlmodel import SQLModel, Field,Relationship
from datetime import datetime
from pydantic import BaseModel
from . import File
class UserForm(BaseModel):
    username:str
    email:str
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Form(BaseModel):
    username:str
    password:str

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    files: list["File"] = Relationship(back_populates="user")
