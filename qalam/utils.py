from langchain_core.documents import Document
from loguru import logger
from pydantic import ValidationError
from qalam.static_analyser import PythonFileAnalysis


def parse_python_file_analysis_to_embedding_documents(
    analysis_filse: list[PythonFileAnalysis],
) -> list[str]:
    result: list[str] = []
    for f in analysis_filse:
        out = f"""
        File name with relative path: {f.file_path}
        {f"Defined classes: {f.classes}" if f.classes else "No classes defined"}
        {f"Defined functions: {f.functions}" if f.functions else "No functions defined"}
        {f"Imports used in file: {f.imports}" if f.imports else "No imports used in file"}
        """
        result.append(out)

    return result


def generate_plan_system_prompt(
    retrieved_docs: list[Document],
    user_prompt: str,
) -> str:
    logger.info("Combining retrieved context...")
    try:
        context = "\n".join([doc.page_content for doc in retrieved_docs])
        if not context.strip():
            logger.error("Retrieved documents have no valid content.")
            raise ValidationError(
                "No relevant information found in the database. Please refine your query.",
            )
        logger.info("Retrieved context: {}...", context[:200])
    except Exception as context_error:
        logger.error("Error combining retrieved context: {}", context_error)
        raise ValidationError("Error combining retrieved context.")

    system_prompt = f"""
        Context: {context}
        Question: {user_prompt}
        Instructions: Give only a plan for the implementation, that includes the stubs for:
            - any files that need to be created or edited
            - any functions that need to be created or edited
            - any classes that need to be created or edited
            - any tests that need to be created or edited
            - or any other stubs that need to be created or edited
        Answer:
    """
    logger.info("Generated prompt: {}...", user_prompt[:200])

    return system_prompt
