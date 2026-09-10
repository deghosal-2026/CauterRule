"""Path-traversal regression tests (#499)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.store.archive import archive_rule
from cauterule.store.manager import StoreManager, resolve_inside, validate_rule_id


def _rule(rid: str) -> StandingRule:
    return StandingRule(
        id=rid,
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
    )


TRAVERSAL_IDS = [
    "..",
    "../..",
    "../../tmp/evil",
    "/etc/passwd",
    "a/b",
    "a\\b",
    "~",
    "R-001.yaml",
    "R 001",
    "",
]


@pytest.mark.parametrize("bad_id", TRAVERSAL_IDS)
def test_rule_path_rejects_traversal(tmp_path: Path, bad_id: str) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    with pytest.raises(ValueError, match="invalid rule_id|escapes"):
        m._rule_path(bad_id)


@pytest.mark.parametrize("bad_id", ["../../evil", "/abs/path", "a/b"])
def test_store_crud_rejects_traversal_no_io(tmp_path: Path, bad_id: str) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    with pytest.raises(ValueError):
        m.get_rule(bad_id)
    with pytest.raises(ValueError):
        m.add_rule(_rule(bad_id))
    with pytest.raises(ValueError):
        m.retire_rule(bad_id, "x")
    with pytest.raises(ValueError):
        m.supersede_rule(bad_id, "R-002")
    with pytest.raises(ValueError):
        archive_rule(bad_id, str(tmp_path / "rules"))
    # Nothing escaped the store dir.
    assert list(tmp_path.iterdir()) == [] or all(p.name == "rules" for p in tmp_path.iterdir())


def test_legitimate_ids_still_work(tmp_path: Path) -> None:
    m = StoreManager(str(tmp_path / "rules"))
    m.add_rule(_rule("abc-123_X"))
    assert m.get_rule("abc-123_X") is not None


def test_resolve_inside_rejects_escape(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="escapes"):
        resolve_inside(tmp_path, "..", "evil.yaml")


def test_validate_rule_id_accepts_normal() -> None:
    validate_rule_id("R-001")
    validate_rule_id("abc-123_X")


def test_validate_rule_id_rejects_non_string() -> None:
    # Review: re.match raises TypeError on non-str; API promises ValueError.
    with pytest.raises(ValueError, match="invalid rule_id"):
        validate_rule_id(None)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="invalid rule_id"):
        validate_rule_id(123)  # type: ignore[arg-type]
