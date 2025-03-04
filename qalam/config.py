import sys
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


_is_logging_configured = False


def setup_logging():
    global _is_logging_configured  # noqa: PLW0603
    if _is_logging_configured:
        return

    serialize = False
    log_format = "<g>{time}</g> {level} <c>{module}.{file}:{line}</c> <bold>{message}</bold>\n  <le>{extra}</le>"
    sink = sys.stderr

    logger.configure(
        handlers=[
            {
                "sink": sink,
                "level": settings.log_level.upper(),
                "serialize": serialize,
                "format": log_format,
            }
        ]
    )

    _is_logging_configured = True


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="QALAM_", env_nested_delimiter="__")
    log_level: str = "INFO"

    deepseek_api_key: str = ""
    openai_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = ""


settings = Settings()
setup_logging()

logger.info("Configuration loaded successfully.")
