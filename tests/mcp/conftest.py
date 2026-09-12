"""MCP docker conftest — records docker test outcomes to same dir as field/.

The field conftest lives under tests/field/ and only sees tests under that dir.
This sibling ensures the 4 tests in tests/mcp/test_docker_http_transport.py are
also captured in field-test/results/0.3.0/docker/ (#642 recommendation).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

RESULTS_DIR = Path("field-test/results/0.3.0/docker")
RESULTS_JSONL = RESULTS_DIR / "docker-results.jsonl"
RESULTS_MD = RESULTS_DIR / "docker-test-report.md"

_records: list[dict[str, object]] = []


def _is_docker_test(item: pytest.Item) -> bool:
    return any(marker.name == "docker" for marker in item.iter_markers())


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call) -> object:  # type: ignore[no-untyped-def]
    outcome = yield
    rep: pytest.TestReport = outcome.get_result()
    if not _is_docker_test(item):
        return
    if rep.when == "call" or (rep.when == "setup" and rep.outcome == "skipped"):
        _records.append(
            {
                "nodeid": item.nodeid,
                "outcome": rep.outcome,
                "duration_s": round(getattr(rep, "duration", 0.0), 3),
                "file": item.location[0],
            }
        )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # type: ignore[no-untyped-def]
    if not _records:
        return
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    # Merge with any records from tests/field/ run in same session:
    # if field conftest already wrote, append rather than overwrite.
    existing: list[dict[str, object]] = []
    if RESULTS_JSONL.exists():
        try:
            existing = [json.loads(line) for line in RESULTS_JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
        except Exception:
            existing = []
    merged = existing + _records
    # Deduplicate by nodeid
    seen: set[str] = set()
    deduped: list[dict[str, object]] = []
    for rec in merged:
        nid = str(rec.get("nodeid"))
        if nid not in seen:
            seen.add(nid)
            deduped.append(rec)
    with RESULTS_JSONL.open("w", encoding="utf-8") as fh:
        for rec in deduped:
            fh.write(json.dumps(rec) + "\n")
    passed = [r for r in deduped if r["outcome"] == "passed"]
    failed = [r for r in deduped if r["outcome"] == "failed"]
    skipped = [r for r in deduped if r["outcome"] == "skipped"]
    lines = [
        "# Docker Field Test Report — v0.3.0",
        "",
        f"**Result:** {len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped "
        f"(exit status {exitstatus})",
        "",
        "| Test | Outcome | Duration (s) |",
        "|------|---------|--------------|",
    ]
    for rec in sorted(deduped, key=lambda r: str(r["nodeid"])):
        lines.append(f"| `{rec['nodeid']}` | {rec['outcome']} | {rec['duration_s']} |")
    RESULTS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def pytest_terminal_summary(terminalreporter, config) -> None:  # type: ignore[no-untyped-def]
    if not _records:
        return
    terminalreporter.write_line(f"docker results -> {RESULTS_JSONL} ({RESULTS_MD})")
