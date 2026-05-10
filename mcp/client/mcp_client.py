"""
MCP Client — LangGraph Agent that connects to multiple MCP servers.

This client discovers tools from separate MCP servers (math, search, groq)
and builds a LangGraph StateGraph agent that can use all of them.

Usage:
    python mcp/client/mcp_client.py
"""

import asyncio
import sys
import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq


# ============================================
# 1. Define LangGraph State
# ============================================
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ============================================
# 2. MCP Server configurations
# ============================================
# Get the path to the servers directory
SERVERS_DIR = os.path.join(os.path.dirname(__file__), "..", "servers")

MCP_SERVERS = {
    "math": {
        "command": "python",
        "args": [os.path.join(SERVERS_DIR, "math_server.py")],
    },
    "search": {
        "command": "python",
        "args": [os.path.join(SERVERS_DIR, "search_server.py")],
    },
    "groq": {
        "command": "python",
        "args": [os.path.join(SERVERS_DIR, "groq_server.py")],
    },
}


# ============================================
# 3. Build and run the agent
# ============================================
async def run_agent(query: str, thread_id: str = "1"):
    """Connect to MCP servers, build LangGraph agent, and run a query."""

    async with MultiServerMCPClient(MCP_SERVERS) as client:
        # Get all tools from all MCP servers
        tools = client.get_tools()

        print(f"\n🔧 Discovered {len(tools)} tools from MCP servers:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description[:60]}...")

        # Build LangGraph agent with discovered tools
        llm = ChatGroq(model="llama-3.1-8b-instant")
        llm_with_tools = llm.bind_tools(tools)

        def chatbot_node(state: State):
            return {"messages": [llm_with_tools.invoke(state["messages"])]}

        # Build graph
        builder = StateGraph(State)
        builder.add_node("chatbot", chatbot_node)
        builder.add_node("tools", ToolNode(tools))
        builder.add_edge(START, "chatbot")
        builder.add_conditional_edges("chatbot", tools_condition)
        builder.add_edge("tools", "chatbot")

        # Compile with memory
        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)

        # Run the query
        config = {"configurable": {"thread_id": thread_id}}
        print(f"\n💬 Query: {query}")
        print("-" * 50)

        response = graph.invoke({"messages": query}, config=config)

        # Print the response
        print(f"\n🤖 Response: {response['messages'][-1].content}")
        print("=" * 50)

        return response["messages"][-1].content


# ============================================
# 4. Interactive chat loop
# ============================================
async def interactive_chat():
    """Run an interactive chat session with the MCP-powered agent."""

    print("=" * 50)
    print("🚀 MCP Client — LangGraph Agent")
    print("   Connected to: Math, Search, Groq servers")
    print("   Type 'quit' to exit")
    print("=" * 50)

    thread_id = "interactive-1"

    while True:
        query = input("\n📝 You: ").strip()
        if query.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        if not query:
            continue

        await run_agent(query, thread_id=thread_id)


# ============================================
# 5. Main
# ============================================
if __name__ == "__main__":
    # Single query mode
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        asyncio.run(run_agent(query))
    else:
        # Interactive mode
        asyncio.run(interactive_chat())
