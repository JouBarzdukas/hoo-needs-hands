from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END

# Import agent functions.
from agents.master_agent import master_agent
from agents.db_agent import db_agent
from agents.browser_agent import browser_agent
from agents.computer_agent import computer_agent

# Import prebuilt ToolNode and tools_condition.
from langgraph.prebuilt import ToolNode, tools_condition

# Import our tool functions.
from tools.db_tool import store_sentence, search_sentences, list_all_sentences
from tools.browseruse_tool import browseruse_tool
from tools.computeruse_tool import computeruse_tool

# Import voice activation and text-to-speech functions.
from voice.voice_activation import (
    get_voice_command,
    record_for_duration,
    transcribe_audio_from_bytes,
    is_affirmative_response
)
from voice.text_to_speech import text_to_speech

# Import OpenAI for GPT-3.5-turbo
from openai import OpenAI

# Import pyaudio for audio recording
import pyaudio

# Define the shared state schema.
class State(TypedDict):
    messages: Annotated[list, "messages"]  # Each message is a dict (or AIMessage) with a 'content' field.
    # Additional keys (like 'current_command') can be added as needed.

def build_graph() -> StateGraph:
    """
    Build a simple flow:
      1) START -> master_agent
      2) master_agent routes to one of db_agent, browser_agent, or computer_agent.
      3) Each agent can optionally call a tool node.
      4) After the tool, return to END.
      5) End when the agent says done.
    """
    graph_builder = StateGraph(State)
    graph_builder.add_node("master_agent", master_agent)
    graph_builder.add_node("db_agent", db_agent)
    graph_builder.add_node("browser_agent", browser_agent)
    graph_builder.add_node("computer_agent", computer_agent)
    
    graph_builder.add_node("db_tools", ToolNode(tools=[store_sentence, search_sentences, list_all_sentences]))
    graph_builder.add_node("browser_tools", ToolNode(tools=[browseruse_tool]))
    graph_builder.add_node("computer_tools", ToolNode(tools=[computeruse_tool]))
    
    graph_builder.add_edge(START, "master_agent")
    graph_builder.add_conditional_edges(
        "db_agent",
        tools_condition,
        {"tools": "db_tools", END: END}
    )
    graph_builder.add_conditional_edges(
        "browser_agent",
        tools_condition,
        {"tools": "browser_tools", END: END}
    )
    graph_builder.add_conditional_edges(
        "computer_agent",
        tools_condition,
        {"tools": "computer_tools", END: END}
    )
    
    graph_builder.add_edge("db_tools", END)
    graph_builder.add_edge("browser_tools", END)
    graph_builder.add_edge("computer_tools", END)
    
    return graph_builder.compile()

def visualize_graph(graph: StateGraph):
    try:
        from langchain_core.runnables.graph import MermaidDrawMethod
        png_data = graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
        with open("graph.png", "wb") as f:
            f.write(png_data)
        print("Graph visualization saved as 'graph.png' in the current directory.")
    except Exception as e:
        print("Visualization not available. Error:", e)

def is_end_conversation(text: str) -> bool:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that determines if a text response indicates wanting to end a conversation (yes) or continue (no). Respond with only 'true' or 'false'."},
            {"role": "user", "content": f"Does this response indicate wanting to end the conversation (yes) or continue (no)? Text: {text}"}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content.strip().lower() == 'true'

def main():
    while True:
        # Run voice activation to obtain the command.
        should_execute, command, pa, porcupine = get_voice_command()
        print("Voice command obtained:", command)
        print("Should execute command:", should_execute)
        
        if not should_execute:
            print("Command execution cancelled by user.")
            text_to_speech("Command cancelled", voice="af_heart", sample_rate=24000)
        else:
            graph = build_graph()
            # visualize_graph(graph)
            
            # Seed the graph with the voice command.
            initial_state: State = {"messages": [{"role": "user", "content": command}]}
            for event in graph.stream(initial_state):
                print("Graph event:", event)
            
            # Indicate that processing is complete
            text_to_speech("Task completed", voice="af_heart", sample_rate=24000)
        
        # Ask if user wants to end conversation
        text_to_speech("Would you like to end this conversation? Say yes or no.", voice="af_heart", sample_rate=24000)
        print("Waiting for conversation end confirmation...")
        
        # Record for 3 seconds to get response
        confirmation_audio = record_for_duration(pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        ), porcupine, 3, porcupine.sample_rate)
        
        if confirmation_audio is None:
            print("Failed to record end conversation confirmation")
            # Clean up resources
            if pa:
                pa.terminate()
            if porcupine:
                porcupine.delete()
            continue
            
        confirmation_text = transcribe_audio_from_bytes(confirmation_audio, porcupine.sample_rate)
        print("End conversation response:", confirmation_text)
        
        if is_end_conversation(confirmation_text):
            print("Ending conversation.")
            text_to_speech("Goodbye!", voice="af_heart", sample_rate=24000)
            # Clean up resources
            if pa:
                pa.terminate()
            if porcupine:
                porcupine.delete()
            break
        else:
            print("Continuing conversation.")
            text_to_speech("What else can I help you with?", voice="af_heart", sample_rate=24000)
            # Clean up resources
            if pa:
                pa.terminate()
            if porcupine:
                porcupine.delete()

if __name__ == "__main__":
    main()