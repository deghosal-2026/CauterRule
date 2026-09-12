# v0.3.0 — WBS Part 3: Phase 3 — Field Test

**Milestone:** M7 ([v0.3.0-M7: Field Test](https://github.com/deghosal-2026/CauterRule/milestone/62))

**Theme:** Prove the hardening + ecosystem work on real models with new trajectories covering packs/adapters/lifecycle safety.

---

## M7: Field Test (13 issues)

**Goal:** Run the v0.3.0 field test across 2 OMLX local LLMs + cloud LLMs (gpt-4o-mini + llama-3.1-8b-instruct), with updated runner scripts, new corpus trajectories, Docker validation, cost + repeat-failure measurements, and a published report.

**Execution order:** plan (#625) → runner scripts (#629) → corpus (#635) → Docker plan/run (#641-#642) → model runs (#648, #650) → measurements (#653, #658, #663) → report (#667) → known issues (#671) → exit gate (#673)

**Dependencies:** M1-M6 (all features + fixes under test)

| # | Task | Issue |
|---|------|-------|
| 7.1 | Create field test plan — methodology, corpus plan, thresholds, scoring | [#625](https://github.com/deghosal-2026/CauterRule/issues/625) | ✓ closed |
| 7.2 | Update field test runner scripts for v0.3.0 changes | [#629](https://github.com/deghosal-2026/CauterRule/issues/629) | ✓ closed |
| 7.3 | Update corpus for v0.3.0 field test — packs/adapters/lifecycle safety | [#635](https://github.com/deghosal-2026/CauterRule/issues/635) | ✓ closed |
| 7.4 | Docker test plan — container validation, compose scenarios, image size, multi-arch | [#641](https://github.com/deghosal-2026/CauterRule/issues/641) | ✓ closed |
| 7.5 | Create and run Docker tests — compose suites, CLI smoke, preflight, full pipeline | [#642](https://github.com/deghosal-2026/CauterRule/issues/642) | ✓ closed |
| 7.6 | Run field test against 2 OMLX local LLMs — capture results | [#648](https://github.com/deghosal-2026/CauterRule/issues/648) | ✓ closed |
| 7.7 | Run field test against cloud LLMs — gpt-4o-mini + llama-3.1-8b-instruct | [#650](https://github.com/deghosal-2026/CauterRule/issues/650) | ✓ closed |
| 7.8 | Cost measurement — LLM cost per candidate, per promoted rule | [#653](https://github.com/deghosal-2026/CauterRule/issues/653) | #682 (cost data available) |
| 7.9 | Multi-environment validation — macOS, Linux, Docker end-to-end | [#658](https://github.com/deghosal-2026/CauterRule/issues/658) | macOS + Docker ✓; Linux CI pending |
| 7.10 | Cross-session repeat-failure reduction measurement — before/after protocol | [#663](https://github.com/deghosal-2026/CauterRule/issues/663) | #683 |
| 7.11 | Generate field test report — comprehensive assessment with safety-adjusted metrics | [#667](https://github.com/deghosal-2026/CauterRule/issues/667) | ✓ closed |
| 7.12 | Document known issues from field testing — severity, workaround, assignee | [#671](https://github.com/deghosal-2026/CauterRule/issues/671) | ✓ closed |
| 7.13 | M7 exit gate — code review, lint strict, coverage, docs updated | [#673](https://github.com/deghosal-2026/CauterRule/issues/673) | in progress |

**Model sweep data captured (this session):** all 30 corpora × 4 models (4,537 trajectory-runs). Local Llama-3.2-3B + Qwen3-4B (OMLX), cloud gpt-4o-mini + llama-3.1-8b (OpenRouter). Results: `docs/field-test/v0.3.0/field-test-results-4model.md` + per-model sheets + `FIELD_TEST_REPORT.md`. Safety 100% silence (all models), nearmiss 98% correct (1 FP), adversarial 0 promoted, 8 fixes applied + #601 MCP auth bug found+fixed. Quality gate (golden ≥70%, fp ≥50%) unreachable on all 4 — structural matcher issue (see #677). Recall 0.02-0.04 (target ≥0.10) — semantic matching is the v0.4.0 lever (#680).

**New issues filed from the field test:** #677 (quality gate regression — ✅ fixed: domain-aware context, golden recall 0.50→0.90), #678 (preflight signature — ✅ fixed), #679 (baseline.json artifact — ✅ fixed: 12.4MB→1.2KB), #680 (semantic matching — v0.4.0 lever), #681 (coverage, re-#494), #682 (cost measurement, re-#653), #683 (cross-session, re-#663), #684 (human agreement, re-#493).

**Docker work closed (this session):** #641 (plan) + #642 (suite) + #676 (MCP HTTP in-container) + deferred #524/#607 (Docker/CI + compose hardening). Dockerfile hardened (non-root, git, HEALTHCHECK, OCI labels, .dockerignore), compose profiled (name:, profiles:, no dead 8025, pip baked in, pip --user in test service), image rebuilt. New `tests/field/test_docker_v030.py` (22 tests, #642), `tests/mcp/test_docker_http_transport.py` (4 tests, #676), results reporter `tests/field/conftest.py` → `field-test/results/0.3.0/docker/` (jsonl + markdown + junit). Runner `scripts/docker_field_test.sh` (v0.3.0 default). 151/153 docker tests passing; 2 compose re-runs (mcp-accepts, test-service) marked done per scope — documented in `docs/field-test/v0.3.0/docker-test-results.md`.

### M7 Code Review Follow-ups (23 issues)

**Source:** `[0.3.0 Code Review]` issues filed from the v0.3.0 code review; all assigned to this milestone ([v0.3.0-M7: Field Test](https://github.com/deghosal-2026/CauterRule/milestone/62)).

| # | Task | Issue | Status |
|---|------|-------|--------|
| 7.14 | Trajectory-count mismatch (908 vs 1093/1156/1156/1132) — doc totals drift from raw results | [#685](https://github.com/deghosal-2026/CauterRule/issues/685) | ✓ done |
| 7.15 | Add regeneration pipeline for field-test reports (`scripts/generate_field_test_report.py`) | [#686](https://github.com/deghosal-2026/CauterRule/issues/686) | ✓ done |
| 7.16 | Link #667/#671/#673/#677-684 references in FIELD_TEST_REPORT.md to local WBS mirror | [#687](https://github.com/deghosal-2026/CauterRule/issues/687) | ✓ done |
| 7.17 | Resolve docker-test-plan.md "~70 tests" ambiguity vs docker-test-results.md's 153 | [#688](https://github.com/deghosal-2026/CauterRule/issues/688) | ✓ done |
| 7.18 | matcher.py: add semantic/embedding similarity to bridge paraphrase gap | [#689](https://github.com/deghosal-2026/CauterRule/issues/689) | ✓ done (opt-in) |
| 7.19 | Root-cause split: 0-pass corpora (lifecycle, otel, packs, raw/ci) — extraction vs threshold | [#690](https://github.com/deghosal-2026/CauterRule/issues/690) | ✓ done |
| 7.20 | Calibrate matcher thresholds (`STRATEGY_THRESHOLDS`, `OMLX_THRESHOLD`) with provenance test | [#691](https://github.com/deghosal-2026/CauterRule/issues/691) | ✓ done |
| 7.21 | gate.py: recovery-keyword substring match can silently suppress real failures | [#692](https://github.com/deghosal-2026/CauterRule/issues/692) | ✓ done |
| 7.22 | gate.py `_step_shows_success()`: non-empty output treated as success even on error text | [#693](https://github.com/deghosal-2026/CauterRule/issues/693) | ✓ done |
| 7.23 | matcher.py: `check_domain_mismatch()`/`extract_trigger_domain()` are dead code | [#694](https://github.com/deghosal-2026/CauterRule/issues/694) | code done; field-test revalidation pending |
| 7.24 | Add confidence intervals to field-test metrics (small n=10, n=50 samples) | [#695](https://github.com/deghosal-2026/CauterRule/issues/695) | ✓ done |
| 7.25 | Adversarial corpus: add tool-output-borne + multi-turn/compounding vectors | [#696](https://github.com/deghosal-2026/CauterRule/issues/696) | ✓ done |
| 7.26 | Spot-audit gate-dropped trajectories — expose false-positive gate silence | [#697](https://github.com/deghosal-2026/CauterRule/issues/697) | ✓ done |
| 7.27 | Corpus expansion: real production agent-trajectory sources + synthetic gaps | [#698](https://github.com/deghosal-2026/CauterRule/issues/698) | ✓ internal (agent/lifecycle/mcp refs + paraphrase); external #699-#706 pending |
| 7.28 | Corpus source: AgentHarm (Hugging Face) for adversarial/unsafe realism | [#699](https://github.com/deghosal-2026/CauterRule/issues/699) | ✓ done |
| 7.29 | Corpus source: InjecAgent (GitHub) for tool-output-borne injection | [#700](https://github.com/deghosal-2026/CauterRule/issues/700) | ✓ done |
| 7.30 | Corpus source: HarmBench (GitHub) for adversarial/misleading + contradiction | [#701](https://github.com/deghosal-2026/CauterRule/issues/701) | ✓ done |
| 7.31 | Corpus source: OpenTelemetry Demo (GitHub) for otel reference-corpus gap | [#702](https://github.com/deghosal-2026/CauterRule/issues/702) |
| 7.32 | Corpus source: modelcontextprotocol/servers (GitHub) for mcp reference-corpus gap | [#703](https://github.com/deghosal-2026/CauterRule/issues/703) |
| 7.33 | Corpus source: Terraform provider issue trackers for lifecycle/infra failures | [#704](https://github.com/deghosal-2026/CauterRule/issues/704) |
| 7.34 | Corpus source: WebArena / VisualWebArena (GitHub) for browser-tool failure diversity | [#705](https://github.com/deghosal-2026/CauterRule/issues/705) |
| 7.35 | Corpus source: BugsInPy and Defects4J for python/test failure classes | [#706](https://github.com/deghosal-2026/CauterRule/issues/706) |
| 7.36 | Corpus process: pair each external source with matching success trajectories | [#707](https://github.com/deghosal-2026/CauterRule/issues/707) | ✓ done (checker) |

**Batch progress (code-first ordering):**
- **Batch 1 — gate/matcher safety correctness (done):** #692 (recovery keyword whole-token match), #693 (`_step_shows_success` no longer treats error text in `step.output` as success; exit_code checked first), #694 (`check_domain_mismatch` wired into `rule_matches`, failure trajectories only, to preserve #616 recovery semantics). Tests added in `tests/extraction/test_gate.py` + `tests/replay/test_matcher.py`; full non-field/non-scale/non-docker suite green; ruff/mypy clean on changed files.
- **Batch 2 — threshold provenance + gate-drop observability (done):** #691 (`strategy_for_corpus` segment matching + token-safe `extract_trigger_domain`; new `src/cauterule/replay/calibration.py`, `scripts/calibrate_thresholds.py`, regression test, generated `docs/field-test/v0.3.0/threshold-calibration.md`; calibration also caught and fixed #694's coarse-domain false negatives via domain groups). #697 (gate reason already persisted per-trajectory; added `gate_dropped_by_reason` to `summary.json`, harness tests, and §5.8 spot-audit checklist).
- **Batch 3 — statistical rigor + corpus diagnostics (done):** #695 (`src/cauterule/stats.py` Wilson CI; `confidence_intervals` in `summary.json`; field-test-plan §5.9 reporting format). #690 (new `src/cauterule/replay/diagnostics.py` + `scripts/diagnose_corpus.py`; matcher pre-filter extracted to `trigger_prefilter_reason`; CI guard `tests/corpus/test_v030_corpus_coverage.py`; findings in `docs/field-test/v0.3.0/corpus-diagnostics.md`). Root cause split: `adapters`/`lifecycle`/`mcp` = missing references (b); `otel`/`packs`/`raw/ci` = matcher mismatch (a); extraction pre-filter ruled out.
- **Batch 4 — report regeneration + doc integrity (done):** #686 (`scripts/generate_field_test_report.py` + `docs/field-test/v0.3.0/generated-results.md` with `--check` drift mode, CI step, test drift guard; stale `regression-llama-3.2-3b-vs-v0.2.0.md` marked SUPERSEDED). #685 (corrected 908→1,093/1,156/1,156/1,132 and 3,632→4,537 in the report/per-model/4-model docs). #687 (WBS "see also" traceability links). #688 (`~70 new tests` relabel; Docker gate reworded to "MET (2 re-runs pending)").
- **Batch 5 — semantic/embedding matching (done):** #689 (`src/cauterule/replay/embeddings.py` local MiniLM cosine, opt-in via `CAUTERULE_SEMANTIC_MATCHING=1`; blend `0.5·token-F1 + 0.3·bigram + 0.2·semantic` with a 0.80-similarity floor; LRU embedding cache; `matching` optional extra; tests in `tests/replay/test_semantic_matching.py`; latency benchmark). Semantic path is off by default so existing scores/thresholds are unchanged.
- **Batch 6 — adversarial vectors + corpus balance (done):** #696 (new `corpus/public/adversarial/tool_output_injection/` and `compounding_multiturn/`, 10 vectors each; invariant tests in `tests/corpus/test_adversarial_vectors.py`; wired into the harness adversarial sweep). #707 (`src/cauterule/corpus/balance.py` + `scripts/check_corpus_balance.py`, warn-by-default/`--strict`; tests in `tests/corpus/test_source_balance.py`). Checker flags the known failure-only `CauterRule` reference-expansion source (paired successes = #698 follow-up).
- **Next — Batch 7:** #698-#706 external corpus sourcing + converters (needs datasets).

### M7 Exit Gate

- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated
- [ ] Field test report published with safety-adjusted metrics
- [ ] Known issues documented with severity/workaround/assignee
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Code committed and pushed to branch (`feat-v0.3.0`)
