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
        Instructions: Give only the implementation plan that includes the code stubs. An example of code stubs to implement login system:

            ### ###
            ### schema/user_models.py
            ### ###

            from typing import Optional

            class User:
                user_id: int
                username: str

            class LoginSchema(BaseModel):
                email: str
                hashed_password: str

            ### ###
            ### controllers/auth.py
            ### ###

            from typing import Optional
            from models import User

            # Registers a new user and returns the created User object.
            def register_user(username: str, email: str, password: str) -> User:
                raise NotImplementedError

            # Retrieves a user by their unique ID. Returns None if not found.
            def get_user_by_id(user_id: int) -> Optional[User]:
                raise NotImplementedError

            # Authenticates a user with the given username and password.
            # Returns a session token as a string if authentication is successful, otherwise None.
            def login(username: str, password: str) -> Optional[str]:
                raise NotImplementedError

            # Validates the provided session token.
            # Returns True if the token is valid, False otherwise.
            def validate_token(token: str) -> bool:
                raise NotImplementedError

            # Logs out the user by invalidating the session token.
            # Returns True if logout is successful.
            def logout(token: str) -> bool:
                raise NotImplementedError

            ### ###
            ### routes/auth_routes.py
            ### ###

            @fs_router.post("/login")
            @proj_router.post("/login")
            async def login_route(
                body: LoginUserBody
                fiscal_sponsor_id: str,
                project_id: str | None = None,
                data_context: DataContext = Depends(get_data_context()),
            ):
                # TODO: Use bcrypt
                raise NotImplementedError

        Answer:
    """
    logger.info("Generated prompt: {}...", user_prompt[:200])

    return system_prompt


def generate_code_impl_system_prompt() -> str:
    system_prompt = """
        Question: Write complete code implementation
        Instructions: Give code implementation for the code stubs in the above step. An example of code implementation:

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
                await auth_db.login_user(data_context, data_context.user_id)

                return SuccessResponse()

        Answer:
    """
    logger.info("Generated prompt: {}...", system_prompt[:200])

    return system_prompt
