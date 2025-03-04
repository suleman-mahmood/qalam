from loguru import logger
from qalam.llm import LLM
from qalam.pinecone import PineconeDb
from qalam.static_analyser import StaticAnalyser

if __name__ == "__main__":
    static_analyser = StaticAnalyser()
    pinecone_db = PineconeDb()
    llm = LLM()

    logger.info("Initialized classes")

    breakpoint()

    directory = input("Enter directory path to analyze: ")
    if directory == "-1":
        directory = "/Users/sulemanmahmood/Projects/mazlo/mazlo-backend"

    result = static_analyser.analyze_directory(directory)

    # Print results
    for file, data in result.items():
        print(f"\nFile: {file}")
        print(f"Classes: {data['classes']}")
        print(f"Functions: {data['functions']}")
        print(f"Imports: {data['imports']}")

    documents = static_analyser.get_directory_documents(directory)
    pinecone_db.add_directory_documents_to_pinecone_index(documents)

    user_prompt = input("Ask something about your codebase: ")

    docs_with_context = pinecone_db.query_docs_for_prompt(user_prompt)
    system_prompt = pinecone_db.generate_system_prompt(docs_with_context, user_prompt)

    llm_res = llm.invoke_chat(system_prompt)
    print(llm_res)
