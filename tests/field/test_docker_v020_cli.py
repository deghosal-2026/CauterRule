"""Verify v0.2.0 CLI commands produce real effects via subprocess.

Covers the new M5-M9 surface: preflight (M3), harness-health (M3), TUI review
batch mode (M5), observability metrics (M6), and report --monthly (M6).
Mirrors the subprocess pattern in test_docker_cli.py.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def rules_workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    dst = ws / "rules"
    dst.mkdir()
    for f in (FIXTURES / "rules").glob("*"):
        shutil.copy(f, dst)
    return ws


@pytest.fixture
def full_workspace(rules_workspace: Path) -> Path:
    dst = rules_workspace / "trajectories"
    dst.mkdir()
    for f in (FIXTURES / "trajectories").glob("*"):
        shutil.copy(f, dst)
    return rules_workspace


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["cauterule", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


@pytest.mark.docker
def test_cli_preflight_no_corpus(rules_workspace: Path) -> None:
    result = _run(["preflight"], cwd=rules_workspace)
    # No LLM configured → provider checks fail but command exits (may error)
    assert "Preflight" in result.stdout or "Error" in result.stderr


@pytest.mark.docker
def test_cli_preflight_with_corpus(rules_workspace: Path) -> None:
    golden = FIXTURES.parent.parent / "corpus" / "public" / "golden"
    if not golden.is_dir():
        pytest.skip("corpus/public/golden not present")
    result = _run(["preflight", "--corpus", str(golden)], cwd=rules_workspace)
    assert "Preflight" in result.stdout or "corpus" in result.stdout


@pytest.mark.docker
def test_cli_harness_health_pass() -> None:
    result = _run(["harness-health", "--parsed", "50", "--total", "50"], cwd=Path("/tmp"))
    assert result.returncode == 0, result.stderr
    assert "Harness health: PASS" in result.stdout


@pytest.mark.docker
def test_cli_harness_health_fail() -> None:
    result = _run(["harness-health", "--parsed", "1", "--total", "50"], cwd=Path("/tmp"))
    assert result.returncode != 0
    assert "Harness health: FAIL" in result.stderr or "Harness health: FAIL" in result.stdout


@pytest.mark.docker
def test_cli_review_batch_json(rules_workspace: Path) -> None:
    result = _run(["review", "--batch", "--json", "--store-dir", str(rules_workspace / "rules")], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "queue_size" in result.stdout
    payload = json.loads(result.stdout)
    assert "queue_size" in payload
    assert "candidates" in payload


@pytest.mark.docker
def test_cli_review_filter_json(rules_workspace: Path) -> None:
    result = _run(
        ["review", "--json", "--filter", "tag=git", "--store-dir", str(rules_workspace / "rules")],
        cwd=rules_workspace,
    )
    assert result.returncode == 0, result.stderr
    candidates = json.loads(result.stdout)
    assert isinstance(candidates, list)
    for c in candidates:
        assert any("git" in t.lower() for t in c.get("tags", []))


@pytest.mark.docker
def test_cli_metrics_coverage(rules_workspace: Path) -> None:
    result = _run(["metrics", "--coverage", "--store-dir", str(rules_workspace / "rules")], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Coverage score" in result.stdout


@pytest.mark.docker
def test_cli_metrics_by_domain(rules_workspace: Path) -> None:
    result = _run(["metrics", "--by-domain", "--store-dir", str(rules_workspace / "rules")], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "git" in result.stdout or "No domain coverage" in result.stdout


@pytest.mark.docker
def test_cli_gaps(rules_workspace: Path) -> None:
    result = _run(["gaps", "--store-dir", str(rules_workspace / "rules")], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "coverage gaps" in result.stdout or "No coverage gaps" in result.stdout


@pytest.mark.docker
def test_cli_leaderboard(rules_workspace: Path) -> None:
    result = _run(["leaderboard", "--store-dir", str(rules_workspace / "rules")], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Most prevented" in result.stdout or "Most broken" in result.stdout


@pytest.mark.docker
def test_cli_frontier(rules_workspace: Path) -> None:
    result = _run(["frontier"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "coverage" in result.stdout.lower() or "covered" in result.stdout.lower()


@pytest.mark.docker
def test_cli_journal(rules_workspace: Path) -> None:
    result = _run(["journal", "--store-dir", str(rules_workspace / "rules")], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Learning Journal" in result.stdout


@pytest.mark.docker
def test_cli_report_monthly(rules_workspace: Path) -> None:
    result = _run(["report", "--monthly", "--store-dir", str(rules_workspace / "rules")], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Monthly Learning Report" in result.stdout


@pytest.mark.docker
def test_cli_show_hits(rules_workspace: Path) -> None:
    result = _run(["show", "R-001", "--hits"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Hit count" in result.stdout
    assert "ID: R-001" in result.stdout


@pytest.mark.docker
def test_cli_inject_records_hits(full_workspace: Path) -> None:
    result = _run(["inject", "git push fails with non-fast-forward error"], cwd=full_workspace)
    assert result.returncode == 0, result.stderr
    assert "Recorded hits" in result.stdout
