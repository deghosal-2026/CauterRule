import pytest

from cauterule.models.conflict import ConflictReport


def test_conflict_valid() -> None:
    c = ConflictReport(
        type="contradiction",
        rules=("R-001", "R-002"),
        trigger="git push fails",
        resolution="keep more specific",
        specificity_scores={"R-001": 0.9, "R-002": 0.5},
    )
    assert c.type == "contradiction"
    d = c.to_dict()
    assert d["rules"] == ["R-001", "R-002"]
    assert ConflictReport.from_dict(d) == c
    # minimal
    c2 = ConflictReport(type="overlap", rules=("R-001",))
    assert "trigger" not in c2.to_dict()
    assert "specificity_scores" not in c2.to_dict()


def test_conflict_validation() -> None:
    with pytest.raises(ValueError, match="type"):
        ConflictReport(type="bad", rules=("R-001",))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="rules must be non-empty"):
        ConflictReport(type="overlap", rules=())
    with pytest.raises(ValueError, match="rules items"):
        ConflictReport(type="overlap", rules=(" ",))
    with pytest.raises(ValueError, match="trigger"):
        ConflictReport(type="overlap", rules=("R-001",), trigger="   ")
    with pytest.raises(ValueError, match="specificity_scores keys"):
        ConflictReport(type="overlap", rules=("R-001",), specificity_scores={" ": 0.5})
    with pytest.raises(ValueError, match="specificity_scores values"):
        ConflictReport(type="overlap", rules=("R-001",), specificity_scores={"R-001": 1.5})
