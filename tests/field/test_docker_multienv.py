"""Verify CauterRule builds and tests pass on all supported Python versions."""

from __future__ import annotations

import subprocess

import pytest

PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]


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
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "cauterule:py311",
            "sh",
            "-c",
            "pytest tests/ -m 'not slow' --tb=short -q",
        ],
        capture_output=True,
        text=True,
    )
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
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "cauterule:py312",
            "sh",
            "-c",
            "pytest tests/ -m 'not slow' --tb=short -q",
        ],
        capture_output=True,
        text=True,
    )
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
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "cauterule:py313",
            "sh",
            "-c",
            "pytest tests/ -m 'not slow' --tb=short -q",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
