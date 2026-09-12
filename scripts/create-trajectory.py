#!/usr/bin/env python3
"""create-trajectory.py — Interactive tool to create trajectory JSONL files.

Usage:
    python scripts/create-trajectory.py                    # Interactive mode
    python scripts/create-trajectory.py --batch <file>     # Batch from YAML/JSON
    python scripts/create-trajectory.py --list             # List existing trajectories
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

VALID_DOMAINS = {"git", "python", "docker", "test", "ci", "deploy", "shell", "env", "workflow"}
VALID_LABELS = {"clear", "ambiguous", "multi-causal", "misleading", "operator-induced"}
VALID_SEVERITIES = {"low", "medium", "high"}
VALID_SOURCES = {"opencode", "ci", "sibling-repos", "corrections", "manual"}
CORPUS_DIR = Path("field-test/corpus")


def _next_id(source: str, domain: str) -> str:
    """Generate the next sequential ID for a source/domain combo."""
    raw_dir = CORPUS_DIR / "raw" / source
    raw_dir.mkdir(parents=True, exist_ok=True)
    existing = list(raw_dir.glob("*.jsonl"))
    prefix = source[:3]
    seq = len(existing) + 1
    return f"{prefix}-{seq:03d}-{domain}"


def create_trajectory_interactive() -> dict:
    """Interactive trajectory creation wizard."""
    print("\n=== Trajectory Creator ===\n")

    source = _prompt_choice("Source", sorted(VALID_SOURCES))
    domain = _prompt_choice("Domain", sorted(VALID_DOMAINS))
    traj_id = input(f"Trajectory ID [{_next_id(source, domain)}]: ").strip()
    if not traj_id:
        traj_id = _next_id(source, domain)

    task = input("Task description: ").strip()
    while not task:
        task = input("  Task description (required): ").strip()

    failure_class = input(f"Failure class (e.g. {domain}/push): ").strip()
    if not failure_class:
        failure_class = f"{domain}/failure"

    quality_label = _prompt_choice("Quality label", sorted(VALID_LABELS))
    severity = _prompt_choice("Severity", sorted(VALID_SEVERITIES))
    success_str = input("Success? (y/N): ").strip().lower()
    success = success_str == "y"

    failure_point = ""
    if not success:
        failure_point = input("Failure point (error message): ").strip()

    tags_str = input("Tags (comma-separated, e.g. git,push): ").strip()
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]

    human_correction = input("Human correction (or blank): ").strip() or None
    expected_rule = input("Expected rule (or blank): ").strip() or ""
    notes = input("Notes (or blank): ").strip() or ""

    # Steps
    steps = []
    step_num = 1
    print("\n--- Enter steps (blank tool name to stop) ---")
    while True:
        tool = input(f"  Step {step_num} tool: ").strip()
        if not tool:
            break
        inp = input(f"  Step {step_num} input: ").strip() or None
        out = input(f"  Step {step_num} output: ").strip() or None
        err = input(f"  Step {step_num} error: ").strip() or None
        steps.append(
            {
                "step_number": step_num,
                "tool": tool,
                "input": inp,
                "output": out,
                "error": err,
                "state": None,
            }
        )
        step_num += 1

    if not steps:
        # Default single step
        steps.append(
            {
                "step_number": 1,
                "tool": domain,
                "input": task,
                "output": None,
                "error": failure_point or None,
                "state": None,
            }
        )

    trajectory = {
        "trajectory_id": traj_id,
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task": task,
        "domain": domain,
        "failure_class": failure_class,
        "quality_label": quality_label,
        "severity": severity,
        "success": success,
        "failure_point": failure_point or None,
        "steps": steps,
        "tags": tags or [domain],
        "expected_rule": expected_rule,
        "human_correction": human_correction,
        "source": source,
        "source_repo": "CauterRule",
        "redacted": False,
        "notes": notes,
    }

    # Save
    outpath = CORPUS_DIR / "raw" / source / f"{traj_id}.jsonl"
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with Path(outpath).open("w") as f:
        f.write(json.dumps(trajectory) + "\n")
    print(f"\n✅ Saved: {outpath}")
    return trajectory


def list_trajectories() -> None:
    """List all existing trajectories in the corpus."""
    print("\n=== Corpus Trajectories ===\n")
    total = 0
    for source in VALID_SOURCES:
        src_dir = CORPUS_DIR / "raw" / source
        if not src_dir.exists():
            continue
        files = list(src_dir.glob("*.jsonl"))
        if not files:
            continue
        print(f"\n{source}/ ({len(files)}):")
        for f in sorted(files):
            try:
                with Path(f).open() as fh:
                    traj = json.loads(fh.read().strip())
                success = "✅" if traj.get("success") else "❌"
                domain = traj.get("domain", "?")
                label = traj.get("quality_label", "?")
                task = traj.get("task", "?")[:60]
                print(f"  {success} {f.stem} [{domain}/{label}] {task}")
            except Exception:
                print(f"  ⚠️  {f.name} (parse error)")
            total += 1

    # Also count curated
    curated_dir = CORPUS_DIR / "curated"
    if curated_dir.exists():
        curated_count = sum(1 for _ in curated_dir.rglob("*.jsonl"))
        print(f"\nCurated: {curated_count} trajectories")
    golden_dir = CORPUS_DIR / "golden"
    if golden_dir.exists():
        golden_count = sum(1 for _ in golden_dir.rglob("*.jsonl"))
        print(f"Golden: {golden_count} trajectories")
    print(f"\nTotal raw: {total}")


def batch_import(filepath: str) -> int:
    """Import trajectories from a JSON file (list of trajectory dicts)."""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        return 1

    with Path(path).open() as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    count = 0
    for item in data:
        traj_id = item.get("trajectory_id", f"batch-{count:03d}")
        source = item.get("source", "manual")
        outpath = CORPUS_DIR / "raw" / source / f"{traj_id}.jsonl"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        with Path(outpath).open("w") as f:
            f.write(json.dumps(item) + "\n")
        count += 1

    print(f"✅ Imported {count} trajectories from {filepath}")
    return count


def _prompt_choice(label: str, options: list[str]) -> str:
    """Prompt user to choose from a list."""
    print(f"\n{label}:")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            choice = input(f"  Select [{', '.join(options[:3])}...] (1-{len(options)}): ").strip()
            if choice in options:
                return choice
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except (ValueError, IndexError):
            pass
        print(f"  Please enter 1-{len(options)} or one of: {', '.join(options)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create trajectory JSONL files")
    parser.add_argument("--batch", type=str, help="Batch import from JSON file")
    parser.add_argument("--list", action="store_true", help="List existing trajectories")
    args = parser.parse_args()

    if args.list:
        list_trajectories()
        return 0
    if args.batch:
        batch_import(args.batch)
        return 0

    create_trajectory_interactive()
    return 0


if __name__ == "__main__":
    sys.exit(main())
