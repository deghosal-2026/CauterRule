# Observability: OpenTelemetry Export

Cauterule emits rule lifecycle events as OpenTelemetry spans to any
OTLP/HTTP-compatible backend (Jaeger, Tempo, Honeycomb, OTLP collector).

## Config

```toml
[otel]
enabled = true
endpoint = "http://localhost:4317"
service_name = "cauterule"
headers = { "x-api-key" = "..." }
batch_size = 512
export_interval_ms = 5000
retry_max = 3
```

The exporter initializes lazily on the first rule/replay event, batches
spans, and never raises into the rule pipeline (emit failures are logged).
With `enabled = false` (default) everything is a no-op. Requires the
`otel` extra: `pip install cauterule[otel]`.

## Span schema

| Span | Attributes |
|---|---|
| `rule.match` | `rule_id`, `agent`, `trigger`, `confidence`, `match_type` |
| `rule.promote` | `rule_id`, `from_state`, `to_state`, `evidence_id`, `justification` |
| `rule.retire` | `rule_id`, `reason` (stale/harmful/superseded), `superseded_by` |
| `replay.verdict` | `evidence_id`, `verdict`, `precision_score`, `recall_score` |

## Verify

```bash
cauterule otel test                        # uses [otel] endpoint
cauterule otel test --endpoint http://localhost:4318
```

## Jaeger quickstart

```bash
docker run -d -p 4318:4318 -p 16686:16686 jaegertracing/all-in-one
# cauterule.toml: endpoint = "http://localhost:4318"
cauterule demo   # spans flow; open http://localhost:16686
```

Tempo works the same way against its OTLP receiver.
