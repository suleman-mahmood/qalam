from loguru import logger
from qalam.llm import LLM
from qalam.pinecone import PineconeDb
from qalam.static_analyser import StaticAnalyser
from qalam.utils import parse_python_file_analysis_to_embedding_documents

if __name__ == "__main__":
    static_analyser = StaticAnalyser()
    pinecone_db = PineconeDb()
    llm = LLM()

    logger.info("Initialized classes")

    directory = input("Enter directory path to analyze: ")
    if directory == "-1":
        directory = "/Users/sulemanmahmood/Projects/mazlo/mazlo-backend"

    analysis_files = static_analyser.analyze_directory(directory)
    documents = parse_python_file_analysis_to_embedding_documents(analysis_files)

    # Print results
    # for data in analysis_files[:5]:
    #     print(f"\nFile: {data.file_path}")
    #     print(f"Classes: {data.classes}")
    #     print(f"Functions: {data.functions}")
    #     print(f"Imports: {data.imports}")
    #
    # for doc in documents[:5]:
    #     print(doc)

    """ Write files to pinecone db index """
    # ids = [f.file_path.replace("/", "-") for f in analysis_files]
    # pinecone_db.add_directory_documents_to_pinecone_index(documents, ids)

    user_prompt = input("Ask something about your codebase: ")

    docs_with_context = pinecone_db.query_docs_for_prompt(user_prompt)
    system_prompt = pinecone_db.generate_system_prompt(docs_with_context, user_prompt)

    llm_res = llm.invoke_chat(system_prompt)
