"""``cauterule mcp`` launcher — start the MCP server on the chosen transport."""

from __future__ import annotations

from cauterule.mcp.server import CauteruleMCPServer
from cauterule.store.manager import StoreManager


def launch_mcp(
    transport: str = "stdio",
    host: str = "localhost",
    port: int = 9000,
) -> None:
    """Start the CauterRule MCP server.

    Args:
        transport: Transport to use — ``"stdio"`` or ``"http"``.
        host: Host to bind when using ``"http"`` transport.
        port: Port to bind when using ``"http"`` transport.
    """
    store = StoreManager()

    if transport == "stdio":
        server = CauteruleMCPServer(store)
        server.run_stdio()
    elif transport == "http":
        server = CauteruleMCPServer(store, host=host, port=port)
        server.run_http()
    else:
        msg = f"Unknown transport {transport!r}; use 'stdio' or 'http'"
        raise ValueError(msg)
