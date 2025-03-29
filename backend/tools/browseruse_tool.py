import asyncio
from langchain_core.tools import tool
from browser_use import Agent as BrowserAgent
from langchain_openai import ChatOpenAI

@tool
def browseruse_tool(command: str) -> str:
    """
    Executes a browser command using the browser-use tool.
    Args:
        command: The command to execute in the browser
    """
    print(f"DEBUG: Command received in browseruse_tool: '{command}'")
    
    # Format the command to be more explicit
    formatted_command = command
    
    print(f"DEBUG: Formatted command being passed to BrowserAgent: '{formatted_command}'")
    
    # Instantiate and run the BrowserAgent synchronously.
    agent = BrowserAgent(task=formatted_command, llm=ChatOpenAI(model="gpt-4o"))
    # Run the async function in a synchronous context
    result = asyncio.run(agent.run())
    return result
