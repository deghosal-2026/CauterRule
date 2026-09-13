from __future__ import annotations

import asyncio
from tempfile import TemporaryDirectory

from textual.widgets import RichLog

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.store.manager import StoreManager
from cauterule.tui.app import CauterRuleApp
from cauterule.tui.review import ReviewScreen


def _make_candidate(trigger: str = "x fails") -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger),
        do=RuleDo(directive="do y"),
        confidence=0.85,
        reasoning="test reasoning",
        extraction_pass=1,
    )


def test_screen_instantiates() -> None:
    screen = ReviewScreen()
    assert screen is not None


def test_screen_with_store() -> None:
    with TemporaryDirectory() as tmp:
        store = StoreManager(base_dir=tmp)
        screen = ReviewScreen(store=store)
        assert screen._store is store


def test_empty_queue_shows_no_candidates() -> None:
    screen = ReviewScreen()
    assert len(screen._candidates) == 0


def test_mock_candidate_data() -> None:
    candidate = _make_candidate()
    assert candidate.when.trigger == "x fails"
    assert candidate.do.directive == "do y"
    assert candidate.confidence == 0.85


def test_compose_yields_widgets() -> None:
    screen = ReviewScreen()
    widgets = list(screen.compose())
    assert len(widgets) > 0


def test_reject_current_empty_queue() -> None:
    screen = ReviewScreen()
    screen.reject_current()
    assert screen._current_index == 0


def test_approve_current_empty_queue() -> None:
    screen = ReviewScreen()
    screen.approve_current()
    assert screen._current_index == 0


def test_reject_current_removes_candidate() -> None:
    async def _run() -> None:
        screen = ReviewScreen()
        async with CauterRuleApp().run_test() as pilot:
            pilot.app.push_screen(screen)
            await pilot.pause()
            screen._candidates = [_make_candidate("a"), _make_candidate("b")]
            screen._current_index = 0
            screen.reject_current()
            await pilot.pause()
            assert len(screen._candidates) == 1
            assert screen._current_index == 0

    asyncio.run(_run())


def test_reject_current_refreshes_detail_panel() -> None:
    async def _run() -> None:
        screen = ReviewScreen()
        async with CauterRuleApp().run_test() as pilot:
            pilot.app.push_screen(screen)
            await pilot.pause()
            screen._candidates = [_make_candidate("first"), _make_candidate("second")]
            screen._current_index = 0
            screen._show_candidate(screen._candidates[0])
            await pilot.pause()

            screen.reject_current()
            await pilot.pause()

            detail = screen.query_one("#detail", RichLog)
            shown = "".join(strip.text for strip in detail.lines)
            assert "second" in shown
            assert "first" not in shown
            assert screen._current_index == 0

    asyncio.run(_run())


def test_reject_last_candidate_clears_detail_panel() -> None:
    async def _run() -> None:
        screen = ReviewScreen()
        async with CauterRuleApp().run_test() as pilot:
            pilot.app.push_screen(screen)
            await pilot.pause()
            screen._candidates = [_make_candidate("only")]
            screen._current_index = 0
            screen._show_candidate(screen._candidates[0])
            await pilot.pause()

            screen.reject_current()
            await pilot.pause()

            detail = screen.query_one("#detail", RichLog)
            shown = "".join(strip.text for strip in detail.lines)
            assert "No more candidates." in shown
            assert len(screen._candidates) == 0

    asyncio.run(_run())


def test_populate_from_store_empty() -> None:
    with TemporaryDirectory() as tmp:
        store = StoreManager(base_dir=tmp)
        screen = ReviewScreen(store=store)
        screen._populate_candidates()
        assert len(screen._candidates) == 0


def test_populate_from_store_with_rules() -> None:
    with TemporaryDirectory() as tmp:
        store = StoreManager(base_dir=tmp)
        from cauterule.models.rule import Provenance, StandingRule

        rule = StandingRule(
            id="R-001",
            when=RuleWhen(trigger="deploy fails"),
            do=RuleDo(directive="check env"),
            confidence=0.9,
            provenance=Provenance(
                source_trajectory="T-1",
                extracted_by="test",
                extract_timestamp="2024-01-01T00:00:00Z",
                extraction_pass=1,
            ),
            status="active",
            promoted_at="2024-01-01T00:00:00Z",
        )
        store.add_rule(rule)
        screen = ReviewScreen(store=store)
        screen._populate_candidates()
        assert len(screen._candidates) == 1
        assert screen._candidates[0].when.trigger == "deploy fails"
