"""Tests for scripts/compare_benchmarks.py (#605)."""

from __future__ import annotations

import json
from pathlib import Path


def _bench(path: Path, means: dict[str, float]) -> None:
    payload = {
        "benchmarks": [
            {"name": name, "stats": {"mean": mean}} for name, mean in means.items()
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


class TestCompareBenchmarks:
    def test_no_regression(self, tmp_path: Path) -> None:
        import sys

        sys.path.insert(0, "scripts")
        from compare_benchmarks import main

        old = tmp_path / "old.json"
        new = tmp_path / "new.json"
        _bench(old, {"a": 1.0})
        _bench(new, {"a": 1.05})
        assert main(["compare", str(old), str(new)]) == 0

    def test_regression_fails(self, tmp_path: Path) -> None:
        import sys

        sys.path.insert(0, "scripts")
        from compare_benchmarks import main

        old = tmp_path / "old.json"
        new = tmp_path / "new.json"
        _bench(old, {"a": 1.0})
        _bench(new, {"a": 1.5})
        assert main(["compare", str(old), str(new)]) == 1

    def test_usage_error(self) -> None:
        import sys

        sys.path.insert(0, "scripts")
        from compare_benchmarks import main

        assert main(["compare"]) == 2

    def test_write_baseline_emits_minimal_json(self, tmp_path: Path) -> None:
        import sys

        sys.path.insert(0, "scripts")
        from compare_benchmarks import write_baseline

        full = tmp_path / "full.json"
        full.write_text(
            json.dumps(
                {
                    "machine_info": {"node": "x" * 5000},
                    "benchmarks": [
                        {"name": "a", "stats": {"mean": 1.25, "stddev": 9.9}, "extra": "y" * 5000}
                    ],
                }
            ),
            encoding="utf-8",
        )
        out = tmp_path / "baseline.json"
        write_baseline(full, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data == {"benchmarks": [{"name": "a", "stats": {"mean": 1.25}}]}
        assert out.stat().st_size < 200

    def test_write_baseline_cli(self, tmp_path: Path) -> None:
        import sys

        sys.path.insert(0, "scripts")
        from compare_benchmarks import main

        full = tmp_path / "full.json"
        full.write_text(
            json.dumps({"benchmarks": [{"name": "a", "stats": {"mean": 2.0}}]}),
            encoding="utf-8",
        )
        out = tmp_path / "baseline.json"
        assert main(["cb", "--write-baseline", str(full), str(out)]) == 0
        assert json.loads(out.read_text(encoding="utf-8"))["benchmarks"][0]["stats"]["mean"] == 2.0
