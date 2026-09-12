#!/usr/bin/env python3
r"""Cross-session repeat-failure measurement (#663/#496; plan §5.2/§7.3).

Consumes the two JSONL files emitted by the runner's ``--cross-session`` mode
(``cross-session-baseline.jsonl`` / ``cross-session-intervention.jsonl``), each
record carrying ``session``, ``failure_class``, ``success``. Writes
``docs/field-test/v0.3.0/cross-session-results.md``.

Usage:
    python scripts/cross_session.py \\
        --baseline field-test/results/0.3.0/cross-session-baseline.jsonl \\
        --intervention field-test/results/0.3.0/cross-session-intervention.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cauterule.measurement.cross_session import (  # noqa: E402
    REDUCTION_TARGET,
    cross_session_delta,
)


def _load(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def render_markdown(report, late: set[int]) -> str:  # type: ignore[no-untyped-def]
    """Render the cross-session report as markdown."""
    window = f"sessions {sorted(late)}" if late else "all sessions"
    lines = [
        "# Cross-Session Repeat-Failure Reduction — CauterRule v0.3.0",
        "",
        "**Issue:** #663/#496 · **Plan:** §5.2/§7.3 · **Target:** "
        f"reduction ≥{REDUCTION_TARGET:.0%}",
        "",
        f"**Measurement window:** {window}",
        "",
        "| Metric | Baseline (no CauterRule) | Intervention | ",
        "|--------|--------------------------|--------------|",
        f"| Failures | {report.baseline_failures} | {report.intervention_failures} |",
        f"| Repeat failures | {report.baseline_repeats} | {report.intervention_repeats} |",
        f"| Repeat-failure rate | {report.baseline_repeat_rate:.3f} | "
        f"{report.intervention_repeat_rate:.3f} |",
        "",
        f"**Reduction:** {report.reduction:.3f} "
        f"({'✅ meets' if report.meets_target else '❌ below'} ≥{REDUCTION_TARGET:.0%})",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point; returns 0 when the ≥50% reduction target is met."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--intervention", required=True)
    parser.add_argument(
        "--late-sessions", default="4,5", help="Comma-separated late-session window"
    )
    parser.add_argument(
        "--output",
        default=str(REPO / "docs" / "field-test" / "v0.3.0" / "cross-session-results.md"),
    )
    args = parser.parse_args(argv)

    late = {int(s) for s in args.late_sessions.split(",") if s.strip()}
    report = cross_session_delta(_load(Path(args.baseline)), _load(Path(args.intervention)), late_sessions=late)
    md = render_markdown(report, late)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"wrote {out}")
    return 0 if report.meets_target else 1


if __name__ == "__main__":
    raise SystemExit(main())
