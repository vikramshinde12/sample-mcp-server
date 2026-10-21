"""Convenience entry point for running the sample MCP server directly."""

import sys
from pathlib import Path

# Ensure src/ is on sys.path for direct execution
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from sample_mcp_server.server import main

if __name__ == "__main__":
    main()
