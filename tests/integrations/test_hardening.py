"""Webhook + OTel hardening tests (#508)."""

from __future__ import annotations

import pytest

from cauterule.integrations.otel import _coerce_attribute
from cauterule.integrations.webhook import WebhookNotifier


@pytest.mark.parametrize(
    "url",
    [
        "http://169.254.169.254/latest/meta-data/",
        "http://127.0.0.1/hook",
        "http://0.0.0.0/hook",
        "http://localhost/hook",
        "http://localhost.localdomain/hook",
        "http://[::1]/hook",
        "ftp://example.com/hook",
        "file:///etc/passwd",
        "not-a-url",
        "",
    ],
)
def test_webhook_rejects_unsafe_urls(url: str) -> None:
    with pytest.raises(ValueError, match="webhook URL"):
        WebhookNotifier(url)


def test_webhook_accepts_public_https() -> None:
    assert WebhookNotifier("https://example.com/hook").url == "https://example.com/hook"


def test_webhook_failure_log_redacts_url(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    import urllib.request

    def _boom(*args: object, **kwargs: object) -> object:
        raise ConnectionError("down")

    monkeypatch.setattr(urllib.request, "urlopen", _boom)
    notifier = WebhookNotifier("https://example.com/hook?token=secret123")
    with caplog.at_level("ERROR", logger="cauterule.integrations.webhook"):
        assert notifier.notify_promotion("R-001", "title") is False
    assert "secret123" not in caplog.text
    assert "example.com" in caplog.text


def test_otel_coerce_attribute_passthrough() -> None:
    assert _coerce_attribute("x") == "x"
    assert _coerce_attribute(True) is True
    assert _coerce_attribute(3) == 3
    assert _coerce_attribute(2.5) == 2.5
    assert _coerce_attribute(["a", "b"]) == ["a", "b"]


def test_otel_coerce_attribute_never_raises() -> None:
    assert _coerce_attribute({"nested": "dict"}) == "{'nested': 'dict'}"
    assert _coerce_attribute(None) == "None"
    assert _coerce_attribute(["a", 1]) == "['a', 1]"
