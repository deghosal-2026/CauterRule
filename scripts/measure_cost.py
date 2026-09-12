#!/usr/bin/env python3
"""Cost measurement for the v0.3.0 field test (#653/#486; plan §5.4/§7.4).

Reads raw ``results.jsonl`` files under a results root and computes per-model
cost metrics, writing ``docs/field-test/v0.3.0/cost-measurement.md``.

The results tree is ``<root>/<corpus>/<model>/<date>/results.jsonl``; the model
is the directory two levels above the file. Cost is token-based when prices are
supplied, otherwise ``cost_per_request × llm_requests`` (matching preflight).

Usage:
    python scripts/measure_cost.py --results field-test/results/0.3.0
    python scripts/measure_cost.py --results field-test/results/0.3.0 \\
        --input-price 0.00015 --output-price 0.0006 --cost-per-request 0.01
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cauterule.measurement.cost import (  # noqa: E402
    CostModel,
    CostReport,
    measure_cost,
    records_from_results,
)


def _load_results(results_file: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in results_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _model_for(results_file: Path, root: Path) -> str:
    parts = results_file.relative_to(root).parts
    # <corpus>/<model>/<date>/results.jsonl -> model
    return parts[-3] if len(parts) >= 3 else parts[0]


# Real OpenRouter list prices (USD per 1k tokens), matched by model substring.
# Source: openrouter.ai model pages, 2026-09. Override with --input-price /
# --output-price for models not listed.
_PRICE_MAP: dict[str, CostModel] = {
    "gpt-4o-mini": CostModel(input_price_per_1k=0.00015, output_price_per_1k=0.0006),
    "llama-3.1-8b": CostModel(input_price_per_1k=0.00006, output_price_per_1k=0.00006),
}


def _cost_model_for(model_name: str, fallback: CostModel) -> CostModel:
    for key, cost_model in _PRICE_MAP.items():
        if key in model_name:
            return cost_model
    return fallback


def collect(
    root: Path,
    model: CostModel,
    *,
    extraction_passes: int = 2,
    exclude_local: bool = True,
) -> dict[str, list[dict]]:
    """Return {model: [per-corpus report dict, ...]}.

    Local OMLX runs are excluded by default (they are not part of the v0.3.0
    cloud-only reports, #713).
    """
    by_model: dict[str, list[dict]] = {}
    for results_file in sorted(root.rglob("results.jsonl")):
        model_name = _model_for(results_file, root)
        if exclude_local and "omlx" in model_name.lower():
            continue
        cost_model = _cost_model_for(model_name, model)
        records = records_from_results(
            _load_results(results_file), extraction_passes=extraction_passes
        )
        report: CostReport = measure_cost(records, cost_model=cost_model)
        corpus = results_file.relative_to(root).parts[0]
        by_model.setdefault(model_name, []).append(
            {
                "corpus": corpus,
                "trajectories": report.trajectories,
                "llm_requests": report.llm_requests,
                "candidates": report.candidates_produced,
                "promoted": report.rules_promoted,
                "gate_dropped": report.gate_dropped,
                "prompt_tokens": report.prompt_tokens,
                "completion_tokens": report.completion_tokens,
                "total_cost_usd": report.total_cost_usd,
                "cost_per_candidate": report.cost_per_candidate,
                "cost_per_promoted_rule": report.cost_per_promoted_rule,
                "cost_per_1k_trajectories": report.cost_per_1k_trajectories,
                # Gate savings = cost avoided on gate-dropped trajectories, using
                # the measured average cost per LLM request for this model.
                "gate_savings_usd": (
                    report.total_cost_usd / report.llm_requests * report.gate_dropped
                    if report.llm_requests
                    else 0.0
                ),
            }
        )
    return by_model


def render_markdown(by_model: dict[str, list[dict]], model: CostModel) -> str:
    lines = [
        "# Cost Measurement — CauterRule v0.3.0",
        "",
        "**Issues:** #653/#486 · **Plan:** §5.4/§7.4",
        "",
        f"**Pricing:** real per-model token prices (gpt-4o-mini $0.15/$0.60 per 1M; "
        f"llama-3.1-8b $0.06/$0.06 per 1M). Fallback request price "
        f"${model.cost_per_request_usd}/request for models not in the price map. "
        "**Cloud models only** (#713).",
        "",
        "| Model | Trajs | LLM reqs | Candidates | Promoted | Total $ | $/candidate | $/promoted | $/1k trajs | Gate savings |",
        "|-------|-------|----------|------------|----------|---------|-------------|------------|------------|--------------|",
    ]
    for model_name, rows in sorted(by_model.items()):
        trajs = sum(r["trajectories"] for r in rows)
        reqs = sum(r["llm_requests"] for r in rows)
        cands = sum(r["candidates"] for r in rows)
        promoted = sum(r["promoted"] for r in rows)
        total = sum(r["total_cost_usd"] for r in rows)
        savings = sum(r["gate_savings_usd"] for r in rows)
        per_cand = total / cands if cands else 0.0
        per_promoted = total / promoted if promoted else 0.0
        per_1k = total / trajs * 1000 if trajs else 0.0
        lines.append(
            f"| {model_name} | {trajs} | {reqs} | {cands} | {promoted} | "
            f"${total:.4f} | ${per_cand:.4f} | ${per_promoted:.4f} | "
            f"${per_1k:.2f} | ${savings:.4f} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default=str(REPO / "field-test" / "results" / "0.3.0"))
    parser.add_argument("--input-price", type=float, default=0.0)
    parser.add_argument("--output-price", type=float, default=0.0)
    parser.add_argument("--cost-per-request", type=float, default=0.01)
    parser.add_argument(
        "--output",
        default=str(REPO / "docs" / "field-test" / "v0.3.0" / "cost-measurement.md"),
    )
    parser.add_argument("--json-output", default=None)
    parser.add_argument(
        "--include-local",
        action="store_true",
        help="Include local OMLX runs (excluded by default; #713).",
    )
    args = parser.parse_args(argv)

    root = Path(args.results)
    if not root.is_dir():
        print(f"[error] results root not found: {root}")
        return 1
    model = CostModel(
        input_price_per_1k=args.input_price,
        output_price_per_1k=args.output_price,
        cost_per_request_usd=args.cost_per_request,
    )
    by_model = collect(root, model, exclude_local=not args.include_local)
    if not by_model:
        print(f"[error] no results.jsonl found under {root}")
        return 1
    md = render_markdown(by_model, model)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"wrote {out}")
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(by_model, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
