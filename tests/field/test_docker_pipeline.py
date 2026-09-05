"""Verify the full extract → test → promote → inject pipeline in the Docker container."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

DOCKER_TAG = "cauterule:field-test"
WORKSPACE = "/workspace"
FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    for subdir in ("trajectories", "candidates", "rules"):
        src = FIXTURES / subdir
        dst = tmp_path / subdir
        dst.mkdir(parents=True)
        for f in src.glob("*"):
            shutil.copy(f, dst)
    return tmp_path


def _run(cmd: list[str], workspace: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{workspace}:{WORKSPACE}",
            "-w", WORKSPACE,
            DOCKER_TAG,
            *cmd,
        ],
        capture_output=True,
        text=True,
    )


@pytest.mark.docker
def test_pipeline_init(workspace: Path) -> None:
    result = _run(["init", "--dir", WORKSPACE], workspace)
    assert result.returncode == 0, result.stderr
    assert (workspace / "cauterule.toml").is_file()
    assert (workspace / "rules").is_dir()
    assert (workspace / "trajectories").is_dir()


@pytest.mark.docker
def test_pipeline_extract_dry_run(workspace: Path) -> None:
    traj = f"{WORKSPACE}/trajectories/git_push_failure.jsonl"
    result = _run(["extract", traj, "--dry-run"], workspace)
    assert result.returncode == 0, result.stderr
    assert "dry-run candidate" in result.stdout
    assert "when:" in result.stdout.lower()
    assert "do:" in result.stdout.lower()


@pytest.mark.docker
def test_pipeline_test(workspace: Path) -> None:
    result = _run(["test", "R-001"], workspace)
    assert result.returncode == 0, result.stderr
    assert "Testing rule" in result.stdout
    assert "Failures prevented" in result.stdout
    assert "Successes broken" in result.stdout
    assert "Precision" in result.stdout
    assert "Recall" in result.stdout
    assert "Verdict" in result.stdout


@pytest.mark.docker
def test_pipeline_promote(workspace: Path) -> None:
    result = _run(["promote", "R-001"], workspace)
    assert result.returncode == 0, result.stderr
    assert "Cannot promote" in result.stdout


@pytest.mark.docker
def test_pipeline_list(workspace: Path) -> None:
    result = _run(["list"], workspace)
    assert result.returncode == 0, result.stderr
    assert "R-001" in result.stdout
    assert "R-002" in result.stdout


@pytest.mark.docker
def test_pipeline_inject(workspace: Path) -> None:
    result = _run(["inject", "git push fails with non-fast-forward"], workspace)
    assert result.returncode == 0, result.stderr
    assert "Found" in result.stdout
    assert "R-001" in result.stdout


@pytest.mark.docker
def test_pipeline_show(workspace: Path) -> None:
    result = _run(["show", "R-001"], workspace)
    assert result.returncode == 0, result.stderr
    assert "ID: R-001" in result.stdout
    assert "When:" in result.stdout
    assert "Do:" in result.stdout


@pytest.mark.docker
def test_pipeline_health(workspace: Path) -> None:
    result = _run(["health"], workspace)
    assert result.returncode == 0, result.stderr
    assert "Total rules" in result.stdout


@pytest.mark.docker
def test_pipeline_validate(workspace: Path) -> None:
    result = _run(["validate"], workspace)
    assert result.returncode == 0, result.stderr
    assert "Store" in result.stdout


@pytest.mark.docker
def test_pipeline_hash_check(workspace: Path) -> None:
    rule_path = workspace / "rules" / "R-001.yaml"
    data = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    commit: str = data.get("provenance", {}).get("promotion_commit", "")
    assert len(commit) == 40
    assert all(c in "0123456789abcdef" for c in commit)
