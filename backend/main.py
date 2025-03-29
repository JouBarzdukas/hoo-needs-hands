import sys
from dotenv import load_dotenv
load_dotenv()
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# Import agent functions.
from agents.master_agent import master_agent
from agents.db_agent import db_agent
from agents.browser_agent import browser_agent
from agents.computer_agent import computer_agent

# Import prebuilt ToolNode and tools_condition.
from langgraph.prebuilt import ToolNode, tools_condition

# Import our tool functions.
from tools.db_tool import db_retriever_tool
from tools.browseruse_tool import browseruse_tool
from tools.computeruse_tool import computeruse_tool

# Define the shared state schema.
class State(TypedDict):
    messages: list  # Each message is a dict or AIMessage with a 'content' field.
    # 'steps' holds parsed sub-tasks; 'current_command' stores the active command.

def build_graph() -> StateGraph:
    """
    Build a simple flow:
      1) Start -> master_agent
      2) master_agent can route to one of db_agent, browser_agent, computer_agent
      3) Each agent can optionally call a single tool node
      4) After the tool, return to master_agent
      5) End when master_agent says done
    """
    graph_builder = StateGraph(State)
    graph_builder.add_node("master_agent", master_agent)
    graph_builder.add_node("db_agent", db_agent)
    graph_builder.add_node("browser_agent", browser_agent)
    graph_builder.add_node("computer_agent", computer_agent)
    
    # Add separate tool nodes for each subordinate agent.
    graph_builder.add_node("db_tools", ToolNode(tools=[db_retriever_tool]))
    graph_builder.add_node("browser_tools", ToolNode(tools=[browseruse_tool]))
    graph_builder.add_node("computer_tools", ToolNode(tools=[computeruse_tool]))
    
    # Set up control flow.
    graph_builder.add_edge(START, "master_agent")
    
    # For each subordinate agent, add conditional edges to route tool calls or end.
    graph_builder.add_conditional_edges(
        "db_agent",
        tools_condition,
        {
            "tools": "db_tools",
            END: "master_agent"  # If no tool call is needed, jump back
        }
    )
    graph_builder.add_conditional_edges(
        "browser_agent",
        tools_condition,
        {
            "tools": "browser_tools",
            END: "master_agent"
        }
    )
    graph_builder.add_conditional_edges(
        "computer_agent",
        tools_condition,
        {
            "tools": "computer_tools",
            END: "master_agent"
        }
    )
    
    # After tool execution, control returns to the master agent.
    graph_builder.add_edge("db_tools", "master_agent")
    graph_builder.add_edge("browser_tools", "master_agent")
    graph_builder.add_edge("computer_tools", "master_agent")
    
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

def main():
    graph = build_graph()
    visualize_graph(graph)
    
    print("Enter your command (type 'quit' or 'exit' to stop):")
    while True:
        user_input = input("Command: ").strip()
        if user_input.lower() in ["quit", "exit"]:
            print("Exiting.")
            break
        
        # Construct the initial state from the user input.
        initial_state: State = {"messages": [{"role": "user", "content": user_input}]}
        
        # Run the graph on the provided state and print each event in sequence.
        for event in graph.stream(initial_state):
            print("Graph event:", event)

if __name__ == "__main__":
    main()
