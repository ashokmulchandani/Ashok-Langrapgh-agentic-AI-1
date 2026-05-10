# MCP — Separate Servers + Client Architecture

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client                                │
│            (client/mcp_client.py)                            │
│                                                             │
│   LangGraph Agent (Llama 3.1 via Groq)                      │
│   • Discovers tools from all servers automatically          │
│   • Decides which tool to call based on user query          │
│   • ReAct pattern: chatbot ↔ tools loop                     │
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
```

## Files

```
mcp/
├── servers/
│   ├── math_server.py       # multiply, add, divide, power
│   ├── search_server.py     # search_web, search_news (Tavily)
│   └── groq_server.py       # chat, summarize, translate (Llama 3.1)
├── client/
│   └── mcp_client.py        # LangGraph agent connecting to all servers
└── README.md
```

## Usage

### Interactive mode

```bash
cd C:\Users\ashok\OneDrive\NOblox\Agentic-LanggraphCrash
python mcp/client/mcp_client.py
```

### Single query mode

```bash
python mcp/client/mcp_client.py "What is 5 times 4?"
python mcp/client/mcp_client.py "Search for latest AI news"
python mcp/client/mcp_client.py "Translate hello world to Spanish"
```

### Run individual servers (for external clients like Claude Desktop)

```bash
python mcp/servers/math_server.py
python mcp/servers/search_server.py
python mcp/servers/groq_server.py
```

## Example Session

```
==================================================
🚀 Starting MCP servers...
==================================================

🔧 Discovered 9 tools from MCP servers:
   - multiply: Multiply two numbers....
   - add: Add two numbers....
   - divide: Divide first number by second number....
   - power: Raise base to the power of exponent....
   - search_web: Search the web for current information using Tavily....
   - search_news: Search for recent news articles using Tavily....
   - chat: Chat with Llama 3.1 via Groq for AI-powered responses....
   - summarize: Summarize a long piece of text using Llama 3.1....
   - translate: Translate text to a target language using Llama 3.1....

==================================================
💬 Interactive Chat (type 'quit' to exit)
==================================================

📝 You: what is 5 times 4
--------------------------------------------------
🤖 Response: The result of 5 times 4 is 20.
==================================================

📝 You: search for latest AI news
--------------------------------------------------
🤖 Response: The latest AI news includes...
==================================================
```

## How It Works

1. **Client starts** → launches all 3 MCP servers as subprocesses (stdio transport)
2. **Tool discovery** → `langchain-mcp-adapters` auto-discovers all 9 tools
3. **LangGraph agent** → binds discovered tools to Llama 3.1 via Groq
4. **User asks question** → agent decides which tool(s) to call (ReAct pattern)
5. **Tools execute** → MCP protocol sends request to correct server
6. **Agent responds** → final answer returned to user

## Key Technologies

| Package | Role |
|---------|------|
| `fastmcp` | Create MCP servers (expose tools) |
| `langchain-mcp-adapters` | Connect to MCP servers from LangGraph |
| `langgraph` | Agent orchestration (StateGraph) |
| `langchain-groq` | LLM (Llama 3.1 via Groq) |
| `langchain-tavily` | Web search tool |

## Transport Options

Each server supports two transport modes (configured in server files):

```python
# stdio (default) — for local clients
mcp.run()

# HTTP/SSE — for remote/shared access
# mcp.run(transport="sse", host="0.0.0.0", port=8001)
```

## Adding New Servers

1. Create a new file in `mcp/servers/` (e.g., `weather_server.py`)
2. Add tools with `@mcp.tool()` decorator
3. Add the server config to `MCP_SERVERS` dict in `mcp_client.py`
4. Restart the client — new tools are auto-discovered
