from langchain_openai import ChatOpenAI

def general_knowledge_tool(query: str) -> str:
    """
    Answers a general knowledge question using ChatOpenAI.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    # messages = [{"role": "user", "content": query}]
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides concise, conversational answers. Keep responses short and natural, as if speaking to someone. Avoid complex language or lengthy explanations."
        },
        {"role": "user", "content": query}
    ]
    response = llm.invoke(messages)
    return response.content.strip()