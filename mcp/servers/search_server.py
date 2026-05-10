from fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Search-Tools")


@mcp.tool()
def search_web(query: str) -> str:
    """Search the web for current information using Tavily.

    Args:
        query: The search query to look up
    """
    from langchain_tavily import TavilySearch

    tool = TavilySearch(max_results=3)
    results = tool.invoke(query)
    return str(results)


@mcp.tool()
def search_news(query: str) -> str:
    """Search for recent news articles using Tavily.

    Args:
        query: The news topic to search for
    """
    from langchain_tavily import TavilySearch

    tool = TavilySearch(max_results=3, search_depth="advanced", topic="news")
    results = tool.invoke(query)
    return str(results)


if __name__ == "__main__":
    # stdio (default) — for local clients
    mcp.run()

    # HTTP/SSE — uncomment for remote access
    # mcp.run(transport="sse", host="0.0.0.0", port=8002)
