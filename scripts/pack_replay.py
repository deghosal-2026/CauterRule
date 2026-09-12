#!/usr/bin/env python3
"""Pack replay scoring for the v0.3.0 field test (#479/#481; plan §5.3/§7.2).

Replays each official pack's rules against its pack-replay fixtures and writes
``docs/field-test/v0.3.0/pack-replay.md`` plus a JSON summary.

Usage:
    python scripts/pack_replay.py
    python scripts/pack_replay.py --packs-dir rules/packs --threshold 0.70
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import yaml  # noqa: E402

from cauterule.measurement.pack_replay import pack_replay_score  # noqa: E402

OFFICIAL_PACKS = [
    "pack-git",
    "pack-docker",
    "pack-deploy",
    "pack-testing",
    "pack-python",
]


def _load_rules(pack_dir: Path) -> list[dict[str, object]]:
    rules: list[dict[str, object]] = []
    for path in sorted(pack_dir.glob("R-*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rules.append(
            {
                "id": data.get("id", path.stem),
                "trigger": (data.get("when") or {}).get("trigger", ""),
                "directive": (data.get("do") or {}).get("directive", ""),
                "confidence": data.get("confidence", 0.9),
            }
        )
    return rules


def _load_fixtures(pack_dir: Path, pack: str) -> list[dict[str, object]]:
    path = pack_dir / "tests" / f"replay_{pack}.jsonl"
    if not path.is_file():
        return []
    records: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def run(packs_dir: Path, threshold: float) -> list[dict[str, object]]:
    reports: list[dict[str, object]] = []
    for pack in OFFICIAL_PACKS:
        pack_dir = packs_dir / pack
        if not pack_dir.is_dir():
            continue
        rules = _load_rules(pack_dir)
        fixtures = _load_fixtures(pack_dir, pack)
        # Fixtures without an explicit outcome are pack-replay failures.
        for record in fixtures:
            record.setdefault("expected_outcome", "should_extract")
        report = pack_replay_score(pack, rules, fixtures, threshold=threshold)
        reports.append(
            {
                "pack": report.pack,
                "rules": report.rules,
                "trajectories": report.trajectories,
                "prevented": report.prevented,
                "broke": report.broke,
                "neutral": report.neutral,
                "score": round(report.score, 3),
                "meets_target": report.meets_target,
            }
        )
    return reports


def render_markdown(reports: list[dict[str, object]], threshold: float) -> str:
    lines = [
        "# Pack Replay Score — CauterRule v0.3.0",
        "",
        "**Issues:** #479/#481 · **Plan:** §5.3/§7.2 · "
        f"**Match threshold:** {threshold:.2f}",
        "",
        "| Pack | Rules | Replays | Prevented | Broke | Neutral | Score | Meets ≥0.5 |",
        "|------|-------|---------|-----------|-------|---------|-------|------------|",
    ]
    for r in reports:
        lines.append(
            f"| {r['pack']} | {r['rules']} | {r['trajectories']} | {r['prevented']} | "
            f"{r['broke']} | {r['neutral']} | {r['score']:.2f} | "
            f"{'✅' if r['meets_target'] else '❌'} |"
        )
    replayable = [r for r in reports if r["trajectories"] > 0]
    passed = sum(1 for r in replayable if r["meets_target"])
    no_fixtures = [r["pack"] for r in reports if r["trajectories"] == 0]
    lines += [
        "",
        f"**Summary:** {passed}/{len(replayable)} packs with replay fixtures meet the "
        "≥1-prevented and score ≥0.5 gate.",
    ]
    if no_fixtures:
        lines.append(
            f"Packs without replay fixtures (create-only, not scored): "
            f"{', '.join(no_fixtures)}."
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--packs-dir", default=str(REPO / "rules" / "packs"), help="Official packs dir"
    )
    parser.add_argument("--threshold", type=float, default=0.70, help="Match threshold")
    parser.add_argument(
        "--output",
        default=str(REPO / "docs" / "field-test" / "v0.3.0" / "pack-replay.md"),
    )
    parser.add_argument("--json-output", default=None)
    args = parser.parse_args(argv)

    reports = run(Path(args.packs_dir), args.threshold)
    md = render_markdown(reports, args.threshold)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"wrote {out}")
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(reports, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
