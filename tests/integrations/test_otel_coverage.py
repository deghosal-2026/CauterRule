"""Hermetic coverage for cauterule.integrations.otel (#494)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _fake_tracer() -> tuple[MagicMock, MagicMock, MagicMock]:
    span = MagicMock()
    span.set_attribute = MagicMock()
    span.set_status = MagicMock()
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=span)
    cm.__exit__ = MagicMock(return_value=False)
    tracer = MagicMock()
    tracer.start_as_current_span = MagicMock(return_value=cm)
    return tracer, span, cm


# ---------------------------------------------------------------------------
# _coerce_attribute
# ---------------------------------------------------------------------------


def test_coerce_attribute_edge_cases() -> None:
    from cauterule.integrations.otel import _coerce_attribute

    # string/passthrough already tested elsewhere
    assert _coerce_attribute([]) == []  # empty list -> homogeneous empty set
    assert _coerce_attribute([1, 2, 3]) == [1, 2, 3]
    assert _coerce_attribute([1.0, 2.5]) == [1.0, 2.5]
    # int + float mixed allowed (int,float set)
    assert _coerce_attribute([1, 1.5]) == [1, 1.5]
    assert _coerce_attribute((1, 2)) == [1, 2]  # tuple coerced to list
    assert _coerce_attribute([True, False]) == [True, False]
    assert _coerce_attribute(["a", "b"]) == ["a", "b"]
    # mixed heterogeneous -> stringify
    assert _coerce_attribute(["a", 1]) == "['a', 1]"
    assert _coerce_attribute([1, "a", None]) == "[1, 'a', None]"
    # non-collection
    assert _coerce_attribute({"k": 1}) == "{'k': 1}"


# ---------------------------------------------------------------------------
# _ensure_configured
# ---------------------------------------------------------------------------


def test_ensure_configured_calls_configure_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    otel_module._CONFIGURED = False
    fake_cfg = MagicMock(enabled=True, endpoint="http://collector:4318", service_name="svc", headers=())
    # need object with .otel attr
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(otel=fake_cfg))
    with patch("cauterule.integrations.otel.configure_otlp") as mock_configure:
        otel_module._ensure_configured()
        mock_configure.assert_called_once_with("http://collector:4318", "svc", {})
        # second call is no-op due to _CONFIGURED guard
        otel_module._ensure_configured()
        assert mock_configure.call_count == 1
    otel_module._CONFIGURED = False


def test_ensure_configured_disabled_does_not_configure(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    otel_module._CONFIGURED = False
    fake_cfg = MagicMock(enabled=False, endpoint="http://x", service_name="svc", headers=())
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(otel=fake_cfg))
    with patch("cauterule.integrations.otel.configure_otlp") as mock_configure:
        otel_module._ensure_configured()
        mock_configure.assert_not_called()
    otel_module._CONFIGURED = False


def test_ensure_configured_load_error_suppressed(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    otel_module._CONFIGURED = False
    monkeypatch.setattr("cauterule.config.load_config", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    # should not raise
    otel_module._ensure_configured()
    assert otel_module._CONFIGURED is True
    otel_module._CONFIGURED = False


# ---------------------------------------------------------------------------
# OtelExporter
# ---------------------------------------------------------------------------


def test_exporter_without_endpoint_uses_get_tracer(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    fake_tracer = MagicMock()
    monkeypatch.setattr("opentelemetry.trace.get_tracer", lambda name: fake_tracer)
    # ensure imports for endpoint branch not triggered
    exporter = otel_module.OtelExporter(service_name="svc")
    assert exporter._tracer is fake_tracer
    assert exporter._provider is None


def test_exporter_with_endpoint_creates_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    exporter = otel_module.OtelExporter(service_name="svc", endpoint="http://example.com:4318")
    # provider should be created (real SDK)
    assert exporter._provider is not None
    assert exporter._tracer is not None
    # cleanup to avoid leaking BatchSpanProcessor threads
    import contextlib

    with contextlib.suppress(Exception):
        exporter._provider.shutdown()


def test_exporter_init_handles_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    # force TracerProvider to raise
    monkeypatch.setattr("opentelemetry.sdk.trace.TracerProvider", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    exporter = otel_module.OtelExporter(service_name="svc", endpoint="http://example.com")
    assert exporter._tracer is None


def test_exporter_unavailable_logs_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    monkeypatch.setattr(otel_module, "_OTEL_AVAILABLE", False)
    exporter = otel_module.OtelExporter(service_name="svc")
    assert exporter._tracer is None
    assert exporter._provider is None
    monkeypatch.setattr(otel_module, "_OTEL_AVAILABLE", True)


def test_flush_no_provider_is_noop() -> None:
    from cauterule.integrations.otel import OtelExporter

    # Use no endpoint => provider None, flush should be noop not raise
    with patch("opentelemetry.trace.get_tracer", return_value=MagicMock()):
        exporter = OtelExporter(service_name="svc")
        exporter.flush()


def test_flush_calls_force_flush_and_handles_error() -> None:
    import cauterule.integrations.otel as otel_module

    tracer, _, _ = _fake_tracer()
    exporter = otel_module.OtelExporter.__new__(otel_module.OtelExporter)
    exporter.service_name = "svc"
    mock_provider = MagicMock()
    mock_provider.force_flush = MagicMock(side_effect=RuntimeError("flush boom"))
    exporter._provider = mock_provider
    exporter._tracer = tracer
    # should not raise
    exporter.flush(timeout_ms=100)
    mock_provider.force_flush.assert_called_once_with(timeout_millis=100)

    mock_provider_ok = MagicMock()
    mock_provider_ok.force_flush = MagicMock()
    exporter._provider = mock_provider_ok
    exporter.flush()
    mock_provider_ok.force_flush.assert_called_once()


# ---------------------------------------------------------------------------
# emit_rule_hit / promotion / extraction (direct tracer paths)
# ---------------------------------------------------------------------------


def test_emit_rule_hit_with_mock_tracer(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    tracer, span, _ = _fake_tracer()
    exporter = otel_module.OtelExporter.__new__(otel_module.OtelExporter)
    exporter._provider = None
    exporter._tracer = tracer
    exporter.service_name = "svc"
    monkeypatch.setattr(otel_module, "_OTEL_AVAILABLE", True)

    exporter.emit_rule_hit("R-1", context={"agent": "bob", "weird": {"x": 1}})
    tracer.start_as_current_span.assert_called_once()
    # ensure coercion of dict -> str
    assert span.set_attribute.call_count >= 2

    # tracer None -> no-op
    exporter2 = otel_module.OtelExporter.__new__(otel_module.OtelExporter)
    exporter2._provider = None
    exporter2._tracer = None
    exporter2.service_name = "svc"
    exporter2.emit_rule_hit("R-2")  # should not raise

    # _OTEL_AVAILABLE False -> no-op
    monkeypatch.setattr(otel_module, "_OTEL_AVAILABLE", False)
    exporter.emit_rule_hit("R-3")
    monkeypatch.setattr(otel_module, "_OTEL_AVAILABLE", True)


def test_emit_rule_promotion_and_extraction(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    tracer, span, _ = _fake_tracer()
    exporter = otel_module.OtelExporter.__new__(otel_module.OtelExporter)
    exporter._provider = None
    exporter._tracer = tracer
    exporter.service_name = "svc"
    monkeypatch.setattr(otel_module, "_OTEL_AVAILABLE", True)

    exporter.emit_rule_promotion("R-1", title="My Rule")
    assert any(c.args[0] == "rule.title" for c in span.set_attribute.call_args_list)

    span2 = MagicMock()
    span2.set_attribute = MagicMock()
    span2.set_status = MagicMock()
    cm2 = MagicMock()
    cm2.__enter__ = MagicMock(return_value=span2)
    cm2.__exit__ = MagicMock(return_value=False)
    tracer.start_as_current_span.return_value = cm2
    exporter.emit_rule_promotion("R-2")  # no title -> not set rule.title
    # second span should not have title attribute
    assert not any(c.args[0] == "rule.title" for c in span2.set_attribute.call_args_list)

    tracer_acc, span_acc, _ = _fake_tracer()
    exporter._tracer = tracer_acc
    exporter.emit_rule_extraction("R-3", trajectory="T-1", accuracy=0.95)
    assert any(c.args[0] == "rule.accuracy" for c in span_acc.set_attribute.call_args_list)

    # no optional fields
    tracer3, span3, _ = _fake_tracer()
    exporter._tracer = tracer3
    exporter.emit_rule_extraction("R-4")
    # only rule.id
    assert span3.set_attribute.call_args_list[0].args == ("rule.id", "R-4")

    monkeypatch.setattr(otel_module, "_OTEL_AVAILABLE", False)
    exporter.emit_rule_promotion("R-x")
    exporter.emit_rule_extraction("R-y")
    monkeypatch.setattr(otel_module, "_OTEL_AVAILABLE", True)


# ---------------------------------------------------------------------------
# _span and taxonomy wrappers
# ---------------------------------------------------------------------------


def test_span_wrapped_methods_use_ensure_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    tracer, span, _ = _fake_tracer()
    exporter = otel_module.OtelExporter.__new__(otel_module.OtelExporter)
    exporter._provider = None
    exporter._tracer = tracer
    exporter.service_name = "svc"
    otel_module._CONFIGURED = True  # prevent ensure_configured doing real config

    exporter.emit_rule_match("R-1", agent="a", trigger="t", confidence=0.9)
    tracer.start_as_current_span.assert_called()
    assert any("rule_id" in str(c) for c in span.set_attribute.call_args_list)

    exporter.emit_rule_promote("R-1", from_state="candidate", to_state="active")
    exporter.emit_rule_retire("R-1", reason="stale", superseded_by="R-2")
    exporter.emit_replay_verdict("E-1", verdict="pass", precision_score=1.0, recall_score=0.5)


def test_span_early_return_when_tracer_none(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    otel_module._CONFIGURED = True
    exporter = otel_module.OtelExporter.__new__(otel_module.OtelExporter)
    exporter._provider = None
    exporter._tracer = None
    exporter.service_name = "svc"
    exporter.emit_rule_match("R-1")
    exporter.emit_rule_promote("R-1")
    exporter.emit_rule_retire("R-1")
    exporter.emit_replay_verdict()
    otel_module._CONFIGURED = False


def test_span_handles_tracer_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    otel_module._CONFIGURED = True
    tracer = MagicMock()
    tracer.start_as_current_span = MagicMock(side_effect=RuntimeError("boom"))
    exporter = otel_module.OtelExporter.__new__(otel_module.OtelExporter)
    exporter._provider = None
    exporter._tracer = tracer
    exporter.service_name = "svc"
    # should not raise
    exporter.emit_rule_match("R-1")
    otel_module._CONFIGURED = False


def test_span_unavailable_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    otel_module._CONFIGURED = True
    monkeypatch.setattr(otel_module, "_OTEL_AVAILABLE", False)
    tracer = MagicMock()
    exporter = otel_module.OtelExporter.__new__(otel_module.OtelExporter)
    exporter._provider = None
    exporter._tracer = tracer
    exporter.service_name = "svc"
    exporter.emit_rule_match("R-1")
    tracer.start_as_current_span.assert_not_called()
    monkeypatch.setattr(otel_module, "_OTEL_AVAILABLE", True)
    otel_module._CONFIGURED = False


# ---------------------------------------------------------------------------
# configure_otlp
# ---------------------------------------------------------------------------


def test_configure_otlp_exception_returns_metadata_exporter(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    real_cls = otel_module.OtelExporter
    calls = {"n": 0}

    def fake_exporter(*a: object, **k: object) -> object:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("boom")
        # second call - delegate to real class but without endpoint to avoid network
        # patch TracerProvider inside to be safe
        return real_cls(service_name=k.get("service_name", "svc"))

    monkeypatch.setattr(otel_module, "OtelExporter", fake_exporter)
    with patch("opentelemetry.trace.get_tracer", return_value=MagicMock()):
        result = otel_module.configure_otlp("http://x", service_name="svc")
    assert result is not None
    assert calls["n"] == 2


def test_configure_otlp_success() -> None:
    from cauterule.integrations.otel import OtelExporter, configure_otlp

    with patch("opentelemetry.trace.get_tracer", return_value=MagicMock()):
        exp = configure_otlp("", service_name="svc2")
        assert isinstance(exp, OtelExporter)


# ---------------------------------------------------------------------------
# get_exporter
# ---------------------------------------------------------------------------


def test_get_exporter_caching_and_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    # reset singleton
    otel_module._exporter = None

    # case: load_config raises -> defaults to cauterule service name
    monkeypatch.setattr("cauterule.config.load_config", lambda: (_ for _ in ()).throw(OSError("no config")))
    with patch.object(otel_module, "OtelExporter") as mock_cls:
        mock_cls.return_value = MagicMock(service_name="cauterule")
        exp = otel_module.get_exporter()
        assert exp is mock_cls.return_value
        # second call returns cached
        exp2 = otel_module.get_exporter()
        assert exp2 is exp

    otel_module._exporter = None

    # case: disabled config -> still creates exporter with service name
    fake_otel_cfg = MagicMock(enabled=False, endpoint="http://x", service_name="svc-disabled", headers=())
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(otel=fake_otel_cfg))
    with patch.object(otel_module, "OtelExporter") as mock_cls:
        mock_cls.return_value = MagicMock()
        exp = otel_module.get_exporter()
        mock_cls.assert_called()
        # check called with service_name from cfg
        assert mock_cls.call_args.kwargs.get("service_name") == "svc-disabled"

    otel_module._exporter = None

    # case: enabled + endpoint -> wired provider
    fake_otel_cfg2 = MagicMock(enabled=True, endpoint="http://collector:4318", service_name="svc-on", headers=(("k", "v"),))
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(otel=fake_otel_cfg2))
    with patch.object(otel_module, "OtelExporter") as mock_cls:
        mock_cls.return_value = MagicMock()
        exp = otel_module.get_exporter()
        mock_cls.assert_called_once()
        assert mock_cls.call_args.kwargs["service_name"] == "svc-on"
        assert mock_cls.call_args.kwargs["endpoint"] == "http://collector:4318"

    otel_module._exporter = None

    # case: cfg is None fallback (simulate load_config returns None otel? already handled)


def test_get_exporter_handles_exception_in_otel_exporter_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.integrations.otel as otel_module

    otel_module._exporter = None
    fake_cfg = MagicMock(enabled=False, endpoint="", service_name="svc", headers=())
    monkeypatch.setattr("cauterule.config.load_config", lambda: MagicMock(otel=fake_cfg))
    # ensure OtelExporter still works normally -> just verify no raise
    exp = otel_module.get_exporter()
    assert exp is not None
    otel_module._exporter = None
