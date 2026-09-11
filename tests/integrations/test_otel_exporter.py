"""Tests for the OTEL exporter + [otel] config + otel test CLI (#588)."""

from __future__ import annotations

import http.server
import threading
from typing import ClassVar

import pytest
from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.config import load_config


class _Collector(http.server.BaseHTTPRequestHandler):
    bodies: ClassVar[list[bytes]] = []

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        _Collector.bodies.append(self.rfile.read(length))
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture
def collector():
    pytest.importorskip("opentelemetry.sdk")
    _Collector.bodies = []
    server = http.server.HTTPServer(("127.0.0.1", 0), _Collector)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    # Shut down the collector + reset the global tracer provider so
    # later tests don't retry spans against a dead endpoint.
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.trace import get_tracer_provider, set_tracer_provider

    provider = get_tracer_provider()
    if isinstance(provider, TracerProvider):
        provider.shutdown()
    # Replace with a fresh no-op provider.
    set_tracer_provider(TracerProvider())
    from cauterule.integrations import otel as otel_module

    otel_module._CONFIGURED = False
    server.shutdown()


class TestOtelExporter:
    def test_four_span_types_arrive(self, collector: str) -> None:
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.trace import get_tracer_provider

        from cauterule.integrations import otel as otel_module
        from cauterule.integrations.otel import OtelExporter, configure_otlp

        otel_module._CONFIGURED = True
        exporter = configure_otlp(collector, service_name="test")
        assert isinstance(exporter, OtelExporter)
        exporter.emit_rule_match("R-1", agent="a", trigger="t", confidence=0.9)
        exporter.emit_rule_promote("R-1", justification="j")
        exporter.emit_rule_retire("R-1", reason="stale")
        exporter.emit_replay_verdict("E-1", verdict="pass", precision_score=1.0)
        provider = get_tracer_provider()
        if isinstance(provider, TracerProvider):
            provider.force_flush(timeout_millis=5000)
        assert len(_Collector.bodies) >= 1
        otel_module._CONFIGURED = False

    def test_emit_never_raises(self) -> None:
        from cauterule.integrations.otel import OtelExporter

        exporter = OtelExporter(service_name="test-never-raise")
        exporter.emit_rule_match("R-1")
        exporter.emit_rule_promote("R-1")
        exporter.emit_rule_retire("R-1")
        exporter.emit_replay_verdict()


class TestOtelConfig:
    def test_defaults_disabled(self, tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert load_config().otel.enabled is False

    def test_parses_section(self, tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / "cauterule.toml").write_text(
            '[otel]\nenabled = true\nendpoint = "http://collector:4318"\n'
            'service_name = "x"\nbatch_size = 100\n'
        )
        monkeypatch.chdir(tmp_path)
        cfg = load_config().otel
        assert cfg.enabled is True
        assert cfg.endpoint == "http://collector:4318"
        assert cfg.batch_size == 100

    def test_rejects_bad_endpoint(self, tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / "cauterule.toml").write_text('[otel]\nenabled = true\nendpoint = "ftp://x"\n')
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="http"):
            load_config()


class TestOtelCli:
    def test_otel_test_cli(self, tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
        from cauterule.integrations import otel as otel_module

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(otel_module, "_CONFIGURED", True)
        calls: list[str] = []
        monkeypatch.setattr(
            otel_module.OtelExporter, "emit_rule_match", lambda self, *a, **k: calls.append("match")
        )
        result = CliRunner().invoke(main, ["otel", "test", "--endpoint", "http://x:4318"])
        assert result.exit_code == 0, result.output
        assert "otel test span sent" in result.output
        assert calls == ["match"]
        otel_module._CONFIGURED = False
