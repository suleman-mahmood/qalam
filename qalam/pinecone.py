import time
import logging
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from qalam.config import settings


logging.info("Initializing Pinecone client...")
pc = Pinecone(api_key=settings.pinecone_api_key)
logging.info("Pinecone client initialized successfully.")

# Check if index exists
index_name = settings.pinecone_index_name
if index_name not in [index_info["name"] for index_info in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        deletion_protection="enabled",
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

    logging.info(f"Created pine cone index: {index_name}")

# Connect to the index
pinecone_index = pc.Index(index_name)
logging.info(f"Successfully connected to Pinecone index: {index_name}")
vector_store = PineconeVectorStore(index=pinecone_index, embedding=OpenAIEmbeddings())


async def add_directory_documents_to_pinecone_index():
    pass
