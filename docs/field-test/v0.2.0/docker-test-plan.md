# Docker Field Test Plan — CauterRule v0.2.0

> **Goal:** Validate the full CauterRule v0.2.0 system end-to-end in a Docker container under field conditions. Extends the v0.1.0 Docker plan (`docs/field-test/v0.1.0/docker-test-plan.md`, 15 stages, 104 tests) with the new M1-M9 surface: pre-extraction gate, safety scoring, preflight/harness-health, TUI review, observability metrics, expanded corpus, benchmarks, adversarial corpora, and scale benchmarks.

**Issue:** #436 — Docker validation.
**Deliverable:** `docs/field-test/v0.2.0/docker-test-results.md` (results).

---

## 1. Changes vs v0.1.0 Docker Plan

| # | v0.1.0 stage | v0.2.0 change |
|---|-------------|---------------|
| 1 | Build & Install | Version non-asserted (still 0.1.0 until M11 bump); new `--help` commands added |
| 2 | Hermetic unit suite | Adds `tests/observe`, `tests/review`, `tests/release`, `tests/benchmark`, `tests/corpus`, `tests/adversarial`, `tests/scale` |
| 3 | Scale suite | Unchanged (M9 tests live in `tests/scale/`) |
| 4 | Adversarial | 50 JSONL corpora now on disk (M9) — suite runs `tests/adversarial/` |
| 5 | Corpus & benchmarks | Adds metadata guard `tests/corpus/test_field_test_metadata.py`; public corpus 160 trajs |
| 6 | CLI | Adds `preflight`, `harness-health`, `metrics --coverage/--by-domain/--by-class`, `gaps`, `leaderboard`, `frontier`, `journal`, `report --monthly`, `review --json/--batch`, `show --hits` |
| 7 | TUI | Adds `review` CLI-driven TUI launch + `--batch` non-interactive JSON |
| 8 | MCP | Unchanged (4 tools) |
| 9 | Pipeline | Adds pre-flight gate check + harness-health in sweep loop |
| 10 | Demo | Same target <60s |
| 11-15 | Redaction/Export/Git/Loop/Multi-env | Unchanged except new test dirs |

---

## 2. Test Environment

Reuses the v0.1.0 image build:

```bash
docker build -t cauterule:field-test .
```

Base image `python:3.12-slim`, wheel install via `python -m build`. Multi-python (3.11/3.12/3.13) via `--build-arg PYTHON_VERSION`.

---

## 3. Test Matrix

| Test Layer | What It Tests | How Verified | v0.2.0-specific |
|-----------|---------------|--------------|-----------------|
| CLI | All 30+ commands produce real output | `pytest tests/cli/` + subprocess | `preflight`, `harness-health`, `metrics`, `gaps`, `leaderboard`, `frontier`, `journal`, `report --monthly`, `review --batch`, `show --hits` |
| Pipeline | capture → gate → extract → replay → promote → inject | scripted scenario | Gate drops clean successes before LLM |
| Preflight | `cauterule preflight` runs provider + corpus checks | subprocess in container | ✅ NEW |
| Harness health | `cauterule harness-health` PASS/FAIL self-assert | subprocess in container | ✅ NEW |
| MCP | stdio transport, 4 tools | mock client | — |
| TUI | Textual app renders, approve/reject/filter | Textual Pilot | `cauterule review` CLI launch + `--batch` JSON |
| Observability | `metrics --coverage`, domain coverage, gaps, leaderboard, frontier, journal, monthly report | subprocess against seeded rule store | ✅ NEW |
| Adversarial | 6 corpora produce 0 promoted rules | `pytest tests/adversarial/` | 50 on-disk trajectories |
| Corpus | 394 field-test + 160 public trajs metadata-complete | `pytest tests/corpus/` incl metadata guard | ✅ NEW |
| Benchmarks | 12 sentinel benchmarks w/ enforced thresholds | `pytest tests/benchmark/` | 100-run determinism |
| Scale | latency/memory/indexing/concurrency targets | `pytest tests/scale/` (slow) | — |
| Demo | full loop <60s | `docker run cauterule demo` | — |
| Redaction | secrets stripped before disk | `pytest tests/field/test_docker_redaction.py` | — |
| Export | 7 formats round-trip | `pytest tests/export/` | — |
| Git | hash, commit, rollback | `pytest tests/field/test_docker_git.py` | — |

---

## 4. Test Stages

### Stage 1 — Build & Install
```bash
docker build -t cauterule:field-test .
docker run --rm cauterule:field-test --version
docker run --rm cauterule:field-test --help
```
Pass: image builds; `--help` lists `extract`, `promote`, `review`, `preflight`, `harness-health`, `metrics`, `gaps`, `leaderboard`, `frontier`, `journal`, `demo`.

### Stage 2 — Hermetic Unit Suite (v0.2.0 expanded)
```bash
docker run --rm cauterule:field-test sh -c "pip install -q pytest && \
pytest tests/ -m 'not slow and not docker' --tb=short -q -p no:cacheprovider"
```
Pass: zero failures; includes new `observe/review/release/benchmark/corpus/adversarial` dirs.

### Stage 3 — Scale Suite (M9)
```bash
docker run --rm cauterule:field-test sh -c "pytest tests/scale/ -v --tb=short"
```
Pass: replay tiny<2s/small<10s/medium<60s; injection p50<100ms/p95<500ms; conflict <5s@1k; memory<1GB; indexing<1s@1k; stability 0-variance.

### Stage 4 — Adversarial (M9 corpora)
```bash
docker run --rm cauterule:field-test sh -c "pytest tests/adversarial/ -v"
```
Pass: injection/misleading/contradiction/unsafe/poisoning all 0 promoted; leakage 0 secrets.

### Stage 5 — Corpus & Benchmarks (v0.2.0)
```bash
docker run --rm cauterule:field-test sh -c "pytest tests/corpus/ tests/benchmark/ -v"
```
Pass: 394 field-test + 160 public trajs metadata-complete (`test_field_test_metadata.py`); gold ≥85%, counterexample rejection ≥90%, nearmiss ≥90%, regression ≥95%, 100-run determinism.

### Stage 6 — CLI (v0.2.0 new commands)
```bash
docker run --rm cauterule:field-test sh -c "pytest tests/cli/ -v"
```
Plus v0.2.0 subprocess checks:
- `cauterule preflight --corpus corpus/public/golden`
- `cauterule harness-health --parsed 50 --total 50`
- `cauterule metrics --coverage`, `metrics --by-domain`
- `cauterule gaps`, `leaderboard`, `frontier`, `journal`
- `cauterule report --monthly`
- `cauterule review --batch --json`

### Stage 7 — TUI Review (M5)
```bash
docker run --rm cauterule:field-test sh -c "pytest tests/tui/ -v"
```
Pass: screens render, keybindings fire, approve promotes, `cauterule review --batch` emits JSON.

### Stage 8 — MCP Server
```bash
docker run --rm cauterule:field-test sh -c "pytest tests/mcp/ -v"
```

### Stage 9 — Pipeline E2E (with gate + harness)
```bash
docker run --rm -v $(pwd)/field-test-data:/data cauterule:field-test sh -c "
  cauterule init --dir /data/p
  cauterule extract --trajectory /data/p/trajectories/failure.jsonl --dry-run
  cauterule test --candidate /data/p/candidates/candidate-1.yaml
  cauterule promote --candidate /data/p/candidates/candidate-1.yaml
  cauterule list && cauterule inject 'git push origin main'
  cauterule health && cauterule validate
"
```

### Stage 10 — Demo
```bash
docker run --rm cauterule:field-test demo
```
Pass: <60s, ≥1 rule promoted, git commit exists.

### Stage 11-15 — Redaction, Export/Import, Git, Loop, Multi-Env
Same as v0.1.0 (unchanged), run via `pytest tests/field/`.

---

## 5. docker-compose.yaml Update

Add v0.2.0 test dirs to `cauterule-test` service command so compose validates the expanded suite:

```yaml
command: ["pip install -q pytest && cd /repo && python -m pytest \
  tests/models tests/store tests/serialization tests/injection tests/redaction \
  tests/export tests/cli tests/capture tests/promotion tests/conflict tests/loop \
  tests/packs tests/observe tests/review tests/release tests/benchmark \
  tests/corpus tests/adversarial tests/scale tests/tui tests/mcp tests/extraction \
  tests/replay tests/safety tests/test_preflight \
  -m 'not slow and not docker' --tb=short -q -p no:cacheprovider"]
```

---

## 6. Pass/Fail Summary

| Stage | Tests | Pass Criteria |
|-------|-------|---------------|
| 1. Build & Install | 4 | Image builds, help lists v0.2.0 commands |
| 2. Hermetic unit | ~900+ | All pass incl new dirs |
| 3. Scale | 24 | Latency/capacity targets met |
| 4. Adversarial | 41 | 0 promoted from 6 corpora |
| 5. Corpus & Benchmarks | ~170 | Metadata complete, thresholds met |
| 6. CLI | 30+ | All v0.2.0 commands produce output |
| 7. TUI | 41 | Review/batch work |
| 8. MCP | 15 | 4 tools respond |
| 9. Pipeline | 9 | Full loop incl gate |
| 10. Demo | 5 | <60s, rule promoted |
| 11-15 | ~100 | Redaction/export/git/loop/multi-env |
| **Total** | **~1350+** | **All stages pass** |

---

## 7. Deferred (unchanged from v0.1.0)

Playwright/browser UI (v0.5.0), real LLM cost (M10 #447 measures separately), Homebrew/binary tests (M11 #34/#36), GitHub Action (M11 #38), webhook delivery (M11 #39), OTel collector (M11 #40).

---

## 8. Results Artifact

The #436 run writes `field-test/v0.2.0/docker-validation.md` with per-stage PASS/FAIL, test counts, and timings — parallel to `docs/field-test/v0.1.0/docker-test-results.md`.