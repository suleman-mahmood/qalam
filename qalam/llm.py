from loguru import logger
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from qalam.config import settings


class LLM:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=SecretStr(settings.openai_api_key),
        )

    def generate_messages(self, prompt: str) -> list[tuple[str, str]]:
        return [
            ("system", "You are a helpful assistant."),
            ("user", prompt),
        ]

    def invoke_chat(self, prompt: str) -> str | list[str | dict]:
        messages = self.generate_messages(prompt)
        llm_res = self.llm.invoke(messages)
        logger.info("LLM response received.")

        response_text = llm_res.content
        logger.info("LLM response text: {}", response_text)

        return response_text
