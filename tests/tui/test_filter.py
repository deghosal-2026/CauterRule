from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cauterule.tui.filter import FilterWidget


@dataclass
class _MockCandidate:
    tags: tuple[str, ...] = ()
    confidence: float = 0.0
    status: str = "active"


def test_filter_instantiates() -> None:
    widget = FilterWidget()
    assert widget is not None


def test_filter_toggle() -> None:
    widget = FilterWidget()
    assert not widget._visible
    widget.toggle()
    assert widget._visible
    widget.toggle()
    assert not widget._visible


def test_filter_default_passes_all() -> None:
    widget = FilterWidget()
    candidates: list[Any] = [
        _MockCandidate(tags=("python",), confidence=0.8, status="active"),
        _MockCandidate(tags=("deploy",), confidence=0.5, status="retired"),
    ]
    result = widget.apply_filter(candidates, _tag="", _status="all", _min_conf=0.0, _max_conf=1.0)
    assert len(result) == 2


def test_filter_by_tag() -> None:
    widget = FilterWidget()
    candidates: list[Any] = [
        _MockCandidate(tags=("python",), confidence=0.8, status="active"),
        _MockCandidate(tags=("deploy",), confidence=0.5, status="active"),
    ]
    result = widget.apply_filter(candidates, _tag="python", _status="all", _min_conf=0.0, _max_conf=1.0)
    assert len(result) == 1


def test_filter_by_status() -> None:
    widget = FilterWidget()
    candidates: list[Any] = [
        _MockCandidate(tags=(), confidence=0.8, status="active"),
        _MockCandidate(tags=(), confidence=0.5, status="retired"),
    ]
    result = widget.apply_filter(candidates, _tag="", _status="active", _min_conf=0.0, _max_conf=1.0)
    assert len(result) == 1


def test_filter_by_confidence_range() -> None:
    widget = FilterWidget()
    candidates: list[Any] = [
        _MockCandidate(tags=(), confidence=0.8, status="active"),
        _MockCandidate(tags=(), confidence=0.5, status="active"),
    ]
    result = widget.apply_filter(candidates, _tag="", _status="all", _min_conf=0.6, _max_conf=1.0)
    assert len(result) == 1
