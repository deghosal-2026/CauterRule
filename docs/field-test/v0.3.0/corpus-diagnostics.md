# Corpus Root-Cause Diagnostics (v0.3.0) — #690

<!-- generated from scripts/diagnose_corpus.py + field-test/results/0.3.0 sweeps -->

> **Update (2026-09-12, Llama-3.2-3B re-run):** the #698/#702/#703 reference
> corpora are now loaded — the runner's `REFERENCE_BUCKETS` reference set grew
> to **444 trajectories** and `scripts/diagnose_corpus.py` reports
> `uncovered_domains: []` for all five v0.3.0 corpora. The fresh single-model
> funnel below shows `mcp` now produces passes (3), confirming the reference
> gap was real; the remaining 0-pass corpora are matcher-side.

The code-review issue #690 flagged that several corpora showed **0 passes
across all 4 models** and the field-test report attributed all of them to one
cause ("matcher threshold too strict"). This diagnostic splits that result into
the three candidate causes: missing references, extraction pre-filter rejection,
or genuine matcher-threshold failure.

Method: `scripts/diagnose_corpus.py` (reference coverage) plus the candidate
pre-filter funnel over `field-test/results/0.3.0/<corpus>/*/*/results.jsonl`.
The funnel table below is the **2026-09-12 Llama-3.2-3B** re-run (single model);
the reference-coverage table is model-independent.

## Reference coverage

Shared reference set = **444 trajectories**, consisting of the curated buckets
(`failures/positive`, `failures/negative`, `successes`, `nearmiss`, `noisy`,
`corrections`) plus the v0.3.0 public reference corpora
(`corpus/public/{adapters,lifecycle,mcp,otel,browser,lifecycle_infra,real-world/bugsinpy,successes}`).

| Corpus | Target trajs | Reference set sufficient | Target domains with **zero** reference coverage |
|---|---|---|---|
| adapters | 60 | yes | — (#698) |
| lifecycle | 40 | yes | — (#698) |
| mcp | 20 | yes | — (#698, #703) |
| otel | 20 | yes | — (#702) |
| packs | 40 | yes | — |

## Candidate pre-filter funnel (Llama-3.2-3B, 2026-09-12)

| Corpus | Candidates | Generic | Reached scoring | Pass |
|---|---|---|---|---|
| adapters | 93 | 1 | 93 | 0 |
| lifecycle | 71 | 0 | 71 | 0 |
| packs | 75 | 31 | 75 | 0 |
| mcp | 25 | 0 | 25 | **3** |
| otel | 40 | 0 | 40 | 0 |
| raw/ci | 204 | 133 | 204 | 0 |

Candidates overwhelmingly **reach `match_score()`** — the pre-filter
(hypothesis c) is essentially ruled out. `packs`/`raw/ci` lose a meaningful
share to the generic-trigger pre-filter (31/75, 133/204).

## Root-cause classification

| Corpus | Root cause |
|---|---|
| `mcp` | reference gap **was** real (#698/#703); now produces passes (3/25 scored) |
| `adapters` | ~~(b) missing references~~ → reference set added (#698); still 0 pass → **(a) matcher-content mismatch** |
| `lifecycle` | ~~(b) missing references~~ → reference set added (#698); still 0 pass → **(a) matcher-content mismatch** |
| `otel` | **(a) matcher/reference-content mismatch** (#702 references added; candidates score, 0 pass) |
| `packs` | **(a) matcher/reference-content mismatch** + generic pre-filter (31/75) |
| `raw/ci` | **(a) matcher/reference-content mismatch** + generic pre-filter (133/204) |

This confirms #690's core claim: the blanket "matcher threshold" explanation is
wrong for a meaningful slice of the matrix. With references now in place, the
remaining 0-pass corpora (`adapters`/`lifecycle`/`otel`/`packs`/`raw/ci`) are the
genuine matcher-side cases that #689 (semantic matching) and threshold work
address.

## Follow-ups

- #689 — semantic/embedding matching for the matcher-side corpora.
- #698/#702/#703 — reference corpora added and loaded (done).
- #677 — domain-aware context matching (landed; lifted calibration golden recall 0.50→0.90).

## Regression guard

`tests/corpus/test_v030_corpus_coverage.py` fails if a v0.3.0 target corpus or a
shared reference bucket drops below `MIN_REFERENCE_TRAJECTORIES` (5), so a silent
empty-reference regression can no longer masquerade as an unexplained 0-pass.
`tests/test_run_field_test_harness.py::test_all_corpus_types_resolve_to_existing_dirs`
guards that every `CORPUS_TYPES` entry points at a real directory.
