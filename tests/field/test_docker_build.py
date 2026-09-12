"""Verify the Docker image builds and Cauterule installs correctly."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import cauterule

DOCKER_TAG = "cauterule:field-test"
REPO = Path(__file__).resolve().parents[2]


def _pyproject_version() -> str:
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.strip().startswith("version"):
            return line.split("=")[1].strip().strip('"').strip("'")
    return ""


@pytest.mark.docker
def test_docker_image_builds() -> None:
    result = subprocess.run(
        ["docker", "build", "-t", DOCKER_TAG, "."],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.docker
def test_docker_version() -> None:
    result = subprocess.run(
        ["docker", "run", "--rm", DOCKER_TAG, "--version"],
        capture_output=True,
        text=True,
    )
    assert _pyproject_version() in result.stdout


@pytest.mark.docker
def test_docker_help() -> None:
    result = subprocess.run(
        ["docker", "run", "--rm", DOCKER_TAG, "--help"],
        capture_output=True,
        text=True,
    )
    assert "extract" in result.stdout
    assert "promote" in result.stdout
    assert "demo" in result.stdout


@pytest.mark.docker
def test_docker_pip_show() -> None:
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "python",
            DOCKER_TAG,
            "-m",
            "pip",
            "show",
            "cauterule",
        ],
        capture_output=True,
        text=True,
    )
    assert "Name: cauterule" in result.stdout


@pytest.mark.docker
def test_docker_import() -> None:
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "python",
            DOCKER_TAG,
            "-c",
            "import cauterule; print(cauterule.__version__)",
        ],
        capture_output=True,
        text=True,
    )
    assert _pyproject_version() in result.stdout
    assert cauterule.__version__ == _pyproject_version()
