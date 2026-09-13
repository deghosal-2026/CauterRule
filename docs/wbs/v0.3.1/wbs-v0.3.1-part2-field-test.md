# v0.3.1 — WBS Part 2: Phase 2 — Evaluation & Field Test

**Milestone:** M2 ([v0.3.1-M2: Field Test](https://github.com/deghosal-2026/CauterRule/milestone/67))

**Theme:** Measure the fixes directly (extraction accuracy, reference signatures, reproducible report) and re-verify with a full cloud field test; run the measurements that stayed pending in v0.3.0.

---

## M2: Evaluation & Field Test (60 issues)

> **2026-09-12 update — code review added.** A full-repo review (code, tests, field-test infrastructure) logged 42 defects to M2 plus the replay-directive-invariance bug (#762) — see [Code review findings](#code-review-findings-43-issues) below. M2 is now **60 issues**: 17 original evaluation/field-test + 43 code-review. The 10 Critical code-review defects must be fixed (or explicitly deferred with rationale) before the M2 exit gate, because several undermine the field-test numbers M2 exists to produce.

**Goal:** A fix-and-re-verify release. Add the missing evaluation instrumentation, freeze the corpus, run the full sweep on the corrected pipeline, measure cost / cross-session / human agreement, and publish a report whose every number is reproducible from committed artifacts.

**Execution order:** evaluation implementation (#726, #730) → plan (#733) → runner (#734) → corpus (#735) → calibration (#736) → cloud sweep (#737) → Docker (#738) → multi-env (#739) → cost (#740) → cross-session (#741) → human agreement (#742) → report (#743) → known issues (#744) → exit gate (#745). (#728, #729 frame the measurement/reproducibility goals.)

**Dependencies:** M1 complete (fixes under test). Cost/cross-session/human-agreement depend on the sweep; the report depends on all measurements.

### Evaluation & measurement (kept from the original M2)

| # | Task | Issue |
|---|------|-------|
| 2.1 | Reference corpus: add adapter/CI failure signatures | [#726](https://github.com/deghosal-2026/CauterRule/issues/726) |
| 2.2 | Make field-test report numbers reproducible from artifacts | [#728](https://github.com/deghosal-2026/CauterRule/issues/728) |
| 2.3 | Run release-gate measurements (human agreement, cross-session, cost) | [#729](https://github.com/deghosal-2026/CauterRule/issues/729) |
| 2.4 | Add extraction-accuracy metric vs `expected_rule` | [#730](https://github.com/deghosal-2026/CauterRule/issues/730) |

> These overlap the field-test tickets below (#726↔#735, #730↔#734, #729↔#740-#742, #728↔#743). They were kept per request; close each as its counterpart lands.

### Field test

| # | Task | Issue |
|---|------|-------|
| 2.5 | Create the v0.3.1 field test plan — methodology, corpora, models, thresholds, exit criteria | [#733](https://github.com/deghosal-2026/CauterRule/issues/733) |
| 2.6 | Wire M1/M2 fixes into the runner + add extraction-accuracy measurement | [#734](https://github.com/deghosal-2026/CauterRule/issues/734) |
| 2.7 | Corpus: backfill `expected_rule` and add adapter/CI reference signatures | [#735](https://github.com/deghosal-2026/CauterRule/issues/735) |
| 2.8 | Re-calibrate matcher thresholds after semantic and scorer changes | [#736](https://github.com/deghosal-2026/CauterRule/issues/736) |
| 2.9 | Re-run the full cloud field-test sweep — 2 models × 40 corpora | [#737](https://github.com/deghosal-2026/CauterRule/issues/737) |
| 2.10 | Re-run the Docker field test on the v0.3.1 image | [#738](https://github.com/deghosal-2026/CauterRule/issues/738) |
| 2.11 | Multi-environment validation — macOS, Linux, Docker | [#739](https://github.com/deghosal-2026/CauterRule/issues/739) |
| 2.12 | Cost measurement — token-enabled re-run + `$`/1k table | [#740](https://github.com/deghosal-2026/CauterRule/issues/740) |
| 2.13 | Cross-session repeat-failure reduction protocol (5 sessions) | [#741](https://github.com/deghosal-2026/CauterRule/issues/741) |
| 2.14 | Human-vs-replay agreement sampling and scoring | [#742](https://github.com/deghosal-2026/CauterRule/issues/742) |
| 2.15 | Regenerate and publish the v0.3.1 field test report (reproducible from artifacts) | [#743](https://github.com/deghosal-2026/CauterRule/issues/743) |
| 2.16 | Document known issues from the v0.3.1 field test | [#744](https://github.com/deghosal-2026/CauterRule/issues/744) |
| 2.17 | M2 exit gate — thresholds, tests, docs, committed results | [#745](https://github.com/deghosal-2026/CauterRule/issues/745) |

### Code review findings (43 issues)

**Goal:** a `[0.3.1-M2-CodeReview]` audit of `feat-v0.3.1` @ `be960c2` — replay, extraction/models/serialization, promotion/loop/linter/conflict, CLI/TUI/MCP, packs/export/LLM/benchmark — logged **42 defects** (10 Critical, 32 Important) plus the replay-directive-invariance bug (#762). Each carries file:line, a reproduction, and a suggested fix.

**Why these block M2:** several defects corrupt the measurements M2 exists to publish — cost reports `$0.00` for Anthropic/LiteLLM/Ollama (#802), the end-to-end loop promotes with no gate and never persists (#775), the #727 injection defense has no production caller (#776), and the unsafe-directive blocklist is trivially bypassed (#777). **Fix the Criticals before the M2 exit gate; Importants may be fixed or explicitly deferred with rationale.**

**Fix progress (2026-09-12):** ✅ all 11 Criticals fixed with tests. First batch: CR-1 (#763), CR-2 (#764), CR-7 (#769), CR-8 (#770), CR-13 (#775). Second batch: CR-14 (#776), CR-15 (#777), CR-16 (#778), CR-29 (#791), CR-33 (#795). Third batch: CR-43 (#762) Phase 0 (invariance pinned) + Phase 1 (directive-aware `simulate_outcome` grounding + destructive-directive linter hardening + `auto_promote` guard); Phase 2 (true executor) remains tracked in #720. `mypy src/ tests/`, `ruff check .`, and the non-field/scale/docker `pytest` suite green. Importants batches 1-3 fixed with tests: CR-3/4/5/6/9/10, CR-11/12/17/18/19/20, CR-21/22/23/24/25/26/27/28/30/31/32/39/40. Importants batch 4 (CR-34/35/36/37/38/41/42) fixed. All 43 code-review findings addressed.

**Replay / matcher / cache (6)**

| # | Severity | Task | Issue |
|---|----------|------|-------|
| CR-1 | Critical | ✅ Replay cache key omits `when.signature` → stale verdicts | [#763](https://github.com/deghosal-2026/CauterRule/issues/763) |
| CR-2 | Critical | ✅ `simulate()` doesn't forward threshold to the near-miss path | [#764](https://github.com/deghosal-2026/CauterRule/issues/764) |
| CR-3 | Important | ✅ `is_near_miss` skips the trigger prefilter (degenerate triggers) | [#765](https://github.com/deghosal-2026/CauterRule/issues/765) |
| CR-4 | Important | ✅ Generic-trigger prefilter bypassed by punctuation (`"Error:"`) | [#766](https://github.com/deghosal-2026/CauterRule/issues/766) |
| CR-5 | Important | ✅ `corpus_hash` omits `trajectory.domain` → stale invalidation signal | [#767](https://github.com/deghosal-2026/CauterRule/issues/767) |
| CR-6 | Important | ✅ Vacuous assertion in `tests/replay/test_report.py:29` | [#768](https://github.com/deghosal-2026/CauterRule/issues/768) |

**Extraction / models / serialization (6)**

| # | Severity | Task | Issue |
|---|----------|------|-------|
| CR-7 | Critical | ✅ `Trajectory.from_dict`: `bool()` inverts `success`/`redacted`/`injection_signal` | [#769](https://github.com/deghosal-2026/CauterRule/issues/769) |
| CR-8 | Critical | ✅ `enrich_trajectory` drops `injection_signal` + `expected_outcome*` | [#770](https://github.com/deghosal-2026/CauterRule/issues/770) |
| CR-9 | Important | ✅ `RuleWhen.from_dict` splits scalar `context` into characters | [#771](https://github.com/deghosal-2026/CauterRule/issues/771) |
| CR-10 | Important | ✅ Extraction gate misses state-only failures (`exit_code=1`, no error text) | [#772](https://github.com/deghosal-2026/CauterRule/issues/772) |
| CR-11 | Important | ✅ `load_trajectories` silently drops EOF-truncated multi-line record in strict mode | [#773](https://github.com/deghosal-2026/CauterRule/issues/773) |
| CR-12 | Important | ✅ `is_duplicate` ignores `when.signature` → false dedup | [#774](https://github.com/deghosal-2026/CauterRule/issues/774) |

**Promotion / loop / linter / conflict (12)**

| # | Severity | Task | Issue |
|---|----------|------|-------|
| CR-13 | Critical | ✅ `run_loop` "promotes" with zero gates and never persists | [#775](https://github.com/deghosal-2026/CauterRule/issues/775) |
| CR-14 | Critical | ✅ #727 injection defense wired into `run_loop` (`is_source_tainted`) | [#776](https://github.com/deghosal-2026/CauterRule/issues/776) |
| CR-15 | Critical | ✅ `check_unsafe` blocklist bypassed (`rm -fr`, `push -f`, `chmod 0777`, `\| sudo bash`) | [#777](https://github.com/deghosal-2026/CauterRule/issues/777) |
| CR-16 | Critical | ✅ Rule-ID assignment TOCTOU race → concurrent promotions overwrite | [#778](https://github.com/deghosal-2026/CauterRule/issues/778) |
| CR-17 | Important | ✅ Injection-marker detection bypassed by whitespace/newlines/homoglyphs | [#779](https://github.com/deghosal-2026/CauterRule/issues/779) |
| CR-18 | Important | ✅ `execute_promotion` has no dedup → duplicate active rules | [#780](https://github.com/deghosal-2026/CauterRule/issues/780) |
| CR-19 | Important | ✅ `hybrid_promote` silently disables safety/cutoff/source-trust gates | [#781](https://github.com/deghosal-2026/CauterRule/issues/781) |
| CR-20 | Important | ✅ `check_tautology` false-positives on "note"/"notes" | [#782](https://github.com/deghosal-2026/CauterRule/issues/782) |
| CR-21 | Important | ✅ Near-duplicate check false-positives on distinct failure modes | [#783](https://github.com/deghosal-2026/CauterRule/issues/783) |
| CR-22 | Important | ✅ Hyphenated generic phrases score as "specific" | [#784](https://github.com/deghosal-2026/CauterRule/issues/784) |
| CR-23 | Important | ✅ `consolidate()` sets `superseded` without `superseded_by` → store invalid | [#785](https://github.com/deghosal-2026/CauterRule/issues/785) |
| CR-24 | Important | ✅ Test-suite defects (vacuous poisoning asserts, inverted injection test, fake-ID loop test) | [#786](https://github.com/deghosal-2026/CauterRule/issues/786) |

**CLI / TUI / MCP (8)**

| # | Severity | Task | Issue |
|---|----------|------|-------|
| CR-25 | Important | ✅ `cauterule retire` exits 0 on failure | [#787](https://github.com/deghosal-2026/CauterRule/issues/787) |
| CR-26 | Important | ✅ `cauterule test` ignores `--store` | [#788](https://github.com/deghosal-2026/CauterRule/issues/788) |
| CR-27 | Important | ✅ `cauterule init` overwrites existing `.gitignore` | [#789](https://github.com/deghosal-2026/CauterRule/issues/789) |
| CR-28 | Important | ✅ `cauterule extract` crashes on non-existent path | [#790](https://github.com/deghosal-2026/CauterRule/issues/790) |
| CR-29 | Critical | ✅ `cauterule report --safety-adjusted` saves an empty file | [#791](https://github.com/deghosal-2026/CauterRule/issues/791) |
| CR-30 | Important | ✅ MCP `report_failure` returns `accepted: true` on construction failure | [#792](https://github.com/deghosal-2026/CauterRule/issues/792) |
| CR-31 | Important | ✅ TUI `reject_current` leaves detail panel stale → wrong candidate approved | [#793](https://github.com/deghosal-2026/CauterRule/issues/793) |
| CR-32 | Important | ✅ MCP server allows unauthenticated non-loopback binding | [#794](https://github.com/deghosal-2026/CauterRule/issues/794) |

**Packs / export / LLM / benchmark / measurement (10)**

| # | Severity | Task | Issue |
|---|----------|------|-------|
| CR-33 | Critical | ✅ `pack publish` ships `.git/` (incl. credentials in `.git/config`) | [#795](https://github.com/deghosal-2026/CauterRule/issues/795) |
| CR-34 | Important | ✅ `pack install`: `tar.extractall` without filter → path traversal (3.11–3.13) | [#796](https://github.com/deghosal-2026/CauterRule/issues/796) |
| CR-35 | Important | ✅ Exporters don't escape rule text → forged rule entry (prompt injection) | [#797](https://github.com/deghosal-2026/CauterRule/issues/797) |
| CR-36 | Important | ✅ Aider export emits unescaped YAML → corruption/injection | [#798](https://github.com/deghosal-2026/CauterRule/issues/798) |
| CR-37 | Important | ✅ Gist import skips cert + safety yet reports `cert.passed=True` | [#799](https://github.com/deghosal-2026/CauterRule/issues/799) |
| CR-38 | Important | ✅ Pack `latest` cache stale forever; dropped connection poisons cache | [#800](https://github.com/deghosal-2026/CauterRule/issues/800) |
| CR-39 | Important | ✅ `calibration_loop` low-precision escalation branch is dead | [#801](https://github.com/deghosal-2026/CauterRule/issues/801) |
| CR-40 | Important | ✅ Anthropic/Ollama/LiteLLM drop token usage → cost shows `$0.00` | [#802](https://github.com/deghosal-2026/CauterRule/issues/802) |
| CR-41 | Important | ✅ `import_gist(as_id=...)` silently overwrites existing rule | [#803](https://github.com/deghosal-2026/CauterRule/issues/803) |
| CR-42 | Important | ✅ `compare_versions` raises `TypeError` on mixed segments | [#804](https://github.com/deghosal-2026/CauterRule/issues/804) |

**Related — replay gate directive invariance (1)**

| # | Severity | Task | Issue |
|---|----------|------|-------|
| CR-43 | Critical | ✅ Phases 0–1 done: directive-aware outcome grounding + destructive-directive guard; Phase 2 (#720) tracked | [#762](https://github.com/deghosal-2026/CauterRule/issues/762) |

### Scope notes

- **Models:** cloud only — `gpt-4o-mini`, `llama-3.1-8b-instruct` (local OMLX dropped, #713).
- **Sweep command:** `.venv312` (Python 3.12) + `CAUTERULE_SEMANTIC_MATCHING=1`, OpenRouter `--max-workers 6`.
- **Artifacts:** `field-test/results/0.3.1/` (`meta.json`, `results.jsonl`, `summary.json`, `harness_health.json` per run).
- **Thresholds:** golden ≥70%, failures/positive ≥50%, nearmiss precision ≥90%, adversarial 0, generic <10%, inconclusive <15%.
- **Statistical rigor:** Wilson CIs on every rate; paired per-trajectory model deltas; golden expanded to n≥60 (#735).

### M2 Exit Gate

- [ ] **All tests pass:** `pytest` — all pass
- [ ] **Lint strict clean:** `ruff check .` — zero errors
- [ ] **Types strict clean:** `mypy src/ tests/` (strict) — zero errors
- [ ] **Test coverage > 92%** (deterministic subset)
- [ ] **All necessary and affected docs updated** (field test plan, report, per-model sheets, known issues, WBS)
- [ ] **Code committed and pushed** to `feat-v0.3.1`
- [ ] **WBS updated** (`docs/wbs/v0.3.1/`)
- [ ] **All 60 M2 issues closed**
- [x] All 11 M2 Critical issues fixed, or explicitly deferred with rationale (10 `[0.3.1-M2-CodeReview]` Criticals + #762: #763, #764, #769, #770, #775, #776, #777, #778, #791, #795)
- [ ] Full sweep complete with results committed under `field-test/results/0.3.1/`
- [ ] Release thresholds evaluated and reported (met / not-met with CIs)
- [ ] Cost, cross-session, and human-agreement measured (not `_pending_`)
- [ ] Report regenerated from artifacts; artifact-vs-report drift check passes

### See also

- [Part 1 — Critical Code Fixes](wbs-v0.3.1-part1-fixes.md)
- [Part 3 — Release Readiness & Launch](wbs-v0.3.1-part3-release.md)
- [v0.3.0 WBS Part 3](../v0.3.0/wbs-v0.3.0-part3-field-test.md) (the template)
