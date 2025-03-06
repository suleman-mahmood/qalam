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

    def read_file(self, read_type: FileReadType) -> BaseModel:
        file_path: str
        match read_type:
            case FileReadType.STUB_PROMPT:
                file_path = "./inputs/stub_prompt.json"
                return StubPrompt.parse_file(file_path)
            case FileReadType.LLM_STUBS:
                file_path = "./inputs/llm_stubs.json"
                return LllmStubs.parse_file(file_path)

    def _save_dict_to_file(self, file_path: str, data: dict | list):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def save_stub_prompt_docs(self, documents: list[Document]):
        file_path = f"./outputs/{self.timestamp}_stub_prompt_docs.json"
        json_data = [doc.model_dump(mode="json") for doc in documents]
        self._save_dict_to_file(file_path, json_data)

    def save_code_stubs_system_prompt(self, prompt: str):
        sys_prompt = CodeStubsSystemPrompt(prompt=prompt)
        file_path = f"./outputs/{self.timestamp}_code_stubs_system_prompt.json"
        self._save_dict_to_file(file_path, sys_prompt.model_dump(mode="json"))

    def save_llm_stubs_response(self, res: str):
        llm_stubs = LllmStubs(response=res)
        file_path = f"./outputs/{self.timestamp}_llm_stubs.json"
        self._save_dict_to_file(file_path, llm_stubs.model_dump(mode="json"))
