"""
v0.3.0 field-test corpus generator (#635).

Adds the new corpora the field-test-plan §14.1 requires:
  - field-test/corpus/adapters/   (langgraph/crewai/pydanticai, ~6 each)
  - field-test/corpus/lifecycle/   (stale/harmful/superseded/outcome-evolving)
  - field-test/corpus/packs/       (pack-git/pack-docker/pack-testing/pack-deploy replay)
  - field-test/corpus/mcp/         (valid/malformed/abusive report_failure payloads)
  - field-test/corpus/otel/        (extract/test/promote/retire span-attribute trajectories)

Each trajectory carries full annotation metadata (expected_outcome, domain,
quality_label, tags) and the v0.3.0 fields framework / pack / lifecycle_stage /
session_id where relevant (extra keys, ignored by the loader, asserted later).

Usage:
  python scripts/generate-v030-corpus.py
  python scripts/normalize-corpus.py --path field-test/corpus/adapters ...
  pytest tests/corpus/ -q
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

BASE = Path("field-test/corpus")
TS = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write(dirpath: Path, records: list[dict]) -> None:
    dirpath.mkdir(parents=True, exist_ok=True)
    p = dirpath / f"{dirpath.name}.jsonl"
    with p.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    print(f"  wrote {len(records):>3} -> {p}")


def _traj(tid, task, steps, *, success, failure_point, failure_class, domain, severity,
          quality_label, tags, expected_outcome, rationale, confidence="high",
          extra=None) -> dict:
    d = {
        "trajectory_id": tid, "id": tid, "timestamp": TS, "task": task,
        "steps": steps, "success": success,
        "failure_point": failure_point, "failure_class": failure_class,
        "quality_label": quality_label, "domain": domain, "severity": severity,
        "tags": list(tags), "source": "v030-corpus", "source_repo": "CauterRule",
        "redacted": False,
        "expected_outcome": expected_outcome,
        "expected_outcome_rationale": rationale,
        "expected_outcome_confidence": confidence,
    }
    if extra:
        d.update(extra)
    return d


def _step(n, tool, cmd, err=None, out=None) -> dict:
    return {"step_number": n, "tool": tool, "input": cmd, "output": out, "error": err}


# ── adapters: 6 per framework (3 frameworks = 18) ────────────────────────
def gen_adapters() -> int:
    recs: list[dict] = []
    fw = [
        ("langgraph", "python", "agent/graph", "LangGraph node raised an exception"),
        ("crewai", "python", "agent/crew", "CrewAI task errored during execution"),
        ("pydanticai", "python", "agent/pydantic", "PydanticAI agent failed validation"),
    ]
    for framework, domain, fc, err in fw:
        for i in range(1, 7):
            recs.append(_traj(
                f"adapter-{framework}-{i:03d}",
                f"Run {framework} agent task {i} that fails",
                [_step(1, framework, f"agent.run(task_{i})", err)],
                success=False, failure_point="step_1", failure_class=fc,
                domain=domain, severity="medium", quality_label="clear",
                tags=(framework, "adapter", "agent"), expected_outcome="should_extract",
                rationale=f"Adapter captured a real {framework} failure",
                extra={"framework": framework},
            ))
    _write(BASE / "adapters", recs)
    return len(recs)


# ── lifecycle: stale/harmful/superseded/outcome-evolving (10 each = 40) ───
def gen_lifecycle() -> int:
    stages = [
        ("stale", "should_reject", "Rule has not matched any trajectory in 5+ sessions"),
        ("harmful", "should_reject", "Rule matched a should_silence trajectory (broke a success)"),
        ("superseded", "should_reject", "Rule replaced by a more-specific successor"),
        ("outcome-evolving", "should_extract", "Rule outcome shifted from prevented to neutral over sessions"),
    ]
    recs: list[dict] = []
    for stage, outcome, rationale in stages:
        for i in range(1, 11):
            success = stage in ("harmful",)
            recs.append(_traj(
                f"lifecycle-{stage}-{i:03d}",
                f"Lifecycle {stage} scenario {i}",
                [_step(1, "bash", f"run scenario {i}", None if success else f"{stage} failure")],
                success=success, failure_point=None if success else "step_1",
                failure_class=f"lifecycle/{stage}",
                domain=["git", "python", "docker", "ci", "shell"][i % 5],
                severity="low", quality_label="clear",
                tags=("lifecycle", stage), expected_outcome=outcome,
                rationale=rationale,
                extra={"lifecycle_stage": stage, "session_id": f"s-{(i % 5) + 1}"},
            ))
    _write(BASE / "lifecycle", recs)
    return len(recs)


# ── packs: 10 per official pack (4 packs = 40) ──────────────────────────
def gen_packs() -> int:
    packs = [
        ("pack-git", "git", "git", "git/push/non-fast-forward"),
        ("pack-docker", "docker", "docker", "docker/build/package-not-found"),
        ("pack-testing", "testing", "python", "test/flaky"),
        ("pack-deploy", "devops", "devops", "deploy/timeout"),
    ]
    recs: list[dict] = []
    for pack, domain, tag, fc in packs:
        for i in range(1, 11):
            recs.append(_traj(
                f"pack-{pack}-{i:03d}",
                f"Replay {pack} rule {i} against a {tag} failure",
                [_step(1, "bash", f"{tag} cmd {i}", f"{fc}: error {i}")],
                success=False, failure_point="step_1", failure_class=fc,
                domain=domain, severity="medium", quality_label="clear",
                tags=("pack", pack, tag), expected_outcome="should_extract",
                rationale=f"Pack {pack} rule should fire on this {tag} failure",
                extra={"pack": pack},
            ))
    _write(BASE / "packs", recs)
    return len(recs)


# ── mcp: valid + malformed + abusive (20) ────────────────────────────────
def gen_mcp() -> int:
    recs: list[dict] = []
    # valid report_failure payloads (5)
    for i in range(1, 6):
        recs.append(_traj(
            f"mcp-valid-{i:03d}", f"MCP valid report_failure {i}",
            [_step(1, "mcp", "report_failure", None)],
            success=False, failure_point="step_1", failure_class="mcp/valid",
            domain="ci", severity="low", quality_label="clear",
            tags=("mcp", "valid"), expected_outcome="should_extract",
            rationale="Valid report_failure payload accepted by the MCP server",
        ))
    # malformed payloads (10) — should be schema-rejected
    for i, missing in enumerate(["trajectory", "error", "steps", "success", "task"], 1):
        for j in (1, 2):
            recs.append(_traj(
                f"mcp-malformed-{missing}-{j:03d}", f"MCP malformed report_failure missing {missing} ({j})",
                [_step(1, "mcp", "report_failure", f"schema validation: missing {missing}")],
                success=False, failure_point="step_1", failure_class="mcp/malformed",
                domain="ci", severity="medium", quality_label="misleading",
                tags=("mcp", "malformed", missing), expected_outcome="should_reject",
                rationale=f"Malformed payload (missing {missing}) must be schema-rejected (400)",
            ))
    # abusive / rate-limit bursts (5)
    for i in range(1, 6):
        recs.append(_traj(
            f"mcp-abusive-{i:03d}", f"MCP abusive burst {i}",
            [_step(1, "mcp", "report_failure", "rate limit exceeded")],
            success=False, failure_point="step_1", failure_class="mcp/rate-limit",
            domain="ci", severity="medium", quality_label="misleading",
            tags=("mcp", "abusive", "rate-limit"), expected_outcome="should_reject",
            rationale="Burst over the rate limit must be throttled (429)",
        ))
    _write(BASE / "mcp", recs)
    return len(recs)


# ── otel: span emission trajectories (20) ────────────────────────────────
def gen_otel() -> int:
    events = ["extract", "test", "promote", "retire"]
    recs: list[dict] = []
    n = 0
    for ev in events:
        for i in range(1, 6):
            n += 1
            recs.append(_traj(
                f"otel-{ev}-{i:03d}", f"OTEL span emission on {ev} event {i}",
                [_step(1, "otel", f"emit span rule.{ev}", None)],
                success=True, failure_point=None, failure_class=None,
                domain="ci", severity=None, quality_label="clear",
                tags=("otel", "span", ev), expected_outcome="should_silence",
                rationale=f"OTEL rule.{ev} span should be emitted with correct attributes",
                extra={"otel_span": f"rule.{ev}"},
            ))
    _write(BASE / "otel", recs)
    return len(recs)


def main() -> int:
    total = gen_adapters() + gen_lifecycle() + gen_packs() + gen_mcp() + gen_otel()
    print(f"\nv0.3.0 corpus: wrote {total} trajectories under {BASE}/")
    print(f"  adapters + lifecycle + packs + mcp + otel")
    print("next: python scripts/normalize-corpus.py --path field-test/corpus")
    print("      pytest tests/corpus/ -q")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
