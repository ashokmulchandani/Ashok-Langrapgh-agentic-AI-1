# Agentic AI with LangGraph + MCP

An agentic AI crash course built with LangGraph, LangChain, Groq (Llama 3.1), and FastMCP.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client                                │
│            (mcp/client/mcp_client.py)                        │
│                                                             │
│   LangGraph Agent (Llama 3.1 via Groq)                      │
│   • Auto-discovers tools from all MCP servers               │
│   • Decides which tool to call (ReAct pattern)              │
│                                                             │
│   Connects to (via stdio transport):                        │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│   │ Math Server  │  │ Search Server│  │ Groq Server  │     │
│   │              │  │              │  │              │     │
│   │ • multiply   │  │ • search_web │  │ • chat       │     │
│   │ • add        │  │ • search_news│  │ • summarize  │     │
│   │ • divide     │  │              │  │ • translate   │     │
│   │ • power      │  │              │  │              │     │
│   └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘

Also includes a standalone MCP server (mcp_server.py) that exposes
the full LangGraph agent as a single MCP tool with memory.
```

## Project Structure

```
├── 1-BasicChatbot/
│   └── chatbot.ipynb          # Basic chatbot, tools, memory, streaming
├── 2-HumanAssistance/
│   └── humanintheloop.ipynb   # Human-in-the-loop patterns
├── 3-Debugging/
│   ├── agent.py               # Debuggable agent
│   ├── debugging.ipynb        # Debugging techniques
│   └── langgraph.json         # LangGraph config
├── 4-Multimodal/
│   ├── 1-multimodalopenai.ipynb  # Multimodal RAG (PDF + images)
│   └── multimodal_sample.pdf
├── Agents/
│   └── multiaiagent.ipynb     # Multi-agent supervisor pattern
├── mcp/
│   ├── servers/
│   │   ├── math_server.py     # Math tools (multiply, add, divide, power)
│   │   ├── search_server.py   # Web search (Tavily)
│   │   └── groq_server.py     # LLM tools (chat, summarize, translate)
│   ├── client/
│   │   └── mcp_client.py      # LangGraph agent connecting to all servers
│   └── README.md              # MCP architecture docs
├── mcp_server.py              # Standalone MCP server with full LangGraph agent
├── requirements.txt
├── .env                       # API keys (gitignored)
└── .gitignore
```

## Key Concepts Covered

| Notebook/File | Concept |
|---------------|---------|
| 1-BasicChatbot | StateGraph, Nodes, Edges, Tools, Memory, Streaming |
| 2-HumanAssistance | Human-in-the-loop approval patterns |
| 3-Debugging | LangGraph debugging & observability |
| 4-Multimodal | Multimodal RAG with CLIP + GPT-4 |
| Agents | Multi-agent supervisor architecture |
| mcp_server.py | Standalone MCP server exposing LangGraph agent |
| mcp/servers/ | Individual MCP tool servers (math, search, groq) |
| mcp/client/ | LangGraph agent consuming multiple MCP servers |

## Services & APIs

| Service | Purpose |
|---------|---------|
| **Groq** | Fast LLM inference (Llama 3.1) |
| **Tavily** | Web search tool |
| **LangSmith** | Tracing & observability |
| **FastMCP** | MCP server framework |
| **langchain-mcp-adapters** | Consume MCP servers from LangGraph |

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- **Groq**: https://console.groq.com/keys
- **Tavily**: https://tavily.com

### 3. Run the MCP multi-server client (recommended)

```bash
python mcp/client/mcp_client.py
```

This launches all 3 MCP servers and starts an interactive chat.

### 4. Or run the standalone MCP server

```bash
# stdio mode (for Claude Desktop, Cursor, VS Code)
python mcp_server.py

# HTTP mode (uncomment in mcp_server.py for remote access)
# Runs on http://localhost:8000
```

### 5. Connect to Claude Desktop (optional)

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ashok-langgraph-agent": {
      "command": "python",
      "args": ["C:\\Users\\ashok\\OneDrive\\NOblox\\Agentic-LanggraphCrash\\mcp_server.py"]
    }
  }
}
```

## Example Session (MCP Client)

```
==================================================
🚀 Starting MCP servers...
==================================================

🔧 Discovered 9 tools from MCP servers:
   - multiply, add, divide, power
   - search_web, search_news
   - chat, summarize, translate

==================================================
💬 Interactive Chat (type 'quit' to exit)
==================================================

📝 You: what is 5 times 4
🤖 Response: The result of 5 times 4 is 20.

📝 You: search for latest AI news
🤖 Response: The latest AI news includes...

📝 You: translate hello world to Spanish
🤖 Response: Hola mundo
```

## How LangGraph Works Here

```python
# 1. Define State (message history)
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Discover tools from MCP servers
client = MultiServerMCPClient(MCP_SERVERS)
tools = await client.get_tools()

# 3. Build graph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")
graph = builder.compile()

# 4. Agent decides which tool to use
response = await graph.ainvoke({"messages": "what is 5 times 4?"})
```

The agent **decides on its own** whether to use tools or respond directly — that's the ReAct pattern powered by LangGraph's conditional edges.

## License

MIT
