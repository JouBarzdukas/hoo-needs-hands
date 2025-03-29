from langchain_core.tools import tool

@tool
def computeruse_tool(args: dict) -> str:
    """
    Simulates executing a computer command.
    Expects args to be a dict with key "command".
    """
    command_str = args.get("command", "")
    return f"Computer action executed: {command_str}"
