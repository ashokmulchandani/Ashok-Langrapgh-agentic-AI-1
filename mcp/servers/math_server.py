from fastmcp import FastMCP

mcp = FastMCP("Math-Tools")


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number
    """
    return a * b


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers.

    Args:
        a: First number
        b: Second number
    """
    return a + b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide first number by second number.

    Args:
        a: Numerator
        b: Denominator
    """
    if b == 0:
        return "Error: Cannot divide by zero"
    return a / b


@mcp.tool()
def power(base: int, exponent: int) -> int:
    """Raise base to the power of exponent.

    Args:
        base: The base number
        exponent: The exponent
    """
    return base ** exponent


if __name__ == "__main__":
    # stdio (default) — for local clients
    mcp.run()

    # HTTP/SSE — uncomment for remote access
    # mcp.run(transport="sse", host="0.0.0.0", port=8001)
