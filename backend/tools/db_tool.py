from typing import List, Optional
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from voice.text_to_speech import text_to_speech

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
    # try:
    #     # Add the sentence to the vector store
    #     vectorstore.add_texts([sentence])
    #     # vectorstore.persist()
    #     # var = f"I have stored the following message in the database: {formatted_results}"
    #     # text_to_speech(var)
    #     return f"Successfully stored sentence: {sentence}"
    # except Exception as e:
    #     text_to_speech("There was an error storing your sentence. Please try again.")
    #     return f"Error storing sentence: {e}"
    vectorstore.add_texts([sentence])
    print("here1")
    text_to_speech(f"Successfully stored sentence: {sentence}")
    print("here2")

@tool
def search_sentences(query: str, k: int = 1) -> str:
    """
    Search for similar sentences using semantic similarity.
    Args:
        query: The search query
        k: Number of results to return (default: 5)
    """
    # try:
    #     # Perform similarity search
    #     results = vectorstore.similarity_search(query, k=1)
    #     # Format results
    #     formatted_results = "\n".join([f"- {doc.page_content}" for doc in results])
    #     llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    #     messages = [
    #         {
    #             "role": "system",
    #             "content": "You are a helpful assistant that provides concise, conversational answers. Keep responses short and natural, as if speaking to someone. Avoid complex language or lengthy explanations. Your task is to find the most relevant information from a query of memorys in a database and create a single concise response to convey the information to the user. For example, if the raw memory is 'today is friday 3/21/2020 and it is brian's birthday', you should summarize the information and say something like 'Based on the information in the database Brian's birthday is on Friday, March 21st, 2020'. Make sure to include the most relevant information from the database in your response. If there is no relevant information found, please inform the user that no match was found and suggest refining their search."
    #         },
    #         {"role": "user", "content": str({
    #             "user_query": query,
    #             "db_results": formatted_results
    #         })}
    #     ]
    #     response = llm.invoke(messages)
    #     # var = f"The top result from your database is {formatted_results}"
    #     text_to_speech(response)
    #     # print(var)
    #     return f"Found {len(results)} similar sentences:\n{formatted_results}"
    # except Exception as e:
    #     text_to_speech("It seems like there was no match found for your query. Please refine your search or try a different query.")
    #     return f"Error searching sentences: {e}"

    print("here3")
    results = vectorstore.similarity_search(query, k=1)
    # Format results
    formatted_results = "\n".join([f"- {doc.page_content}" for doc in results])
    print("formatted_results", formatted_results)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides concise, conversational answers. Keep responses short and natural, as if speaking to someone. Avoid complex language or lengthy explanations. Your task is to find the most relevant information from a query of memorys in a database and create a single concise response to convey the information to the user. For example, if the raw memory is 'today is friday 3/21/2020 and it is brian's birthday', you should summarize the information and say something like 'Based on the information in the database Brian's birthday is on Friday, March 21st, 2020'. Make sure to include the most relevant information from the database in your response. If there is no relevant information found, please inform the user that no match was found and suggest refining their search."
        },
        {"role": "user", "content": str({
            "user_query": query,
            "db_results": formatted_results
        })}
    ]
    response = llm.invoke(messages)
    # var = f"The top result from your database is {formatted_results}"
    print("here4")
    text_to_speech(response.content)
    # print(var)
    return f"Found {len(results)} similar sentences:\n{formatted_results}"

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