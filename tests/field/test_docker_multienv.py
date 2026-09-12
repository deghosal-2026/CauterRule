"""Verify CauterRule builds and tests pass on all supported Python versions."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_tests_cmd(tag: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "sh",
            "-v",
            f"{REPO_ROOT}:/repo",
            tag,
            "-c",
            "pip install -q pytest && cd /repo && python -m pytest "
            "tests/models tests/store tests/serialization tests/injection "
            "tests/redaction tests/export tests/cli tests/capture tests/promotion "
            "tests/conflict tests/loop tests/packs "
            "-m 'not slow and not docker' --tb=short -q -p no:cacheprovider",
        ],
        capture_output=True,
        text=True,
    )


@pytest.mark.docker
@pytest.mark.slow
def test_build_py311() -> None:
    result = subprocess.run(
        ["docker", "build", "--build-arg", "PYTHON_VERSION=3.11", "-t", "cauterule:py311", "."],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.docker
@pytest.mark.slow
def test_py311_tests_pass() -> None:
    result = _run_tests_cmd("cauterule:py311")
    assert result.returncode == 0, result.stderr


@pytest.mark.docker
@pytest.mark.slow
def test_build_py312() -> None:
    result = subprocess.run(
        ["docker", "build", "--build-arg", "PYTHON_VERSION=3.12", "-t", "cauterule:py312", "."],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.docker
@pytest.mark.slow
def test_py312_tests_pass() -> None:
    result = _run_tests_cmd("cauterule:py312")
    assert result.returncode == 0, result.stderr


@pytest.mark.docker
@pytest.mark.slow
def test_build_py313() -> None:
    result = subprocess.run(
        ["docker", "build", "--build-arg", "PYTHON_VERSION=3.13", "-t", "cauterule:py313", "."],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.docker
@pytest.mark.slow
def test_py313_tests_pass() -> None:
    result = _run_tests_cmd("cauterule:py313")
    assert result.returncode == 0, result.stderr
