"""Tests for the benchmark leaderboard module."""

from __future__ import annotations

from cauterule.benchmark.leaderboard import Leaderboard


class TestLeaderboard:
    def test_empty_leaderboard(self) -> None:
        lb = Leaderboard("Test Board")
        rendered = lb.render()
        assert "# Test Board" in rendered
        assert "No entries" in rendered

    def test_single_entry(self) -> None:
        lb = Leaderboard("Test")
        lb.add_entry({"name": "m1", "score": 0.95})
        rendered = lb.render()
        assert "m1" in rendered
        assert "0.95" in rendered

    def test_multiple_entries(self) -> None:
        lb = Leaderboard("Test")
        lb.add_entries(
            [
                {"name": "m1", "score": 0.9},
                {"name": "m2", "score": 0.95},
                {"name": "m3", "score": 0.85},
            ]
        )
        lb.sort()
        rendered = lb.render()
        lines = [ln for ln in rendered.splitlines() if ln.startswith("|")]
        # header + separator + 3 data rows
        assert len(lines) == 5
        assert lines[2].startswith("| m2")  # highest first
        assert lines[4].startswith("| m3")  # lowest last

    def test_sort_by_custom_key(self) -> None:
        lb = Leaderboard("Test")
        lb.add_entries(
            [
                {"name": "a", "score": 10, "rank": 3},
                {"name": "b", "score": 20, "rank": 1},
                {"name": "c", "score": 15, "rank": 2},
            ]
        )
        lb.sort(key="rank", reverse=False)
        rendered = lb.render()
        lines = [ln for ln in rendered.splitlines() if ln.startswith("|")]
        assert "b" in lines[2]
        assert "c" in lines[3]
        assert "a" in lines[4]

    def test_extra_fields_appear_as_columns(self) -> None:
        lb = Leaderboard("Test")
        lb.add_entry({"name": "m1", "score": 0.9, "trajectory": "t1.jsonl"})
        rendered = lb.render()
        assert "trajectory" in rendered
        assert "t1.jsonl" in rendered

    def test_sort_empty_no_error(self) -> None:
        lb = Leaderboard("Test")
        lb.sort()  # should not raise

    def test_render_empty(self) -> None:
        lb = Leaderboard("Empty Board")
        assert "*No entries.*" in lb.render()

    def test_add_entry_then_add_entries(self) -> None:
        lb = Leaderboard("Mixed")
        lb.add_entry({"name": "first", "score": 1.0})
        lb.add_entries([{"name": "second", "score": 0.9}])
        lb.sort()
        assert "first" in lb.render()
