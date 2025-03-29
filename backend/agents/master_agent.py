import json
import re
from langchain_openai import ChatOpenAI
from langgraph.types import Command

# Initialize the master LLM.
master_llm = ChatOpenAI(model="gpt-4o", temperature=0)

def master_agent(state: dict) -> Command:
    """
    The master agent:
      1. Determines which agent should handle the command
      2. Delegates the command directly to that agent
      3. Returns END once the agent has executed
    """
    # Get the initial command
    initial_msg = state["messages"][0]
    initial_command = (
        initial_msg.get("content", "")
        if isinstance(initial_msg, dict) else str(initial_msg)
    )

    # Determine which agent should handle this command
    prompt = (
        f"You are the master agent. The user command is: '{initial_command}'.\n"
        "Determine which agent should handle this command. The possible agents are:\n"
        "- browser_agent: for web browsing, searching, opening websites\n"
        "- computer_agent: for opening applications, files, or system operations\n"
        "- db_agent: for database operations on the user's database, db contains the user's data\n"
        "Respond with ONLY the agent name, nothing else.\n"
        "Example: browser_agent"
    )
    
    response_obj = master_llm.invoke([{"role": "user", "content": prompt}])
    agent_name = response_obj.content.strip().lower()
    
    # Set the command for the agent
    state["current_command"] = initial_command
    
    # Add a debug message for the conversation
    delegation_msg = {
        "role": "assistant",
        "content": f"Master Agent: Delegating to {agent_name} - '{initial_command}'."
    }
    state["messages"].append(delegation_msg)
    
    # If the agent has already executed, we're done
    if state.get(f"{agent_name}_executed"):
        final_message = {"role": "assistant", "content": "Master Agent: Task completed."}
        state["messages"].append(final_message)
        return Command(goto="END", update=state)
    
    # Otherwise, delegate to the agent
    return Command(goto=agent_name, update=state)
