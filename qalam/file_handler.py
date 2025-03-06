import json
from datetime import datetime
from enum import StrEnum

from langchain_core.documents import Document
from pydantic import BaseModel


class FileReadType(StrEnum):
    STUB_PROMPT = "STUB_PROMPT"
    LLM_STUBS = "LLM_STUBS"


class StubPrompt(BaseModel):
    prompt: str


class LllmStubs(BaseModel):
    response: str


class CodeStubsSystemPrompt(BaseModel):
    prompt: str


class FileHandler:
    def __init__(self) -> None:
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def read_file(self, read_type: FileReadType) -> str:
        file_path: str
        match read_type:
            case FileReadType.STUB_PROMPT:
                file_path = "./inputs/stub_prompt.txt"
            case FileReadType.LLM_STUBS:
                file_path = "./inputs/llm_stubs.txt"

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _save_dict_to_file(self, file_path: str, data: dict | list):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _save_str_to_file(self, file_path: str, data: str):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)

    def save_stub_prompt_docs(self, documents: list[Document]):
        file_path = f"./outputs/{self.timestamp}_stub_prompt_docs.json"
        json_data = [doc.model_dump(mode="json") for doc in documents]
        self._save_dict_to_file(file_path, json_data)

    def save_code_stubs_system_prompt(self, prompt: str):
        file_path = f"./outputs/{self.timestamp}_code_stubs_system_prompt.txt"
        self._save_str_to_file(file_path, prompt)

    def save_llm_stubs_response(self, res: str):
        file_path = f"./outputs/{self.timestamp}_llm_stubs.txt"
        self._save_str_to_file(file_path, res)
