"""Sample Model Context Protocol (MCP) server.

Provides tools, resources, and prompts demonstrating key MCP capabilities.
"""

from __future__ import annotations

from datetime import datetime, timezone
import math
import os
import platform
import re
import sys
from typing import Any

# Backwards and forwards compatibility:
# mcp 2.x renamed FastMCP to MCPServer.
try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer

# Initialize server
app = MCPServer(
    name="sample-mcp-server",
    instructions="A sample MCP server demonstrating tools, resources, and prompt templates.",
)

# In-memory storage for notes demo
_NOTES_STORE: dict[str, dict[str, Any]] = {}


# ==============================================================================
# TOOLS
# ==============================================================================

@app.tool()
def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression.

    Supports basic arithmetic (+, -, *, /, //, %, **), math functions
    (sqrt, sin, cos, tan, abs, log, exp), and constants (pi, e).

    Args:
        expression: The arithmetic expression to evaluate (e.g. "2 * (3 + 4)" or "sqrt(144) + pi").
    """
    allowed_names = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "abs": abs,
        "log": math.log,
        "exp": math.exp,
        "round": round,
        "pi": math.pi,
        "e": math.e,
    }

    cleaned = expression.strip()
    if any(token in cleaned for token in ["__", "import", "eval", "exec", "open", "lambda", "os", "sys"]):
        raise ValueError("Expression contains forbidden keywords or tokens.")

    try:
        code = compile(cleaned, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise ValueError(f"Use of disallowed symbol: '{name}'")
        result = eval(code, {"__builtins__": {}}, allowed_names)
        return f"{expression} = {result}"
    except Exception as exc:
        return f"Calculation error: {exc}"


@app.tool()
def get_system_info() -> dict[str, Any]:
    """Return information about the host environment, platform, and runtime.

    Returns OS name, machine architecture, Python version, working directory,
    and current UTC timestamp.
    """
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "current_directory": os.getcwd(),
        "utc_timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.tool()
def analyze_text(text: str) -> dict[str, Any]:
    """Analyze text metrics including word, sentence, and character counts.

    Args:
        text: The input text to analyze.
    """
    if not text:
        return {
            "character_count_total": 0,
            "character_count_no_spaces": 0,
            "word_count": 0,
            "sentence_count": 0,
            "estimated_reading_time_minutes": 0.0,
        }

    words = re.findall(r"\b[\w'-]+\b", text)
    sentences = [s for s in re.split(r"[.!?]+", text.strip()) if s.strip()]

    word_count = len(words)
    reading_time_minutes = round(word_count / 200.0, 2)

    return {
        "character_count_total": len(text),
        "character_count_no_spaces": len(text.replace(" ", "")),
        "word_count": word_count,
        "sentence_count": len(sentences),
        "estimated_reading_time_minutes": reading_time_minutes,
    }


@app.tool()
def add_note(title: str, content: str) -> str:
    """Store a new note in the server's memory.

    Args:
        title: Short title for the note.
        content: Markdown or plain text body for the note.
    """
    note_id = title.strip().lower().replace(" ", "-")
    now = datetime.now(timezone.utc).isoformat()
    _NOTES_STORE[note_id] = {
        "id": note_id,
        "title": title.strip(),
        "content": content.strip(),
        "created_at": now,
    }
    return f"Note '{title}' stored successfully (id: {note_id})."


@app.tool()
def list_notes() -> list[dict[str, Any]]:
    """List all notes currently saved in the server's memory."""
    return list(_NOTES_STORE.values())


@app.tool()
def clear_notes() -> str:
    """Remove all notes from memory."""
    count = len(_NOTES_STORE)
    _NOTES_STORE.clear()
    return f"Cleared {count} notes."


# ==============================================================================
# RESOURCES
# ==============================================================================

@app.resource("system://info")
def system_info_resource() -> str:
    """Resource providing real-time system specifications."""
    return (
        f"# System Info\n"
        f"- Platform: {platform.platform()}\n"
        f"- OS: {platform.system()} ({platform.release()})\n"
        f"- Architecture: {platform.machine()}\n"
        f"- Python: {sys.version.split()[0]}\n"
        f"- Server Time (UTC): {datetime.now(timezone.utc).isoformat()}\n"
    )


@app.resource("notes://all")
def all_notes_resource() -> str:
    """Resource exposing all saved notes formatted as Markdown."""
    if not _NOTES_STORE:
        return "# Notes\n\nNo notes stored yet. Use the `add_note` tool to add some!"

    output = ["# Notes\n"]
    for note in _NOTES_STORE.values():
        output.append(f"## {note['title']}")
        output.append(f"*Created at: {note['created_at']}*\n")
        output.append(f"{note['content']}\n")
        output.append("---\n")

    return "\n".join(output)


# ==============================================================================
# PROMPTS
# ==============================================================================

@app.prompt()
def code_review(code: str, language: str = "python") -> str:
    """Prompt template for requesting a comprehensive code review.

    Args:
        code: The code snippet to review.
        language: Programming language of the snippet (default: python).
    """
    return (
        f"Please perform a thorough code review of the following {language} code.\n\n"
        f"Analyze for:\n"
        f"1. Potential bugs or edge cases\n"
        f"2. Security vulnerabilities\n"
        f"3. Performance optimizations\n"
        f"4. Code clarity, style, and idiomatic practices\n\n"
        f"```{language}\n{code}\n```"
    )


@app.prompt()
def summarize_notes() -> str:
    """Prompt template asking the model to summarize all notes in memory."""
    notes_text = all_notes_resource()
    return (
        f"Below are the current notes recorded in the MCP server:\n\n"
        f"{notes_text}\n\n"
        f"Please provide an executive summary of these notes and identify any actionable tasks or follow-ups."
    )


# ==============================================================================
# ENTRY POINT
# ==============================================================================

def main() -> None:
    """Run the MCP server with configurable transport."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the sample MCP server.")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol: 'stdio' (for local desktop clients) or 'sse' / 'streamable-http' (for web/ChatGPT)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000)",
    )

    args = parser.parse_args()

    if args.transport == "stdio":
        app.run(transport="stdio")
    else:
        endpoint = "/sse" if args.transport == "sse" else "/mcp"
        print(f"Starting MCP server with {args.transport} transport at http://{args.host}:{args.port}{endpoint}")
        app.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
