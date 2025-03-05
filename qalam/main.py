from loguru import logger

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

    logger.info("Initialized classes")

    user_prompt = input("Ask something about your codebase: ")

    docs_with_context = pinecone_db.query_stub_docs(user_prompt)
    system_prompt = generate_plan_system_prompt(docs_with_context, user_prompt)
    llm_res = llm.invoke_chat(system_prompt)

    docs_with_context = pinecone_db.query_code_docs(llm_res)
    system_prompt = generate_code_impl_system_prompt(docs_with_context)
    llm_res = llm.invoke_chat(system_prompt)
