from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field,Relationship
from . import User

class File(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True)
    file_location: str
    content: str 
    upload_datetime: datetime = Field(default_factory=datetime.now)
    userid: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="files")
