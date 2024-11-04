# imports
from llama_index.embeddings.google import GeminiEmbedding
from dotenv import load_dotenv
import os

load_dotenv()

embed_model = GeminiEmbedding(api_key=os.getenv("API_KEY"))
