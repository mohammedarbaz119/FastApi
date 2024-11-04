from sqlmodel import SQLModel,Session,create_engine
from fastapi import Depends
from typing import Annotated
import os

sqlite_file_name = "data/database/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    os.makedirs(os.path.dirname(sqlite_file_name), exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]