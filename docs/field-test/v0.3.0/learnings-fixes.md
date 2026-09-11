# v0.3.0 Field Test — Learnings & Fixes (Llama-3.2-3B OMLX sweep)

**Date:** 2026-09-11 · **Model:** Llama-3.2-3B-Instruct-4bit (OMLX local, free)

---

## TL;DR

The v0.3.0 field-test sweep surfaced **five fixable issues** — two matcher/scoring bugs that inflated false passes, one runner bug that silently under-counted the multi-record v0.3.0 corpora, one corpus-label bug, and one gate-gap. All five are fixed, and the nearmiss false-pass rate dropped from 5 → 1. The single remaining nearmiss pass is an irreducible designer-intent edge, not a bug.

---

## 1. Nearmiss precision: 5 false-passes → 1

### Symptom
Nearmiss corpus (recovered/near-miss trajectories, `expected_outcome: should_reject`) showed 5/50 candidates passing replay with `precision=1.0`. Release gate requires ≥90% nearmiss precision.

### Root causes (3 compounding)

**1a. Alias-floor overrides corpus threshold** (`src/cauterule/replay/matcher.py`)
- `match_score()` floored alias-phrase hits at a hard 0.70; the OMLX curated threshold is 0.65 → any alias hit auto-passed.
- Aggravated by the M3 #492 "Qwen aliases" (`command fails → exit code`, `pipeline fails → test failed`, `not found error → not found`) — these phrases appear in almost every failure trajectory, so the floor fired constantly.
- **Fix:** removed the 5 broad #492 alias entries. Specific aliases (non-fast-forward → updates were rejected) kept. Qwen abstract triggers still match via the weighted token-F1 path.

**1b. Near-miss references were never penalised** (`src/cauterule/replay/scorer.py`)
- `build_evidence_report()` computed `near_misses` but `compute_scores()` ignored them → a candidate matching both real failures AND near-miss references scored `pass`.
- **Fix:** `compute_scores(..., near_misses=0)` — `near_misses > 0` downgrades `pass → inconclusive` (over-broad trigger). Tests added (`tests/replay/test_scorer.py`).

**1c. Self-match inflated precision** (`scripts/run-field-test.py`)
- A nearmiss/success trajectory counted its OWN extracted candidate as a "prevented" reference → `precision = 1/1 = 1.0` → pass on a single trajectory.
- **Fix:** `replay_test_candidate(..., exclude_ids={source ids})` — the source trajectory is excluded from the reference set.

### Result
- Gate now drops 37/50 nearmiss trajectories (recovered successes silenced).
- 1/50 remains passing = **98% nearmiss correctness** (target ≥90%).

---

## 2. Gate gap: recovered successes slipped through

### Symptom
The N-00x nearmiss series (`N-001-success-git-push`, `N-007-intermittent`, …) are `success=True` trajectories with a fabricated `failure_class` — they produced candidates because the gate read `failure_class` as a failure signal.

### Fix (`src/cauterule/extraction/gate.py`)
- Added `_RECOVERY_KEYWORDS = {temp, near, retry, recover, intermittent, flaky}` (the Fix 8 set).
- `success=True` + recovery keyword in `failure_class` → `SILENCE_REASON_NEARMISS` (gate drop).
- Also added `nearmiss` to the runner's `SAFETY_CORPORA` so nearmiss sweeps run the gate in strict mode (the field-test plan always said nearmiss = strict, but the code didn't include it).

---

## 3. Corpus label bug: 10 nearmiss files mislabeled

### Symptom
10/50 `field-test/corpus/curated/nearmiss/*.jsonl` had `expected_outcome: should_extract` (should be `should_reject`): the N-001..N-010 "success that looks like failure" series.

### Fix
Rebelabeled all 10 → `should_reject` + rationale. `tests/corpus/` still 81 green.

---

## 4. Runner bug: multi-record JSONL silently under-counted

### Symptom
The v0.3.0 corpora (adapters/lifecycle/packs/mcp/otel) are **one `.jsonl` file per corpus with many records**. The runner processed per-FILE:
- `load_trajectory()` did `json.loads(whole_file)` → failed/single-record.
- Result: `adapters traj=1`, `lifecycle traj=1`, `reference-expansion traj=32` (should be 288), etc.

### Fix (`scripts/run-field-test.py`)
- `load_trajectory()` now reads JSONL line-by-line → returns a list of records.
- `run_corpus_type()` expands files into per-record tasks at discovery.
- `process_one_trajectory()` accepts a record dict directly.
- Post-fix: adapters 18/18, lifecycle 40/40, packs 40/40, mcp 20/20, otel 20/20, reference-expansion 288/288.

### Lesson
**Never assume one-record-per-file.** The reference loader already read JSONL correctly; the target loader didn't. When you add a multi-record corpus, run the corpus to verify `Done: N/N` matches `wc -l`.

---

## 5. Matcher threshold gotcha (observation, not changed)

`OMLX_THRESHOLD = 0.65` with a hard 0.70 alias floor is inverted — the floor should be ≤ the threshold. This was the specific mechanism of issue 1a. If we re-lower thresholds for small models, keep any alias floor **at or below** the corpus threshold.

---

## 6. Coverage gaps found (as noted, not fixed here)

- The `openai` package wasn't installed in the dev venv (runner needed it for OMLX) — `pip install openai`.
- `opentelemetry.exporter` isn't installed → `OTel tracer setup failed — export disabled` noise every run (non-fatal; the #588 exporter gracefully degrades). Install `opentelemetry-exporter-otlp` for clean logs.

---

## 7. Numbers To Track Forward

| Corpus | Before fixes | After fixes | Note |
|--------|--------------|-------------|------|
| nearmiss false passes | 5 | **1** | gate + scorer + self-match |
| golden passes | 4 | 1 | near-miss penalty + self-match now honest |
| golden precision | 0.547 | 0.547 | unchanged metric |
| failures/positive | 12P | 5P | self-match exclusion honesty |
| raw/synthetic | 29P | 32P | identical behavior + full corpus |
| reference-expansion | traj=32 | **288** | runner JSONL fix |

Re-run on Qwen3-4B + 2 cloud models (#648/#650) to confirm these fixes generalize (especially the #492 alias removal — Qwen may rely on them; monitor its recall).

---

## 8. New Issues Documented From This Sweep (not GitHub — md tracking)

Per project process, these are documented here (no new GitHub issues filed at sweep time):

| # | New issue | Severity | Status | Location |
|---|-----------|----------|--------|----------|
| N1 | Runner `load_trajectory()` only read single-record JSONL — v0.3.0 multi-record corpora (adapters/lifecycle/packs/mcp/otel/ref-exp) silently under-counted (adapters traj=1, ref-exp=32 instead of 288). Fixed: line-by-line JSONL + per-record discovery. | high | ✅ fixed | `scripts/run-field-test.py` |
| N2 | Near-miss references computed but never penalised in scoring → over-broad triggers passed. Fixed: `near_misses>0` → `pass`→`inconclusive`. | high | ✅ fixed | `scorer.py`, `report.py`; tests `test_scorer.py` |
| N3 | Self-match counted as "prevented" — nearmiss/success trajectory validated its own extracted candidate (precision=1.0/1). Fixed: source-trajectory exclusion from references. | high | ✅ fixed | `run-field-test.py` |
| N4 | Recovery-gate gap: `success=True` + fabricated `failure_class` (e.g. `nearmiss/coding`) passed the gate. Fixed: Fix-8 keyword gate-side + `nearmiss` → `SAFETY_CORPORA`. | high | ✅ fixed | `gate.py` |
| N5 | 10/50 nearmiss files mislabeled `should_extract` (should be `should_reject`) — N-001..N-010. Fixed: relabeled + rationale. | medium | ✅ fixed | corpus |
| N6 | #492 broad Qwen aliases over-fired — reverted (see WBS part1). Re-add only with specific phrases if Qwen recall regresses. | medium | ✅ fixed (amended) | `matcher.py` |
| N7 | `openai` not in dev venv — OMLX sweeps failed before install. | low | fixed | dev env |
| N8 | `opentelemetry.exporter` not installed → "OTel tracer setup failed" log noise every run. Non-fatal (#588 exporter degrades). Install `opentelemetry-exporter-otlp` for clean logs. | low | open (cosmetic) | env |
| N9 | Quality thresholds FAIL on 3B local model: golden 10%, failures/positive 10% vs ≥70%/≥50% gate. Known small-model ceiling; cloud re-measure pending #650. | major | open (measurement) | results doc |

**Tracking note:** #491 (Fix 8 OMLX re-run) is now done gate-side; #492 marked amended in WBS part1. GH issue states remain per milestone (not closed by this sweep — the fixes shipped on `feat-v0.3.0`).