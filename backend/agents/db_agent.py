from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langgraph.graph import END
from tools.db_tool import db_retriever_tool

def db_agent(state: dict) -> Command:
    """
    DB agent uses its LLM bound to the retriever tool to process the current command (state["current_command"]).
    It produces an output message that includes a tool call if retrieval is needed.
    """
    llm = ChatOpenAI(model="gpt-4o")
    llm_with_tools = llm.bind_tools([db_retriever_tool])
    prompt = (
        f"You are the DB agent. Process the command: '{state.get('current_command', '')}'.\n"
        "If you need to retrieve information, output a tool_call with name 'retrieve_blog_posts' and "
        "arguments as a JSON object with a 'query' key. Otherwise, simply return the result."
    )
    state["messages"].append({"role": "user", "content": prompt})
    message = llm_with_tools.invoke(state["messages"])
    return Command(goto="master_agent", update={"messages": [message]})
