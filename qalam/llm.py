from loguru import logger
from langchain_openai import ChatOpenAI
from pydantic import SecretStr, ValidationError

from qalam.config import settings


class LLM:
    def __init__(self) -> None:
        logger.info("Initializing OpenAI client...")

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=SecretStr(settings.openai_api_key),
        )

        logger.info("OpenAI client initialized successfully.")

    def invoke_chat(
        self,
        prompt: str,
        history_message: tuple[str, str] | None = None,
    ) -> str:
        llm_messages: list[tuple]
        if history_message:
            llm_messages = [
                (
                    "developer",
                    "You are a helpful assistant that answers programming questions and writes good quality code",
                ),
                (
                    "user",
                    history_message[0],
                ),
                (
                    "assistant",
                    history_message[1],
                ),
                (
                    "user",
                    prompt,
                ),
            ]
        else:
            llm_messages = [
                (
                    "developer",
                    "You are a helpful assistant that answers programming questions and writes good quality code",
                ),
                (
                    "user",
                    prompt,
                ),
            ]

        llm_res = self.llm.invoke(llm_messages)
        response_text = llm_res.content

        logger.info("LLM response text: {}", response_text)

        if isinstance(response_text, str):
            return response_text
        else:
            logger.error("llm response wasn't of type str", response=response_text)
            raise ValidationError("LLM response wasn't a str")
