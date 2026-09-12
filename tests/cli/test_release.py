"""Tests for the release CLI (#604)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from cauterule import __version__
from cauterule.cli.app import main

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_release_check_consistent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(f'[project]\nversion = "{__version__}"\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(main, ["release", "check"])
    assert result.exit_code == 0, result.output
    assert "versions consistent" in result.output
    assert f"v{__version__}" in result.output


def test_release_check_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nversion = "9.9.9"\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(main, ["release", "check"])
    assert result.exit_code != 0
    assert "version mismatch" in result.output


def test_release_check_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(main, ["release", "check"])
    assert result.exit_code != 0
    assert "pyproject.toml not found" in result.output


def test_release_check_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(REPO_ROOT)
    result = CliRunner().invoke(main, ["release", "check"])
    assert result.exit_code == 0, result.output
