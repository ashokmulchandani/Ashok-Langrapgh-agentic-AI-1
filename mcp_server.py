from fastmcp import FastMCP
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# 1. Define LangGraph State
# ============================================
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ============================================
# 2. Define Tools
# ============================================
def multiply(a: int, b: int) -> int:
    """Multiply a and b

    Args:
        a (int): first int
        b (int): second int

    Returns:
        int: output int
    """
    return a * b


tavily_search = TavilySearch(max_results=2)
tools = [tavily_search, multiply]


# ============================================
# 3. Build LangGraph (StateGraph with Tools + Memory)
# ============================================
llm = ChatGroq(model="llama-3.1-8b-instant")
llm_with_tools = llm.bind_tools(tools)

memory = MemorySaver()


def chatbot_node(state: State):
    """LLM node that can call tools."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build the graph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", ToolNode(tools))

# Add edges
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")

# Compile with memory
graph = builder.compile(checkpointer=memory)


# ============================================
# 4. Create MCP Server (exposes the graph as a tool)
# ============================================
mcp = FastMCP("Ashok-LangGraph-Agent")


@mcp.tool()
def agent_chat(message: str, thread_id: str = "default") -> str:
    """Chat with a LangGraph-powered AI agent that can search the web and do math.
    The agent remembers conversation history per thread_id.

    Args:
        message: Your message to the agent
        thread_id: Conversation thread ID (for memory). Use same ID to continue a conversation.
    """
    config = {"configurable": {"thread_id": thread_id}}
    response = graph.invoke({"messages": message}, config=config)
    return response["messages"][-1].content


@mcp.tool()
def agent_chat_no_memory(message: str) -> str:
    """Chat with the LangGraph agent without memory (single-turn, no history).

    Args:
        message: Your message to the agent
    """
    # Build a graph without checkpointer for stateless use
    stateless_graph = builder.compile()
    response = stateless_graph.invoke({"messages": message})
    return response["messages"][-1].content


@mcp.tool()
def get_graph_diagram() -> str:
    """Get the Mermaid diagram of the LangGraph agent architecture."""
    return graph.get_graph().draw_mermaid()


if __name__ == "__main__":
    mcp.run()
