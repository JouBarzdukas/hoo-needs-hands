import json
import re
from langchain_openai import ChatOpenAI
from langgraph.types import Command

# Initialize the master LLM.
master_llm = ChatOpenAI(model="gpt-4o", temperature=0)

def master_agent(state: dict) -> Command:
    """
    The master agent:
      1. Splits the user's overall command into a JSON list of sub-steps, each {agent, command}.
      2. Iterates over them in order. Once an agent runs, we set <agent>_executed = True.
      3. We skip any further steps for the same agent in this single user request.
      4. Return "END" once no more steps remain.
    """
    # Parse steps only once.
    if "steps" not in state:
        initial_msg = state["messages"][0]
        initial_command = (
            initial_msg.get("content", "")
            if isinstance(initial_msg, dict) else str(initial_msg)
        )

        # Ask the LLM to parse the user input into a JSON array of steps.
        prompt = (
            f"You are the master agent. The user command is: '{initial_command}'.\n"
            "Parse this into a valid JSON list of sub-steps, each sub-step an object "
            "with keys \"agent\" and \"command\". The possible agents are 'db_agent', "
            "'browser_agent', and 'computer_agent'.\n"
            "Output ONLY valid JSON, no extra text.\n"
            "Example output:\n"
            '[{"agent": "browser_agent", "command": "open youtube"}, '
            '{"agent": "computer_agent", "command": "open notes"}]'
        )
        response_obj = master_llm.invoke([{"role": "user", "content": prompt}])
        response_text = response_obj.content if hasattr(response_obj, "content") else str(response_obj)

        # Strip markdown fences if present.
        clean_response = re.sub(r'^```json\s*', '', response_text)
        clean_response = re.sub(r'\s*```$', '', clean_response)

        try:
            steps = json.loads(clean_response)
        except Exception as e:
            print("DEBUG: JSON parsing failed with error:", e)
            print("DEBUG: LLM returned:", response_text)
            steps = []

        state["steps"] = steps

    # Iterate over steps, skipping those for which the agent has already executed.
    while state.get("steps"):
        next_step = state["steps"][0]  # peek at the next step
        next_agent = next_step.get("agent", "").strip().lower()

        # e.g. if next_agent = "browser_agent", we check "browser_agent_executed"
        if state.get(f"{next_agent}_executed"):
            # Already executed for this agent; skip
            state["steps"].pop(0)
            continue

        # Pop the step from the list
        current_step = state["steps"].pop(0)
        # This is the command to pass to that agent
        state["current_command"] = current_step.get("command", "")
        # Add a debug message for the conversation
        delegation_msg = {
            "role": "assistant",
            "content": f"Master Agent: Delegating to {next_agent} - '{state['current_command']}'."
        }
        state["messages"].append(delegation_msg)

        return Command(goto=next_agent, update=state)

    # If no unexecuted steps remain, the task is done.
    final_message = {"role": "assistant", "content": "Master Agent: Task completed."}
    state["messages"].append(final_message)
    return Command(goto="END", update=state)
