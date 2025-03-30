from dotenv import load_dotenv
import os
load_dotenv()  # loads variables from .env file, including OPENAI_API_KEY

from langchain_openai import ChatOpenAI
from langgraph.types import Command

# Initialize the master LLM.
master_llm = ChatOpenAI(model="gpt-4o", temperature=0)

def master_agent(state: dict) -> Command:
    """
    The master agent:
      1. Determines which agent should handle the command.
      2. Delegates the command directly to that agent.
      3. Returns END once the delegated agent has executed.
    """
    # Get the initial command.
    initial_msg = state["messages"][0]
    initial_command = (
        initial_msg.get("content", "")
        if isinstance(initial_msg, dict) else str(initial_msg)
    )

    # Determine which agent should handle this command.
    prompt = (
        f"You are the master agent. The user command is: '{initial_command}'.\n"
        "Determine which agent should handle this command. The possible agents are:\n"
        "- browser_agent: for web browsing, searching, and opening websites\n"
        "- computer_agent: for opening applications, files, or system operations\n"
        "- db_agent: for storing, searching, and managing sentences\n"
        "- general_knowledge_agent: for answering general questions and providing a text-to-speech answer\n"
        "Respond with ONLY the agent name, nothing else.\n"
        "Example: general_knowledge_agent\n\n"
        "Note: Any operations related to storing, searching, or listing sentences should be handled by db_agent."
    )
    
    # Create a new messages list with the prompt.
    messages = [{"role": "user", "content": prompt}]
    response_obj = master_llm.invoke(messages)
    agent_name = response_obj.content.strip().lower()
    
    # Add a debug message for the conversation.
    delegation_msg = {
        "role": "assistant",
        "content": f"Master Agent: Delegating to {agent_name} - '{initial_command}'."
    }
    
    # Create the new state with the initial command and messages.
    new_state = {
        "messages": [initial_msg],
        "current_command": initial_command
    }
    
    # If the agent has already executed, we're done.
    if state.get(f"{agent_name}_executed"):
        final_message = {"role": "assistant", "content": "Master Agent: Task completed."}
        return Command(goto="END", update={"messages": [initial_msg, delegation_msg, final_message]})
    
    # Otherwise, delegate to the appropriate agent.
    return Command(goto=agent_name, update=new_state)