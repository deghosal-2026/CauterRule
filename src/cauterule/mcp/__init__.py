"""MCP server module — expose CauterRule as an MCP server."""

from __future__ import annotations

from cauterule.mcp.launch import launch_mcp
from cauterule.mcp.server import CauteruleMCPServer

__all__ = [
    "CauteruleMCPServer",
    "launch_mcp",
]
