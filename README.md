# Sample Model Context Protocol (MCP) Server

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-2.x-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

A feature-rich, production-ready sample **Model Context Protocol (MCP)** server built in Python.

This project demonstrates all three core primitives of the Model Context Protocol:
- 🛠️ **Tools**: Callable functions that allow LLMs to take actions and calculate answers.
- 📄 **Resources**: Contextual data sources that LLMs can read as attachments or background context.
- 💬 **Prompts**: Reusable prompt templates with argument validation for guided workflows.

---

## 🚀 Features

### 1. Tools
- `calculate(expression: str)`: Safely evaluates mathematical expressions (e.g., `sqrt(144) + 10 * 3`, trigonometry, powers, constants like `pi` and `e`).
- `get_system_info()`: Fetches host environment diagnostics, platform details, architecture, Python version, and UTC timestamps.
- `analyze_text(text: str)`: Provides comprehensive text metrics including word count, character count, sentence count, and reading time estimation.
- `add_note(title: str, content: str)`: Saves a structured note into the server's stateful in-memory scratchpad.
- `list_notes()`: Returns all stored notes.
- `clear_notes()`: Resets and empties all stored notes.

### 2. Resources
- `system://info`: Exposes real-time host specifications and runtime metrics as a markdown document.
- `notes://all`: Exposes an aggregated, markdown-formatted feed of all notes saved in the session.

### 3. Prompt Templates
- `code_review(code: str, language: str)`: Structured prompt template for automated code review covering security, performance, bugs, and idiomatic patterns.
- `summarize_notes()`: Prompt template that pulls notes from the resource and requests an executive summary with action items.

---

## 📦 Project Structure

```
├── pyproject.toml              # Build config and dependencies (Hatchling + uv)
├── README.md                   # Documentation and client setup guides
├── LICENSE                     # MIT License
├── main.py                     # Convenience runner script
├── src/
│   └── sample_mcp_server/
│       ├── __init__.py         # Package exports
│       ├── server.py           # Core MCP server logic (Tools, Resources, Prompts)
│       └── __main__.py         # CLI entrypoint for python -m sample_mcp_server
└── tests/
    └── test_server.py          # Pytest suite verifying tools, resources, and protocol interfaces
```

---

## 🛠️ Quick Start

### 1. Prerequisites
- Python 3.12 or newer
- [`uv`](https://github.com/astral-sh/uv) (recommended) or standard `pip`

### 2. Installation

Clone this repository and install dependencies:

```bash
git clone https://github.com/vikramshinde12/sample-mcp-server.git
cd sample-mcp-server

# Using uv (fast & recommended)
uv sync

# Or using standard venv + pip
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Run the Server
The server runs over standard I/O (`stdio`):

```bash
# Using uv
uv run sample-mcp-server

# Or using python directly
python main.py
```

---

## 🔍 Testing with the MCP Inspector

The official MCP Inspector provides an interactive web UI to test and inspect your server's tools, resources, and prompts:

```bash
npx @modelcontextprotocol/inspector uv run sample-mcp-server
```

---

## 🔌 Connecting to MCP Clients

### Claude Desktop
Add the following entry to your `claude_desktop_config.json` (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "sample-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/sample-mcp-server",
        "sample-mcp-server"
      ]
    }
  }
}
```

### Cursor
Add to your Cursor MCP settings (`Settings -> Features -> MCP -> Add New MCP Server`):
- **Type**: `command`
- **Command**: `uv run --directory /absolute/path/to/sample-mcp-server sample-mcp-server`

### Antigravity IDE / Custom Clients
Add to `mcp_config.json`:

```json
{
  "mcpServers": {
    "sample-mcp-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/sample-mcp-server",
        "sample-mcp-server"
      ]
    }
  }
}
```

### ChatGPT (Web & Desktop)
Because ChatGPT runs remotely, it connects to MCP servers over **HTTP/SSE** rather than local `stdio`:

1. Start the server in SSE mode:
   ```bash
   uv run sample-mcp-server --transport sse --port 8000
   ```
2. Expose your local port via an HTTPS tunnel (e.g. using [ngrok](https://ngrok.com)):
   ```bash
   ngrok http 8000
   ```
3. In ChatGPT:
   - Go to **Settings** > **Advanced / Features** > enable **Developer Mode**.
   - Navigate to **MCP Servers** (or Plugins / Connectors) and click **Add custom MCP server**.
   - Set **Server URL** to your HTTPS tunnel endpoint: `https://<your-ngrok-url>/sse`.
   - Set **Authentication** to `None`.

---

## 🧪 Running Tests

Run the full test suite with `pytest`:

```bash
uv run pytest
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
