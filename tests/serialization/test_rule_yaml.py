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
    rule = _valid_rule()
    # empty dir
    assert load_rules_from_dir(tmp_path) == []
    # two files
    dump_rule_to_file(rule, tmp_path / "R-001.yaml")
    dump_rule_to_file(rule, tmp_path / "R-002.yml")
    # not yaml file ignored
    (tmp_path / "ignore.txt").write_text("hello")
    rules = load_rules_from_dir(tmp_path)
    assert len(rules) == 2
    # non-existent dir returns []
    assert load_rules_from_dir(tmp_path / "nope") == []
    # file with .yaml but invalid content still raises? ensure load works
    # test that index skip works — create subdirectory
    sub = tmp_path / "sub"
    sub.mkdir()
    dump_rule_to_file(rule, sub / "R-003.yaml")
    # non-recursive, so not found
    assert len(load_rules_from_dir(tmp_path)) == 2


def test_yaml_is_valid_yaml() -> None:
    rule = _valid_rule()
    yaml_str = dump_rule(rule)
    data = yaml.safe_load(yaml_str)
    assert isinstance(data, dict)
    assert data["id"] == "R-001"
