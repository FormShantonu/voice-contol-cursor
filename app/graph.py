import subprocess
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool


class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool()
def run_command(cmd: str):
    '''Take a command line prompt as input and execute it on the user's machine and return the output of the command.
    Example: run_command(cmd="ls") where ls is the command line prompt to list files in the current directory.
    '''
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    output = result.stdout
    if result.stderr:
        output += "\nSTDERR:\n" + result.stderr
    return output or "(no output)"

# Define the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Define LLM with tool
llm_with_tools = llm.bind_tools(tools=[run_command])

# Define the chatbot function
def chatbot(state: State):
    system_prompt = "You are a helpful assistant that can execute command line prompts for the user. If the user asks you to run a command, use the tool provided to execute the command and return the output. If the user does not ask you to run a command, respond to their message as a helpful assistant. You can even execute commands and help the user learn about the system. Always make sure to keep your generated files or folders in chat_gpt/ folder. You can create one if it does not exist."

    messages = llm_with_tools.invoke([system_prompt] + state["messages"])
    return {"messages": [messages]}

tool_node = ToolNode(tools=[run_command])

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)