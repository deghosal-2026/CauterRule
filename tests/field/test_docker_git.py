"""Git-based versioning: init, promote, rollback, retire, history."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml


@pytest.mark.docker
def test_git_init(tmp_path: Path) -> None:
    result = subprocess.run(
        ["git", "init"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0
    assert (tmp_path / ".git").is_dir()


@pytest.mark.docker
def test_promote_creates_commit(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], capture_output=True, check=True, cwd=tmp_path)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    rule = {
        "id": "R-100",
        "when": {"trigger": "test trigger"},
        "do": {"directive": "test directive"},
        "confidence": 0.9,
        "provenance": {
            "source_trajectory": "T-001",
            "extracted_by": "test",
            "extract_timestamp": "2026-09-05T12:00:00Z",
            "extraction_pass": 1,
        },
        "status": "active",
        "promoted_at": "2026-09-05T12:30:00Z",
    }
    rule_path = rules_dir / "R-100.yaml"
    rule_path.write_text(yaml.safe_dump(rule, sort_keys=False), encoding="utf-8")

    subprocess.run(
        ["git", "add", str(rules_dir)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    result = subprocess.run(
        ["git", "commit", "-m", "promote: R-100"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )
    assert "promote:" in result.stdout


@pytest.mark.docker
def test_yaml_has_real_hash(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], capture_output=True, check=True, cwd=tmp_path)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    rule = {
        "id": "R-101",
        "when": {"trigger": "test trigger"},
        "do": {"directive": "test directive"},
        "confidence": 0.9,
        "provenance": {
            "source_trajectory": "T-001",
            "extracted_by": "test",
            "extract_timestamp": "2026-09-05T12:00:00Z",
            "extraction_pass": 1,
        },
        "status": "active",
        "promoted_at": "2026-09-05T12:30:00Z",
    }
    rule_path = rules_dir / "R-101.yaml"
    rule_path.write_text(yaml.safe_dump(rule, sort_keys=False), encoding="utf-8")

    subprocess.run(
        ["git", "add", str(rules_dir)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "commit", "-m", "promote: R-101"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    hash_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )
    commit_hash = hash_result.stdout.strip()

    data = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    data.setdefault("provenance", {})["promotion_commit"] = commit_hash
    rule_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    reloaded = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    pc = reloaded["provenance"]["promotion_commit"]
    assert isinstance(pc, str) and len(pc) == 40
    assert all(c in "0123456789abcdef" for c in pc)


@pytest.mark.docker
def test_hash_matches_git(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], capture_output=True, check=True, cwd=tmp_path)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    rule = {
        "id": "R-102",
        "when": {"trigger": "test trigger"},
        "do": {"directive": "test directive"},
        "confidence": 0.9,
        "provenance": {
            "source_trajectory": "T-001",
            "extracted_by": "test",
            "extract_timestamp": "2026-09-05T12:00:00Z",
            "extraction_pass": 1,
        },
        "status": "active",
        "promoted_at": "2026-09-05T12:30:00Z",
    }
    rule_path = rules_dir / "R-102.yaml"
    rule_path.write_text(yaml.safe_dump(rule, sort_keys=False), encoding="utf-8")

    subprocess.run(
        ["git", "add", str(rules_dir)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "commit", "-m", "promote: R-102"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    ).stdout.strip()

    data = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    data.setdefault("provenance", {})["promotion_commit"] = head
    rule_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    reloaded = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    assert reloaded["provenance"]["promotion_commit"] == head


@pytest.mark.docker
def test_rollback(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], capture_output=True, check=True, cwd=tmp_path)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    rule_path = rules_dir / "R-103.yaml"
    rule_path.write_text("id: R-103\n", encoding="utf-8")

    subprocess.run(
        ["git", "add", str(rules_dir)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "commit", "-m", "promote: R-103"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    subprocess.run(
        ["git", "revert", "HEAD", "--no-edit"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )
    assert not rule_path.exists()


@pytest.mark.docker
def test_validate_after_rollback(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], capture_output=True, check=True, cwd=tmp_path)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    rule = {
        "id": "R-104",
        "when": {"trigger": "test trigger"},
        "do": {"directive": "test directive"},
        "confidence": 0.9,
        "provenance": {
            "source_trajectory": "T-001",
            "extracted_by": "test",
            "extract_timestamp": "2026-09-05T12:00:00Z",
            "extraction_pass": 1,
        },
        "status": "active",
        "promoted_at": "2026-09-05T12:30:00Z",
    }
    rule_path = rules_dir / "R-104.yaml"
    rule_path.write_text(yaml.safe_dump(rule, sort_keys=False), encoding="utf-8")

    subprocess.run(
        ["git", "add", str(rules_dir)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "commit", "-m", "promote: R-104"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "revert", "HEAD", "--no-edit"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    result = subprocess.run(
        ["cauterule", "validate"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0


@pytest.mark.docker
def test_retire_creates_commit(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], capture_output=True, check=True, cwd=tmp_path)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    rule = {
        "id": "R-105",
        "when": {"trigger": "test trigger"},
        "do": {"directive": "test directive"},
        "confidence": 0.9,
        "provenance": {
            "source_trajectory": "T-001",
            "extracted_by": "test",
            "extract_timestamp": "2026-09-05T12:00:00Z",
            "extraction_pass": 1,
        },
        "status": "active",
        "promoted_at": "2026-09-05T12:30:00Z",
    }
    rule_path = rules_dir / "R-105.yaml"
    rule_path.write_text(yaml.safe_dump(rule, sort_keys=False), encoding="utf-8")

    subprocess.run(
        ["git", "add", str(rules_dir)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "commit", "-m", "promote: R-105"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    result = subprocess.run(
        ["cauterule", "retire", "R-105"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0

    log = subprocess.run(
        ["git", "log", "--oneline"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )
    assert "R-105" in log.stdout


@pytest.mark.docker
def test_history_timeline(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], capture_output=True, check=True, cwd=tmp_path)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    rule = {
        "id": "R-106",
        "when": {"trigger": "test trigger"},
        "do": {"directive": "test directive"},
        "confidence": 0.9,
        "provenance": {
            "source_trajectory": "T-001",
            "extracted_by": "test",
            "extract_timestamp": "2026-09-05T12:00:00Z",
            "extraction_pass": 1,
        },
        "status": "active",
        "promoted_at": "2026-09-05T12:30:00Z",
    }
    rule_path = rules_dir / "R-106.yaml"
    rule_path.write_text(yaml.safe_dump(rule, sort_keys=False), encoding="utf-8")

    subprocess.run(
        ["git", "add", str(rules_dir)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "commit", "-m", "promote: R-106"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    result = subprocess.run(
        ["cauterule", "history", "--limit", "10"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert "R-106" in result.stdout
    assert "active" in result.stdout


@pytest.mark.docker
def test_rollback_restores(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], capture_output=True, check=True, cwd=tmp_path)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    rule = {
        "id": "R-107",
        "when": {"trigger": "test trigger"},
        "do": {"directive": "test directive"},
        "confidence": 0.9,
        "provenance": {
            "source_trajectory": "T-001",
            "extracted_by": "test",
            "extract_timestamp": "2026-09-05T12:00:00Z",
            "extraction_pass": 1,
        },
        "status": "active",
        "promoted_at": "2026-09-05T12:30:00Z",
    }
    rule_path = rules_dir / "R-107.yaml"
    rule_path.write_text(yaml.safe_dump(rule, sort_keys=False), encoding="utf-8")

    subprocess.run(
        ["git", "add", str(rules_dir)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "commit", "-m", "promote: R-107"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    subprocess.run(
        ["git", "revert", "HEAD", "--no-edit"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )
    assert not rule_path.exists()

    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_path.write_text(yaml.safe_dump(rule, sort_keys=False), encoding="utf-8")
    subprocess.run(
        ["git", "add", str(rule_path)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "commit", "-m", "re-promote: R-107"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    reloaded = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    assert reloaded["id"] == "R-107"
    assert reloaded["status"] == "active"


@pytest.mark.docker
def test_hash_not_uuid(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], capture_output=True, check=True, cwd=tmp_path)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    rule = {
        "id": "R-108",
        "when": {"trigger": "test trigger"},
        "do": {"directive": "test directive"},
        "confidence": 0.9,
        "provenance": {
            "source_trajectory": "T-001",
            "extracted_by": "test",
            "extract_timestamp": "2026-09-05T12:00:00Z",
            "extraction_pass": 1,
        },
        "status": "active",
        "promoted_at": "2026-09-05T12:30:00Z",
    }
    rule_path = rules_dir / "R-108.yaml"
    rule_path.write_text(yaml.safe_dump(rule, sort_keys=False), encoding="utf-8")

    subprocess.run(
        ["git", "add", str(rules_dir)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
    )
    subprocess.run(
        ["git", "commit", "-m", "promote: R-108"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    ).stdout.strip()

    data = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    data.setdefault("provenance", {})["promotion_commit"] = head
    rule_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    reloaded = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    pc = reloaded["provenance"]["promotion_commit"]
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    assert not uuid_pattern.match(pc)
