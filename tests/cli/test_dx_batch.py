"""Tests for M5 DX batch: observe summary, badge, webhook, taxonomy."""

from __future__ import annotations

import http.server
import json
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any, ClassVar

import pytest
from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule
from cauterule.serialization.rule_yaml import dump_rule_to_file
from cauterule.taxonomy import (
    backfill,
    classify_with_confidence,
    ensure_taxonomy,
    validate_taxonomy,
)


def _seed(store: Path, taxonomy: str | None = "git/push") -> None:
    store.mkdir(parents=True, exist_ok=True)
    rule = StandingRule(
        id="R-001",
        when=RuleWhen(trigger="git push rejected non-fast-forward"),
        do=RuleDo(directive="run git pull --rebase"),
        confidence=0.9,
        provenance=Provenance(
            source_trajectory="t", extracted_by="m", extract_timestamp="t", extraction_pass=1
        ),
        status="active",
        promoted_at="2026-09-01T00:00:00Z",
        taxonomy=taxonomy,
        prevented_count=2,
        broke_count=0,
        neutral_count=1,
    )
    dump_rule_to_file(rule, store / "R-001.yaml")


class TestObserve:
    def test_summary(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        store = tmp_path / "store"
        _seed(store)
        monkeypatch.setenv("CAUTERULE_STORE", str(store))
        runner = CliRunner()
        result = runner.invoke(main, ["observe", "--store-dir", str(store)])
        assert result.exit_code == 0, result.output
        assert "Rules learned" in result.output
        assert "prevented=2" in result.output

    def test_summary_json(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        runner = CliRunner()
        result = runner.invoke(main, ["observe", "--store-dir", str(store), "--json"])
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["rules_learned"] == 1
        assert payload["verdicts"]["prevented"] == 2

    def test_subcommands_delegate(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        runner = CliRunner()
        for sub in ("journal", "metrics", "frontier", "gaps"):
            result = runner.invoke(main, ["observe", sub, "--store-dir", str(store)])
            assert result.exit_code == 0, f"{sub}: {result.output}"

    def test_top_level_aliases_still_work(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        runner = CliRunner()
        result = runner.invoke(main, ["journal", "--store-dir", str(store)])
        assert result.exit_code == 0


class TestBadge:
    def test_svg(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        runner = CliRunner()
        result = runner.invoke(main, ["badge", "--store", str(store)])
        assert result.exit_code == 0
        assert "<svg" in result.output

    def test_json_schema(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        runner = CliRunner()
        result = runner.invoke(main, ["badge", "--store", str(store), "--json"])
        payload = json.loads(result.output)
        assert payload["schemaVersion"] == 1
        assert payload["message"] == "1 rules learned"
        assert payload["color"] == "green"

    def test_url(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        runner = CliRunner()
        result = runner.invoke(main, ["badge", "--store", str(store), "--url"])
        assert "img.shields.io/endpoint" in result.output

    def test_count_matches_active(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store)
        runner = CliRunner()
        result = runner.invoke(
            main, ["badge", "--store", str(store), "--svg", "--output", str(tmp_path / "b.svg")]
        )
        assert result.exit_code == 0
        assert (tmp_path / "b.svg").is_file()


class _Handler(http.server.BaseHTTPRequestHandler):
    received: ClassVar[list[dict[str, Any]]] = []
    status: ClassVar[int] = 200

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        _Handler.received.append(json.loads(body))
        self.send_response(_Handler.status)
        self.end_headers()

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture
def webhook_server(monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    _Handler.received = []
    _Handler.status = 200
    server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr("time.sleep", lambda *_: None)
    yield f"http://127.0.0.1:{server.server_port}/hook"
    server.shutdown()


class TestWebhook:
    def test_promotion_triggers(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, webhook_server: str
    ) -> None:
        import cauterule.integrations.webhook as wh

        monkeypatch.setattr(wh, "_validate_webhook_url", lambda url: None)
        report = wh.deliver_payload(
            webhook_server,
            wh.build_payload("slack", {"rule_id": "R-1", "title": "t"}),
        )
        assert report["sent"] is True
        assert _Handler.received[0]["text"].startswith("Cauterule promoted R-1")

    def test_retry_then_success(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, webhook_server: str
    ) -> None:
        import cauterule.integrations.webhook as wh

        monkeypatch.setattr(wh, "_validate_webhook_url", lambda url: None)
        _Handler.status = 500
        report = wh.deliver_payload(webhook_server, {"x": 1}, max_attempts=2, backoff=(0,))
        assert report == {"sent": False, "attempts": 2, "status": 500}

    def test_no_retry_on_4xx(self, monkeypatch: pytest.MonkeyPatch, webhook_server: str) -> None:
        import cauterule.integrations.webhook as wh

        monkeypatch.setattr(wh, "_validate_webhook_url", lambda url: None)
        _Handler.status = 400
        report = wh.deliver_payload(webhook_server, {"x": 1}, max_attempts=3, backoff=(0,))
        assert report["attempts"] == 1 and report["sent"] is False

    def test_providers_format(self) -> None:
        from cauterule.integrations.webhook import build_payload

        assert "text" in build_payload("slack", {"rule_id": "R-1"})
        assert "content" in build_payload("discord", {"rule_id": "R-1"})
        assert "event_type" in build_payload("github", {"rule_id": "R-1"})

    def test_disabled_by_default(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from cauterule.integrations.webhook import notify_promotion

        monkeypatch.chdir(tmp_path)
        assert notify_promotion({"id": "R-1"}) == {"sent": False, "reason": "webhook disabled"}


class TestTaxonomy:
    def test_classify(self) -> None:
        label, conf = classify_with_confidence("git push rejected non-fast-forward")
        assert (label, conf >= 0.5) == ("git/push", True)

    def test_unknown_rejected_without_explicit(self) -> None:
        with pytest.raises(ValueError, match="--taxonomy"):
            ensure_taxonomy("something utterly unrelated xyzzy")

    def test_explicit_other_allowed(self) -> None:
        assert ensure_taxonomy("whatever", explicit="other") == ("other", False)

    def test_unknown_value_rejected(self) -> None:
        with pytest.raises(ValueError, match="unknown taxonomy"):
            validate_taxonomy("nonsense/category")

    def test_list_filter(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        store = tmp_path / "rules"
        _seed(store)
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["list", "--taxonomy", "git/push"])
        assert result.exit_code == 0
        assert "R-001" in result.output
        result = runner.invoke(main, ["list", "--taxonomy", "python/import"])
        assert "No rules found" in result.output

    def test_backfill(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store, taxonomy=None)
        report = backfill(str(store), dry_run=True)
        assert report["updated"] == ["R-001->git/push"]
        assert report["dry_run"] is True
        report = backfill(str(store))
        assert report["updated"] == ["R-001->git/push"]

    def test_cli_backfill(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        _seed(store, taxonomy=None)
        runner = CliRunner()
        result = runner.invoke(main, ["taxonomy", "backfill", "--store", str(store), "--dry-run"])
        assert result.exit_code == 0, result.output
        assert "R-001->git/push" in result.output
