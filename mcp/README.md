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
│   • Has memory (conversation persistence)                   │
│                                                             │
│   Connects to:                                              │
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

### Run the client (interactive mode)

```bash
cd C:\Users\ashok\OneDrive\NOblox\Agentic-LanggraphCrash
python mcp/client/mcp_client.py
```

### Run with a single query

```bash
python mcp/client/mcp_client.py "What is 25 multiplied by 4?"
python mcp/client/mcp_client.py "Search for latest AI news"
python mcp/client/mcp_client.py "Translate hello world to Spanish"
```

### Run individual servers (for external clients)

```bash
# Each server can run independently
python mcp/servers/math_server.py
python mcp/servers/search_server.py
python mcp/servers/groq_server.py
```

## How It Works

1. **Client starts** → launches all 3 MCP servers as subprocesses (stdio)
2. **Tool discovery** → `langchain-mcp-adapters` auto-discovers all tools from all servers
3. **LangGraph agent** → binds discovered tools to Llama 3.1 via Groq
4. **User asks question** → agent decides which tool(s) to call
5. **Tools execute** → results flow back through the graph
6. **Agent responds** → final answer returned to user

## Example Interactions

```
📝 You: What is 15 multiplied by 8?
🤖 Response: 15 multiplied by 8 is 120.

📝 You: Search for the latest news about SpaceX
🤖 Response: Here are the latest SpaceX news...

📝 You: Translate "good morning" to French
🤖 Response: "Bonjour"
```

## Key Benefit

Each server is **independent and reusable**. You can:
- Add new servers without changing the client
- Connect any MCP-compatible client (Claude Desktop, Cursor, etc.) to individual servers
- Deploy servers separately (e.g., math locally, search in cloud)
