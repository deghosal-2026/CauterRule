"""CLI smoke coverage for v0.3.1 M1 (#681).

Invokes read/display/diagnostic commands against a seeded store so the thin
CLI wrappers are exercised end to end.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.serialization.rule_yaml import dump_rule_to_file


def _seed(store: Path) -> None:
    store.mkdir(parents=True, exist_ok=True)
    rule = StandingRule(
        id="R-001",
        when=RuleWhen(trigger="git push rejected non-fast-forward"),
        do=RuleDo(directive="run git pull --rebase"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="t", extracted_by="m", extract_timestamp="t", extraction_pass=1
        ),
        status="active",
        promoted_at="2026-09-01T00:00:00Z",
        taxonomy="git/push",
        prevented_count=2,
        broke_count=0,
        neutral_count=1,
        tags=("git",),
        specificity=0.8,
    )
    dump_rule_to_file(rule, store / "R-001.yaml")


@pytest.fixture
def seeded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    _seed(tmp_path / "rules")
    monkeypatch.chdir(tmp_path)
    return tmp_path


READ_ONLY_INVOCATIONS: list[list[str]] = [
    ["list"],
    ["list", "--status", "active"],
    ["list", "--tag", "git"],
    ["list", "--sort", "spec"],
    ["show", "R-001"],
    ["show", "R-001", "--hits"],
    ["show", "R-001", "--outcomes"],
    ["show", "R-001", "--history"],
    ["audit", "R-001"],
    ["audit"],
    ["conflicts"],
    ["health"],
    ["health", "--by-taxonomy"],
    ["history"],
    ["history", "--limit", "5"],
    ["search", "git"],
    ["diff", "R-001"],
    ["explain", "R-001"],
    ["leaderboard"],
    ["leaderboard", "--top", "5"],
    ["metrics"],
    ["metrics", "--coverage"],
    ["metrics", "--by-domain"],
    ["metrics", "--by-class"],
    ["metrics", "--lowest-spec"],
    ["counterfactual"],
    ["counterfactual", "--days", "7"],
    ["journal"],
    ["review", "--json"],
    ["observe"],
    ["observe", "--json"],
    ["gaps"],
    ["frontier"],
    ["report"],
    ["validate"],
    ["inject", "git push fails"],
    ["taxonomy", "backfill", "--store", "rules", "--dry-run"],
    ["export", "--format", "markdown"],
    ["export", "--format", "json"],
    ["export", "--format", "agents"],
    ["promote", "R-001", "--show-cutoffs"],
    ["promote", "R-001"],
    ["test", "R-001", "--store", "rules"],
    ["test", "R-999", "--store", "rules"],
]


@pytest.mark.parametrize("args", READ_ONLY_INVOCATIONS)
def test_cli_smoke(seeded: Path, args: list[str]) -> None:
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0, f"{args} -> exit {result.exit_code}\n{result.output}"


def test_export_to_file(seeded: Path) -> None:
    out = seeded / "exported.md"
    result = CliRunner().invoke(main, ["export", "--format", "markdown", "-o", str(out)])
    assert result.exit_code == 0, result.output
    assert out.is_file()


def test_test_without_rule_errors(seeded: Path) -> None:
    result = CliRunner().invoke(main, ["test", "--store", "rules"])
    assert result.exit_code != 0
    assert "RULE" in result.output or "pack" in result.output


def test_retire_then_audit_apply(seeded: Path) -> None:
    result = CliRunner().invoke(main, ["retire", "R-001", "--reason", "stale"])
    assert result.exit_code == 0, result.output
    # auditing the retired store with --apply must not crash
    result = CliRunner().invoke(main, ["audit", "--apply", "--yes"])
    assert result.exit_code == 0, result.output


def test_list_unknown_sort_errors(seeded: Path) -> None:
    result = CliRunner().invoke(main, ["list", "--sort", "bogus"])
    assert result.exit_code != 0
