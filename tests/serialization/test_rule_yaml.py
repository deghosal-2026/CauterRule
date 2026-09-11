from pathlib import Path

import pytest
import yaml

from cauterule.models.rule import Provenance, ReplayEvidence, RuleDo, RuleWhen, StandingRule
from cauterule.serialization.rule_yaml import (
    dump_rule,
    dump_rule_to_file,
    load_rule,
    load_rule_from_file,
    load_rules_from_dir,
)


def _valid_rule() -> StandingRule:
    return StandingRule(
        id="R-001",
        when=RuleWhen(trigger="git push fails", context=("shared branch",)),
        do=RuleDo(directive="pull --rebase", because="remote ahead"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="trajectories/2026-09-03/failure-003.jsonl",
            extracted_by="gpt-4o",
            extract_timestamp="2026-09-03T18:30:00Z",
            extraction_pass=1,
            replay_evidence=ReplayEvidence(precision=1.0, recall=0.5),
            promotion_commit="abc",
            promotion_mode="auto",
        ),
        status="active",
        promoted_at="2026-09-03T18:35:00Z",
        hit_count=2,
        tags=("git",),
        taxonomy="git/push",
        template="retry",
    )


def test_dump_load_roundtrip() -> None:
    rule = _valid_rule()
    yaml_str = dump_rule(rule)
    assert "R-001" in yaml_str
    loaded = load_rule(yaml_str)
    assert loaded == rule


def test_dump_load_minimal() -> None:
    rule = StandingRule(
        id="R-002",
        when=RuleWhen(trigger="t"),
        do=RuleDo(directive="d"),
        confidence=0.5,
        provenance=Provenance(
            source_trajectory="a.jsonl", extracted_by="m", extract_timestamp="t", extraction_pass=1
        ),
        status="active",
        promoted_at="2026-09-03T18:35:00Z",
    )
    loaded = load_rule(dump_rule(rule))
    assert loaded == rule


def test_load_invalid_yaml() -> None:
    with pytest.raises(ValueError, match="mapping"):
        load_rule("[1, 2, 3]\n")
    with pytest.raises(ValueError, match="mapping"):
        load_rule("123\n")


def test_file_roundtrip(tmp_path: Path) -> None:
    rule = _valid_rule()
    p = tmp_path / "R-001.yaml"
    dump_rule_to_file(rule, p)
    assert p.exists()
    loaded = load_rule_from_file(p)
    assert loaded == rule
    # nested dir creation
    nested = tmp_path / "nested" / "dir" / "R-002.yaml"
    dump_rule_to_file(rule, nested)
    assert nested.exists()


def test_load_rules_from_dir(tmp_path: Path) -> None:
    # empty dir
    assert load_rules_from_dir(tmp_path) == []
    # two files with distinct ids
    dump_rule_to_file(_rule_with_id("R-001"), tmp_path / "R-001.yaml")
    dump_rule_to_file(_rule_with_id("R-002"), tmp_path / "R-002.yml")
    # not yaml file ignored
    (tmp_path / "ignore.txt").write_text("hello")
    rules = load_rules_from_dir(tmp_path)
    assert len(rules) == 2
    # non-existent dir returns []
    assert load_rules_from_dir(tmp_path / "nope") == []
    # recursion: subdirectory rules loaded (#613)
    sub = tmp_path / "packs" / "git"
    sub.mkdir(parents=True)
    dump_rule_to_file(_rule_with_id("R-003"), sub / "R-003.yaml")
    rules = load_rules_from_dir(tmp_path)
    assert {r.id for r in rules} == {"R-001", "R-002", "R-003"}
    # index skipped at depth (#613)
    dump_rule_to_file(_rule_with_id("R-004"), sub / "index.yaml")
    # pack manifest skipped and never quarantined (#613)
    (sub / "manifest.yaml").write_text("name: pack-git\nversion: '1.0'\n", encoding="utf-8")
    assert {r.id for r in load_rules_from_dir(tmp_path)} == {"R-001", "R-002", "R-003"}
    assert (sub / "manifest.yaml").exists()
    # pack.yaml + packs.lock.yaml are manifests too, never rules (#554)
    (sub / "pack.yaml").write_text("name: pack-git\nversion: '1.0'\n", encoding="utf-8")
    (tmp_path / "packs.lock.yaml").write_text("version: 1\n", encoding="utf-8")
    assert {r.id for r in load_rules_from_dir(tmp_path)} == {"R-001", "R-002", "R-003"}
    assert (sub / "pack.yaml").exists()
    assert (tmp_path / "packs.lock.yaml").exists()
    assert not (tmp_path / ".quarantine").exists()


def test_load_rules_from_dir_bad_yaml_quarantined(tmp_path: Path) -> None:
    dump_rule_to_file(_rule_with_id("R-GOOD-1"), tmp_path / "R-GOOD-1.yaml")
    dump_rule_to_file(_rule_with_id("R-GOOD-2"), tmp_path / "R-GOOD-2.yaml")
    bad = tmp_path / "R-BAD.yaml"
    bad.write_text(": not valid yaml: :", encoding="utf-8")

    from cauterule.serialization.rule_yaml import last_load_errors, load_rules_from_dir

    rules = load_rules_from_dir(tmp_path)
    assert {r.id for r in rules} == {"R-GOOD-1", "R-GOOD-2"}
    # bad file moved to quarantine and recorded
    assert not bad.exists()
    qdir = tmp_path / ".quarantine"
    assert (qdir / "R-BAD.yaml").exists()
    index = (qdir / "index.jsonl").read_text(encoding="utf-8")
    assert "R-BAD.yaml" in index
    assert "Error" in index
    assert len(last_load_errors) == 1
    assert last_load_errors[0][0].endswith("R-BAD.yaml")


def test_load_rules_from_dir_bad_yaml_no_quarantine(tmp_path: Path) -> None:
    dump_rule_to_file(_rule_with_id("R-GOOD"), tmp_path / "R-GOOD.yaml")
    bad = tmp_path / "R-BAD.yaml"
    bad.write_text(": not valid yaml: :", encoding="utf-8")

    from cauterule.serialization.rule_yaml import last_load_errors, load_rules_from_dir

    rules = load_rules_from_dir(tmp_path, quarantine=False)
    assert [r.id for r in rules] == ["R-GOOD"]
    assert bad.exists()  # left in place
    assert len(last_load_errors) == 1


def test_load_rules_from_dir_strict(tmp_path: Path) -> None:
    dump_rule_to_file(_rule_with_id("R-001"), tmp_path / "R-001.yaml")
    (tmp_path / "R-BAD.yaml").write_text(": not valid yaml: :", encoding="utf-8")
    from cauterule.serialization.rule_yaml import load_rules_from_dir

    with pytest.raises(ValueError, match="failed to load"):
        load_rules_from_dir(tmp_path, strict=True)


def _rule_with_id(rid: str) -> StandingRule:
    from dataclasses import replace

    return replace(_valid_rule(), id=rid)


def test_yaml_is_valid_yaml() -> None:
    rule = _valid_rule()
    yaml_str = dump_rule(rule)
    data = yaml.safe_load(yaml_str)
    assert isinstance(data, dict)
    assert data["id"] == "R-001"
