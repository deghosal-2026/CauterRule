"""Shared docker-test result recorder for the v0.3.1 field run.

Writes each docker-marked test outcome to
``field-test/results/0.3.1/docker/docker-results.jsonl`` **as it finishes**, so
the file is a live status surface (watch it with ``tail -f``), then writes the
markdown summary at session end.

Override the destination with ``CAUTERULE_FT_RESULTS_DIR``.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

RESULTS_DIR = Path(os.environ.get("CAUTERULE_FT_RESULTS_DIR", "field-test/results/0.3.1/docker"))
RESULTS_JSONL = RESULTS_DIR / "docker-results.jsonl"
RESULTS_MD = RESULTS_DIR / "docker-test-report.md"
PROGRESS_LOG = RESULTS_DIR / "docker-progress.log"

_SEEN: set[str] = set()


def _is_docker_test(item: Any) -> bool:
    return any(marker.name == "docker" for marker in item.iter_markers())


def _stage(nodeid: str) -> str:
    """Human label for the suite a test belongs to."""
    if "test_docker_v031" in nodeid:
        return "v0.3.1"
    if "test_docker_v030" in nodeid:
        return "v0.3.0"
    if "test_docker_v020" in nodeid:
        return "v0.2.0"
    if "test_docker_http_transport" in nodeid:
        return "mcp-transport"
    return "inherited"


def record(item: Any, report: Any) -> None:
    """Append one docker-test outcome immediately (live status)."""
    if not _is_docker_test(item):
        return
    nodeid = str(item.nodeid)
    if nodeid in _SEEN:
        return
    _SEEN.add(nodeid)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    duration = round(float(getattr(report, "duration", 0.0)), 3)
    entry = {
        "nodeid": nodeid,
        "outcome": report.outcome,
        "duration_s": duration,
        "when": report.when,
        "file": str(item.location[0]),
    }
    with RESULTS_JSONL.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    # Human-readable progress line: [HH:MM:SS] stage OUTCOME test (Ns)
    short = nodeid.split("::")[-1]
    line = f"[{time.strftime('%H:%M:%S')}] {_stage(nodeid):16} {report.outcome.upper():7} {short} ({duration}s)"
    with PROGRESS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(line, flush=True)


def write_summary(exitstatus: int) -> None:
    """Rewrite jsonl deduped-by-nodeid (last wins) and write the markdown report."""
    if not RESULTS_JSONL.exists():
        return
    records: list[dict[str, Any]] = []
    for line in RESULTS_JSONL.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    by_nodeid: dict[str, dict[str, Any]] = {}
    for rec in records:
        by_nodeid[str(rec.get("nodeid"))] = rec
    final = sorted(by_nodeid.values(), key=lambda r: str(r.get("nodeid")))
    with RESULTS_JSONL.open("w", encoding="utf-8") as fh:
        for rec in final:
            fh.write(json.dumps(rec) + "\n")
    passed = [r for r in final if r.get("outcome") == "passed"]
    failed = [r for r in final if r.get("outcome") == "failed"]
    skipped = [r for r in final if r.get("outcome") == "skipped"]
    lines = [
        "# Docker Field Test Report — v0.3.1",
        "",
        f"**Result:** {len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped "
        f"(exit status {exitstatus})",
        "",
        "| Test | Outcome | Duration (s) |",
        "|------|---------|--------------|",
    ]
    lines += [
        f"| `{r['nodeid']}` | {r.get('outcome')} | {r.get('duration_s')} |" for r in final
    ]
    RESULTS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
