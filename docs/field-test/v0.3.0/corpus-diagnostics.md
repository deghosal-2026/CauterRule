# Corpus Root-Cause Diagnostics (v0.3.0) — #690

<!-- generated from scripts/diagnose_corpus.py + field-test/results/0.3.0 sweeps -->

The code-review issue #690 flagged that several corpora showed **0 passes
across all 4 models** and the field-test report attributed all of them to one
cause ("matcher threshold too strict"). This diagnostic splits that result into
the three candidate causes: missing references, extraction pre-filter rejection,
or genuine matcher-threshold failure.

Method: `scripts/diagnose_corpus.py` (reference coverage) plus the candidate
pre-filter funnel over `field-test/results/0.3.0/<corpus>/*/*/results.jsonl`,
aggregated across all 4 models (Llama-3.2-3B, Qwen3-4B, gpt-4o-mini,
llama-3.1-8b).

## Reference coverage

Shared curated reference set = 220 trajectories (`curated/failures/positive`,
`failures/negative`, `successes`, `nearmiss`).

| Corpus | Target trajs | Reference set sufficient | Target domains with **zero** reference coverage |
|---|---|---|---|
| adapters | 18 | yes | `agent` |
| lifecycle | 40 | yes | `lifecycle` |
| mcp | 20 | yes | `mcp` |
| otel | 20 | yes | — |
| packs | 40 | yes | — |

## Candidate pre-filter funnel (all 4 models)

| Corpus | Candidates | Degenerate | Generic | Reached scoring |
|---|---|---|---|---|
| lifecycle | 308 | 0 | 0 | 308 |
| otel | 160 | 0 | 0 | 160 |
| packs | 318 | 1 | 14 | 303 |
| raw/ci | 751 | 0 | 0 | 751 |
| adapters | 130 | 0 | 0 | 130 |
| mcp | 152 | 0 | 0 | 152 |

Candidates overwhelmingly **reach `match_score()`** — the pre-filter
(hypothesis c) is essentially ruled out.

## Root-cause classification

| Corpus | Root cause |
|---|---|
| `adapters` | **(b) missing references** — `agent` domain has no reference trajectories |
| `lifecycle` | **(b) missing references** — `lifecycle` domain has no reference trajectories |
| `mcp` | **(b) missing references** — `mcp` domain has no reference trajectories |
| `otel` | **(a) matcher/reference-content mismatch** — references exist and candidates score, yet 0 pass |
| `packs` | **(a) matcher/reference-content mismatch** — same; 15/318 candidates lost to generic pre-filter |
| `raw/ci` | **(a) matcher/reference-content mismatch** — 751 candidates score, 0 pass |

This confirms #690's core claim: the blanket "matcher threshold" explanation is
wrong for a meaningful slice of the matrix. `adapters`/`lifecycle`/`mcp` need
reference data first (#698); `otel`/`packs`/`raw/ci` are the genuine
matcher-side cases that #689 (semantic matching) and threshold work address.

## Follow-ups

- #698 — corpus expansion (real + synthetic reference data, incl. adapter/lifecycle/mcp classes).
- #702 — OpenTelemetry reference corpus (otel).
- #703 — MCP reference corpus (mcp), informed by #601.
- #689 — semantic/embedding matching for the matcher-side corpora.

## Regression guard

`tests/corpus/test_v030_corpus_coverage.py` fails if a v0.3.0 target corpus or a
shared reference bucket drops below `MIN_REFERENCE_TRAJECTORIES` (5), so a silent
empty-reference regression can no longer masquerade as an unexplained 0-pass.
