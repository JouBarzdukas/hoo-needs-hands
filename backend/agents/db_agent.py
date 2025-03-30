from langchain_openai import ChatOpenAI
from langgraph.types import Command
from tools.db_tool import store_sentence, search_sentences, list_all_sentences

def db_agent(state: dict) -> Command:
    """
    The DB agent processes the current command and determines whether to store a sentence,
    search for similar sentences, or list all stored sentences.
    """
    llm = ChatOpenAI(model="gpt-4o")
    # Bind the sentence store tools
    llm_with_tools = llm.bind_tools([store_sentence, search_sentences, list_all_sentences])
    
    # Get the command from the user's message
    user_message = state["messages"][0]
    command = user_message.get("content", "") if isinstance(user_message, dict) else str(user_message)
    
    prompt = (
        f"You are the DB agent. Process the following command: '{command}'.\n"
        "If the user wants to add or store something, output a tool_call with the tool name 'store_sentence' and arguments as a JSON object with a key 'sentence' containing the command.\n"
        "If the user wants to search, fetch, or retrieve something, output a tool_call with the tool name 'search_sentences' and arguments as a JSON object with a key 'query' containing the command.\n"
        "Do not wrap the arguments in any other keys.\n"
        "Do not include any other text in your response."
    )

    # Create a new messages list with the prompt
    messages = [{"role": "user", "content": prompt}]
    response = llm_with_tools.invoke(messages)
    
    # Return the command with the updated messages
    return Command(goto="sentence_tools", update={"messages": state["messages"] + [response]})
