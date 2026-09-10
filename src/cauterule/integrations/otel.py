"""OpenTelemetry exporter — emit rule events as OTel spans."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from cauterule.log import get_logger

_log = get_logger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.trace import SpanKind, Status, StatusCode

    _OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _OTEL_AVAILABLE = False


AttributeValue = (
    str | bool | int | float | Sequence[str] | Sequence[bool] | Sequence[int] | Sequence[float]
)


def _coerce_attribute(value: object) -> AttributeValue:
    """Coerce *value* to an OTel-safe attribute type (#508).

    Passes through ``str``/``bool``/``int``/``float`` (and homogeneous
    sequences thereof); coerces anything else with ``str()`` so telemetry
    can never crash the caller. ``bool`` is checked before ``int``
    (``bool`` subclasses ``int``) but passes through unchanged either way.
    """
    if isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, (list, tuple)):
        # OTel sequences must be homogeneous; mixed or complex content
        # is stringified instead of crashing the caller.
        kinds = {type(v) for v in value}
        if not kinds or kinds <= {str} or kinds <= {bool} or kinds <= {int, float}:
            return cast(AttributeValue, list(value))
    return str(value)


class OtelExporter:
    """Emits Cauterule rule events as OpenTelemetry spans.

    Uses the global ``opentelemetry.trace`` TracerProvider. If the
    ``opentelemetry-api`` package is not installed, all methods are no-ops.

    Args:
        service_name: Service name for the tracer (default ``"cauterule"``).
    """

    def __init__(self, service_name: str = "cauterule") -> None:
        self.service_name = service_name
        if _OTEL_AVAILABLE:
            self._tracer = trace.get_tracer(service_name)
        else:
            # Actionable hint, logged once per exporter (#507) — the
            # no-op path is otherwise completely silent.
            _log.warning(
                "opentelemetry-api is not installed — OTel export is disabled. "
                "pip install cauterule[otel] to enable it."
            )
            self._tracer = None  # type: ignore[assignment]

    def emit_rule_hit(self, rule_id: str, context: dict[str, Any] | None = None) -> None:
        """Record a rule-hit event as an OTel span.

        Args:
            rule_id: The identifier of the rule that was hit.
            context: Optional attributes to attach to the span.
        """
        if not _OTEL_AVAILABLE or self._tracer is None:
            return
        with self._tracer.start_as_current_span(
            "rule.hit",
            kind=SpanKind.INTERNAL,
        ) as span:
            span.set_attribute("rule.id", rule_id)
            if context:
                for k, v in context.items():
                    span.set_attribute(k, _coerce_attribute(v))

    def emit_rule_promotion(self, rule_id: str, title: str | None = None) -> None:
        """Record a rule-promotion event as an OTel span.

        Args:
            rule_id: The identifier of the promoted rule.
            title: Optional human-readable title.
        """
        if not _OTEL_AVAILABLE or self._tracer is None:
            return
        with self._tracer.start_as_current_span(
            "rule.promotion",
            kind=SpanKind.INTERNAL,
        ) as span:
            span.set_attribute("rule.id", rule_id)
            span.set_status(Status(StatusCode.OK))
            if title:
                span.set_attribute("rule.title", title)

    def emit_rule_extraction(
        self,
        rule_id: str,
        trajectory: str | None = None,
        accuracy: float | None = None,
    ) -> None:
        """Record a rule-extraction event as an OTel span.

        Args:
            rule_id: The identifier of the extracted rule.
            trajectory: Optional source trajectory identifier.
            accuracy: Optional extraction accuracy score.
        """
        if not _OTEL_AVAILABLE or self._tracer is None:
            return
        with self._tracer.start_as_current_span(
            "rule.extraction",
            kind=SpanKind.INTERNAL,
        ) as span:
            span.set_attribute("rule.id", rule_id)
            if trajectory:
                span.set_attribute("rule.trajectory", trajectory)
            if accuracy is not None:
                span.set_attribute("rule.accuracy", accuracy)