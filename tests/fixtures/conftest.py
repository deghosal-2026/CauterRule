"""pytest fixtures for CauterRule tests."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import StandingRule
from cauterule.models.trajectory import Trajectory
from cauterule.serialization.rule_yaml import load_rule_from_file, load_rules_from_dir
from cauterule.serialization.trajectory_jsonl import load_trajectories
from cauterule.store.manager import StoreManager

FIXTURES = Path(__file__).parent


@pytest.fixture
def test_trajectory() -> Trajectory:
    path = FIXTURES / "trajectories" / "git_push_failure.jsonl"
    (loaded,) = list(load_trajectories(path))
    return loaded


@pytest.fixture
def test_candidate() -> CandidateRule:
    path = FIXTURES / "candidates" / "candidate_git_push.yaml"
    data = __import__("yaml").safe_load(path.read_text(encoding="utf-8"))
    return CandidateRule.from_dict(data)


@pytest.fixture
def test_rule() -> StandingRule:
    path = FIXTURES / "rules" / "R-001.yaml"
    return load_rule_from_file(path)


@pytest.fixture
def test_store(tmp_path: Path) -> Iterator[StoreManager]:
    store = StoreManager(base_dir=str(tmp_path))
    src = FIXTURES / "rules"
    for rule in load_rules_from_dir(str(src)):
        store.add_rule(rule)
    yield store
