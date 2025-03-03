import logging

from langchain_openai import ChatOpenAI
from pydantic import SecretStr, ValidationError
from qalam.config import settings
from qalam.pinecone import pinecone_index
from qalam.pinecone import vector_store


def query_rag(query: str):
    logging.info(f"Received query: {query}")

    # Step 2: Query Pinecone for relevant documents
    logging.info("Retrieving relevant documents from Pinecone...")
    try:
        retrieved_docs = vector_store.similarity_search(query=query)
        if not retrieved_docs:
            logging.warning("No relevant documents found in Pinecone.")
            raise ValidationError(
                "I'm sorry, I couldn't find any relevant information in the database.",
            )
        logging.info(f"Retrieved {len(retrieved_docs)} documents: {retrieved_docs}")
    except Exception as retrieval_error:
        logging.error(
            f"Error during document retrieval from Pinecone: {retrieval_error}"
        )
        try:
            pinecone_stats = pinecone_index.describe_index_stats()
            logging.info(f"Pinecone index stats: {pinecone_stats}")
        except Exception as stats_error:
            logging.error(f"Error fetching Pinecone index stats: {stats_error}")
        raise ValidationError("Error retrieving documents from Pinecone.")

    # Step 3: Combine retrieved context for LLM prompt
    logging.info("Combining retrieved context...")
    try:
        context = "\n".join([doc.page_content for doc in retrieved_docs])
        if not context.strip():
            logging.warning("Retrieved documents have no valid content.")
            raise ValidationError(
                "No relevant information found in the database. Please refine your query.",
            )
        logging.info(
            f"Retrieved context: {context[:200]}..."
        )  # Log snippet of the context
    except Exception as context_error:
        logging.error(f"Error combining retrieved context: {context_error}")
        raise ValidationError("Error combining retrieved context.")

    # Step 4: Query the LLM with contextualized prompt
    prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
    logging.info(f"Generated prompt: {prompt[:200]}...")  # Log snippet of the prompt
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=SecretStr(settings.openai_api_key),
        )
        messages = [
            ("system", "You are a helpful assistant."),
            ("user", prompt),
        ]
        llm_res = llm.invoke(messages)
        logging.info("LLM response received.")
    except Exception as llm_error:
        logging.error(f"Error during LLM query: {llm_error}")
        raise ValidationError("Error querying the language model.")

    # Step 5: Extract response text from LLM output
    logging.info("Extracting response text from LLM output...")
    try:
        response_text = llm_res.content
        logging.info(f"LLM response text: {response_text}")
        return response_text
    except Exception as parse_error:
        logging.error(f"Error parsing LLM response: {parse_error}")
        raise ValidationError("Error parsing the LLM response.")
