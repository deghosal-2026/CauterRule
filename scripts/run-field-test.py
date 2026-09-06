#!/usr/bin/env python3
"""Field-test runner for CauterRule corpora.

Run per corpus type with configurable LLM, output to dated subdirs.
Writes results incrementally so you can tail progress mid-run.

Output structure: {output-dir}/{corpus-type}/{llm_provider}-{llm_model}/{timestamp}/
  meta.json       — run config
  results.jsonl   — one result per trajectory (appended live)
  summary.json    — aggregate metrics (rewritten live)

Usage:
  # Run golden corpus with local OMLX (Llama via OpenAI-compatible endpoint)
  CAUTERULE_LLM_API_KEY=dummy \
  python scripts/run-field-test.py golden \
    --llm-provider openai --llm-model llama-3.2-3b-instruct \
    --llm-base-url http://localhost:8000/v1 \
    --output-dir field-test/results
  # Output: field-test/results/golden/openai-llama-3.2-3b-instruct/<ts>/

  # Run curated failures with cloud GPT-4o-mini via OpenRouter
  CAUTERULE_LLM_API_KEY=sk-or-... \
  python scripts/run-field-test.py failures/positive \
    --llm-provider openai --llm-model openai/gpt-4o-mini \
    --llm-base-url https://openrouter.ai/api/v1 \
    --output-dir field-test/results
  # Output: field-test/results/failures_positive/openai-openai_gpt-4o-mini/<ts>/

  # Run all corpus types (serially, one after another)
  CAUTERULE_LLM_API_KEY=sk-or-... \
  python scripts/run-field-test.py --all \
    --llm-provider openai --llm-model openai/gpt-4o-mini \
    --llm-base-url https://openrouter.ai/api/v1 \
    --output-dir field-test/results
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CORPUS_ROOT = Path("field-test/corpus")

# ── corpus type → subdirectory under CORPUS_ROOT ──
CORPUS_TYPES: dict[str, Path] = {
    "golden":                  CORPUS_ROOT / "golden",
    "failures/positive":       CORPUS_ROOT / "curated" / "failures" / "positive",
    "failures/negative":       CORPUS_ROOT / "curated" / "failures" / "negative",
    "successes":               CORPUS_ROOT / "curated" / "successes",
    "nearmiss":                CORPUS_ROOT / "curated" / "nearmiss",
    "noisy":                   CORPUS_ROOT / "curated" / "noisy",
    "corrections":             CORPUS_ROOT / "curated" / "corrections",
    "raw/opencode":            CORPUS_ROOT / "raw" / "opencode",
    "raw/synthetic":           CORPUS_ROOT / "raw" / "synthetic",
    "raw/ci":                  CORPUS_ROOT / "raw" / "ci",
    "raw/sibling-repos":       CORPUS_ROOT / "raw" / "sibling-repos",
    "raw/corrections":         CORPUS_ROOT / "raw" / "corrections",
    "raw/cross-session":       CORPUS_ROOT / "raw" / "cross-session",
}

# Reference corpus loaded for replay-testing every candidate
REFERENCE_BUCKETS = [
    CORPUS_ROOT / "curated" / "failures" / "positive",
    CORPUS_ROOT / "curated" / "failures" / "negative",
    CORPUS_ROOT / "curated" / "successes",
    CORPUS_ROOT / "curated" / "nearmiss",
    CORPUS_ROOT / "curated" / "noisy",
    CORPUS_ROOT / "curated" / "corrections",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CauterRule field-test runner")
    parser.add_argument("corpus_type", nargs="?", help="Corpus type to test (e.g. golden, failures/positive)")
    parser.add_argument("--all", action="store_true", help="Run all corpus types sequentially")
    parser.add_argument("--llm-provider", default="openai", help="LLM provider (openai, anthropic, ollama, litellm)")
    parser.add_argument("--llm-model", default="gpt-4o-mini", help="Model name")
    parser.add_argument("--llm-base-url", default="", help="Base URL for custom endpoints (e.g. OMLX)")
    parser.add_argument("--output-dir", default="field-test/results/0.1.0", help="Output directory for results")
    parser.add_argument("--max-workers", type=int, default=4, help="Parallel trajectories per corpus type")
    parser.add_argument("--extraction-passes", type=int, default=2, help="Multi-pass extraction passes")
    parser.add_argument("--temperatures", default="0.2,0.5", help="Comma-separated temperatures for multi-pass")
    args = parser.parse_args()
    if not args.all and not args.corpus_type:
        parser.error("specify a corpus_type or --all")
    return args


# ── LLM + extraction (library calls, no subprocess) ────────────────────

_LLM_CACHE: dict[str, Any] = {}


def _get_llm(provider: str, model: str, base_url: str):
    """Build or return cached LLM provider instance."""
    cache_key = f"{provider}/{model}/{base_url}"
    if cache_key in _LLM_CACHE:
        return _LLM_CACHE[cache_key]

    from cauterule.config import (
        Config, LLMConfig, PathsConfig, ThresholdsConfig,
        PromotionConfig, RedactionConfig, ExtractionConfig,
    )
    from cauterule.llm.factory import get_llm

    api_key = os.getenv("CAUTERULE_LLM_API_KEY", "")
    cfg = Config(
        llm=LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
        ),
        paths=PathsConfig(),
        thresholds=ThresholdsConfig(),
        promotion=PromotionConfig(),
        redaction=RedactionConfig(),
        extraction=ExtractionConfig(),
    )
    llm = get_llm(cfg)
    _LLM_CACHE[cache_key] = llm
    return llm


def extract_candidates(
    trajectory: dict,
    llm_provider: str,
    llm_model: str,
    llm_base_url: str,
    temperatures: list[float],
) -> list[dict]:
    """Run multi-pass extraction using the CauterRule library directly.

    Returns a list of candidate dicts with keys:
        when, do, confidence, extraction_pass, reasoning, llm_response
    """
    from cauterule.extraction.extractor import _parse_candidate_json
    from cauterule.extraction.prompt import build_extraction_prompt
    from cauterule.models.trajectory import Trajectory

    llm = _get_llm(llm_provider, llm_model, llm_base_url)
    traj = Trajectory.from_dict(trajectory)

    candidates: list[dict] = []
    for idx, temp in enumerate(temperatures, start=1):
        try:
            prompt = build_extraction_prompt(traj)
            result = llm.complete(prompt, temperature=temp)
            raw_text = result.text if hasattr(result, "text") else str(result)

            candidate = _parse_candidate_json(
                raw_text, extraction_pass=idx, template=None,
            )

            from cauterule.extraction.quality import check_quality
            _ = check_quality(candidate, traj)

            candidates.append({
                "when": candidate.when.trigger,
                "do": candidate.do.directive,
                "confidence": candidate.confidence,
                "extraction_pass": candidate.extraction_pass,
                "reasoning": candidate.reasoning,
                "temperature": temp,
                "llm_response": raw_text,
            })
        except Exception as exc:
            print(f"NO CANDIDATE (pass {idx}, temp={temp}): {exc}")

    return candidates


# ── Replay testing (library calls) ──────────────────────────────────────

def replay_test_candidate(
    candidate: dict,
    reference_trajs: list[dict],
) -> dict:
    """Test candidate against reference trajectories using the replay engine."""
    from cauterule.models.candidate import CandidateRule
    from cauterule.models.rule import RuleDo, RuleWhen
    from cauterule.models.trajectory import Trajectory
    from cauterule.replay.report import build_evidence_report

    cand = CandidateRule(
        when=RuleWhen(trigger=candidate["when"]),
        do=RuleDo(directive=candidate["do"]),
        confidence=candidate["confidence"],
        reasoning=candidate.get("reasoning"),
        extraction_pass=candidate.get("extraction_pass", 1),
    )

    traj_objs: list[Trajectory] = []
    for t in reference_trajs:
        try:
            traj_objs.append(Trajectory.from_dict(t))
        except Exception:
            pass

    report = build_evidence_report(cand, traj_objs)

    return {
        "candidate": candidate,
        "failures_prevented": list(report.failures_prevented),
        "successes_broken": list(report.successes_broken),
        "near_misses": list(report.near_misses),
        "precision": report.precision,
        "recall": report.recall,
        "verdict": report.verdict,
        "replay_trace": [dict(r) for r in report.replay_trace],
    }


# ── Corpus loading ──────────────────────────────────────────────────────

def load_trajectories(dir_path: Path) -> list[dict]:
    """Load all JSONL trajectories from *dir_path*."""
    if not dir_path.is_dir():
        return []
    trajs: list[dict] = []
    for f in sorted(dir_path.glob("*.jsonl")):
        try:
            trajs.append(json.loads(f.read_text().strip()))
        except Exception as exc:
            print(f"  [warn] skipping {f.name}: {exc}")
    return trajs


def load_trajectory(file_path: Path) -> dict | None:
    try:
        return json.loads(file_path.read_text().strip())
    except Exception as exc:
        print(f"  [warn] skipping {file_path.name}: {exc}")
        return None


# ── Per-trajectory processing ───────────────────────────────────────────

def process_one_trajectory(
    traj_path: Path,
    traj_idx: int,
    total: int,
    corpus_type: str,
    reference_trajs: list[dict],
    args: argparse.Namespace,
) -> dict:
    """Extract + test a single trajectory, return result record."""
    tid = traj_path.stem
    print(f"  [{traj_idx}/{total}] {tid} ... ", end="", flush=True)

    trajectory = load_trajectory(traj_path)
    if trajectory is None:
        print("SKIP (load failed)")
        return {"trajectory_id": tid, "status": "skipped", "error": "load failed"}

    temperatures = [float(t) for t in args.temperatures.split(",")]

    candidates = extract_candidates(
        trajectory, args.llm_provider, args.llm_model, args.llm_base_url, temperatures,
    )
    if not candidates:
        print("NO CANDIDATES")
        return {"trajectory_id": tid, "status": "no_candidates", "candidates": []}

    test_results = []
    for cand in candidates:
        test_result = replay_test_candidate(cand, reference_trajs)
        test_results.append(test_result)

    best = max(test_results, key=lambda r: r["precision"] * r["recall"]) if test_results else {}
    print(f"{len(candidates)} candidates, best: precision={best.get('precision',0):.2f} recall={best.get('recall',0):.2f} verdict={best.get('verdict','?')}")

    return {
        "trajectory_id": tid,
        "status": "done",
        "trajectory": {k: trajectory.get(k) for k in ("task", "domain", "failure_class", "quality_label", "success", "expected_rule")},
        "candidate_count": len(candidates),
        "candidates": test_results,
        "best": best,
    }


# ── Summary writer (incremental) ───────────────────────────────────────

def _write_summary(results: list[dict], summary_file: Path, meta: dict, start_time: float) -> None:
    """Write a live summary that gets updated after each trajectory."""
    done = [r for r in results if r.get("status") == "done"]
    skipped = [r for r in results if r.get("status") != "done"]
    total_candidates = sum(r.get("candidate_count", 0) for r in done)

    best_results = [r.get("best", {}) for r in done if r.get("best")]
    avg_precision = sum(r.get("precision", 0) for r in best_results) / len(best_results) if best_results else 0.0
    avg_recall = sum(r.get("recall", 0) for r in best_results) / len(best_results) if best_results else 0.0
    passing = sum(1 for r in best_results if r.get("verdict") == "pass")
    failing = sum(1 for r in best_results if r.get("verdict") == "fail")
    inconclusive = sum(1 for r in best_results if r.get("verdict") == "inconclusive")

    summary = {
        "meta": meta,
        "elapsed_seconds": round(time.time() - start_time, 1),
        "total": len(results),
        "done": len(done),
        "skipped": len(skipped),
        "total_candidates": total_candidates,
        "avg_precision": round(avg_precision, 3),
        "avg_recall": round(avg_recall, 3),
        "passing": passing,
        "failing": failing,
        "inconclusive": inconclusive,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    summary_file.write_text(json.dumps(summary, indent=2))


# ── Main per-corpus runner ──────────────────────────────────────────────

def run_corpus_type(corpus_type: str, args: argparse.Namespace) -> int:
    """Run field test for one corpus type. Returns number of trajectories processed."""
    corpus_dir = CORPUS_TYPES.get(corpus_type)
    if corpus_dir is None:
        print(f"[error] unknown corpus type: {corpus_type}. Known: {list(CORPUS_TYPES)}")
        return 0

    if not corpus_dir.is_dir():
        print(f"[error] corpus directory not found: {corpus_dir}")
        return 0

    print(f"\n{'='*60}")
    print(f"Field Test: {corpus_type}")
    print(f"  LLM:      {args.llm_provider}/{args.llm_model}")
    if args.llm_base_url:
        print(f"  Base URL: {args.llm_base_url}")
    print(f"  Corpus:   {corpus_dir}")
    print(f"{'='*60}\n")

    # Load reference trajectories once
    reference_trajs: list[dict] = []
    for bucket in REFERENCE_BUCKETS:
        reference_trajs.extend(load_trajectories(bucket))
    print(f"  Reference corpus: {len(reference_trajs)} trajectories loaded")

    # Discover trajectories
    traj_files = sorted(corpus_dir.glob("*.jsonl"))
    if not traj_files:
        print(f"  [warn] no .jsonl files in {corpus_dir}")
        return 0
    print(f"  Target corpus: {len(traj_files)} trajectories\n")

    # Output directory: {output-dir}/{corpus-type}/{llm_provider}-{llm_model}/{timestamp}/
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if args.llm_base_url and "localhost" in args.llm_base_url:
        llm_label = f"omlx-{args.llm_provider}-{args.llm_model}"
    else:
        llm_label = f"{args.llm_provider}-{args.llm_model}"
    llm_label = llm_label.replace("/", "_")
    out_dir = Path(args.output_dir) / corpus_type.replace("/", "_") / llm_label / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    results_file = out_dir / "results.jsonl"
    summary_file = out_dir / "summary.json"
    meta_file = out_dir / "meta.json"

    # Clear previous results from same-day reruns to avoid contamination
    results_file.write_text("")
    summary_file.write_text("{}")

    # Write run metadata
    meta = {
        "corpus_type": corpus_type,
        "timestamp": timestamp,
        "llm_provider": args.llm_provider,
        "llm_model": args.llm_model,
        "llm_base_url": args.llm_base_url,
        "extraction_passes": args.extraction_passes,
        "temperatures": args.temperatures,
        "target_trajectories": len(traj_files),
        "reference_trajectories": len(reference_trajs),
    }
    meta_file.write_text(json.dumps(meta, indent=2))

    # Process trajectories in parallel
    results: list[dict] = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {}
        for i, f in enumerate(traj_files, 1):
            future = executor.submit(process_one_trajectory, f, i, len(traj_files), corpus_type, reference_trajs, args)
            futures[future] = f

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)

                # Write incrementally: append to results.jsonl
                with open(results_file, "a") as fh:
                    fh.write(json.dumps(result, default=str) + "\n")

                # Write incremental summary
                _write_summary(results, summary_file, meta, start_time)

            except Exception as exc:
                print(f"  [error] worker failed: {exc}")

    elapsed = time.time() - start_time
    print(f"\n  Done: {len(results)}/{len(traj_files)} processed in {elapsed:.0f}s")
    print(f"  Results: {results_file}")
    return len(results)


def main() -> None:
    args = parse_args()
    api_key = os.getenv("CAUTERULE_LLM_API_KEY")
    if not api_key and args.llm_provider in ("openai", "anthropic", "litellm") and not args.llm_base_url:
        print("[warn] CAUTERULE_LLM_API_KEY not set. Cloud LLMs will likely fail.")
        print("       Set it: export CAUTERULE_LLM_API_KEY=sk-...")
        print("       For local OMLX, use --llm-base-url http://localhost:8000/v1\n")

    types_to_run: list[str] = list(CORPUS_TYPES) if args.all else [args.corpus_type]
    for ct in types_to_run:
        run_corpus_type(ct, args)

    print("\nAll runs complete.")


if __name__ == "__main__":
    main()