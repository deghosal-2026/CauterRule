"""Comprehensive tests for the store module."""

from __future__ import annotations

from pathlib import Path

import pytest

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule, Status
from cauterule.serialization.rule_yaml import dump_rule_to_file
from cauterule.store.archive import archive_rule
from cauterule.store.health import health_report
from cauterule.store.index import IndexManager
from cauterule.store.manager import StoreManager
from cauterule.store.validator import validate_store


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _rule(
    rid: str,
    status: Status = "active",
    tags: tuple[str, ...] = (),
    last_match: str | None = None,
    trigger: str = "git push fails",
) -> StandingRule:
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="check remote"),
        confidence=0.85,
        provenance=Provenance(
            source_trajectory="T-1",
            extracted_by="test",
            extract_timestamp="2025-01-01T00:00:00",
            extraction_pass=1,
        ),
        status=status,
        promoted_at="2025-01-02T00:00:00",
        hit_count=5,
        tags=tags,
        last_match=last_match,
    )


# ------------------------------------------------------------------
# StoreManager
# ------------------------------------------------------------------
def test_add_rule(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    rid = m.add_rule(_rule("R-001"))
    assert rid == "R-001"
    assert (tmp_path / "rules" / "R-001.yaml").is_file()


def test_get_rule(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    m.add_rule(_rule("R-002"))
    rule = m.get_rule("R-002")
    assert rule is not None
    assert rule.id == "R-002"
    assert rule.when.trigger == "git push fails"


def test_get_rule_missing(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    assert m.get_rule("R-NONE") is None


def test_list_rules(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    m.add_rule(_rule("R-001"))
    m.add_rule(_rule("R-002"))
    all_rules = m.list_rules()
    assert len(all_rules) == 2
    ids = {r.id for r in all_rules}
    assert ids == {"R-001", "R-002"}


def test_list_rules_filter_status(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    m.add_rule(_rule("R-A1"))
    m.add_rule(_rule("R-A2"))
    m.add_rule(_rule("R-R1", status="retired"))
    active = m.list_rules(status="active")
    retired = m.list_rules(status="retired")
    assert len(active) == 2
    assert len(retired) == 1


def test_list_rules_empty(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    assert m.list_rules() == []


def test_retire_rule(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    m.add_rule(_rule("R-003"))
    m.retire_rule("R-003", "no longer needed")
    rule = m.get_rule("R-003")
    assert rule is not None
    assert rule.status == "retired"


def test_retire_rule_not_found(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    with pytest.raises(ValueError, match="not found"):
        m.retire_rule("R-MISSING", "reason")


def test_retire_already_retired(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    m.add_rule(_rule("R-004", status="retired"))
    with pytest.raises(ValueError, match="Cannot retire"):
        m.retire_rule("R-004", "again")


def test_supersede_rule(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    m.add_rule(_rule("R-005"))
    m.supersede_rule("R-005", "R-006")
    rule = m.get_rule("R-005")
    assert rule is not None
    assert rule.status == "superseded"


def test_supersede_rule_not_found(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    with pytest.raises(ValueError, match="not found"):
        m.supersede_rule("R-MISSING", "R-NEW")


# ------------------------------------------------------------------
# IndexManager
# ------------------------------------------------------------------
def test_index_empty(tmp_path: Path) -> None:
    idx = IndexManager(str(tmp_path / "rules"))
    assert idx.load_index() == {"rules": []}


def test_index_add_entry(tmp_path: Path) -> None:
    idx = IndexManager(str(tmp_path / "rules"))
    rule = _rule("R-010")
    idx.add_entry(rule)
    data = idx.load_index()
    assert "rules" in data
    assert data["rules"][0]["id"] == "R-010"
    assert data["rules"][0]["status"] == "active"


def test_index_remove_entry(tmp_path: Path) -> None:
    idx = IndexManager(str(tmp_path / "rules"))
    idx.add_entry(_rule("R-010"))
    idx.remove_entry("R-010")
    assert idx.load_index() == {"rules": []}


def test_index_remove_missing(tmp_path: Path) -> None:
    idx = IndexManager(str(tmp_path / "rules"))
    idx.remove_entry("R-GHOST")
    assert idx.load_index() == {"rules": []}


def test_index_update_entry(tmp_path: Path) -> None:
    idx = IndexManager(str(tmp_path / "rules"))
    idx.add_entry(_rule("R-010", status="active"))
    idx.update_entry(_rule("R-010", status="retired"))
    data = idx.load_index()
    assert data["rules"][0]["status"] == "retired"


def test_index_save_index(tmp_path: Path) -> None:
    idx = IndexManager(str(tmp_path / "rules"))
    entries = {"rules": [{"id": "R-A", "status": "active", "summary": "test"}]}
    idx.save_index(entries)
    loaded = idx.load_index()
    assert loaded == entries


# ------------------------------------------------------------------
# Archive
# ------------------------------------------------------------------
def test_archive_rule(tmp_path: Path) -> None:
    base = str(tmp_path / "rules")
    m = StoreManager(base)
    m.add_rule(_rule("R-ARC"))
    src = Path(base) / "R-ARC.yaml"
    assert src.is_file()
    archived = archive_rule("R-ARC", base)
    assert archived == Path(base) / "archived" / "R-ARC.yaml"
    assert archived.is_file()
    assert not src.exists()


def test_archive_rule_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        archive_rule("R-GHOST", str(tmp_path / "rules"))


# ------------------------------------------------------------------
# Validator
# ------------------------------------------------------------------
def test_validate_store_clean(tmp_path: Path) -> None:
    base = str(tmp_path / "rules")
    m = StoreManager(base)
    m.add_rule(_rule("R-V01"))
    m.add_rule(_rule("R-V02"))
    assert validate_store(base) == []


def test_validate_store_missing_dir(tmp_path: Path) -> None:
    base = str(tmp_path / "no-such-dir")
    warnings = validate_store(base)
    assert any("not found" in w for w in warnings)


def test_validate_store_bad_yaml(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    base.mkdir(parents=True)
    f = base / "corrupt.yaml"
    f.write_text("!!invalid yaml: [", encoding="utf-8")
    warnings = validate_store(str(base))
    assert any("failed to deserialize" in w for w in warnings)


def test_validate_store_empty(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    base.mkdir(parents=True)
    warnings = validate_store(str(base))
    assert any("No rule files found" in w for w in warnings)


def test_validate_store_duplicate_ids(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    base.mkdir(parents=True)
    r = _rule("R-DUP")
    dump_rule_to_file(r, base / "R-DUP-a.yaml")
    dump_rule_to_file(r, base / "R-DUP-b.yaml")
    warnings = validate_store(str(base))
    assert any("Duplicate ID" in w for w in warnings)


def test_validate_store_missing_provenance(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    base.mkdir(parents=True)
    import yaml

    data = {
        "id": "R-NOPROV",
        "when": {"trigger": "x"},
        "do": {"directive": "y"},
        "confidence": 0.5,
        "provenance": {},
        "status": "active",
        "promoted_at": "t",
    }
    (base / "R-NOPROV.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    warnings = validate_store(str(base))
    assert any("failed to deserialize" in w for w in warnings)


# ------------------------------------------------------------------
# Health
# ------------------------------------------------------------------
def test_health_report(tmp_path: Path) -> None:
    base = str(tmp_path / "rules")
    m = StoreManager(base)
    m.add_rule(_rule("R-H01", tags=("git",), last_match="2026-09-01T00:00:00+00:00"))
    m.add_rule(_rule("R-H02", tags=("git",), last_match="2026-09-01T00:00:00+00:00"))
    m.add_rule(_rule("R-H03", status="retired"))
    report = health_report(base)
    assert report["total_rules"] == 3
    assert report["by_status"]["active"] == 2
    assert report["by_status"]["retired"] == 1
    assert report["avg_confidence"] == 0.85
    assert "R-H01" not in report["stale_rules"] and "R-H02" not in report["stale_rules"]
    assert "report_time" in report


def test_health_report_empty(tmp_path: Path) -> None:
    base = str(tmp_path / "rules")
    report = health_report(base)
    assert report["total_rules"] == 0
    assert report["avg_confidence"] == 0.0
    assert report["avg_effectiveness"] == 0.0


def test_health_report_stale(tmp_path: Path) -> None:
    base = str(tmp_path / "rules")
    m = StoreManager(base)
    m.add_rule(
        StandingRule(
            id="R-STALE",
            when=RuleWhen(trigger="git push fails"),
            do=RuleDo(directive="check remote"),
            confidence=0.85,
            provenance=Provenance(
                source_trajectory="T-1",
                extracted_by="test",
                extract_timestamp="2025-01-01T00:00:00",
                extraction_pass=1,
            ),
            status="active",
            promoted_at="2025-01-02T00:00:00",
            hit_count=0,
            last_match="2020-01-01T00:00:00+00:00",
            tags=("old",),
        )
    )
    report = health_report(base)
    assert "R-STALE" in report["stale_rules"]


def test_health_report_conflict_count(tmp_path: Path) -> None:
    base = str(tmp_path / "rules")
    m = StoreManager(base)
    m.add_rule(_rule("R-A", last_match="2026-09-01T00:00:00+00:00"))
    m.add_rule(_rule("R-B", last_match="2026-09-01T00:00:00+00:00"))
    report = health_report(base)
    assert report["conflict_count"] == 1


# ------------------------------------------------------------------
# Git operations
# ------------------------------------------------------------------
def test_git_commit_returns_none_outside_git(tmp_path: Path) -> None:
    from cauterule.store.git import git_commit

    result = git_commit("test message", str(tmp_path))
    assert result is None


def test_rollback_false_outside_git(tmp_path: Path) -> None:
    from cauterule.store.rollback import rollback_promotion

    assert rollback_promotion("abc1234", str(tmp_path)) is False


def test_rollback_false_no_git_executable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import subprocess

    def fake_run(*args: object, **kwargs: object) -> object:
        raise FileNotFoundError("No such file or directory: 'git'")

    monkeypatch.setattr(subprocess, "run", fake_run)
    from cauterule.store.rollback import rollback_promotion

    assert rollback_promotion("abc1234", str(tmp_path)) is False


def test_git_commit_called_process_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import subprocess

    def fake_run(*args: object, **kwargs: object) -> object:
        raise subprocess.CalledProcessError(1, ["git", "commit"])

    monkeypatch.setattr(subprocess, "run", fake_run)
    from cauterule.store.git import git_commit

    assert git_commit("test", str(tmp_path)) is None


def test_git_commit_file_not_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import subprocess

    def fake_run(*args: object, **kwargs: object) -> object:
        raise FileNotFoundError("No such file or directory: 'git'")

    monkeypatch.setattr(subprocess, "run", fake_run)
    from cauterule.store.git import git_commit

    assert git_commit("test", str(tmp_path)) is None


def test_extract_hash_valid() -> None:
    from cauterule.store.git import _extract_hash

    assert _extract_hash("[main abc1234] test message") == "abc1234"
    assert _extract_hash("no brackets here") is None


def test_extract_hash_long() -> None:
    from cauterule.store.git import _extract_hash

    long_hash = "abc1234def5678abc1234def5678abc1234abcd1"
    assert len(long_hash) == 40
    assert _extract_hash(f"[main {long_hash}] test") == long_hash


@pytest.mark.parametrize(
    "payload", ["--help", "-h", "--upload-pack=x", "HEAD --extra", "abc123", "xyz", ""]
)
def test_rollback_rejects_non_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, payload: str
) -> None:
    # #505: option-injection payloads raise before any subprocess runs.
    import subprocess
    from collections.abc import Sequence
    from typing import Any

    from cauterule.store.rollback import rollback_promotion

    def _boom(cmd: Sequence[str], **kwargs: Any) -> Any:
        raise AssertionError("subprocess must not run for invalid hash")

    monkeypatch.setattr(subprocess, "run", _boom)
    with pytest.raises(ValueError, match="invalid commit hash"):
        rollback_promotion(payload, str(tmp_path))


def test_rollback_argv_has_separator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # #505: argv contains -- before the hash.
    import subprocess
    from collections.abc import Sequence
    from typing import Any

    seen: list[list[str]] = []

    def fake_run(cmd: Sequence[str], **kwargs: Any) -> Any:
        seen.append(list(cmd))
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    from cauterule.store.rollback import rollback_promotion

    assert rollback_promotion("abc1234", str(tmp_path)) is False
    assert seen and seen[0][:4] == ["git", "revert", "--no-edit", "--"]
    assert seen[0][4] == "abc1234"


def test_rollback_rejects_non_string() -> None:
    # Review: non-string hash raises ValueError, not TypeError.
    import tempfile

    from cauterule.store.rollback import rollback_promotion

    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(ValueError, match="invalid commit hash"):
            rollback_promotion(None, tmp)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="invalid commit hash"):
            rollback_promotion(123, tmp)  # type: ignore[arg-type]


def test_rollback_success_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Review: valid hash + exit 0 returns True.
    import subprocess
    from collections.abc import Sequence
    from typing import Any

    def fake_run(cmd: Sequence[str], **kwargs: Any) -> Any:
        assert list(cmd)[:4] == ["git", "revert", "--no-edit", "--"]
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    from cauterule.store.rollback import rollback_promotion

    assert rollback_promotion("abc1234def", str(tmp_path)) is True


def test_git_commit_error_log_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # Review: failure logs returncode + stderr at error level.
    import logging
    import subprocess

    def fake_run(*args: object, **kwargs: object) -> object:
        raise subprocess.CalledProcessError(1, ["git", "commit"], stderr="fatal: oops")

    monkeypatch.setattr(subprocess, "run", fake_run)
    from cauterule.store.git import git_commit

    with caplog.at_level(logging.ERROR, logger="cauterule.store.git"):
        assert git_commit("test", str(tmp_path)) is None
    assert "rc=1" in caplog.text
    assert "fatal: oops" in caplog.text


# ------------------------------------------------------------------
# #523 — index upsert + malformed index + near-duplicate health + two-pass validator
# ------------------------------------------------------------------
def test_index_add_entry_upserts(tmp_path: Path) -> None:
    idx = IndexManager(str(tmp_path / "rules"))
    idx.add_entry(_rule("R-UPS"))
    idx.add_entry(_rule("R-UPS"))
    data = idx.load_index()
    assert len(data["rules"]) == 1


def test_index_load_malformed_raises(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    base.mkdir(parents=True)
    (base / "index.yaml").write_text("just a list\n- 1\n- 2\n", encoding="utf-8")
    idx = IndexManager(str(base))
    with pytest.raises(ValueError, match="index.yaml must be a mapping"):
        idx.load_index()


def test_health_near_duplicate_pairs(tmp_path: Path) -> None:
    base = str(tmp_path / "rules")
    m = StoreManager(base)
    m.add_rule(_rule("R-ND1", trigger="permission denied pushing to remote", last_match="2026-09-01T00:00:00+00:00"))
    m.add_rule(_rule("R-ND2", trigger="access denied pushing to remote", last_match="2026-09-01T00:00:00+00:00"))
    report = health_report(base)
    assert report["conflict_count"] == 0
    assert len(report["near_duplicate_pairs"]) >= 1


def test_health_near_duplicate_pairs_empty_on_distinct(tmp_path: Path) -> None:
    base = str(tmp_path / "rules")
    m = StoreManager(base)
    m.add_rule(_rule("R-A", trigger="git push fails", last_match="2026-09-01T00:00:00+00:00"))
    m.add_rule(_rule("R-B", trigger="docker build fails", last_match="2026-09-01T00:00:00+00:00"))
    report = health_report(base)
    assert report["near_duplicate_pairs"] == []


def test_validator_two_pass_superseded(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    base.mkdir(parents=True)
    import yaml
    aaa = _rule("AAA")
    zzz = _rule("ZZZ")
    aaa_data = aaa.to_dict()
    aaa_data["superseded_by"] = "ZZZ"
    (base / "aaa.yaml").write_text(yaml.safe_dump(aaa_data, sort_keys=False), encoding="utf-8")
    zzz_data = zzz.to_dict()
    (base / "zzz.yaml").write_text(yaml.safe_dump(zzz_data, sort_keys=False), encoding="utf-8")
    warnings = validate_store(str(base))
    assert not any("ZZZ" in w and "not found" in w for w in warnings)


def test_validator_dangling_superseded_warns(tmp_path: Path) -> None:
    base = tmp_path / "rules"
    base.mkdir(parents=True)
    import yaml
    aaa = _rule("AAA")
    aaa_data = aaa.to_dict()
    aaa_data["superseded_by"] = "MISSING"
    (base / "aaa.yaml").write_text(yaml.safe_dump(aaa_data), encoding="utf-8")
    warnings = validate_store(str(base))
    assert any("MISSING" in w and "not found" in w for w in warnings)
