from __future__ import annotations

import click


@click.command("mcp")
@click.option("--transport", default="stdio", help="Transport: 'stdio' or 'http'.")
@click.option("--host", default="localhost", help="Host for HTTP transport.")
@click.option("--port", default=9000, type=int, help="Port for HTTP transport.")
def mcp(transport: str, host: str, port: int) -> None:
    """Start the CauterRule MCP server."""
    from cauterule.mcp.launch import launch_mcp

    launch_mcp(transport=transport, host=host, port=port)
