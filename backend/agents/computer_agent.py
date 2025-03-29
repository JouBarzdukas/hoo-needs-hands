from langchain_openai import ChatOpenAI
from langgraph.types import Command
from tools.computeruse_tool import computeruse_tool

def computer_agent(state: dict) -> Command:
    """
    Computer agent uses its LLM bound to the computer tool to process the current command (state["current_command"]).
    It outputs a message that contains a tool call if a computer action is required.
    """
    llm = ChatOpenAI(model="gpt-4o")
    llm_with_tools = llm.bind_tools([computeruse_tool])
    prompt = (
        f"You are the Computer agent. Process the command: '{state.get('current_command', '')}'.\n"
        "If you need to perform a computer action, output a tool_call with name 'computeruse_tool' and "
        "arguments as a JSON object with a 'command' key. Otherwise, simply return your result."
    )
    state["messages"].append({"role": "user", "content": prompt})
    message = llm_with_tools.invoke(state["messages"])
    return Command(goto="master_agent", update={"messages": [message]})
