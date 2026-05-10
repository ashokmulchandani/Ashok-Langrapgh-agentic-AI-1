"""
LangGraph Studio Agent — Exposes graphs for visual debugging in LangGraph Studio.

Run with: langgraph dev
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()


# ============================================
# State
# ============================================
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ============================================
# Tools
# ============================================
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.

    Args:
        a: first number
        b: second number
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add two numbers.

    Args:
        a: first number
        b: second number
    """
    return a + b


tavily_search = TavilySearch(max_results=2)
tools = [tavily_search, multiply, add]


# ============================================
# Graph: ReAct Agent with Tools + Memory
# ============================================
def make_agent():
    llm = ChatGroq(model="llama-3.1-8b-instant")
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")

    # No checkpointer — LangGraph Studio handles persistence automatically
    return builder.compile()


# Expose the graph for LangGraph Studio
agent = make_agent()
