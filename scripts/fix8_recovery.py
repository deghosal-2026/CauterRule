#!/usr/bin/env python3
"""Fix 8 recovery-exclusion re-run (#491; plan §5.6).

Runs the pre-extraction gate (strict) over the recovery/near-miss corpora on the
local tier and measures how often recovered trajectories are correctly excluded
from extraction. Writes
``docs/field-test/v0.3.0/fix8-recovery-exclusion.md``.

Usage:
    python scripts/fix8_recovery.py
    python scripts/fix8_recovery.py --corpora field-test/corpus/curated/nearmiss corpus/public/nearmiss
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cauterule.measurement.recovery import recovery_exclusion  # noqa: E402

DEFAULT_CORPORA = [
    "field-test/corpus/curated/nearmiss",
    "corpus/public/nearmiss",
    "field-test/corpus/raw/cross-session",
]


def _load(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for jsonl in sorted(path.rglob("*.jsonl")):
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    return records


def _gate_verdicts(records: list[dict[str, object]]) -> list[dict[str, object]]:
    from cauterule.extraction.gate import run_gate
    from cauterule.models.trajectory import Trajectory

    out: list[dict[str, object]] = []
    for record in records:
        try:
            traj = Trajectory.from_dict(record)
        except Exception:
            continue
        result = run_gate(traj, mode="strict")
        out.append(
            {
                "trajectory_id": record.get("trajectory_id"),
                "expected_outcome": record.get("expected_outcome"),
                "gate_is_silence": result.is_silence,
            }
        )
    return out


def run(corpora: list[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for corpus in corpora:
        records = _load(corpus)
        report = recovery_exclusion(_gate_verdicts(records))
        rows.append(
            {
                "corpus": str(corpus),
                "recovered_expected": report.recovered_expected,
                "excluded": report.excluded,
                "extracted": report.extracted,
                "exclusion_rate": report.exclusion_rate,
                "meets_target": report.meets_target,
            }
        )
    return rows


def render_markdown(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Fix 8 Recovery-Exclusion Re-run — CauterRule v0.3.0",
        "",
        "**Issue:** #491 · **Plan:** §5.6 · **Tier:** local (gate-level, hermetic)",
        "",
        "| Corpus | Recovered-expected | Excluded | Extracted (false) | Exclusion rate | Meets ≥0.5 |",
        "|--------|--------------------|----------|-------------------|----------------|------------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['corpus']} | {r['recovered_expected']} | {r['excluded']} | "
            f"{r['extracted']} | {r['exclusion_rate']:.3f} | "
            f"{'✅' if r['meets_target'] else '❌'} |"
        )
    total_recovered = sum(int(r["recovered_expected"]) for r in rows)
    total_excluded = sum(int(r["excluded"]) for r in rows)
    overall = (total_excluded / total_recovered) if total_recovered else 0.0
    lines += [
        "",
        f"**Overall:** {total_excluded}/{total_recovered} recovered trajectories "
        f"excluded ({overall:.3f}); {'✅ holds' if overall >= 0.5 else '❌ regression'} on local tier.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpora", nargs="*", default=DEFAULT_CORPORA)
    parser.add_argument(
        "--output",
        default=str(REPO / "docs" / "field-test" / "v0.3.0" / "fix8-recovery-exclusion.md"),
    )
    args = parser.parse_args(argv)

    corpora = [Path(c) for c in args.corpora]
    missing = [str(c) for c in corpora if not c.is_dir()]
    if missing:
        print(f"[warn] missing corpora: {missing}")
    rows = run([c for c in corpora if c.is_dir()])
    md = render_markdown(rows)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
