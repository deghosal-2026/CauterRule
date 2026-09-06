from __future__ import annotations

from textual.binding import Binding

from cauterule.tui.app import CauterRuleApp


def test_app_instantiates() -> None:
    app = CauterRuleApp()
    assert app.title is not None


def test_app_title_default() -> None:
    app = CauterRuleApp()
    assert app.title == "CauterRuleApp"


def test_keybindings_registered() -> None:
    app = CauterRuleApp()
    bindings = [b for b in app.BINDINGS if isinstance(b, Binding)]
    keys = {b.key for b in bindings}
    assert "q" in keys
    assert "r" in keys
    assert "f" in keys
    assert "a" in keys
    assert "x" in keys


def test_binding_actions() -> None:
    app = CauterRuleApp()
    bindings = [b for b in app.BINDINGS if isinstance(b, Binding)]
    binding_map: dict[str, str] = {b.key: b.action for b in bindings}
    assert binding_map["q"] == "quit"
    assert binding_map["r"] == "push_review"
    assert binding_map["f"] == "toggle_filter"
    assert binding_map["a"] == "approve"
    assert binding_map["x"] == "reject"


def test_screens_registered() -> None:
    app = CauterRuleApp()
    assert "review" in app.SCREENS
    assert "batch" in app.SCREENS
    assert "annotate" in app.SCREENS
