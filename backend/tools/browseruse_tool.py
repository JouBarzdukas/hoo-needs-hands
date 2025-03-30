import asyncio
from langchain_core.tools import tool
from browser_use import Agent as BrowserAgent
from browser_use import Browser, BrowserConfig
from langchain_openai import ChatOpenAI
import os

@tool
def browseruse_tool(command: str) -> str:
    """
    Executes a browser command using the browser-use tool.
    Args:
        command: The command to execute in the browser
    """
    device = os.getenv('DEVICE', 'macos').lower()
    if device not in ['mac', 'windows', 'linux']:
        raise ValueError("Invalid DEVICE environment variable. Must be 'macos', 'windows', or 'linux'.")

    if device == 'mac':
        device = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    elif device == 'windows':
        device = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    elif device == 'linux':
        device = '/usr/bin/google-chrome'

    browser = Browser(
    config=BrowserConfig(
        # Specify the path to your Chrome executable
        chrome_instance_path=device
        # chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
        # For Windows, typically: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        # For Linux, typically: '/usr/bin/google-chrome'
    )
    )

    print(f"DEBUG: Command received in browseruse_tool: '{command}'")
    
    # Format the command to be more explicit
    formatted_command = command
    
    print(f"DEBUG: Formatted command being passed to BrowserAgent: '{formatted_command}'")
    
    # Instantiate and run the BrowserAgent synchronously.
    agent = BrowserAgent(task=formatted_command, llm=ChatOpenAI(model="gpt-4o"), browser=browser)
    # Run the async function in a synchronous context
    result = asyncio.run(agent.run())
    return result
