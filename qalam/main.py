from loguru import logger

from qalam.file_handler import FileHandler, FileReadType, LllmStubs, StubPrompt
from qalam.config import settings
from qalam.llm import LLM
from qalam.pinecone import PineconeDb
from qalam.static_analyser import StaticAnalyser
from qalam.utils import (
    generate_code_impl_system_prompt,
    generate_plan_system_prompt,
    parse_python_code_to_embedding_documents,
    parse_python_file_analysis_to_embedding_documents,
)


def analyze_files_and_add_docs_to_index(
    static_analyser: StaticAnalyser,
    pinecone_db: PineconeDb,
):
    # directory = input("Enter directory path to analyze: ")
    # if directory == "-1":
    #     directory = settings.default_dir

    directory = settings.default_dir
    analysis_files = static_analyser.analyze_directory(directory)

    # Embedding stubs
    documents = parse_python_file_analysis_to_embedding_documents(analysis_files)
    ids = [f.file_path.replace("/", "-") for f in analysis_files]
    pinecone_db.add_documents_to_pinecone_index(documents, ids)

    # Embedding actual code
    documents = parse_python_code_to_embedding_documents(analysis_files)
    pinecone_db.add_documents_to_pinecone_index(documents)


if __name__ == "__main__":
    static_analyser = StaticAnalyser()
    pinecone_db = PineconeDb()
    llm = LLM()
    file_handler = FileHandler()

    logger.info("Initialized classes")

    print("Choose any option")
    print(">>> 1: Generate stubs")
    print(">>> 2: Generate code implementation from stubs provided")

    user_input = input()

    if user_input == "1":
        user_prompt = file_handler.read_file(FileReadType.STUB_PROMPT)
        logger.info("User prompt: {}", user_prompt)

        docs_with_context = pinecone_db.query_stub_docs(user_prompt)
        file_handler.save_stub_prompt_docs(docs_with_context)

        system_prompt = generate_plan_system_prompt(docs_with_context, user_prompt)
        file_handler.save_code_stubs_system_prompt(system_prompt)

        llm_res = llm.invoke_chat(system_prompt)
        file_handler.save_llm_stubs_response(llm_res)

    elif user_input == "2":
        # TODO:  Incomplete stuff
        raise NotImplementedError
        stubs_llm_res = file_handler.read_file(FileReadType.LLM_STUBS)
        logger.info("Stubs llm response: {}", stubs_llm_res)

        docs_with_context = pinecone_db.query_code_docs(stubs_llm_res)
        system_prompt = generate_code_impl_system_prompt(docs_with_context)

        # TODO: Handle llm chat history appropriately
        llm_res = llm.invoke_chat(system_prompt)

    else:
        print("Invalid option, quitting...")
