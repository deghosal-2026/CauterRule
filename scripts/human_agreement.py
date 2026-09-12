#!/usr/bin/env python3
"""Human-vs-replay agreement sampling + scoring (#493; plan §5.5/§15.9).

Two modes:
  1. Sample: read a results tree, pick up to ``--per-bucket`` completed
     candidates per replay-verdict bucket, and write a review template
     (``human-agreement-reviews.jsonl``).
  2. Score: given a filled-in reviews file, compute agreement and write
     ``docs/field-test/v0.3.0/human-agreement.md``.

Usage:
    python scripts/human_agreement.py --results field-test/results/0.3.0 --sample
    python scripts/human_agreement.py --reviews human-agreement-reviews.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cauterule.measurement.human_agreement import (  # noqa: E402
    HUMAN_GATE_THRESHOLD,
    human_agreement_report,
    sample_for_review,
)


def _load_results(root: Path) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for path in sorted(root.rglob("results.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                results.append(json.loads(line))
    return results


def _load_reviews(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def render_markdown(report, source: str) -> str:  # type: ignore[no-untyped-def]
    lines = [
        "# Human-vs-Replay Agreement — CauterRule v0.3.0",
        "",
        "**Issue:** #493 · **Plan:** §5.5/§15.9 · "
        f"**Human gate:** agreement <{HUMAN_GATE_THRESHOLD:.1f} requires approval",
        "",
        f"**Reviewed:** {report.reviewed} · **Matches:** {report.matches} · "
        f"**Agreement:** {report.agreement:.3f}",
        "",
        f"**Decision:** {'⚠️ human gate' if report.below_gate else '✅ replay-only gate'}",
        "",
        "| Replay verdict | Sampled |",
        "|----------------|---------|",
    ]
    for verdict, count in sorted(report.by_verdict.items()):
        lines.append(f"| {verdict} | {count} |")
    lines += ["", f"**Source:** {source}", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default=str(REPO / "field-test" / "results" / "0.3.0"))
    parser.add_argument("--reviews", default=None)
    parser.add_argument("--per-bucket", type=int, default=5)
    parser.add_argument(
        "--sample-output",
        default=str(REPO / "field-test" / "results" / "0.3.0" / "human-agreement-reviews.jsonl"),
    )
    parser.add_argument(
        "--output",
        default=str(REPO / "docs" / "field-test" / "v0.3.0" / "human-agreement.md"),
    )
    args = parser.parse_args(argv)

    if args.reviews:
        reviews = _load_reviews(Path(args.reviews))
        report = human_agreement_report(reviews)
        md = render_markdown(report, args.reviews)
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(md)
        print(f"wrote {out}")
        return 0 if not report.below_gate else 1

    root = Path(args.results)
    if not root.is_dir():
        print(f"[error] results root not found: {root}")
        return 1
    sampled = sample_for_review(_load_results(root), per_bucket=args.per_bucket)
    sample_path = Path(args.sample_output)
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    with sample_path.open("w", encoding="utf-8") as fh:
        for item in sampled:
            fh.write(json.dumps(item) + "\n")
    print(f"sampled {len(sampled)} candidates -> {sample_path}")
    print("Fill in human_verdict (pass/fail/inconclusive) + reviewer, then run with --reviews.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
