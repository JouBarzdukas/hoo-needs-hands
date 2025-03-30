from langchain_openai import ChatOpenAI

def general_knowledge_tool(query: str) -> str:
    """
    Answers a general knowledge question using ChatOpenAI.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    messages = [{"role": "user", "content": query}]
    response = llm.invoke(messages)
    return response.content.strip()