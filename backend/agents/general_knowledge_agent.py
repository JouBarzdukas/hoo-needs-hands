from langchain_openai import ChatOpenAI
from langgraph.types import Command
from tools.general_knowledge_tool import general_knowledge_tool
from voice.text_to_speech import text_to_speech

def general_knowledge_agent(state: dict) -> Command:
    """
    General Knowledge Agent:
      - Answers general questions using an LLM.
      - Speaks the answer via text-to-speech.
    """
    if state.get("general_knowledge_agent_executed"):
        return Command(goto="END", update=state)
    state["general_knowledge_agent_executed"] = True

    # Get the current command/question.
    command_str = state.get("current_command", "")
    if not command_str and state.get("messages"):
        command_str = state["messages"][0].get("content", "")

    # Query the LLM for an answer.
    answer = general_knowledge_tool(command_str)

    # Use text-to-speech to speak the answer.
    text_to_speech(answer, voice="af_heart", sample_rate=24000)

    # Record the answer in the state.
    state["messages"].append({"role": "assistant", "content": f"General Knowledge Agent: {answer}"})
    return Command(goto="END", update=state)