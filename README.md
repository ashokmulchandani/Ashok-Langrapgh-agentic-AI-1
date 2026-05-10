# Agentic AI with LangGraph + MCP

An agentic AI crash course built with LangGraph, LangChain, Groq (Llama 3.1), and FastMCP.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Server                            │
│                 (mcp_server.py)                          │
│                                                         │
│   ┌───────────────────────────────────────────────┐     │
│   │           LangGraph StateGraph                │     │
│   │                                               │     │
│   │   START → [Chatbot Node] → END               │     │
│   │               │                               │     │
│   │               ▼ (if tool call)                │     │
│   │          [Tool Node]                          │     │
│   │           - Tavily Search                     │     │
│   │           - Multiply                          │     │
│   │               │                               │     │
│   │               ▼ (loop back)                   │     │
│   │          [Chatbot Node]                       │     │
│   │                                               │     │
│   │   + MemorySaver (conversation persistence)    │     │
│   └───────────────────────────────────────────────┘     │
│                                                         │
│   Exposed MCP Tools:                                    │
│   • agent_chat (with memory)                            │
│   • agent_chat_no_memory (stateless)                    │
│   • get_graph_diagram                                   │
│                                                         │
│   Transport: stdio (default) | HTTP/SSE (optional)      │
└─────────────────────────────────────────────────────────┘
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
├── mcp_server.py              # MCP server with LangGraph agent
├── requirements.txt
├── .env                       # API keys (gitignored)
└── .gitignore
```

## Key Concepts Covered

| Notebook | Concept |
|----------|---------|
| 1-BasicChatbot | StateGraph, Nodes, Edges, Tools, Memory, Streaming |
| 2-HumanAssistance | Human-in-the-loop approval patterns |
| 3-Debugging | LangGraph debugging & observability |
| 4-Multimodal | Multimodal RAG with CLIP + GPT-4 |
| Agents | Multi-agent supervisor architecture |
| mcp_server.py | MCP server exposing LangGraph agent |

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

### 3. Run the MCP server

```bash
# stdio mode (for Claude Desktop, Cursor, VS Code)
python mcp_server.py

# HTTP mode (uncomment in mcp_server.py for remote access)
# Runs on http://localhost:8000
```

### 4. Connect to Claude Desktop (optional)

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

## How LangGraph Works Here

```python
# 1. Define State (message history)
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Define tools
tools = [TavilySearch(), multiply]

# 3. Build graph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")

# 4. Compile with memory
graph = builder.compile(checkpointer=MemorySaver())
```

The agent **decides on its own** whether to use tools or respond directly — that's the ReAct pattern powered by LangGraph's conditional edges.

## License

MIT
