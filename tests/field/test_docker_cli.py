"""Verify all CLI commands produce real effects via subprocess (not inside Docker)."""

from __future__ import annotations

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
def test_cli_init(tmp_path: Path) -> None:
    result = _run(["init", "--dir", str(tmp_path)], cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "Scaffolded" in result.stdout
    assert (tmp_path / "cauterule.toml").is_file()
    assert (tmp_path / "rules").is_dir()
    assert (tmp_path / "trajectories").is_dir()


@pytest.mark.docker
def test_cli_extract_dry_run(tmp_path: Path) -> None:
    traj_path = FIXTURES / "trajectories" / "git_push_failure.jsonl"
    result = _run(["extract", str(traj_path), "--dry-run"], cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "dry-run candidate" in result.stdout


@pytest.mark.docker
def test_cli_test(full_workspace: Path) -> None:
    result = _run(["test", "R-001"], cwd=full_workspace)
    assert result.returncode == 0, result.stderr
    assert "Testing rule" in result.stdout
    assert "Failures prevented" in result.stdout
    assert "Successes broken" in result.stdout
    assert "Precision" in result.stdout
    assert "Recall" in result.stdout


@pytest.mark.docker
def test_cli_promote(rules_workspace: Path) -> None:
    result = _run(["promote", "R-001"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Cannot promote" in result.stdout


@pytest.mark.docker
def test_cli_list(rules_workspace: Path) -> None:
    result = _run(["list"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "R-001" in result.stdout
    assert "R-002" in result.stdout
    assert "R-003" in result.stdout


@pytest.mark.docker
def test_cli_show(rules_workspace: Path) -> None:
    result = _run(["show", "R-001"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "ID: R-001" in result.stdout
    assert "When:" in result.stdout
    assert "Do:" in result.stdout
    assert "Confidence:" in result.stdout
    assert "Status:" in result.stdout
    assert "Hit count:" in result.stdout
    assert "Tags:" in result.stdout


@pytest.mark.docker
def test_cli_inject(rules_workspace: Path) -> None:
    result = _run(["inject", "git push fails with non-fast-forward error"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Found" in result.stdout
    assert "R-001" in result.stdout


@pytest.mark.docker
def test_cli_retire(rules_workspace: Path) -> None:
    result = _run(["retire", "R-001", "--reason", "test"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "retired" in result.stdout


@pytest.mark.docker
def test_cli_history(rules_workspace: Path) -> None:
    result = _run(["history"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Recent rule activity" in result.stdout


@pytest.mark.docker
def test_cli_conflicts(rules_workspace: Path) -> None:
    result = _run(["conflicts"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "No conflicts detected" in result.stdout or "CONTRADICTION" in result.stdout


@pytest.mark.docker
def test_cli_validate(rules_workspace: Path) -> None:
    result = _run(["validate"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Store" in result.stdout


@pytest.mark.docker
def test_cli_health(rules_workspace: Path) -> None:
    result = _run(["health"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Total rules" in result.stdout


@pytest.mark.docker
def test_cli_search(rules_workspace: Path) -> None:
    result = _run(["search", "git push fails with non-fast-forward"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Found" in result.stdout
    assert "R-001" in result.stdout


@pytest.mark.docker
def test_cli_explain(rules_workspace: Path) -> None:
    result = _run(["explain", "R-001"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Rule **R-001**" in result.stdout
    assert "Trigger:" in result.stdout
    assert "Action:" in result.stdout


@pytest.mark.docker
def test_cli_config() -> None:
    result = _run(["config"], cwd=Path("/tmp"))
    assert result.returncode == 0, result.stderr
    assert "llm" in result.stdout or "provider" in result.stdout


@pytest.mark.docker
def test_cli_metrics(rules_workspace: Path) -> None:
    result = _run(["metrics"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Total rules" in result.stdout


@pytest.mark.docker
def test_cli_report(rules_workspace: Path) -> None:
    result = _run(["report"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "CauterRule Report" in result.stdout


@pytest.mark.docker
def test_cli_pack_list(rules_workspace: Path) -> None:
    store = str(rules_workspace / "rules")
    created = _run(
        ["pack", "create", "p1", "--store", store, "--from-tag", "git"], cwd=rules_workspace
    )
    assert created.returncode == 0, created.stderr
    installed = _run(["pack", "install", "./p1", "--store", store], cwd=rules_workspace)
    assert installed.returncode == 0, installed.stderr
    result = _run(["pack", "list", "--store", store], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "p1" in result.stdout


@pytest.mark.docker
def test_cli_pack_info(rules_workspace: Path) -> None:
    store = str(rules_workspace / "rules")
    created = _run(
        ["pack", "create", "p1", "--store", store, "--from-tag", "git"], cwd=rules_workspace
    )
    assert created.returncode == 0, created.stderr
    installed = _run(["pack", "install", "./p1", "--store", store], cwd=rules_workspace)
    assert installed.returncode == 0, installed.stderr
    result = _run(["pack", "info", "p1", "--store", store], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Pack:" in result.stdout
    assert "Rules:" in result.stdout


@pytest.mark.docker
def test_cli_diff(rules_workspace: Path) -> None:
    result = _run(["diff", "R-001"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "R-001" in result.stdout or "current version" in result.stdout


@pytest.mark.docker
def test_cli_audit(rules_workspace: Path) -> None:
    result = _run(["audit", "R-001"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "Rule: R-001" in result.stdout
    assert "Source trajectory" in result.stdout
    assert "Extracted by" in result.stdout


@pytest.mark.docker
def test_cli_story(rules_workspace: Path) -> None:
    result = _run(["story"], cwd=rules_workspace)
    assert result.returncode == 0, result.stderr
    assert "CauterRule Learning Journey" in result.stdout


@pytest.mark.docker
def test_cli_counterfactual(full_workspace: Path) -> None:
    result = _run(["counterfactual"], cwd=full_workspace)
    assert result.returncode == 0, result.stderr
    assert "active rules" in result.stdout or "counterfactual" in result.stdout.lower()
