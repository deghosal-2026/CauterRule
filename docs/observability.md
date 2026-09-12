# Observability: Observe, Metrics & OpenTelemetry

Cauterule ships two complementary observability surfaces: a local **observe
summary / metrics / leaderboard** over the rule store, and a standalone
**OpenTelemetry exporter** that streams rule lifecycle events to any
OTLP/HTTP-compatible backend (Jaeger, Tempo, Honeycomb, OTLP collector).
Token usage and cost capture round out the picture.

## Observe summary

`cauterule observe` is the top-level entry point:

```bash
cauterule observe                     # learned rules, recent verdicts, top gaps, frontier
cauterule observe --since 7d          # filter by period (7d / 24h / 30m)
cauterule observe --json              # machine-readable summary
cauterule observe journal             # failure → rule → replay → promotion narrative
cauterule observe metrics             # same as top-level `cauterule metrics`
cauterule observe frontier            # recommend the next most valuable domain/failure family
cauterule observe gaps                # domains with failures but no covering rule
```

The summary reports `rules_learned`, a `by_status` breakdown, and recent
verdict counts (`prevented` / `broke` / `neutral`) summed over the filtered
rules.

## Metrics

`cauterule metrics` prints store health and supports focused views:

```bash
cauterule metrics                      # total rules, status, avg confidence/effectiveness, stale, coverage
cauterule metrics --coverage           # coverage score (40% coverage + 40% precision + 20% non-stale)
cauterule metrics --by-domain          # per-domain coverage
cauterule metrics --by-class           # per-class coverage (requires trajectories via the Python API)
cauterule metrics --rule R-001         # per-rule outcome counts + trend sparkline
cauterule metrics --lowest-spec        # lowest-specificity rules (broad < 0.3)
```

Outcome counts are stored per rule in an append-only log so replay-cache hits
do not double-count (see [`ADAPTERS.md`](ADAPTERS.md) §8).

## Leaderboard

`cauterule leaderboard` surfaces failure patterns from replay evidence:

```bash
cauterule leaderboard                  # most prevented, most broken, top gaps
cauterule leaderboard --top 5
```

- **Most prevented** — rules with the most `failures_prevented`.
- **Most broken** — rules with the most `successes_broken`.
- **Top gaps** — active rules with the lowest recall (where to invest next).

## Token usage & cost capture

`LLMResponse` carries provider-reported usage:

```python
from cauterule.llm.provider import LLMResponse

# LLMResponse.prompt_tokens / LLMResponse.completion_tokens
# default to 0 when the provider does not report usage.
```

Cost is computed from those counts by `cauterule.measurement.cost`
(token-based when input/output prices are supplied; otherwise falls back to
`cost_per_request × llm_requests`) and reported by `scripts/measure_cost.py`:

```bash
python scripts/measure_cost.py --results field-test/results/0.3.0 \
  --input-price 0.00015 --output-price 0.0006 --cost-per-request 0.01
```

It emits `total_cost`, `cost_per_candidate`, `cost_per_promoted_rule`,
`cost_per_1k_trajectories`, and `gate_savings`. See
[`docs/field-test/v0.3.0/cost-measurement.md`](field-test/v0.3.0/cost-measurement.md).

## OpenTelemetry export

The standalone exporter emits rule lifecycle events as OpenTelemetry spans to
any OTLP/HTTP-compatible backend (Jaeger, Tempo, Honeycomb, OTLP collector).

### Config

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
`otel` extra: `pip install cauterule[otel]`. Each exporter owns its own
`TracerProvider`, so it never mutates the global provider used by your app.

### Span schema

| Span | Attributes |
|---|---|
| `rule.match` | `rule_id`, `agent`, `trigger`, `confidence`, `match_type` |
| `rule.promote` | `rule_id`, `from_state`, `to_state`, `evidence_id`, `justification` |
| `rule.retire` | `rule_id`, `reason` (stale/harmful/superseded), `superseded_by` |
| `replay.verdict` | `evidence_id`, `verdict`, `precision_score`, `recall_score` |

Legacy helper methods (`emit_rule_hit`, `emit_rule_promotion`,
`emit_rule_extraction`) emit `rule.hit` / `rule.promotion` /
`rule.extraction` spans.

### Verify

```bash
cauterule otel test                        # uses [otel] endpoint
cauterule otel test --endpoint http://localhost:4318
```

### Jaeger quickstart

```bash
docker run -d -p 4318:4318 -p 16686:16686 jaegertracing/all-in-one
# cauterule.toml: endpoint = "http://localhost:4318"
cauterule demo   # spans flow; open http://localhost:16686
```

Tempo works the same way against its OTLP receiver.
