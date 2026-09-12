"""Hermetic coverage for cauterule.badge (#494)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from click.testing import CliRunner

from cauterule.badge import _text_width, badge_svg


def test_badge_svg_basic() -> None:
    svg = badge_svg(5)
    assert "<svg" in svg
    assert "5" in svg
    assert "rules" in svg
    assert 'fill="#555"' in svg
    assert 'fill="#4c1"' in svg


def test_badge_svg_negative_count_coerces_zero() -> None:
    svg = badge_svg(-1)
    assert ">0<" in svg or ">0</text>" in svg


def test_badge_svg_zero_count() -> None:
    svg = badge_svg(0)
    assert ">0<" in svg


def test_badge_svg_custom_label() -> None:
    svg = badge_svg(12, label="learned")
    assert "learned" in svg
    assert "12" in svg


def test_badge_svg_empty_label_defaults_to_rules() -> None:
    svg = badge_svg(3, label="")
    assert "rules" in svg


def test_badge_svg_large_count_width_scales() -> None:
    small = badge_svg(1)
    large = badge_svg(12345)
    # extract width attribute
    def _width(s: str) -> int:
        # width="{width}" first occurrence
        start = s.index('width="') + len('width="')
        end = s.index('"', start)
        return int(s[start:end])

    assert _width(large) > _width(small)


def test_text_width_minimum() -> None:
    assert _text_width("") == 10
    assert _text_width("a") == 10  # len*6=6 but min 10
    assert _text_width("ab") == 12
    assert _text_width("hello") == 30


def test_badge_svg_contains_geometry() -> None:
    svg = badge_svg(7, label="rules")
    # ensure left_w right_w computed via padding + text_width
    # label "rules" -> 30, +6=36, count "7" ->10+6=16 width=52
    assert 'width="52"' in svg


def test_cli_badge_svg_output(tmp_path: Path) -> None:
    from cauterule.cli.app import main
    from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
    from cauterule.store.manager import StoreManager

    store_dir = tmp_path / "rules"
    store = StoreManager(base_dir=str(store_dir))
    for i in range(2):
        store.add_rule(
            StandingRule(
                id=f"R-{i:03d}",
                when=RuleWhen(trigger="t"),
                do=RuleDo(directive="d"),
                confidence=0.9,
                provenance=Provenance(
                    source_trajectory="t", extracted_by="m", extract_timestamp="t", extraction_pass=1
                ),
                status="active",
                promoted_at="t",
            )
        )
    # add retired rule not counted
    store.add_rule(
        StandingRule(
            id="R-999",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.9,
            provenance=Provenance(
                source_trajectory="t", extracted_by="m", extract_timestamp="t", extraction_pass=1
            ),
            status="retired",
            promoted_at="t",
        )
    )
    env = os.environ.copy()
    env["CAUTERULE_STORE"] = str(store_dir)
    runner = CliRunner()
    # default prints svg
    result = runner.invoke(main, ["badge"])
    assert result.exit_code == 0, result.output
    assert "<svg" in result.output
    assert "2" in result.output


def test_cli_badge_as_svg_file(tmp_path: Path) -> None:
    from cauterule.cli.app import main

    store_dir = tmp_path / "rules"
    (store_dir).mkdir()
    out = tmp_path / "out.svg"
    runner = CliRunner()
    result = runner.invoke(main, ["badge", "--store", str(store_dir), "--svg", "--output", str(out)])
    assert result.exit_code == 0, result.output
    assert out.is_file()
    assert "<svg" in out.read_text(encoding="utf-8")


def test_cli_badge_as_json_and_url(tmp_path: Path) -> None:
    from cauterule.cli.app import main

    runner = CliRunner()
    # needs empty store
    result_json = runner.invoke(main, ["badge", "--store", str(tmp_path / "rules"), "--json"])
    assert result_json.exit_code == 0, result_json.output
    data = json.loads(result_json.output)
    assert data["schemaVersion"] == 1
    assert data["label"] == "Cauterule"

    result_url = runner.invoke(main, ["badge", "--url"])
    assert result_url.exit_code == 0
    assert "img.shields.io" in result_url.output


def test_cli_badge_json_color_green_when_count_positive(tmp_path: Path) -> None:
    from cauterule.cli.app import main
    from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
    from cauterule.store.manager import StoreManager

    store_dir = tmp_path / "rules"
    StoreManager(base_dir=str(store_dir)).add_rule(
        StandingRule(
            id="R-001",
            when=RuleWhen(trigger="t"),
            do=RuleDo(directive="d"),
            confidence=0.9,
            provenance=Provenance(
                source_trajectory="t", extracted_by="m", extract_timestamp="t", extraction_pass=1
            ),
            status="active",
            promoted_at="t",
        )
    )
    runner = CliRunner()
    result = runner.invoke(main, ["badge", "--store", str(store_dir), "--json"])
    assert result.exit_code == 0
    assert json.loads(result.output)["color"] == "green"
