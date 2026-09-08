#!/usr/bin/env python3
"""Compare two field-test run snapshots — diff key metrics for trend tracking.

Usage:
    python scripts/compare-runs.py <run-dir-1> <run-dir-2>

Each run directory should contain summary.json files under corpus subdirectories.
Reads all summary.json files in each run, aggregates per-model, and produces
a markdown delta table.

Metrics compared:
    - Inconclusive rate (total and by reason)
    - Specificity distribution (specific/moderate/generic)
    - Silence rate (safety corpora)
    - Harness health (parse rate, completion ratio)
    - Candidate count and extraction rate
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


def collect_metrics(run_dir: Path, label: str) -> dict:
    """Walk *run_dir* for summary.json files and aggregate per-model metrics."""
    metrics: dict = {
        "label": label,
        "models": {},
        "totals": {
            "trajectories": 0,
            "candidates": 0,
            "passing": 0,
            "failing": 0,
            "inconclusive": 0,
            "gate_dropped": 0,
            "llm_calls_avoided": 0,
            "specificity": {"specific": 0, "moderate": 0, "generic": 0},
            "inconclusive_breakdown": {},
            "harness_health": {"parse_rate": None, "completion_ratio": None},
        },
    }

    for summary_path in sorted(run_dir.rglob("summary.json")):
        try:
            data = json.loads(summary_path.read_text())
        except Exception:
            continue

        meta = data.get("meta", {})
        corpus_type = meta.get("corpus_type", "?")
        model = f"{meta.get('llm_provider', '?')}/{meta.get('llm_model', '?')}"

        if model not in metrics["models"]:
            metrics["models"][model] = {
                "trajectories": 0,
                "candidates": 0,
                "passing": 0,
                "failing": 0,
                "inconclusive": 0,
                "gate_dropped": 0,
                "llm_calls_avoided": 0,
                "specificity": {"specific": 0, "moderate": 0, "generic": 0},
                "inconclusive_breakdown": {},
                "corpora": [],
            }

        m = metrics["models"][model]
        m["trajectories"] += data.get("done", 0) + data.get("gate_dropped", 0)
        m["candidates"] += data.get("total_candidates", 0)
        m["passing"] += data.get("passing", 0)
        m["failing"] += data.get("failing", 0)
        m["inconclusive"] += data.get("inconclusive", 0)
        m["gate_dropped"] += data.get("gate_dropped", 0)
        m["llm_calls_avoided"] += data.get("total_llm_calls_avoided", 0)
        m["corpora"].append(corpus_type)

        spec = data.get("specificity_distribution", {})
        for k in ("specific", "moderate", "generic"):
            m["specificity"][k] += spec.get(k, 0)

        ib = data.get("inconclusive_breakdown", {})
        for k, v in ib.items():
            m["inconclusive_breakdown"][k] = m["inconclusive_breakdown"].get(k, 0) + v

        metrics["totals"]["trajectories"] += m["trajectories"]
        metrics["totals"]["candidates"] += m["candidates"]
        metrics["totals"]["passing"] += m["passing"]
        metrics["totals"]["failing"] += m["failing"]
        metrics["totals"]["inconclusive"] += m["inconclusive"]
        metrics["totals"]["gate_dropped"] += m["gate_dropped"]
        metrics["totals"]["llm_calls_avoided"] += m["llm_calls_avoided"]
        for k in ("specific", "moderate", "generic"):
            metrics["totals"]["specificity"][k] += spec.get(k, 0)
        for k, v in ib.items():
            metrics["totals"]["inconclusive_breakdown"][k] = metrics["totals"]["inconclusive_breakdown"].get(k, 0) + v

    return metrics


def _pct_str(num: int, total: int) -> str:
    return f"{num} ({num / total * 100:.1f}%)" if total else str(num)


def print_delta(label1: str, v1: int | float | None, label2: str, v2: int | float | None, unit: str = "") -> str:
    if v1 is None and v2 is None:
        return "—"
    v1s = f"{v1}{unit}" if v1 is not None else "—"
    v2s = f"{v2}{unit}" if v2 is not None else "—"
    delta = ""
    if v1 is not None and v2 is not None:
        d = v2 - v1
        sign = "+" if d > 0 else ""
        delta = f" ({sign}{d}{unit})"
    return f"{v1s} → {v2s}{delta}"


def compare(metrics1: dict, metrics2: dict) -> str:
    """Produce a markdown comparison table."""
    lines: list[str] = [
        f"# Run Comparison: {metrics1['label']} → {metrics2['label']}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Aggregate Totals",
        "",
        "| Metric | Baseline | New | Delta |",
        "|--------|----------|-----|-------|",
    ]

    t1 = metrics1["totals"]
    t2 = metrics2["totals"]

    for metric, key in [
        ("Trajectories", "trajectories"),
        ("Candidates", "candidates"),
        ("Passing", "passing"),
        ("Failing", "failing"),
        ("Inconclusive", "inconclusive"),
        ("Gate dropped", "gate_dropped"),
        ("LLM calls avoided", "llm_calls_avoided"),
    ]:
        v1 = t1.get(key, 0)
        v2 = t2.get(key, 0)
        d = v2 - v1
        sign = "+" if d > 0 else ""
        lines.append(f"| {metric} | {v1} | {v2} | {sign}{d} |")

    lines.append("")
    lines.append("## Inconclusive Breakdown")
    lines.append("")
    lines.append("| Reason | Baseline | New | Delta |")
    lines.append("|--------|----------|-----|-------|")

    all_reasons = sorted(set(t1.get("inconclusive_breakdown", {})) | set(t2.get("inconclusive_breakdown", {})))
    for reason in all_reasons:
        v1 = t1.get("inconclusive_breakdown", {}).get(reason, 0)
        v2 = t2.get("inconclusive_breakdown", {}).get(reason, 0)
        inc_total = t1.get("inconclusive", 1) or 1
        lines.append(f"| {reason} | {_pct_str(v1, t1.get('inconclusive', 1))} | {_pct_str(v2, t2.get('inconclusive', 1))} | {v2 - v1:+d} |")

    lines.append("")
    lines.append("## Specificity Distribution")
    lines.append("")
    lines.append("| Category | Baseline | New | Delta |")
    lines.append("|----------|----------|-----|-------|")

    for cat in ("specific", "moderate", "generic"):
        v1 = t1.get("specificity", {}).get(cat, 0)
        v2 = t2.get("specificity", {}).get(cat, 0)
        tot1 = sum(t1.get("specificity", {}).values()) or 1
        tot2 = sum(t2.get("specificity", {}).values()) or 1
        lines.append(f"| {cat} | {_pct_str(v1, tot1)} | {_pct_str(v2, tot2)} | {v2 - v1:+d} |")

    lines.append("")
    lines.append("## Per-Model Comparison")
    lines.append("")

    all_models = sorted(set(metrics1.get("models", {})) | set(metrics2.get("models", {})))
    for model in all_models:
        m1 = metrics1.get("models", {}).get(model, {})
        m2 = metrics2.get("models", {}).get(model, {})

        lines.append(f"### {model}")
        lines.append("")
        lines.append("| Metric | Baseline | New | Delta |")
        lines.append("|--------|----------|-----|-------|")

        for metric, key in [
            ("Trajectories", "trajectories"),
            ("Candidates", "candidates"),
            ("Passing", "passing"),
            ("Failing", "failing"),
            ("Inconclusive", "inconclusive"),
            ("Gate dropped", "gate_dropped"),
            ("LLM calls avoided", "llm_calls_avoided"),
        ]:
            v1 = m1.get(key, 0)
            v2 = m2.get(key, 0)
            d = v2 - v1
            sign = "+" if d > 0 else ""
            lines.append(f"| {metric} | {v1} | {v2} | {sign}{d} |")

        inc1 = m1.get("inconclusive", 0)
        inc2 = m2.get("inconclusive", 0)
        tot1 = m1.get("trajectories", 0) or 1
        tot2 = m2.get("trajectories", 0) or 1
        lines.append(f"| Inconclusive rate | {inc1/tot1*100:.1f}% | {inc2/tot2*100:.1f}% | {inc2/tot2*100 - inc1/tot1*100:+.1f}% |")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python scripts/compare-runs.py <run-dir-1> <run-dir-2>")
        print()
        print("Each directory should contain summary.json files under corpus subdirectories.")
        print("Example:")
        print("  python scripts/compare-runs.py field-test/results/0.2.0/validation/2026-09-08 field-test/results/0.2.0/validation/2026-09-09")
        sys.exit(1)

    dir1 = Path(sys.argv[1])
    dir2 = Path(sys.argv[2])

    if not dir1.is_dir():
        print(f"Error: {dir1} is not a directory", file=sys.stderr)
        sys.exit(1)
    if not dir2.is_dir():
        print(f"Error: {dir2} is not a directory", file=sys.stderr)
        sys.exit(1)

    label1 = sys.argv[3] if len(sys.argv) > 3 else dir1.name
    label2 = sys.argv[4] if len(sys.argv) > 4 else dir2.name

    metrics1 = collect_metrics(dir1, label1)
    metrics2 = collect_metrics(dir2, label2)

    output = compare(metrics1, metrics2)
    out_path = Path(f"field-test/results/0.2.0/comparison-{label1}-vs-{label2}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output)
    print(output)
    print(f"\nComparison saved to: {out_path}")


if __name__ == "__main__":
    main()