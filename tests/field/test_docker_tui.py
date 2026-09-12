"""TUI tests inside the Docker container using Textual Pilot."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from textual.binding import Binding

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import (
    Provenance,
    ReplayEvidence,
    RuleDo,
    RuleWhen,
    StandingRule,
)
from cauterule.store.manager import StoreManager
from cauterule.tui.annotate import FAILURE_CATEGORIES, AnnotationScreen
from cauterule.tui.app import CauterRuleApp
from cauterule.tui.batch import BatchReviewScreen
from cauterule.tui.cards import EvidenceCard
from cauterule.tui.confidence import ConfidenceCard
from cauterule.tui.filter import FilterWidget
from cauterule.tui.review import ReviewScreen


def _make_candidate(trigger: str = "x fails") -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="do y"),
        confidence=0.85,
        reasoning=f"trajectory-{trigger}",
        extraction_pass=1,
    )


def _make_standing_rule(
    rule_id: str = "R-001",
    trigger: str = "x fails",
    confidence: float = 0.9,
    hit_count: int = 5,
    status: Any = "active",
    tags: tuple[str, ...] = ("python",),
) -> StandingRule:
    return StandingRule(
        id=rule_id,
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="do y"),
        confidence=confidence,
        hit_count=hit_count,
        last_match="2024-01-01",
        status=status,
        tags=tags,
        promoted_at="2024-01-01T00:00:00Z",
        provenance=Provenance(
            source_trajectory=f"traj-{rule_id}.json",
            extracted_by="test",
            extract_timestamp="2024-01-01T00:00:00Z",
            extraction_pass=1,
            replay_evidence=ReplayEvidence(
                failures_prevented=("F-1",),
                successes_broken=(),
                precision=1.0,
                recall=0.5,
            ),
        ),
    )


@dataclass
class _MockFilterCandidate:
    tags: tuple[str, ...] = ()
    confidence: float = 0.0
    status: str = "active"


@pytest.mark.docker
def test_review_screen_mounts() -> None:
    async def _run() -> None:
        app = CauterRuleApp()
        async with app.run_test() as pilot:
            screen = ReviewScreen()
            app.push_screen(screen)
            await pilot.pause()
            assert app.screen is screen
            assert isinstance(app.screen, ReviewScreen)

    asyncio.run(_run())


@pytest.mark.docker
def test_candidates_load() -> None:
    async def _run() -> None:
        with TemporaryDirectory() as tmp:
            store = StoreManager(base_dir=tmp)
            rule = _make_standing_rule(rule_id="R-001", trigger="deploy fails")
            store.add_rule(rule)
            screen = ReviewScreen(store=store)
            screen._populate_candidates()
            assert len(screen._candidates) == 1
            assert screen._candidates[0].when.trigger == "deploy fails"

    asyncio.run(_run())


@pytest.mark.docker
def test_evidence_cards_render() -> None:
    async def _run() -> None:
        app = CauterRuleApp()
        async with app.run_test():
            evidence = ReplayEvidence(
                failures_prevented=("F-1", "F-2"),
                successes_broken=("S-1",),
                precision=1.0,
                recall=0.5,
            )
            card = EvidenceCard()
            card.render_evidence(evidence)
            content = str(card.render())
            assert "Prevented 2 failures" in content
            assert "broke 1 successes" in content
            assert "Precision: 1.00" in content
            assert "Recall: 0.50" in content

    asyncio.run(_run())


@pytest.mark.docker
def test_confidence_cards_render() -> None:
    async def _run() -> None:
        app = CauterRuleApp()
        async with app.run_test():
            rule = _make_standing_rule(confidence=0.9, hit_count=5, tags=("python", "deploy"))
            card = ConfidenceCard()
            card.render_rule(rule)
            content = str(card.render())
            assert "Confidence: 0.90" in content
            assert "Hit count: 5" in content
            assert "Last hit: 2024-01-01" in content
            assert "Status: active" in content
            assert "python" in content
            assert "deploy" in content

    asyncio.run(_run())


@pytest.mark.docker
def test_annotation_screen() -> None:
    async def _run() -> None:
        app = CauterRuleApp()
        async with app.run_test() as pilot:
            candidate = _make_candidate()
            screen = AnnotationScreen(candidate)
            app.push_screen(screen)
            await pilot.pause()
            tags_input = screen.query_one("#tags-input")
            comment_input = screen.query_one("#comment-input")
            assert tags_input is not None
            assert comment_input is not None
            category_select = screen.query_one("#category-select")
            assert category_select is not None
            assert "logic_error" in FAILURE_CATEGORIES

    asyncio.run(_run())


@pytest.mark.docker
def test_batch_review() -> None:
    async def _run() -> None:
        app = CauterRuleApp()
        async with app.run_test() as pilot:
            candidates = [_make_candidate(f"trigger-{i}") for i in range(10)]
            screen = BatchReviewScreen(candidates)
            app.push_screen(screen)
            await pilot.pause()
            assert len(screen._candidates) == 10
            batch_list = screen.query_one("#batch-list")
            assert batch_list is not None
            items = list(batch_list.query("ListItem"))
            assert len(items) == 10

    asyncio.run(_run())


@pytest.mark.docker
def test_filter_by_tag() -> None:
    async def _run() -> None:
        widget = FilterWidget()
        candidates: list[Any] = [
            _MockFilterCandidate(tags=("python",), confidence=0.8, status="active"),
            _MockFilterCandidate(tags=("deploy",), confidence=0.5, status="active"),
        ]
        filtered = widget.apply_filter(
            candidates,
            _tag="python",
            _status="all",
            _min_conf=0.0,
            _max_conf=1.0,
        )
        assert len(filtered) == 1
        assert len(filtered) < len(candidates)

    asyncio.run(_run())


@pytest.mark.docker
def test_approve_promotes() -> None:
    async def _run() -> None:
        with (
            patch("cauterule.tui.review.execute_promotion") as mock_promo,
            TemporaryDirectory() as tmp,
        ):
            mock_promo.return_value = "R-002"
            store = StoreManager(base_dir=tmp)
            rule = _make_standing_rule(rule_id="R-001", trigger="deploy fails")
            store.add_rule(rule)
            screen = ReviewScreen(store=store)
            screen._candidates = [_make_candidate("deploy fails")]
            screen._current_index = 0

            def _fake_push(_target: Any, callback: Any = None) -> None:
                if callback is not None:
                    callback({"category": "logic_error", "tags": (), "comment": "ok"})

            async with CauterRuleApp().run_test() as pilot:
                pilot.app.push_screen(screen)
                await pilot.pause()
                cast(Any, screen).push_screen = MagicMock(side_effect=_fake_push)
                screen.approve_current()
                assert mock_promo.called

    asyncio.run(_run())


@pytest.mark.docker
def test_reject_advances() -> None:
    async def _run() -> None:
        screen = ReviewScreen()
        screen._candidates = [_make_candidate("trigger-a"), _make_candidate("trigger-b")]
        screen._current_index = 0
        cast(Any, screen)._populate_candidates = MagicMock()
        async with CauterRuleApp().run_test() as pilot:
            pilot.app.push_screen(screen)
            await pilot.pause()
            assert screen._current_index == 0
            screen.reject_current()
            assert screen._current_index == 0
            assert len(screen._candidates) == 1
            assert screen._candidates[0].when.trigger == "trigger-b"

    asyncio.run(_run())


@pytest.mark.docker
def test_keybindings() -> None:
    async def _run() -> None:
        app = CauterRuleApp()
        async with app.run_test():
            bindings = [b for b in app.BINDINGS if isinstance(b, Binding)]
            keys = {b.key: b.action for b in bindings}
            assert keys["q"] == "quit"
            assert keys["r"] == "push_review"
            assert keys["f"] == "toggle_filter"
            assert keys["a"] == "approve"
            assert keys["x"] == "reject"

    asyncio.run(_run())
