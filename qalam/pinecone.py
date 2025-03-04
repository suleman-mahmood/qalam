import time
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from loguru import logger
from pinecone import Pinecone, ServerlessSpec
from pydantic import SecretStr, ValidationError
from qalam.config import settings


class PineconeDb:
    def __init__(self) -> None:
        logger.info("Initializing Pinecone client...")
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        logger.info("Pinecone client initialized successfully.")

        # Check if index exists
        self.index_name = settings.pinecone_index_name

        if self.index_name not in [
            index_info["name"] for index_info in self.pc.list_indexes()
        ]:
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                deletion_protection="enabled",
            )
            while not self.pc.describe_index(self.index_name).status["ready"]:
                time.sleep(1)

            logger.info("Created pine cone index: {}", self.index_name)

        # Connect to the index
        self.pinecone_index = self.pc.Index(self.index_name)
        logger.info("Successfully connected to Pinecone index: {}", self.index_name)

        self.vector_store = PineconeVectorStore(
            index=self.pinecone_index,
            embedding=OpenAIEmbeddings(api_key=SecretStr(settings.openai_api_key)),
        )

    def add_documents_to_pinecone_index(self, documents: list[str], ids: list[str]):
        docs = [Document(page_content=d) for d in documents]
        self.vector_store.add_documents(documents=docs, ids=ids)

    def query_docs_for_prompt(self, prompt: str) -> list[Document]:
        logger.info("Retrieving relevant documents from Pinecone...")

        try:
            retrieved_docs = self.vector_store.similarity_search(query=prompt)
            if not retrieved_docs:
                logger.error("No relevant documents found in Pinecone.")
                raise ValidationError(
                    "I'm sorry, I couldn't find any relevant information in the database.",
                )
            logger.info(
                "Retrieved {} documents: {}", len(retrieved_docs), retrieved_docs
            )

        except Exception as retrieval_error:
            logger.error(
                "Error during document retrieval from Pinecone: {}", retrieval_error
            )
            try:
                pinecone_stats = self.pinecone_index.describe_index_stats()
                logger.info("Pinecone index stats: {}", pinecone_stats)
            except Exception as stats_error:
                logger.error("Error fetching Pinecone index stats: {}", stats_error)
            finally:
                raise ValidationError("Error retrieving documents from Pinecone.")

        return retrieved_docs
