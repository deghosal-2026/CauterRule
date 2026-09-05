from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListView, RichLog

from cauterule.models.candidate import CandidateRule
from cauterule.tui.annotate import AnnotationScreen
from cauterule.tui.cards import EvidenceCard
from cauterule.tui.confidence import ConfidenceCard
from cauterule.tui.filter import FilterWidget


class ReviewScreen(Screen[Any]):
    DEFAULT_CSS = """
    ReviewScreen {
        align: center top;
    }
    ReviewScreen > Vertical {
        width: 80;
        height: 100%;
        margin: 1;
    }
    ReviewScreen #queue {
        height: 12;
        border: solid $primary;
    }
    ReviewScreen #detail {
        height: 8;
        border: solid $secondary;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._candidates: list[CandidateRule] = []
        self._current_index: int = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            FilterWidget(),
            Label("Candidate Queue", id="queue-label"),
            ListView(id="queue"),
            Label("Details", id="detail-label"),
            RichLog(id="detail", highlight=True),
            Horizontal(
                EvidenceCard(),
                ConfidenceCard(),
                id="cards",
            ),
        )
        yield Footer()

    def approve_current(self) -> None:
        if not self._candidates or self._current_index >= len(self._candidates):
            return
        self.push_screen(AnnotationScreen(self._candidates[self._current_index]))  # type: ignore[attr-defined]
        self._advance()

    def reject_current(self) -> None:
        if not self._candidates or self._current_index >= len(self._candidates):
            return
        self._candidates.pop(self._current_index)
        if self._candidates:
            self._current_index = min(self._current_index, len(self._candidates) - 1)
        else:
            self._current_index = 0

    def _advance(self) -> None:
        self._current_index += 1
        if self._current_index < len(self._candidates):
            self._show_candidate(self._candidates[self._current_index])
        else:
            detail = self.query_one("#detail", RichLog)
            detail.clear()
            detail.write("No more candidates.")

    def _show_candidate(self, candidate: CandidateRule) -> None:
        detail = self.query_one("#detail", RichLog)
        detail.clear()
        detail.write(f"When: {candidate.when.trigger}")
        detail.write(f"Do: {candidate.do.directive}")
        detail.write(f"Confidence: {candidate.confidence}")
        if candidate.reasoning:
            detail.write(f"Reasoning: {candidate.reasoning}")
