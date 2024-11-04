import pymongo
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
from dotenv import load_dotenv
import os
from .utils import embed_model
from llama_index.core.schema import Document
from typing import List, Union
from .utils import llm
load_dotenv()

# documents: list[Document] = []



mongodb_client = pymongo.MongoClient(host=os.getenv("MongoConn"))

store = MongoDBAtlasVectorSearch(
    mongodb_client=mongodb_client,
    db_name = os.getenv("DB_NAME"),
    collection_name =os.getenv("COLLECTION_NAME"),
    vector_index_name =os.getenv("VECTOR_INDEX_NAME") 
)
storage_context = StorageContext.from_defaults(vector_store=store)


index = VectorStoreIndex.from_vector_store(
store,embed_model=embed_model
)

def buildfilter(filename:str):
    filter = MetadataFilters(filters=[
        MetadataFilter(key="filename",operator=FilterOperator.EQ,value=filename)
    ])
    return filter

