from typing import List, Optional
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Initialize the vector store and embeddings
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(
    collection_name="sentences",
    embedding_function=embeddings,
    persist_directory="./data/chroma"
)

@tool
def store_sentence(sentence: str) -> str:
    """
    Store a single sentence in the vector database.
    """
    try:
        # Add the sentence to the vector store
        vectorstore.add_texts([sentence])
        vectorstore.persist()
        return f"Successfully stored sentence: {sentence}"
    except Exception as e:
        return f"Error storing sentence: {e}"

@tool
def search_sentences(query: str, k: int = 1) -> str:
    """
    Search for similar sentences using semantic similarity.
    Args:
        query: The search query
        k: Number of results to return (default: 5)
    """
    try:
        # Perform similarity search
        results = vectorstore.similarity_search(query, k=1)
        # Format results
        formatted_results = "\n".join([f"- {doc.page_content}" for doc in results])
        return f"Found {len(results)} similar sentences:\n{formatted_results}"
    except Exception as e:
        return f"Error searching sentences: {e}"

@tool
def list_all_sentences() -> str:
    """
    List all sentences stored in the database.
    """
    try:
        # Get all documents from the vector store
        results = vectorstore.get()
        if not results['documents']:
            return "No sentences stored yet."
        
        # Format results
        formatted_results = "\n".join([f"- {doc}" for doc in results['documents']])
        return f"All stored sentences:\n{formatted_results}"
    except Exception as e:
        return f"Error listing sentences: {e}" 