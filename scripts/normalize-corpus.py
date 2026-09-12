"""Normalize all corpus JSONL files — fill missing metadata fields to match format spec.

Usage:
    python scripts/normalize-corpus.py                          # Walk corpus/public/
    python scripts/normalize-corpus.py --path corpus/public/     # Explicit path
    python scripts/normalize-corpus.py --dry-run                 # Report without writing

Idempotent — safe to rerun on already-normalized files.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Domains where specific failure classes are known
_DOMAIN_FAILURE_MAP: dict[str, str] = {
    "coding": "coding/test-failure",
    "devops": "devops/deploy-failure",
    "research": "research/web-scrape-failure",
    "support": "support/triage-issue",
    "browser_automation": "browser/navigation-issue",
}


def infer_expected_outcome_confidence(
    source: str | None, tags: list[str], failure_class: str | None
) -> str:
    """Infer expected_outcome_confidence (high/medium/low) from trajectory fields.

    - high: known expected rule (golden, synthetic hand-crafted, manual)
    - medium: inferred from failure class or curated source
    - low: best guess for noisy or raw corpora
    """
    source_lower = (source or "").lower()
    tag_lower = [t.lower() for t in (tags or [])]

    # High confidence
    if source_lower in ("manual", "synthetic", "golden"):
        return "high"
    if "golden" in tag_lower:
        return "high"

    # Low confidence
    if source_lower in ("ci", "raw", "sibling-repos"):
        return "low"

    # Medium confidence — inferred from failure class or curated
    if failure_class:
        return "medium"
    if source_lower in ("curated",):
        return "medium"

    return "low"


def infer_expected_outcome(
    success: bool,
    task: str,
    failure_class: str | None,
    tags: tuple[str, ...],
    domain: str | None,
) -> tuple[str, str]:
    """Infer expected_outcome and rationale from trajectory fields."""

    # Staleness — historical failures that no longer matter
    if any("deprecated" in t.lower() or "stale" in t.lower() for t in tags):
        return ("should_reject", "Outdated agent config or environment — rule would be stale")

    # Counterexample — success that looks like failure
    if "counterexample" in tags:
        return ("should_reject", "Looks like a failure pattern but succeeds — rule would overfire")

    # Near miss — ambiguous, retry succeeded
    if "nearmiss" in tags:
        return ("should_reject", "Ambiguous — retry after first failure succeeded; no rule needed")

    # Prompt injection / misleading / unsafe / poisoning
    if "adversarial" in tags or "injection" in tags:
        return ("should_reject", "Adversarial trajectory — should not produce a rule")

    # Clear success — no failure signal
    if success and not failure_class:
        return ("should_silence", "Clean success — no failure pattern to extract")

    # Failure with known failure class
    if failure_class:
        return ("should_extract", f"Clear failure pattern: {failure_class}")

    # Success with failure_class (may be misleading)
    if success and failure_class:
        return (
            "should_extract",
            f"Has failure_class '{failure_class}' despite success — likely multi-step recovery",
        )

    # Generic failure — infer from domain
    if not success:
        if domain and domain in _DOMAIN_FAILURE_MAP:
            return ("should_extract", f"In-domain failure pattern: {_DOMAIN_FAILURE_MAP[domain]}")
        return ("should_extract", "Generic failure trajectory — may contain learnable pattern")

    return ("should_silence", "No failure signal detected")


def normalize_trajectory_metadata(record: dict) -> dict:
    """Fill missing metadata fields in a single trajectory dict (in-place)."""
    original = record.copy()

    # Key alias: some files write as trajectory_id
    if "trajectory_id" in record and "id" not in record:
        record["id"] = record["trajectory_id"]

    # Required fields — fail if missing
    for field in ("id", "timestamp", "task", "steps", "success"):
        if field not in record:
            raise ValueError(f"Missing required field {field!r} in {record.get('id', 'unknown')}")

    # Default quality_label
    if "quality_label" not in record or not record["quality_label"]:
        record["quality_label"] = "unlabeled"

    # Default domain
    if "domain" not in record or not record["domain"]:
        if not record.get("steps"):
            record["domain"] = "unknown"
        else:
            record["domain"] = "unknown"

    # Default tags
    if "tags" not in record:
        record["tags"] = []
    elif isinstance(record["tags"], (list, tuple)):
        record["tags"] = list(record["tags"])
    else:
        record["tags"] = []

    # Ensure tags is a list of strings
    record["tags"] = [str(t) for t in record["tags"]]

    # Default failure_point
    if "failure_point" not in record:
        record["failure_point"] = None

    # Default failure_class
    if "failure_class" not in record:
        record["failure_class"] = None

    # Default severity
    if "severity" not in record:
        record["severity"] = None

    # Default environment
    if "environment" not in record:
        record["environment"] = {"os": "unknown", "ci": False}
    elif isinstance(record["environment"], dict):
        record["environment"].setdefault("os", "unknown")
        record["environment"].setdefault("ci", False)

    # Default agent_config
    if "agent_config" not in record:
        record["agent_config"] = {"model": "unknown", "tools": []}

    # Default redacted
    if "redacted" not in record:
        record["redacted"] = False

    # Fill expected_outcome and rationale
    if not record.get("expected_outcome"):
        tags = tuple(record.get("tags", []))
        record["expected_outcome"], record["expected_outcome_rationale"] = infer_expected_outcome(
            success=record.get("success", True),
            task=record.get("task", ""),
            failure_class=record.get("failure_class"),
            tags=tags,
            domain=record.get("domain"),
        )
    if not record.get("expected_outcome_rationale"):
        record["expected_outcome_rationale"] = "Inferred by normalization"

    # Fill expected_outcome_confidence
    if not record.get("expected_outcome_confidence"):
        record["expected_outcome_confidence"] = infer_expected_outcome_confidence(
            source=record.get("source"),
            tags=record.get("tags", []),
            failure_class=record.get("failure_class"),
        )

    # Keep trajectory_id for backward compat
    if "trajectory_id" in original:
        record["trajectory_id"] = original["trajectory_id"]

    return record


def normalize_file(path: Path, dry_run: bool = False) -> dict:
    """Normalize all trajectories in a JSONL file. Returns change stats."""
    stats: dict = {"read": 0, "modified": 0, "wrote": 0, "errors": 0}
    lines = path.read_text(encoding="utf-8").strip().split("\n")
    records: list[str] = []
    for raw in lines:
        if not raw.strip():
            continue
        stats["read"] += 1
        try:
            record = json.loads(raw)
            before = json.dumps(record, sort_keys=True)
            normalize_trajectory_metadata(record)
            after = json.dumps(record, sort_keys=True)
            if before != after:
                stats["modified"] += 1
            records.append(json.dumps(record))
        except Exception as e:
            print(f"  ERROR in {path}: {e}", file=sys.stderr)
            stats["errors"] += 1
            records.append(raw)  # keep original

    if not dry_run:
        path.write_text("\n".join(records) + "\n", encoding="utf-8")
        stats["wrote"] = stats["read"] - stats["errors"]

    return stats


def walk_corpus(root: Path, dry_run: bool = False) -> dict:
    """Walk all JSONL files under root and normalize them."""
    totals: dict = {"files": 0, "read": 0, "modified": 0, "wrote": 0, "errors": 0}
    for path in sorted(root.rglob("*.jsonl")):
        stats = normalize_file(path, dry_run=dry_run)
        for k in totals:
            totals[k] += stats.get(k, 0)
        if stats["modified"] or stats["errors"] or dry_run:
            op = "DRY-RUN" if dry_run else "OK"
            print(
                f"  [{op}] {path.relative_to(root.parent)}: {stats['read']} trajs, {stats['modified']} modified, {stats['errors']} errors"
            )
    return totals


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize corpus JSONL metadata")
    parser.add_argument("--path", default="corpus/public", help="Corpus root directory")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    root = Path(args.path)
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    totals = walk_corpus(root, dry_run=args.dry_run)
    action = "Would modify" if args.dry_run else "Modified"
    print(
        f"\n{totals['files']} files, {totals['read']} trajectories, {action} {totals['modified']} ({totals['errors']} errors)"
    )


if __name__ == "__main__":
    main()
