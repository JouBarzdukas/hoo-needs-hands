from langchain_openai import ChatOpenAI
from langgraph.types import Command
from tools.browseruse_tool import browseruse_tool

def browser_agent(state: dict) -> Command:
    """
    The Browser agent. Invoked if the master agent decides a step belongs here.
    We only run once per user request. If 'browser_agent_executed' is set, we skip.
    Otherwise, we do the step, possibly calling browseruse_tool exactly once.
    """
    # If this agent already executed, skip.
    if state.get("browser_agent_executed"):
        return Command(goto="master_agent", update=state)

    # Mark that we are now "in use," so we won't re-run.
    state["browser_agent_executed"] = True
    
    # Use the correct model name.
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    llm_with_tools = llm.bind_tools([browseruse_tool])
    
    current_command = state.get("current_command", "")
    
    # Prompt to encourage the LLM to optionally call the tool once.
    prompt = (
        f"You are the Browser agent. The user wants to: '{current_command}'.\n"
        "You may call 'browseruse_tool' exactly once (if needed) to perform a browser action. "
        "After that, just summarize. If no browser action is relevant, simply respond with a text summary.\n"
        "Example usage:\n"
        "tool_call: browseruse_tool {\"command\": \"search cat videos\"}\n"
    )
    
    messages_for_prompt = state.get("messages", []) + [
        {"role": "user", "content": prompt}
    ]

    # Let the LLM respond with either plain text or a single tool_call:
    message = llm_with_tools.invoke(messages_for_prompt)
    
    # Debug: print the raw message output.
    print("DEBUG: Raw browser agent message output:", message)
    
    # Attempt to get content from the LLM response.
    content = getattr(message, "content", "")
    
    # If no content was returned and a tool call is present, execute the tool.
    if not content and hasattr(message, "additional_kwargs") and message.additional_kwargs.get("tool_calls"):
        tool_call = message.additional_kwargs["tool_calls"][0]
        if tool_call.get("name") == "browseruse_tool":
            args_dict = tool_call.get("args", {})
            # Check for "v__args" key first, then fallback to "command"
            if "v__args" in args_dict:
                args_list = args_dict.get("v__args", [])
            elif "command" in args_dict:
                args_list = [args_dict.get("command")]
            else:
                args_list = []
            tool_result = browseruse_tool({"v__args": args_list})  # Pass as dict
            content = f"Browser Agent executed tool: {tool_result}"
    
    # Fallback if still no content.
    if not content:
        content = "Browser Agent: No further response."
    else:
        content = content.strip()
    
    # Record the response.
    state["messages"].append({"role": "assistant", "content": content})

    # Return control to master agent.
    return Command(goto="master_agent", update=state)