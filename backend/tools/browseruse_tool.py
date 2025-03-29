import asyncio
from langchain_core.tools import tool
from browser_use import Agent as BrowserAgent
from langchain_openai import ChatOpenAI

@tool
def browseruse_tool(args: dict) -> str:
    """
    Executes a browser command using the browser-use tool.
    Expects args to be a dict with a 'command' key.
    If the key 'v__args' is present, use its first element as the command.
    """
    if "v__args" in args:
        command_list = args["v__args"]
        command_str = command_list[0] if command_list else ""
    else:
        command_str = args.get("command", "")
    
    # Instantiate and run the BrowserAgent synchronously.
    agent = BrowserAgent(task=command_str, llm=ChatOpenAI(model="gpt-4o"))
    result = agent.run()  # Assuming `run()` is a synchronous method.
    return result
