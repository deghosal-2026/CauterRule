"""Browser alias coverage for the WebArena reference corpus (#705)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Trajectory
from cauterule.replay.matcher import match_score

_REPO = Path(__file__).resolve().parents[2]
_BROWSER_CORPUS = _REPO / "corpus" / "public" / "browser" / "browser-issues.jsonl"

# Every browser distinctive/alias phrase from matcher.py that must have a trajectory.
_REQUIRED_PHRASES = (
    "stale element",
    "staleelementreferenceexception",
    "unexpected alert",
    "browser alert",
    "no such frame",
    "frame not found",
    "switch to frame",
    "element not found",
    "nosuchelementexception",
    "timeout",
    "page load timeout",
)


def _load_browser_trajectories() -> list[Trajectory]:
    records = [
        json.loads(line)
        for line in _BROWSER_CORPUS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [Trajectory.from_dict(r) for r in records]


def _cand(trigger: str) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger), do=RuleDo(directive="d"), confidence=0.9)


def test_browser_corpus_exists_and_has_20_failures() -> None:
    trajs = _load_browser_trajectories()
    assert len(trajs) == 20
    assert all(not t.success for t in trajs)
    assert all((t.failure_class or "").startswith("browser/") for t in trajs)


def test_each_browser_alias_has_trajectory() -> None:
    trajs = _load_browser_trajectories()
    # Build haystack per trajectory (tool browser).
    for phrase in _REQUIRED_PHRASES:
        norm = phrase.lower().replace("-", " ")
        found = False
        for traj in trajs:
            hay = " ".join(
                [traj.task]
                + [s.error or "" for s in traj.steps]
                + [s.input or "" for s in traj.steps]
                + [traj.failure_class or ""]
            ).lower()
            if norm in hay or phrase.lower() in hay:
                found = True
                break
        assert found, f"no browser trajectory covers alias phrase {phrase!r}"


@pytest.mark.parametrize(
    "trigger,expected_phrase",
    [
        ("stale element reference", "stale element"),
        ("browser alert not handled", "browser alert"),
        ("unexpected alert open", "unexpected alert"),
        ("no such frame: switch to frame failed", "no such frame"),
        ("frame not found checkout-iframe", "frame not found"),
        ("element not found: Unable to locate element", "element not found"),
        ("NoSuchElementException", "nosuchelementexception"),
        ("StaleElementReferenceException", "staleelementreferenceexception"),
        ("page load timeout", "page load timeout"),
    ],
)
def test_browser_trigger_matches_corpus(trigger: str, expected_phrase: str) -> None:
    trajs = _load_browser_trajectories()
    # Find at least one trajectory where match_score >= 0.6
    cand = _cand(trigger)
    scores = [match_score(cand, t) for t in trajs]
    assert max(scores) >= 0.6, (
        f"trigger {trigger!r} (phrase {expected_phrase!r}) max score {max(scores):.3f} < 0.6; scores={scores}"
    )


def test_browser_failure_classes_cover_five_subcategories() -> None:
    trajs = _load_browser_trajectories()
    classes = {t.failure_class for t in trajs}
    # Expect at least 5 distinct browser/* subcategories.
    assert len(classes) >= 5, classes
    for required in (
        "browser/stale_element",
        "browser/unexpected_alert",
        "browser/no_such_frame",
        "browser/element_not_found",
        "browser/timeout",
    ):
        assert required in classes, f"missing failure_class {required!r} in {classes}"
