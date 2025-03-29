from langchain_openai import ChatOpenAI
from langgraph.types import Command
from tools.browseruse_tool import browseruse_tool

def browser_agent(state: dict) -> Command:
    """
    The Browser agent. Invoked if the master agent decides a step belongs here.
    We only run once per user request. If 'browser_agent_executed' is set, we skip.
    Otherwise, we do the step, possibly calling browseruse_tool exactly once.
    """
    # If this agent already executed, skip
    if state.get("browser_agent_executed"):
        return Command(goto="END", update=state)

    # Mark that we are now "in use," so we won't re-run
    state["browser_agent_executed"] = True
    
    # Get the command from the current_command in state
    current_command = state.get("current_command", "")
    if not current_command:
        # If no current_command, try to get it from the last message
        messages = state.get("messages", [])
        if messages:
            current_command = messages[0].get("content", "")
    
    print(f"DEBUG: Current command in browser_agent: '{current_command}'")
    
    if not current_command:
        content = "Browser Agent: No command received."
        state["messages"].append({"role": "assistant", "content": content})
        return Command(goto="END", update=state)
    
    # Execute the browser tool directly with the command
    try:
        result = browseruse_tool(current_command)
        content = f"Browser Agent: Executed command '{current_command}'. Result: {result}"
    except Exception as e:
        content = f"Browser Agent: Error executing command: {str(e)}"
    
    # Record the response
    state["messages"].append({"role": "assistant", "content": content})

    # Return control to END
    return Command(goto="END", update=state)
