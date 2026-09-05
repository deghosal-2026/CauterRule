"""Verify the Docker image builds and Cauterule installs correctly."""

from __future__ import annotations

import subprocess

import pytest

DOCKER_TAG = "cauterule:field-test"


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
    assert "0.1.0" in result.stdout


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
        ["docker", "run", "--rm", DOCKER_TAG, "sh", "-c", "pip show cauterule"],
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
            DOCKER_TAG,
            "python",
            "-c",
            "import cauterule; print(cauterule.__version__)",
        ],
        capture_output=True,
        text=True,
    )
    assert "0.1.0" in result.stdout
