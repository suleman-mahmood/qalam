import logging
from pydantic_settings import BaseSettings, SettingsConfigDict


# Logging setup
logging.basicConfig(
    filename="data/logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Logging initialized.")


# Configuration settings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="QALAM_", env_nested_delimiter="__")

    openai_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = ""


logging.info("Loading configuration from environment variables.")
settings = Settings()
logging.info("Configuration loaded successfully.")
