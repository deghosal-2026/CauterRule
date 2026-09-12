#!/usr/bin/env python3
"""Compare benchmark runs against a baseline; fail on >15% regression (#605).

Usage:
    python scripts/compare_benchmarks.py <baseline.json> <.benchmarks-dir-or-current.json>

Reads pytest-benchmark JSON files, prints per-benchmark deltas, exits non-zero
when any benchmark regressed beyond the threshold in benchmarks/thresholds.toml
(default 15%; 5-15% prints a warning).
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

DEFAULT_FAIL_PCT = 15.0
DEFAULT_WARN_PCT = 5.0


def _load(path: Path) -> dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, float] = {}
    for bench in data.get("benchmarks", []):
        stats = bench.get("stats", {})
        mean = stats.get("mean")
        if mean is not None:
            out[bench["name"]] = float(mean)
    return out


def _thresholds() -> tuple[float, float]:
    config = Path("benchmarks/thresholds.toml")
    if config.is_file():
        with config.open("rb") as fh:
            data = tomllib.load(fh)
        section = data.get("regression", {})
        return (
            float(section.get("fail_pct", DEFAULT_FAIL_PCT)),
            float(section.get("warn_pct", DEFAULT_WARN_PCT)),
        )
    return DEFAULT_FAIL_PCT, DEFAULT_WARN_PCT


def write_baseline(src: str | Path, dst: str | Path) -> None:
    """Write a minimal baseline (name -> mean) derived from a full pytest-benchmark JSON.

    Keeps the committed ``benchmarks/baseline.json`` tiny instead of checking in
    the multi-MB raw artifact (#679).
    """
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    benchmarks: list[dict[str, dict[str, float]]] = []
    for bench in data.get("benchmarks", []):
        stats = bench.get("stats", {})
        mean = stats.get("mean")
        if mean is not None:
            benchmarks.append({"name": bench["name"], "stats": {"mean": float(mean)}})
    Path(dst).write_text(
        json.dumps({"benchmarks": benchmarks}, separators=(",", ":")), encoding="utf-8"
    )


def main(argv: list[str]) -> int:
    """Compare baseline vs current benchmark JSON. Returns exit status."""
    if len(argv) == 4 and argv[1] == "--write-baseline":
        write_baseline(argv[2], argv[3])
        print(f"wrote baseline {argv[3]}")
        return 0
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[0])
        print("usage: compare_benchmarks.py <baseline.json> <current.json>")
        return 2
    baseline = _load(Path(argv[1]))
    current_path = Path(argv[2])
    if current_path.is_dir():
        candidates = sorted(current_path.glob("*.json"))
        if not candidates:
            print(f"no benchmark json in {current_path}")
            return 2
        current_path = candidates[-1]
    current = _load(current_path)
    fail_pct, warn_pct = _thresholds()
    failed: list[str] = []
    for name, old in sorted(baseline.items()):
        new = current.get(name)
        if new is None:
            print(f"{name}: missing in current run (skipped)")
            continue
        delta = (new - old) / old * 100 if old else 0.0
        flag = ""
        if delta > fail_pct:
            flag = "  FAIL"
            failed.append(name)
        elif delta > warn_pct:
            flag = "  WARN"
        print(f"{name}: {old:.6f}s -> {new:.6f}s ({delta:+.1f}%){flag}")
    if failed:
        print(f"regressed: {', '.join(failed)}")
        return 1
    print("no regressions beyond threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
