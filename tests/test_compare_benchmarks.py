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
