from fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Groq-LLM-Tools")


@mcp.tool()
def chat(message: str) -> str:
    """Chat with Llama 3.1 via Groq for AI-powered responses.

    Args:
        message: The message to send to the AI
    """
    from langchain_groq import ChatGroq

    llm = ChatGroq(model="llama-3.1-8b-instant")
    response = llm.invoke(message)
    return response.content


@mcp.tool()
def summarize(text: str) -> str:
    """Summarize a long piece of text using Llama 3.1.

    Args:
        text: The text to summarize
    """
    from langchain_groq import ChatGroq

    llm = ChatGroq(model="llama-3.1-8b-instant")
    prompt = f"Summarize the following text concisely:\n\n{text}"
    response = llm.invoke(prompt)
    return response.content


@mcp.tool()
def translate(text: str, target_language: str) -> str:
    """Translate text to a target language using Llama 3.1.

    Args:
        text: The text to translate
        target_language: The language to translate to (e.g., Spanish, French, Hindi)
    """
    from langchain_groq import ChatGroq

    llm = ChatGroq(model="llama-3.1-8b-instant")
    prompt = f"Translate the following text to {target_language}. Only return the translation:\n\n{text}"
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    # stdio (default) — for local clients
    mcp.run()

    # HTTP/SSE — uncomment for remote access
    # mcp.run(transport="sse", host="0.0.0.0", port=8003)
