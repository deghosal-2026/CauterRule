"""MCP server scaffold — wraps CauterRule as an MCP server via FastMCP."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from cauterule.mcp.tools import get_matching_rules, get_rule, list_rules, report_failure
from cauterule.store.manager import StoreManager

_SERVER_NAME = "cauterule"
_SERVER_INSTRUCTIONS = (
    "Expose CauterRule's standing-rule store as MCP tools. "
    "Supports matching rules to tasks, retrieving single rules with provenance, "
    "browsing the rule store, and reporting failures for extraction."
)
_TOOL_ANNOTATIONS: dict[str, ToolAnnotations] = {
    "get_matching_rules": ToolAnnotations(readOnlyHint=True),
    "get_rule": ToolAnnotations(readOnlyHint=True),
    "list_rules": ToolAnnotations(readOnlyHint=True),
    "report_failure": ToolAnnotations(readOnlyHint=False),
}


class CauteruleMCPServer:
    """MCP server that exposes Cauterule standing-rule functionality.

    Wraps an internal :class:`FastMCP` instance and registers all tools
    from :mod:`cauterule.mcp.tools` during construction.
    """

    def __init__(
        self,
        store: StoreManager,
        host: str = "localhost",
        port: int = 9000,
    ) -> None:
        """Initialise server with a rule store and optional HTTP bind parameters."""
        self.store = store
        self._mcp = FastMCP(
            name=_SERVER_NAME,
            instructions=_SERVER_INSTRUCTIONS,
            host=host,
            port=port,
        )
        self._register_tools()

    # ------------------------------------------------------------------
    # Tool registration
    # ------------------------------------------------------------------
    def _register_tools(self) -> None:

        @self._mcp.tool(annotations=_TOOL_ANNOTATIONS["get_matching_rules"])
        def get_matching_rules_tool(task: str) -> list[dict[str, Any]]:
            rules = get_matching_rules(task, self.store.list_rules())
            return [r.to_dict() for r in rules]

        @self._mcp.tool(annotations=_TOOL_ANNOTATIONS["get_rule"])
        def get_rule_tool(rule_id: str) -> dict[str, Any] | None:
            rule = get_rule(rule_id, self.store)
            return rule.to_dict() if rule is not None else None

        @self._mcp.tool(annotations=_TOOL_ANNOTATIONS["list_rules"])
        def list_rules_tool(
            status: str | None = None,
            tag: str | None = None,
        ) -> list[dict[str, Any]]:
            rules = list_rules(status=status, tag=tag, store=self.store)
            return [r.to_dict() for r in rules]

        @self._mcp.tool(annotations=_TOOL_ANNOTATIONS["report_failure"])
        def report_failure_tool(trajectory_json: str) -> dict[str, Any]:
            return report_failure(trajectory_json)

    # ------------------------------------------------------------------
    # Transport runners
    # ------------------------------------------------------------------
    def run_stdio(self) -> None:
        """Run the server over stdio transport (for MCP subprocess mode)."""
        self._mcp.run(transport="stdio")

    def run_http(self, host: str = "localhost", port: int = 9000) -> None:  # noqa: ARG002
        """Run the server over streamable HTTP transport.

        The *host* and *port* are honoured when the server is constructed;
        they are accepted here for API consistency.
        """
        self._mcp.run(transport="streamable-http")
