# ruff: noqa: SIM117
"""Hermetic coverage for cauterule.integrations.webhook (#494)."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cauterule.integrations.webhook import (
    WebhookNotifier,
    _validate_webhook_url,
    build_payload,
    deliver_payload,
    notify_promotion,
)

# ---------------------------------------------------------------------------
# _validate_webhook_url
# ---------------------------------------------------------------------------


def test_validate_rejects_urlparse_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.parse

    def boom(url: str) -> object:
        raise ValueError("bad parse")

    monkeypatch.setattr(urllib.parse, "urlparse", boom)
    # also need patch at webhook module level which imported urlparse directly
    import cauterule.integrations.webhook as wh

    monkeypatch.setattr(wh, "urlparse", boom)
    with pytest.raises(ValueError, match="invalid webhook URL"):
        _validate_webhook_url("http://example.com/hook")


def test_validate_rejects_ftp_scheme() -> None:
    with pytest.raises(ValueError, match="http"):
        _validate_webhook_url("ftp://example.com/hook")


def test_validate_rejects_empty_host() -> None:
    with pytest.raises(ValueError, match="host not allowed"):
        _validate_webhook_url("https://")


def test_validate_rejects_loopback_ip_literal() -> None:
    with pytest.raises(ValueError, match="host not allowed"):
        _validate_webhook_url("http://127.0.0.1/hook")


def test_validate_rejects_link_local_and_reserved(monkeypatch: pytest.MonkeyPatch) -> None:
    # 169.254.169.254 is link-local, 240.0.0.1 is reserved (240/4)
    with pytest.raises(ValueError, match="host not allowed"):
        _validate_webhook_url("http://169.254.169.254/latest")
    with pytest.raises(ValueError, match="host not allowed"):
        _validate_webhook_url("http://240.0.0.1/hook")


def test_validate_allows_unresolvable_host(monkeypatch: pytest.MonkeyPatch) -> None:
    # offline/air-gapped: host doesn't resolve -> allowed
    monkeypatch.setattr(socket, "gethostbyname", lambda h: (_ for _ in ()).throw(OSError("no dns")))
    # use a public-looking hostname (example.com would actually resolve, but we mock)
    _validate_webhook_url("https://example.com/hook")  # should not raise


def test_validate_rejects_resolved_loopback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "gethostbyname", lambda h: "127.0.0.1")
    with pytest.raises(ValueError, match="host not allowed"):
        _validate_webhook_url("https://example.com/hook")


def test_validate_allows_resolved_public_ip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "gethostbyname", lambda h: "8.8.8.8")
    _validate_webhook_url("https://example.com/hook")


def test_validate_rejects_multicast_and_unspecified() -> None:
    with pytest.raises(ValueError, match="host not allowed"):
        _validate_webhook_url("http://224.0.0.1/hook")
    with pytest.raises(ValueError, match="host not allowed"):
        _validate_webhook_url("http://0.0.0.0/hook")


# ---------------------------------------------------------------------------
# build_payload
# ---------------------------------------------------------------------------


def test_build_payload_all_providers() -> None:
    fields = {"rule_id": "R-1", "title": "t", "verdict": "promoted"}
    slack = build_payload("slack", fields)
    assert "text" in slack and "blocks" in slack
    assert "R-1" in slack["text"]

    discord = build_payload("discord", fields)
    assert "content" in discord

    github = build_payload("github", fields)
    assert github["event_type"] == "rule-promoted"
    assert github["client_payload"] == fields

    custom = build_payload("custom", fields)
    assert custom["event"] == "rule_promoted"


def test_build_payload_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError, match="webhook provider"):
        build_payload("unknown", {})


# ---------------------------------------------------------------------------
# deliver_payload - mocked urlopen + sleep
# ---------------------------------------------------------------------------

def _mock_response(status: int = 200) -> MagicMock:
    m = MagicMock()
    m.status = status
    m.__enter__ = lambda s: s
    m.__exit__ = lambda s, *a: False
    return m


def _valid_url(monkeypatch: pytest.MonkeyPatch) -> str:
    # make validation pass by forcing DNS unresolvable branch
    monkeypatch.setattr(socket, "gethostbyname", lambda h: (_ for _ in ()).throw(OSError("no dns")))
    return "https://example.com/hook"


def test_deliver_payload_success_first_try(monkeypatch: pytest.MonkeyPatch) -> None:
    url = _valid_url(monkeypatch)
    with patch("cauterule.integrations.webhook.urlopen", return_value=_mock_response(200)):
        with patch("cauterule.integrations.webhook.time.sleep") as mock_sleep:
            report = deliver_payload(url, {"a": 1}, max_attempts=3, backoff=(1, 5, 30))
    assert report == {"sent": True, "attempts": 1, "status": 200}
    mock_sleep.assert_not_called()


def test_deliver_payload_non_retryable_status_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    url = _valid_url(monkeypatch)
    with patch("cauterule.integrations.webhook.urlopen", return_value=_mock_response(400)):
        report = deliver_payload(url, {}, max_attempts=3)
    assert report["sent"] is False
    assert report["status"] == 400
    assert report["attempts"] == 1


def test_deliver_payload_retryable_then_success(monkeypatch: pytest.MonkeyPatch) -> None:
    url = _valid_url(monkeypatch)
    seq = [_mock_response(503), _mock_response(200)]
    with patch("cauterule.integrations.webhook.urlopen", side_effect=seq):
        with patch("cauterule.integrations.webhook.time.sleep") as mock_sleep:
            report = deliver_payload(url, {}, max_attempts=3, backoff=(1, 5, 30))
    assert report["sent"] is True
    assert report["attempts"] == 2
    mock_sleep.assert_called_once_with(1)


def test_deliver_payload_backoff_index_clamped(monkeypatch: pytest.MonkeyPatch) -> None:
    url = _valid_url(monkeypatch)
    # 3 failing retryable attempts, backoff list length 3 -> capped at last entry
    seq = [_mock_response(500), _mock_response(500), _mock_response(500)]
    with patch("cauterule.integrations.webhook.urlopen", side_effect=seq):
        with patch("cauterule.integrations.webhook.time.sleep") as mock_sleep:
            report = deliver_payload(url, {}, max_attempts=3, backoff=(1, 5, 30))
    assert report["sent"] is False
    assert mock_sleep.call_count == 2
    assert mock_sleep.call_args_list[0].args[0] == 1
    assert mock_sleep.call_args_list[1].args[0] == 5


def test_deliver_payload_httperror_retryable_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    url = _valid_url(monkeypatch)
    err_retry = HTTPError(url, 429, "retry", None, None)  # type: ignore[arg-type]
    with patch("cauterule.integrations.webhook.urlopen", side_effect=[err_retry, _mock_response(200)]):
        with patch("cauterule.integrations.webhook.time.sleep"):
            report = deliver_payload(url, {}, max_attempts=2)
    assert report["sent"] is True
    assert report["attempts"] == 2


def test_deliver_payload_httperror_non_retryable_immediate_false(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    url = _valid_url(monkeypatch)
    err = HTTPError(url, 400, "bad", None, None)  # type: ignore[arg-type]
    with patch("cauterule.integrations.webhook.urlopen", side_effect=err):
        report = deliver_payload(url, {}, max_attempts=3)
    assert report["sent"] is False
    assert report["status"] == 400
    assert report["attempts"] == 1


def test_deliver_payload_generic_exception_retries_then_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    url = _valid_url(monkeypatch)
    with patch("cauterule.integrations.webhook.urlopen", side_effect=ConnectionError("down")):
        with patch("cauterule.integrations.webhook.time.sleep"):
            report = deliver_payload(url, {}, max_attempts=2)
    assert report["sent"] is False
    assert report["attempts"] == 2


def test_deliver_payload_resp_without_status_defaults_200(monkeypatch: pytest.MonkeyPatch) -> None:
    url = _valid_url(monkeypatch)
    m = MagicMock()
    # no .status attribute -> getattr defaults to 200
    del m.status
    m.__enter__ = lambda s: s
    m.__exit__ = lambda s, *a: False
    with patch("cauterule.integrations.webhook.urlopen", return_value=m):
        report = deliver_payload(url, {}, max_attempts=1)
    assert report["sent"] is True
    assert report["status"] == 200


# ---------------------------------------------------------------------------
# WebhookNotifier.deliver / notify_promotion
# ---------------------------------------------------------------------------


def test_notifier_deliver_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "gethostbyname", lambda h: (_ for _ in ()).throw(OSError("no dns")))
    with patch("cauterule.integrations.webhook.deliver_payload", return_value={"sent": True, "attempts": 1, "status": 200}) as mock:
        n = WebhookNotifier("https://example.com/hook")
        assert n.deliver({"x": 1}) is True
        mock.assert_called_once()


def test_notifier_notify_promotion_builds_timestamp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "gethostbyname", lambda h: (_ for _ in ()).throw(OSError("no dns")))
    with patch("cauterule.integrations.webhook.deliver_payload", return_value={"sent": True, "attempts": 1, "status": 200}) as mock:
        n = WebhookNotifier("https://example.com/hook")
        assert n.notify_promotion("R-1", "title") is True
        payload = mock.call_args[0][1]
        assert payload["event"] == "rule_promoted"
        assert payload["promotion"]["rule_id"] == "R-1"
        assert "timestamp" in payload["promotion"]

    # explicit timestamp passthrough
    with patch("cauterule.integrations.webhook.deliver_payload", return_value={"sent": True, "attempts": 1, "status": 200}) as mock:
        n.notify_promotion("R-1", "title", timestamp="2024-01-01T00:00:00Z")
        assert mock.call_args[0][1]["promotion"]["timestamp"] == "2024-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# top-level notify_promotion(store_dir)
# ---------------------------------------------------------------------------


def test_notify_promotion_config_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("cauterule.config.load_config", lambda: (_ for _ in ()).throw(OSError("no toml")))
    report = notify_promotion({"id": "R-1"}, store_dir="rules")
    assert report["sent"] is False
    assert report["reason"] == "config unavailable"


def test_notify_promotion_disabled(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class Cfg:
        webhook = MagicMock(enabled=False)

    monkeypatch.setattr("cauterule.config.load_config", lambda: Cfg())
    report = notify_promotion({"id": "R-1"}, store_dir=str(tmp_path))
    assert report["sent"] is False
    assert report["reason"] == "webhook disabled"


def test_notify_promotion_enabled_no_url_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    class Cfg:
        webhook = MagicMock(enabled=True, url="", provider="slack", max_attempts=1, backoff=(1,), redact=False)

    monkeypatch.setattr("cauterule.config.load_config", lambda: Cfg())
    with pytest.raises(ValueError, match="no url"):
        notify_promotion({"id": "R-1"}, store_dir="rules")


def test_notify_promotion_success_and_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "gethostbyname", lambda h: (_ for _ in ()).throw(OSError("no dns")))
    wh_cfg = MagicMock(
        enabled=True,
        url="https://example.com/hook",
        provider="slack",
        max_attempts=1,
        backoff=(1,),
        redact=False,
    )
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(webhook=wh_cfg))

    with patch("cauterule.integrations.webhook.deliver_payload", return_value={"sent": True, "attempts": 1, "status": 200}) as mock_deliver:
        with patch("cauterule.integrations.webhook.build_payload", wraps=build_payload) as mock_build:
            report = notify_promotion(
                {"id": "R-123", "title": "t", "trigger": "trig", "verdict": "promoted"},
                store_dir=str(tmp_path),
            )
    assert report["sent"] is True
    mock_deliver.assert_called_once()
    mock_build.assert_called_once()
    log_path = tmp_path / "webhook-deliveries.jsonl"
    assert log_path.is_file()
    content = log_path.read_text(encoding="utf-8")
    assert "R-123" in content
    assert json.loads(content)["sent"] is True


def test_notify_promotion_redaction_applied(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "gethostbyname", lambda h: (_ for _ in ()).throw(OSError("no dns")))
    wh_cfg = MagicMock(
        enabled=True,
        url="https://example.com/hook",
        provider="custom",
        max_attempts=1,
        backoff=(1,),
        redact=True,
    )
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(webhook=wh_cfg))
    # inject secret-like title so redact_export will replace
    with patch("cauterule.integrations.webhook.redact_export", return_value="[REDACTED]") as mock_redact:
        with patch("cauterule.integrations.webhook.deliver_payload", return_value={"sent": True, "attempts": 1, "status": 200}):
            notify_promotion({"id": "R-1", "title": "ghp_123456789012345678901234567890123456"}, store_dir=str(tmp_path))
    mock_redact.assert_called()


def test_notify_promotion_url_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(socket, "gethostbyname", lambda h: (_ for _ in ()).throw(OSError("no dns")))
    wh_cfg = MagicMock(
        enabled=True,
        url="https://example.com/hook",
        provider="custom",
        max_attempts=1,
        backoff=(1,),
        redact=False,
    )
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(webhook=wh_cfg))
    with patch("cauterule.integrations.webhook.deliver_payload", return_value={"sent": True, "attempts": 1, "status": 200}) as mock:
        notify_promotion({"id": "R-1"}, store_dir=str(tmp_path), url_override="https://example.com/other")
        assert mock.call_args[0][0] == "https://example.com/other"


def test_notify_promotion_log_oserror_handled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    wh_cfg = MagicMock(
        enabled=True,
        url="https://example.com/hook",
        provider="custom",
        max_attempts=1,
        backoff=(1,),
        redact=False,
    )
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(webhook=wh_cfg))
    monkeypatch.setattr(socket, "gethostbyname", lambda h: (_ for _ in ()).throw(OSError("no dns")))
    with patch("cauterule.integrations.webhook.deliver_payload", return_value={"sent": False, "attempts": 1, "status": 500}):
        with patch.object(Path, "open", side_effect=OSError("disk full")):
            report = notify_promotion({"id": "R-1"}, store_dir=str(tmp_path))
    assert report["sent"] is False


def test_webhook_cli_test_success(monkeypatch: pytest.MonkeyPatch) -> None:
    from click.testing import CliRunner

    from cauterule.cli.app import main

    monkeypatch.setattr(socket, "gethostbyname", lambda h: (_ for _ in ()).throw(OSError("no dns")))
    wh_cfg = MagicMock(
        enabled=True, url="https://example.com/hook", provider="slack", max_attempts=1, backoff=(1,), redact=False
    )
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(webhook=wh_cfg))
    with patch("cauterule.integrations.webhook.deliver_payload", return_value={"sent": True, "attempts": 1, "status": 200}):
        runner = CliRunner()
        result = runner.invoke(main, ["webhook", "test"])
    assert result.exit_code == 0, result.output
    assert "sent=True" in result.output


def test_webhook_cli_test_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    from click.testing import CliRunner

    from cauterule.cli.app import main

    monkeypatch.setattr(socket, "gethostbyname", lambda h: (_ for _ in ()).throw(OSError("no dns")))
    wh_cfg = MagicMock(
        enabled=True, url="https://example.com/hook", provider="slack", max_attempts=1, backoff=(1,), redact=False
    )
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(webhook=wh_cfg))
    with patch("cauterule.integrations.webhook.deliver_payload", return_value={"sent": False, "attempts": 1, "status": 500}):
        runner = CliRunner()
        result = runner.invoke(main, ["webhook", "test"])
    assert result.exit_code != 0
    assert "delivery failed" in result.output


def test_webhook_cli_test_no_url_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    from click.testing import CliRunner

    from cauterule.cli.app import main

    wh_cfg = MagicMock(enabled=True, url="", provider="slack", max_attempts=1, backoff=(1,), redact=False)
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(webhook=wh_cfg))
    runner = CliRunner()
    result = runner.invoke(main, ["webhook", "test"])
    assert result.exit_code != 0
    assert "no webhook url" in result.output
