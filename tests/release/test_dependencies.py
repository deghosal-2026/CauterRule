"""Dependency-metadata tests (#507).

Every third-party import in ``src/cauterule`` must map to ``dependencies``
or an extra in ``pyproject.toml`` — prevents recurrence of undeclared
runtime imports (requests/litellm/opentelemetry).
"""

from __future__ import annotations

import ast
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "cauterule"

# Third-party top-level packages mapped to (distribution name, location),
# where location is "core" ([project].dependencies) or an extra name.
KNOWN_THIRD_PARTY = {
    "openai": ("openai", "llm"),
    "anthropic": ("anthropic", "llm"),
    "litellm": ("litellm", "llm"),
    "requests": ("requests", "llm"),
    "opentelemetry": ("opentelemetry-api", "otel"),
    "yaml": ("pyyaml", "core"),
    "click": ("click", "core"),
    "textual": ("textual", "core"),
    "mcp": ("mcp", "core"),
    "fastmcp": ("mcp", "core"),
}


def _pyproject() -> dict[str, Any]:
    with (REPO_ROOT / "pyproject.toml").open("rb") as f:
        return tomllib.load(f)


def _imported_top_levels() -> set[str]:
    found: set[str] = set()
    for path in sorted(SRC_ROOT.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found.add(node.module.split(".")[0])
    return found


def test_known_optionals_covered_by_extras() -> None:
    data = _pyproject()
    deps = data["project"]["dependencies"]
    extras = data["project"]["optional-dependencies"]
    dep_names = {re.split(r"[<>=!~\s\[]", d)[0].lower().replace("-", "_") for d in deps}
    extra_names = {
        extra: {re.split(r"[<>=!~\s\[]", d)[0].lower().replace("-", "_") for d in reqs}
        for extra, reqs in extras.items()
    }
    for package, (dist, location) in KNOWN_THIRD_PARTY.items():
        dist_norm = dist.lower().replace("-", "_")
        if location == "core":
            assert dist_norm in dep_names, package
        else:
            assert location in extra_names, f"extra [{location}] missing"
            provided = extra_names[location] | extra_names.get("all", set())
            assert dist_norm in provided, f"{package} not in [{location}]"


def test_no_unknown_third_party_imports() -> None:
    stdlib = set(sys.stdlib_module_names)
    imported = _imported_top_levels() - {"cauterule"} - stdlib
    unknown = imported - set(KNOWN_THIRD_PARTY)
    assert not unknown, f"third-party imports without metadata mapping: {sorted(unknown)}"


def test_otel_extra_exists() -> None:
    extras = _pyproject()["project"]["optional-dependencies"]
    assert "otel" in extras
    assert "all" in extras
