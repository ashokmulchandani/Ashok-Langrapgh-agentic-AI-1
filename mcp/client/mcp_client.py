"""
MCP Client — LangGraph Agent that connects to multiple MCP servers.

Usage:
    python mcp/client/mcp_client.py
    python mcp/client/mcp_client.py "What is 5 times 4?"
"""

import asyncio
import sys
import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq


# ============================================
# 1. Define LangGraph State
# ============================================
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ============================================
# 2. MCP Server configurations
# ============================================
SERVERS_DIR = os.path.join(os.path.dirname(__file__), "..", "servers")

MCP_SERVERS = {
    "math": {
        "transport": "stdio",
        "command": "python",
        "args": [os.path.join(SERVERS_DIR, "math_server.py")],
    },
    "search": {
        "transport": "stdio",
        "command": "python",
        "args": [os.path.join(SERVERS_DIR, "search_server.py")],
    },
    "groq": {
        "transport": "stdio",
        "command": "python",
        "args": [os.path.join(SERVERS_DIR, "groq_server.py")],
    },
}


# ============================================
# 3. Main async function
# ============================================
async def main():
    """Start MCP client, discover tools, build agent, and chat."""

    print("=" * 50)
    print("🚀 Starting MCP servers...")
    print("=" * 50)

    # Create client and keep it alive for the entire session
    client = MultiServerMCPClient(MCP_SERVERS)
    tools = await client.get_tools()

    print(f"\n🔧 Discovered {len(tools)} tools from MCP servers:")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description[:60]}...")

    # Build LangGraph agent
    llm = ChatGroq(model="llama-3.1-8b-instant")
    llm_with_tools = llm.bind_tools(tools)

    async def chatbot_node(state: State):
        return {"messages": [await llm_with_tools.ainvoke(state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("chatbot", chatbot_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")
    graph = builder.compile()

    # Single query mode
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n💬 Query: {query}")
        print("-" * 50)
        response = await graph.ainvoke({"messages": query})
        print(f"\n🤖 Response: {response['messages'][-1].content}")
        return

    # Interactive mode
    print("\n" + "=" * 50)
    print("💬 Interactive Chat (type 'quit' to exit)")
    print("=" * 50)

    while True:
        try:
            query = input("\n📝 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            break

        if query.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        if not query:
            continue

        print("-" * 50)
        try:
            response = await graph.ainvoke({"messages": query})
            print(f"\n🤖 Response: {response['messages'][-1].content}")
        except Exception as e:
            print(f"\n❌ Error: {e}")

        print("=" * 50)


# ============================================
# 4. Entry point
# ============================================
if __name__ == "__main__":
    asyncio.run(main())
