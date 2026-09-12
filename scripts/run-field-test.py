#!/usr/bin/env python3
"""Field-test runner for CauterRule corpora (v0.2.0).

Run per corpus type with configurable LLM, output to dated subdirs.
Writes results incrementally so you can tail progress mid-run.

Output structure: {output-dir}/{corpus-type}/{llm_provider}-{llm_model}/{timestamp}/
  meta.json            — run config
  preflight.json       — preflight check results
  results.jsonl        — one result per trajectory (appended live)
  summary.json         — aggregate metrics with safety-adjusted scoring (rewritten live)
  harness_health.json  — harness health after sweep

v0.2.0 additions:
  — Pre-extraction gate (strict/relaxed modes per corpus type)
  — Corpus-aware matcher thresholds (0.70 curated, 0.45 raw, 0.40 cross-repo)
  — Safety-adjusted scoring (silence_rate, safety_summary)
  — Trigger specificity distribution (specific/moderate/generic)
  — Inconclusive attribution breakdown (broad_trigger/matcher_gap/corpus_mismatch/ambiguous_evidence)
  — Preflight checks (provider, corpus, cost estimate)
  — Harness health assertions (parse rate, completion ratio)
  — LLM call avoidance tracking (gate savings)
  — Validation suite runner: --run-validation runs all or a single hermetic suite
    (#432 hermetic CI, #433 sentinel benchmarks, #434 adversarial, #435 corpus,
     #437 scale, #443 TUI, #444 observability)

Usage:
  # Run golden corpus with local OMLX
  CAUTERULE_LLM_API_KEY=dummy \
  python scripts/run-field-test.py golden \
    --llm-provider openai --llm-model llama-3.2-3b-instruct \
    --llm-base-url http://localhost:8000/v1 \
    --output-dir field-test/results/0.2.0

  # Run all corpus types
  CAUTERULE_LLM_API_KEY=sk-or-... \
  python scripts/run-field-test.py --all \
    --llm-provider openai --llm-model openai/gpt-4o-mini \
    --llm-base-url https://openrouter.ai/api/v1 \
    --output-dir field-test/results/0.2.0

  # Run all hermetic validation suites (pre-field validation)
  python scripts/run-field-test.py --run-validation \
    --output-dir field-test/results/0.2.0

  # Run a single validation suite
  python scripts/run-field-test.py --run-validation --validation-suite sentinel_benchmark \
    --output-dir field-test/results/0.2.0
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

FIELD_TEST_ROOT = Path("field-test/corpus")
PUBLIC_ROOT = Path("corpus/public")

# ── corpus type → subdirectory ──
CORPUS_TYPES: dict[str, Path] = {
    # v0.1.0 curated corpora (field-test/corpus)
    "golden":                  FIELD_TEST_ROOT / "golden",
    "failures/positive":       FIELD_TEST_ROOT / "curated" / "failures" / "positive",
    "failures/negative":       FIELD_TEST_ROOT / "curated" / "failures" / "negative",
    "successes":               FIELD_TEST_ROOT / "curated" / "successes",
    "nearmiss":                FIELD_TEST_ROOT / "curated" / "nearmiss",
    "noisy":                   FIELD_TEST_ROOT / "curated" / "noisy",
    "corrections":             FIELD_TEST_ROOT / "curated" / "corrections",
    "raw/opencode":            FIELD_TEST_ROOT / "raw" / "opencode",
    "raw/synthetic":           FIELD_TEST_ROOT / "raw" / "synthetic",
    "raw/ci":                  FIELD_TEST_ROOT / "raw" / "ci",
    "raw/sibling-repos":       FIELD_TEST_ROOT / "raw" / "sibling-repos",
    "raw/corrections":         FIELD_TEST_ROOT / "raw" / "corrections",
    "raw/cross-session":       FIELD_TEST_ROOT / "raw" / "cross-session",
    # v0.2.0 public corpora (corpus/public)
    "public/golden":           PUBLIC_ROOT / "golden",
    "public/counterexample":   PUBLIC_ROOT / "counterexample",
    "public/nearmiss":         PUBLIC_ROOT / "nearmiss",
    "public/staleness":        PUBLIC_ROOT / "staleness",
    "public/synthetic":        PUBLIC_ROOT / "synthetic",
    "public/domains":          PUBLIC_ROOT / "domains",
    "adversarial/injection":   PUBLIC_ROOT / "adversarial" / "injection",
    "adversarial/misleading":  PUBLIC_ROOT / "adversarial" / "misleading",
    "adversarial/contradiction": PUBLIC_ROOT / "adversarial" / "contradiction",
    "adversarial/unsafe":      PUBLIC_ROOT / "adversarial" / "unsafe",
    "adversarial/poisoning":   PUBLIC_ROOT / "adversarial" / "poisoning",
    # v0.3.0 code-review #696: tool-output-borne + multi-turn compounding vectors
    "adversarial/tool_output_injection": PUBLIC_ROOT / "adversarial" / "tool_output_injection",
    "adversarial/compounding_multiturn": PUBLIC_ROOT / "adversarial" / "compounding_multiturn",
    # v0.3.0 code-review #699: AgentHarm-derived realistic unsafe vectors
    "adversarial/unsafe_realistic": PUBLIC_ROOT / "adversarial" / "unsafe_realistic",
    # v0.3.0 code-review #701: HarmBench-derived misleading + contradiction
    "adversarial/misleading_harmbench": PUBLIC_ROOT / "adversarial" / "misleading_harmbench",
    "adversarial/contradiction_harmbench": PUBLIC_ROOT / "adversarial" / "contradiction_harmbench",
    # v0.3.0 corpora (#635)
    "adapters":                FIELD_TEST_ROOT / "adapters",
    "lifecycle":               FIELD_TEST_ROOT / "lifecycle",
    "packs":                   FIELD_TEST_ROOT / "packs",
    "mcp":                     FIELD_TEST_ROOT / "mcp",
    "otel":                    FIELD_TEST_ROOT / "otel",
    # #489 reference expansion (public, 288 trajs)
    "reference-expansion":     PUBLIC_ROOT / "reference-expansion",
    # v0.3.0 code-review #698: paraphrase-diversity validation set (#689)
    "reference-expansion/paraphrase-diversity": PUBLIC_ROOT / "reference-expansion" / "paraphrase-diversity",
}

# Safety corpora use strict gate mode
SAFETY_CORPORA: frozenset[str] = frozenset({"successes", "failures/negative", "negative", "nearmiss"})

# Corpus-aware matcher thresholds
CORPUS_THRESHOLDS: dict[str, float] = {
    "golden": 0.70,
    "failures/positive": 0.70,
    "failures/negative": 0.70,
    "successes": 0.70,
    "nearmiss": 0.70,
    "noisy": 0.70,
    "corrections": 0.70,
    "raw/opencode": 0.45,
    "raw/synthetic": 0.45,
    "raw/ci": 0.45,
    "raw/sibling-repos": 0.40,
    "raw/corrections": 0.45,
    "raw/cross-session": 0.45,
    "public/golden": 0.70,
    "public/counterexample": 0.70,
    "public/nearmiss": 0.70,
    "public/staleness": 0.70,
    "public/synthetic": 0.60,
    "public/domains": 0.60,
    "adversarial/injection": 0.70,
    "adversarial/misleading": 0.70,
    "adversarial/contradiction": 0.70,
    "adversarial/unsafe": 0.70,
    "adversarial/poisoning": 0.70,
    "adversarial/tool_output_injection": 0.70,
    "adversarial/compounding_multiturn": 0.70,
    "adversarial/unsafe_realistic": 0.70,
    "adversarial/misleading_harmbench": 0.70,
    "adversarial/contradiction_harmbench": 0.70,
}

# Reference bucket paths (field-test/corpus curated)
REFERENCE_BUCKETS = [
    FIELD_TEST_ROOT / "curated" / "failures" / "positive",
    FIELD_TEST_ROOT / "curated" / "failures" / "negative",
    FIELD_TEST_ROOT / "curated" / "successes",
    FIELD_TEST_ROOT / "curated" / "nearmiss",
    FIELD_TEST_ROOT / "curated" / "noisy",
    FIELD_TEST_ROOT / "curated" / "corrections",
    # v0.3.0 #698: reference coverage for the previously-uncovered target
    # domains agent/lifecycle/mcp (see docs/field-test/v0.3.0/corpus-diagnostics.md).
    PUBLIC_ROOT / "adapters",
    PUBLIC_ROOT / "lifecycle",
    PUBLIC_ROOT / "mcp",
    # #700/#707: success counterparts from external sources (InjecAgent).
    PUBLIC_ROOT / "successes",
]

GATE_MODE_STRICT = "strict"
GATE_MODE_RELAXED = "relaxed"

# ── v0.2.0 hermetic validation suites (pre-field validation, issues #432-#437) ──
# Each maps to a section of field-test-plan.md §4. Suite → pytest target paths.
VALIDATION_SUITES: dict[str, dict[str, str]] = {
    "pre_extraction_gate": {
        "issue": "#432 (hermetic CI)",
        "targets": ["tests/extraction/test_gate.py"],
    },
    "replay_matcher": {
        "issue": "#432",
        "targets": ["tests/replay/test_matcher.py", "tests/replay/test_corpus_thresholds.py"],
    },
    "replay_safety": {
        "issue": "#432",
        "targets": ["tests/replay/test_safety.py"],
    },
    "replay_attribution": {
        "issue": "#432",
        "targets": ["tests/replay/test_attribution.py"],
    },
    "promotion_safety": {
        "issue": "#432",
        "targets": ["tests/promotion/test_safety.py"],
    },
    "extraction_specificity": {
        "issue": "#432",
        "targets": ["tests/extraction/test_specificity.py"],
    },
    "sentinel_benchmark": {
        "issue": "#433 (sentinel regression)",
        "targets": ["tests/benchmark/"],
    },
    "scale_benchmark": {
        "issue": "#437 (scale benchmarks)",
        "targets": ["tests/scale/"],
    },
    "adversarial": {
        "issue": "#434 (adversarial validation)",
        "targets": ["tests/adversarial/"],
    },
    "corpus": {
        "issue": "#435 (corpus validation)",
        "targets": ["tests/corpus/"],
    },
    "observe": {
        "issue": "#444 (observability)",
        "targets": ["tests/observe/"],
    },
    "tui": {
        "issue": "#443 (TUI review)",
        "targets": ["tests/tui/"],
    },
    # ── v0.3.0 validation suites (#629) ──
    "adapter_conformance": {
        "issue": "#540 (M4 adapter conformance)",
        "targets": ["tests/adapter_conformance/"],
    },
    "lifecycle": {
        "issue": "#512 (M4 rule lifecycle)",
        "targets": ["tests/lifecycle/"],
    },
    "packs": {
        "issue": "#479/#481 (M5 packs)",
        "targets": ["tests/packs/"],
    },
    "mcp_security": {
        "issue": "#601 (M6 MCP security)",
        "targets": ["tests/mcp/test_security.py"],
    },
    "otel_exporter": {
        "issue": "#588 (M6 OTEL exporter)",
        "targets": ["tests/integrations/test_otel_exporter.py"],
    },
    "corpus_cli": {
        "issue": "#606 (M6 corpus CLI)",
        "targets": ["tests/cli/test_corpus_cli.py"],
    },
    "benchmark_cli": {
        "issue": "#605/#606 (M6 benchmark CLI)",
        "targets": ["tests/cli/test_benchmark_cli.py", "benchmarks/"],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CauterRule field-test runner (v0.3.0)")
    parser.add_argument("corpus_type", nargs="?", help="Corpus type to test")
    parser.add_argument("--all", action="store_true", help="Run all corpus types sequentially")
    parser.add_argument("--llm-provider", default="openai", help="LLM provider")
    parser.add_argument("--llm-model", default="gpt-4o-mini", help="Model name")
    parser.add_argument("--llm-base-url", default="", help="Base URL for custom endpoints")
    parser.add_argument("--output-dir", default="field-test/results/0.3.0", help="Output directory")
    parser.add_argument("--max-workers", type=int, default=None, help="Parallel trajectories (default: 2 for local OMLX, otherwise 4)")
    parser.add_argument("--extraction-passes", type=int, default=2, help="Multi-pass extraction passes")
    parser.add_argument("--temperatures", default="0.2,0.5", help="Comma-separated temperatures")
    parser.add_argument("--skip-preflight", action="store_true", help="Skip preflight checks")
    parser.add_argument("--cost-per-request", type=float, default=0.01, help="Estimated $ per LLM request")
    parser.add_argument("--run-validation", action="store_true", help="Run all v0.2.0 hermetic validation suites (#432-#437, #443-#444)")
    parser.add_argument("--validation-suite", default=None, help="Run a single validation suite only (see VALIDATION_SUITES keys)")
    parser.add_argument("--model-config", default=None, help="YAML file with per-model overrides (v0.3.0 #629)")
    parser.add_argument("--regression-v020", action="store_true", help="Compare v0.3.0 results to v0.2.0 baseline (v0.3.0 #629)")
    args = parser.parse_args()
    if args.max_workers is None:
        args.max_workers = 2 if (args.llm_base_url and "localhost" in args.llm_base_url) else 4
    if not args.all and not args.corpus_type and not args.run_validation:
        parser.error("specify a corpus_type, --all, or --run-validation")
    return args


# ── Preflight ──────────────────────────────────────────────────────────

def run_preflight_checks(corpus_type: str, corpus_dir: Path, args: argparse.Namespace) -> dict:
    from cauterule.config import Config, LLMConfig, PathsConfig, ThresholdsConfig, PromotionConfig, RedactionConfig, ExtractionConfig
    from cauterule.preflight import run_preflight

    api_key = os.getenv("CAUTERULE_LLM_API_KEY", "")
    cfg = Config(
        llm=LLMConfig(provider=args.llm_provider, model=args.llm_model, api_key=api_key, base_url=args.llm_base_url),
        paths=PathsConfig(),
        thresholds=ThresholdsConfig(),
        promotion=PromotionConfig(),
        redaction=RedactionConfig(),
        extraction=ExtractionConfig(),
    )
    result = run_preflight(cfg, corpus_path=str(corpus_dir), cost_per_request_usd=args.cost_per_request)
    return {
        "passed": result.passed,
        "provider_checks": [{"name": c.name, "passed": c.passed, "message": c.message} for c in result.provider_checks],
        "corpus_checks": [{"name": c.name, "passed": c.passed, "message": c.message} for c in result.corpus_checks],
        "cost_estimate_usd": result.cost_estimate_usd,
        "warnings": result.warnings,
    }


# ── LLM + extraction ──────────────────────────────────────────────────

_LLM_CACHE: dict[str, Any] = {}


def _get_llm(provider: str, model: str, base_url: str):
    cache_key = f"{provider}/{model}/{base_url}"
    if cache_key in _LLM_CACHE:
        return _LLM_CACHE[cache_key]
    from cauterule.config import Config, LLMConfig, PathsConfig, ThresholdsConfig, PromotionConfig, RedactionConfig, ExtractionConfig
    from cauterule.llm.factory import get_llm
    api_key = os.getenv("CAUTERULE_LLM_API_KEY", "")
    cfg = Config(
        llm=LLMConfig(provider=provider, model=model, api_key=api_key, base_url=base_url),
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
            candidate = _parse_candidate_json(raw_text, extraction_pass=idx, template=None)
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


# ── Gate ───────────────────────────────────────────────────────────────

def run_gate(trajectory: dict, corpus_type: str) -> dict:
    from cauterule.extraction.gate import run_gate, GateMode
    from cauterule.models.trajectory import Trajectory
    base = corpus_type.split("/")[-1].strip().lower()
    mode: GateMode = GATE_MODE_STRICT if base in SAFETY_CORPORA else GATE_MODE_RELAXED
    traj = Trajectory.from_dict(trajectory)
    result = run_gate(traj, mode=mode)
    return {
        "should_extract": result.should_extract,
        "reason": result.reason,
        "failure_signals": list(result.failure_signals),
        "is_silence": result.is_silence,
        "gate_mode": mode,
    }


# ── Replay testing ─────────────────────────────────────────────────────

def replay_test_candidate(
    candidate: dict,
    reference_trajs: list[dict],
    corpus_type: str,
    is_omlx: bool = False,
    exclude_ids: set[str] | None = None,
) -> dict:
    from cauterule.models.candidate import CandidateRule
    from cauterule.models.rule import RuleDo, RuleWhen
    from cauterule.models.trajectory import Trajectory
    from cauterule.replay.report import build_evidence_report
    from cauterule.replay.matcher import threshold_for_corpus, match_detail

    cand = CandidateRule(
        when=RuleWhen(trigger=candidate["when"]),
        do=RuleDo(directive=candidate["do"]),
        confidence=candidate["confidence"],
        reasoning=candidate.get("reasoning"),
        extraction_pass=candidate.get("extraction_pass", 1),
    )
    traj_objs: list[Trajectory] = []
    for t in reference_trajs:
        # Exclude the candidate's own source trajectory from the reference
        # set — a nearmiss/success trajectory must not count itself as a
        # "prevented" failure (v0.3.0 field-test fix: N-00x self-matches
        # inflated precision to 1.0 on a single trajectory).
        if exclude_ids and t.get("trajectory_id") in exclude_ids:
            continue
        if exclude_ids and t.get("id") in exclude_ids:
            continue
        try:
            traj_objs.append(Trajectory.from_dict(t))
        except Exception:
            pass

    threshold = threshold_for_corpus(corpus_type, omlx=is_omlx)
    report = build_evidence_report(cand, traj_objs, threshold=threshold)

    # Capture match_detail diagnostics from the first reference trajectory
    match_diag: dict | None = None
    if traj_objs:
        try:
            match_diag = match_detail(cand, traj_objs[0])
        except Exception:
            match_diag = None

    return {
        "candidate": candidate,
        "failures_prevented": list(report.failures_prevented),
        "successes_broken": list(report.successes_broken),
        "near_misses": list(report.near_misses),
        "precision": report.precision,
        "recall": report.recall,
        "verdict": report.verdict,
        "replay_trace": [dict(r) for r in report.replay_trace],
        "threshold": threshold,
        "match_detail": match_diag,
    }


# ── Corpus loading ────────────────────────────────────────────────────

def load_trajectories(dir_path: Path) -> list[dict]:
    if not dir_path.is_dir():
        return []
    trajs: list[dict] = []
    for f in sorted(dir_path.glob("*.jsonl")):
        try:
            lines = f.read_text().strip().split("\n")
            for line in lines:
                line = line.strip()
                if line:
                    trajs.append(json.loads(line))
        except Exception as exc:
            print(f"  [warn] skipping {f.name}: {exc}")
    return trajs


def load_trajectory(file_path: Path) -> list[dict]:
    """Load a trajectory file as JSONL; return the list of record dicts.

    Single-record .jsonl files yield one dict; multi-record files (the
    v0.3.0 corpora: adapters/lifecycle/packs/mcp/otel) yield many.  The
    previous whole-file json.loads() could only read one-record files —
    the new corpora were silently processed as a single trajectory.
    """
    records: list[dict] = []
    try:
        text = file_path.read_text().strip()
    except Exception as exc:
        print(f"  [warn] skipping {file_path.name}: {exc}")
        return records
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except Exception as exc:
            print(f"  [warn] skipping line in {file_path.name}: {exc}")
    return records


# ── Per-trajectory processing ─────────────────────────────────────────

def process_one_trajectory(
    trajectory: dict,
    tid: str,
    traj_idx: int,
    total: int,
    corpus_type: str,
    reference_trajs: list[dict],
    args: argparse.Namespace,
) -> dict:
    print(f"  [{traj_idx}/{total}] {tid} ... ", end="", flush=True)

    gate_result = run_gate(trajectory, corpus_type)
    pre_extraction_drop = gate_result["is_silence"]

    # v0.2.0: specificity scoring on trajectory task
    from cauterule.extraction.specificity import score_specificity
    task_specificity = score_specificity(trajectory.get("task", ""))

    temperatures = [float(t) for t in args.temperatures.split(",")]

    # If gate dropped, no LLM call
    if pre_extraction_drop:
        print("GATE DROPPED (no failure signal)")
        return {
            "trajectory_id": tid,
            "status": "gate_dropped",
            "candidate_count": 0,
            "candidates": [],
            "gate": gate_result,
            "task_specificity": task_specificity,
            "pre_extraction_drop": True,
            "llm_calls_avoided": len(temperatures),
        }

    candidates = extract_candidates(
        trajectory, args.llm_provider, args.llm_model, args.llm_base_url, temperatures,
    )
    if not candidates:
        print("NO CANDIDATES")
        return {
            "trajectory_id": tid,
            "status": "no_candidates",
            "candidates": [],
            "gate": gate_result,
            "task_specificity": task_specificity,
            "pre_extraction_drop": False,
            "llm_calls_avoided": 0,
        }

    test_results = []
    is_omlx = args.llm_base_url and "localhost" in args.llm_base_url
    exclude_ids = {
        str(oid) for oid in (trajectory.get("id"), trajectory.get("trajectory_id"), tid)
        if oid is not None
    }
    for cand in candidates:
        test_result = replay_test_candidate(cand, reference_trajs, corpus_type, is_omlx=is_omlx, exclude_ids=exclude_ids)
        # v0.2.0: specificity scoring on trigger
        test_result["trigger_specificity"] = score_specificity(cand["when"])
        # v0.2.0: inconclusive attribution
        if test_result.get("verdict") == "inconclusive":
            from cauterule.replay.attribution import attribute_inconclusive
            from cauterule.models.candidate import CandidateRule
            from cauterule.models.rule import RuleDo, RuleWhen
            from cauterule.models.trajectory import Trajectory
            from cauterule.replay.report import build_evidence_report
            cand_obj = CandidateRule(
                when=RuleWhen(trigger=cand["when"]),
                do=RuleDo(directive=cand["do"]),
                confidence=cand["confidence"],
                reasoning=cand.get("reasoning"),
                extraction_pass=cand.get("extraction_pass", 1),
            )
            traj_objs = []
            for t in reference_trajs:
                try:
                    traj_objs.append(Trajectory.from_dict(t))
                except Exception:
                    pass
            ev_report = build_evidence_report(cand_obj, traj_objs)
            reason = attribute_inconclusive(cand_obj, traj_objs, ev_report)
            test_result["inconclusive_reason"] = reason
        test_results.append(test_result)

    best = max(test_results, key=lambda r: r["precision"] * r["recall"]) if test_results else {}
    print(f"{len(candidates)} candidates, best: precision={best.get('precision',0):.2f} recall={best.get('recall',0):.2f} verdict={best.get('verdict','?')}")

    return {
        "trajectory_id": tid,
        "status": "done",
        "trajectory": {k: trajectory.get(k) for k in ("task", "domain", "failure_class", "quality_label", "success", "expected_rule", "expected_outcome")},
        "candidate_count": len(candidates),
        "candidates": test_results,
        "best": best,
        "gate": gate_result,
        "task_specificity": task_specificity,
        "pre_extraction_drop": False,
        "llm_calls_avoided": 0,
    }


# ── Summary writer (v0.2.0 with safety-adjusted scoring) ──────────────

def _write_summary(results: list[dict], summary_file: Path, meta: dict, start_time: float, corpus_type: str) -> None:
    done = [r for r in results if r.get("status") == "done"]
    gate_dropped = [r for r in results if r.get("status") == "gate_dropped"]
    skipped = [r for r in results if r.get("status") not in ("done", "gate_dropped")]

    total_candidates = sum(r.get("candidate_count", 0) for r in done)
    total_llm_calls_avoided = sum(r.get("llm_calls_avoided", 0) for r in results)
    total_trajectories = len(results)

    best_results = [r.get("best", {}) for r in done if r.get("best")]
    avg_precision = sum(r.get("precision", 0) for r in best_results) / len(best_results) if best_results else 0.0
    avg_recall = sum(r.get("recall", 0) for r in best_results) / len(best_results) if best_results else 0.0
    passing = sum(1 for r in best_results if r.get("verdict") == "pass")
    failing = sum(1 for r in best_results if r.get("verdict") == "fail")
    inconclusive = sum(1 for r in best_results if r.get("verdict") == "inconclusive")

    # v0.2.0: safety-adjusted scoring
    from cauterule.replay.safety import classify_outcome, score_safety_trajectory, safety_summary
    safety_outcomes = []
    for r in done:
        best = r.get("best", {})
        outcome = classify_outcome(
            gate_is_silence=False,
            has_parse_error=False,
            candidate_count=r.get("candidate_count", 0),
            replay_verdict=best.get("verdict"),
        )
        safety_outcomes.append(outcome)
    for r in gate_dropped:
        safety_outcomes.append("silence")
    safety = safety_summary(safety_outcomes, corpus_type)

    # v0.2.0: specificity distribution
    specificity_counts: dict[str, int] = {"specific": 0, "moderate": 0, "generic": 0}
    for r in results:
        spec = r.get("task_specificity", "generic")
        specificity_counts[spec] = specificity_counts.get(spec, 0) + 1
    for r in done:
        for c in r.get("candidates", []):
            spec = c.get("trigger_specificity", "generic")
            specificity_counts[spec] = specificity_counts.get(spec, 0) + 1

    # v0.2.0: inconclusive attribution breakdown
    inconclusive_breakdown: dict[str, int] = {"broad_trigger": 0, "matcher_gap": 0, "corpus_mismatch": 0, "ambiguous_evidence": 0}
    for r in done:
        for c in r.get("candidates", []):
            if c.get("verdict") == "inconclusive" and c.get("inconclusive_reason") in inconclusive_breakdown:
                inconclusive_breakdown[c["inconclusive_reason"]] += 1

    # v0.2.0: match_detail aggregation
    match_scores: list[float] = []
    for r in done:
        for c in r.get("candidates", []):
            md = c.get("match_detail")
            if md and md.get("score") is not None:
                match_scores.append(md["score"])
    avg_match_score = round(sum(match_scores) / len(match_scores), 3) if match_scores else None

    # v0.3.0 (#697): break gate drops down by silencing reason so a spike in
    # one mechanism (e.g. #692 keyword substring, #693 output-as-success) is
    # visible without re-deriving it from raw results.jsonl.
    gate_dropped_by_reason: dict[str, int] = {}
    for r in gate_dropped:
        reason = (r.get("gate") or {}).get("reason") or "unknown"
        gate_dropped_by_reason[reason] = gate_dropped_by_reason.get(reason, 0) + 1

    # v0.3.0 (#695): report rate metrics with Wilson confidence intervals so
    # small-sample point estimates (n=10 golden, n=50 nearmiss, n=10/vector)
    # are not read as precise facts.
    from cauterule.stats import rate_with_ci
    confidence_intervals = {
        "pass_rate": rate_with_ci(passing, passing + failing),
        "safety_silence_rate": rate_with_ci(
            int(safety.get("silence", 0)), int(safety.get("total", 0))
        ),
    }

    summary = {
        "meta": meta,
        "elapsed_seconds": round(time.time() - start_time, 1),
        "total": total_trajectories,
        "done": len(done),
        "gate_dropped": len(gate_dropped),
        "gate_dropped_by_reason": gate_dropped_by_reason,
        "skipped": len(skipped),
        "total_candidates": total_candidates,
        "total_llm_calls_avoided": total_llm_calls_avoided,
        "avg_precision": round(avg_precision, 3),
        "avg_recall": round(avg_recall, 3),
        "avg_match_score": avg_match_score,
        "match_detail_count": len(match_scores),
        "passing": passing,
        "failing": failing,
        "inconclusive": inconclusive,
        "safety": safety,
        "confidence_intervals": confidence_intervals,
        "specificity_distribution": specificity_counts,
        "inconclusive_breakdown": inconclusive_breakdown,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    summary_file.write_text(json.dumps(summary, indent=2))


# ── Harness health ────────────────────────────────────────────────────

def write_harness_health(results: list[dict], meta: dict, corpus_type: str, health_file: Path) -> None:
    from cauterule.benchmark.harness import harness_health
    done = [r for r in results if r.get("status") == "done"]
    gate_dropped = [r for r in results if r.get("status") == "gate_dropped"]
    parsed = sum(1 for r in done if r.get("candidate_count", 0) > 0)
    total = len(done) + len(gate_dropped)
    candidates = sum(r.get("candidate_count", 0) for r in done)
    base = corpus_type.split("/")[-1].strip().lower()
    is_safety = base in SAFETY_CORPORA
    health = harness_health(
        parsed=parsed,
        total=total,
        candidates=candidates,
        trajectories=total,
        is_safety_corpus=is_safety,
    )
    health_data = {
        "passed": health.passed,
        "checks": [{"name": c.name, "passed": c.passed, "message": c.message, "value": c.value, "threshold": c.threshold} for c in health.checks],
        "warnings": health.warnings,
    }
    health_file.write_text(json.dumps(health_data, indent=2))


# ── Main per-corpus runner ────────────────────────────────────────────

def run_corpus_type(corpus_type: str, args: argparse.Namespace) -> int:
    corpus_dir = CORPUS_TYPES.get(corpus_type)
    if corpus_dir is None:
        print(f"[error] unknown corpus type: {corpus_type}. Known: {list(CORPUS_TYPES)}")
        return 0
    if not corpus_dir.is_dir():
        print(f"[error] corpus directory not found: {corpus_dir}")
        return 0

    print(f"\n{'='*60}")
    print(f"Field Test (v0.2.0): {corpus_type}")
    print(f"  LLM:      {args.llm_provider}/{args.llm_model}")
    if args.llm_base_url:
        print(f"  Base URL: {args.llm_base_url}")
    print(f"  Corpus:   {corpus_dir}")
    print(f"{'='*60}\n")

    # Output directory
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if args.llm_base_url and "localhost" in args.llm_base_url:
        llm_label = f"omlx-{args.llm_provider}-{args.llm_model}"
    else:
        llm_label = f"{args.llm_provider}-{args.llm_model}"
    llm_label = llm_label.replace("/", "_")
    out_dir = Path(args.output_dir) / corpus_type.replace("/", "_") / llm_label / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # Preflight
    if not args.skip_preflight:
        print("  Running preflight checks...")
        preflight_result = run_preflight_checks(corpus_type, corpus_dir, args)
        (out_dir / "preflight.json").write_text(json.dumps(preflight_result, indent=2))
        if not preflight_result["passed"]:
            print(f"  PREFLIGHT FAILED: {preflight_result['warnings']}")
            print("  Aborting. Use --skip-preflight to override.")
            return 0
        print(f"  Preflight OK (cost est: ${preflight_result.get('cost_estimate_usd', '?')})")
    else:
        preflight_result = {"passed": True, "cost_estimate_usd": None}

    # Load reference trajectories
    reference_trajs: list[dict] = []
    for bucket in REFERENCE_BUCKETS:
        reference_trajs.extend(load_trajectories(bucket))
    print(f"  Reference corpus: {len(reference_trajs)} trajectories loaded")

    # Discover trajectories — expand multi-record JSONL files into per-record
    # tasks (v0.3.0 corpora pack many records per file).
    traj_tasks: list[tuple[dict, str]] = []
    for tf in sorted(corpus_dir.rglob("*.jsonl")):
        for rec in load_trajectory(tf):
            tid = str(rec.get("trajectory_id") or rec.get("id") or tf.stem)
            traj_tasks.append((rec, tid))
    if not traj_tasks:
        print(f"  [warn] no .jsonl records in {corpus_dir}")
        return 0
    print(f"  Target corpus: {len(traj_tasks)} trajectories\n")

    results_file = out_dir / "results.jsonl"
    summary_file = out_dir / "summary.json"
    meta_file = out_dir / "meta.json"
    harness_file = out_dir / "harness_health.json"

    results_file.write_text("")
    summary_file.write_text("{}")

    meta = {
        "corpus_type": corpus_type,
        "timestamp": timestamp,
        "llm_provider": args.llm_provider,
        "llm_model": args.llm_model,
        "llm_base_url": args.llm_base_url,
        "extraction_passes": args.extraction_passes,
        "temperatures": args.temperatures,
        "target_trajectories": len(traj_tasks),
        "reference_trajectories": len(reference_trajs),
        "cost_per_request_usd": args.cost_per_request,
        "gate_mode": GATE_MODE_STRICT if corpus_type.split("/")[-1].strip().lower() in SAFETY_CORPORA else GATE_MODE_RELAXED,
    }
    meta_file.write_text(json.dumps(meta, indent=2))

    # Process trajectories
    results: list[dict] = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {}
        for i, (rec, tid) in enumerate(traj_tasks, 1):
            future = executor.submit(process_one_trajectory, rec, tid, i, len(traj_tasks), corpus_type, reference_trajs, args)
            futures[future] = tid

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                with open(results_file, "a") as fh:
                    fh.write(json.dumps(result, default=str) + "\n")
                _write_summary(results, summary_file, meta, start_time, corpus_type)
            except Exception as exc:
                print(f"  [error] worker failed: {exc}")

    # Harness health
    write_harness_health(results, meta, corpus_type, harness_file)
    health_data = json.loads(harness_file.read_text())
    health_status = "PASS" if health_data.get("passed") else "FAIL"
    print(f"  Harness health: {health_status}")

    elapsed = time.time() - start_time
    print(f"\n  Done: {len(results)}/{len(traj_tasks)} processed in {elapsed:.0f}s")
    print(f"  Results: {results_file}")
    return len(results)


# ── Validation suite runner (v0.2.0 pre-field validation) ─────────────

def run_validation(args: argparse.Namespace) -> int:
    """Run all or selected hermetic validation suites, writing results to 0.2.0 dir."""
    suites_to_run: dict[str, dict[str, str]] = {}
    if args.validation_suite:
        if args.validation_suite not in VALIDATION_SUITES:
            print(f"[error] unknown validation suite: {args.validation_suite}. Known: {list(VALIDATION_SUITES)}")
            return 1
        suites_to_run[args.validation_suite] = VALIDATION_SUITES[args.validation_suite]
    else:
        suites_to_run = dict(VALIDATION_SUITES)

    import subprocess

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_root = Path(args.output_dir) / "validation" / timestamp
    out_root.mkdir(parents=True, exist_ok=True)

    overall: dict[str, Any] = {
        "timestamp": timestamp,
        "suites": {},
        "total_passed": 0,
        "total_failed": 0,
        "total_errors": 0,
    }

    for suite_name, suite_info in suites_to_run.items():
        targets = suite_info["targets"]
        suffix = suite_info["issue"]
        xml_path = out_root / f"{suite_name}.xml"
        log_path = out_root / f"{suite_name}.log"

        print(f"\n{'='*60}")
        print(f"Validation Suite: {suite_name} ({suffix})")
        print(f"  Targets: {' '.join(targets)}")
        print(f"  XML:     {xml_path}")
        print(f"{'='*60}")

        cmd = [
            sys.executable, "-m", "pytest",
            *targets,
            "-v",
            f"--junitxml={xml_path}",
            "--tb=short",
        ]
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        elapsed = time.time() - start

        passed = result.returncode == 0
        log_path.write_text(result.stdout + "\n" + result.stderr)

        import re
        passed_count = 0
        failed_count = 0
        error_count = 0
        for line in result.stdout.split("\n"):
            m = re.search(r"=+ (\d+) passed", line)
            if m:
                passed_count += int(m.group(1))
            m = re.search(r"(\d+) failed", line)
            if m:
                failed_count += int(m.group(1))
            m = re.search(r"(\d+) errors?", line)
            if m:
                error_count += int(m.group(1))

        suite_result = {
            "passed": passed,
            "returncode": result.returncode,
            "elapsed_seconds": round(elapsed, 1),
            "passed_count": passed_count,
            "failed_count": failed_count,
            "error_count": error_count,
            "xml": str(xml_path),
            "log": str(log_path),
        }
        overall["suites"][suite_name] = suite_result
        overall["total_passed"] += passed_count
        overall["total_failed"] += failed_count
        overall["total_errors"] += error_count

        status = "PASS" if passed else "FAIL"
        print(f"  Result: {status} ({passed_count} passed, {failed_count} failed, {error_count} errors) in {elapsed:.0f}s")

    overall["all_passed"] = all(s["passed"] for s in overall["suites"].values())
    summary_path = out_root / "validation-summary.json"
    summary_path.write_text(json.dumps(overall, indent=2))

    # Copy sentinel_benchmark JUnit XML to standard location for report consumption
    benchmark_xml_src = out_root / "sentinel_benchmark.xml"
    benchmark_xml_dst = Path(args.output_dir) / "benchmark-results.xml"
    if benchmark_xml_src.exists():
        import shutil
        benchmark_xml_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(benchmark_xml_src), str(benchmark_xml_dst))
        print(f"\n  Benchmark XML: {benchmark_xml_dst}")

    print(f"\n{'='*60}")
    print(f"Validation Summary: {'ALL PASS' if overall['all_passed'] else 'SOME FAILED'}")
    print(f"  {overall['total_passed']} passed, {overall['total_failed']} failed, {overall['total_errors']} errors")
    print(f"  Summary: {summary_path}")
    print(f"{'='*60}")
    return 0 if overall["all_passed"] else 1


def _load_model_config(path: str) -> list[dict[str, str]]:
    """Load a YAML file of per-model overrides (v0.3.0 #629).

    Expected schema:
        models:
          - name: llama-3.2-3b-instruct
            provider: openai
            base_url: http://localhost:8000/v1
            temperatures: "0.2,0.5"
            max_cost: 1.0
    Returns a list of model-config dicts (name/provider/base_url/temperatures/max_cost).
    """
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(f"[error] PyYAML not installed: {exc}") from exc
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("models", [])


def _regression_v020(args: argparse.Namespace) -> int:
    """Compare v0.3.0 results to the v0.2.0 baseline (v0.3.0 #629).

    Walks field-test/results/0.2.0/{corpus}/{model}/{date}/summary.json and the
    current run dir, emits a per-corpus delta table (pass rate, inconclusive
    rate, specificity, silence rate). A >5pp regression on any metric is flagged.
    """
    baseline_root = Path("field-test/results/0.2.0")
    current_root = Path(args.output_dir)
    out_path = current_root / "regression-v020.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# v0.3.0 vs v0.2.0 Regression Comparison\n", "| Corpus | Metric | v0.2.0 | v0.3.0 | Delta | Flag |", "|--------|--------|-------|-------|-------|------|"]
    flagged = 0
    for summary in sorted(baseline_root.rglob("summary.json")):
        corpus = summary.parent.parent.parent.name
        try:
            old = json.loads(summary.read_text())
        except Exception:
            continue
        new_path = current_root / corpus.replace("/", "_") / summary.parent.parent.name / summary.parent.name / "summary.json"
        new = json.loads(new_path.read_text()) if new_path.is_file() else None
        if new is None:
            continue
        for metric in ("pass_rate", "inconclusive_rate", "silence_rate", "generic_trigger_pct"):
            o = float(old.get(metric, 0) or 0)
            n = float(new.get(metric, 0) or 0)
            delta = n - o
            flag = "⚠ regression" if (metric != "silence_rate" and delta < -0.05) or (metric == "silence_rate" and delta < -0.05) else ""
            if flag:
                flagged += 1
            lines.append(f"| {corpus} | {metric} | {o:.2f} | {n:.2f} | {delta:+.2f} | {flag} |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[regression] {out_path} ({flagged} regressions flagged)")
    return 0


def main() -> None:
    args = parse_args()

    if args.regression_v020:
        sys.exit(_regression_v020(args))

    if args.run_validation:
        sys.exit(run_validation(args))

    api_key = os.getenv("CAUTERULE_LLM_API_KEY")
    if not api_key and args.llm_provider in ("openai", "anthropic", "litellm") and not args.llm_base_url:
        print("[warn] CAUTERULE_LLM_API_KEY not set. Cloud LLMs will likely fail.")
        print("       Set it: export CAUTERULE_LLM_API_KEY=sk-...")
        print("       For local OMLX, use --llm-base-url http://localhost:8000/v1\n")

    # Multi-model config (v0.3.0 #629): if --model-config given, iterate models.
    if args.model_config:
        models = _load_model_config(args.model_config)
        if not models:
            raise SystemExit(f"[error] no 'models:' entries in {args.model_config}")
        for m in models:
            args.llm_provider = m.get("provider", args.llm_provider)
            args.llm_model = m.get("name", args.llm_model)
            args.llm_base_url = m.get("base_url", args.llm_base_url)
            if "temperatures" in m:
                args.temperatures = m["temperatures"]
            print(f"\n[model] {args.llm_provider}/{args.llm_model}")
            types_to_run = list(CORPUS_TYPES) if args.all else [args.corpus_type]
            for ct in types_to_run:
                run_corpus_type(ct, args)
    else:
        types_to_run: list[str] = list(CORPUS_TYPES) if args.all else [args.corpus_type]
        for ct in types_to_run:
            run_corpus_type(ct, args)

    print("\nAll runs complete.")


if __name__ == "__main__":
    main()