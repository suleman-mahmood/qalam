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


def parse_python_code_to_embedding_documents(
    analysis_filse: list[PythonFileAnalysis],
) -> list[str]:
    result: list[str] = []
    for file in analysis_filse:
        defs = file.functions_defs + file.classes_defs
        for d in defs:
            out = f"""
            File path: {file.file_path}
            {d}
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
        Instructions:
            - Give only the implementation plan that includes the code stubs.
            - You can also re-use functions / classes in the context if it seems suitable to edit them instead of creating new ones
            - An example of code stubs to implement login system:

            ### schema/user_models.py

            class LoginData(BaseModel):
                pass

            ### routes/auth_routes.py

            @fs_router.post("/login")
            @proj_router.post("/login")
            async def login_route(
                body: LoginUserBody
                fiscal_sponsor_id: str,
                project_id: str | None = None,
                data_context: DataContext = Depends(get_data_context()),
            ):
                raise NotImplementedError

            ### interface/auth_db.py

            @dal()
            async def get_auth_token(data_context: DataContext, user_id: str):
                raise NotImplementedError

            ### controllers/auth.py

            async def login_user(data_context: DataContext, data: LoginData) -> Session:
                raise NotImplementedError

        Answer:
    """
    logger.info("Generated prompt: {}...", user_prompt[:200])

    return system_prompt


def generate_code_impl_system_prompt(retrieved_docs: list[Document]) -> str:
    context = "\n".join([doc.page_content for doc in retrieved_docs])

    system_prompt = f"""
        Context: {context}
        Question: Write complete code implementation
        Instructions:
            - Give code implementation for the code stubs in the above step.
            - An example of code implementation:

            ### ###
            ### routes/auth_routes.py
            ### ###

            @fs_router.post("")
            @proj_router.post("")
            async def login_user_route(
                body: LoginUserBody,
                fiscal_sponsor_id: str,
                project_id: str | None = None,
                data_context: DataContext = Depends(get_data_context()),
            ):
                financial_unit_id = project_id or fiscal_sponsor_id
                await auth_db.get_auth_token(data_context, data_context.user_id)

                return SuccessResponse()

        Answer:
    """
    logger.info("Generated prompt: {}...", system_prompt[:200])

    return system_prompt
