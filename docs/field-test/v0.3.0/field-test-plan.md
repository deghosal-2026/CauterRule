# Field Test Plan — CauterRule v0.3.0

**Date:** 2026-09-11
**Milestone:** M7 — Field Test (milestone 62)
**Prior baseline:** v0.2.0 field test (`docs/field-test/v0.2.0/field-test-plan.md`, 720 trajectories, 4 models, 1275 fast-suite)
**Issues:** #625 (plan) · #629 (runner) · #635 (corpus) · #648/#650 (model runs) · #653 (cost) · #663 (cross-session) · #667 (report) · #671 (known issues) · deferred: #489 (corpus 500+), #491 (Fix 8 OMLX), #493 (human agreement), #496 (cross-session ≥50%)
**Docker plan:** `docs/field-test/v0.3.0/docker-test-plan.md` (#641/#642/#676 — closed)
**Deliverables:** this plan → `docs/field-test/v0.3.0/field-test-raw-results.md` → `docs/field-test/v0.3.0/FIELD_TEST_REPORT.md` → `field-test/v0.3.0/known-issues.md`

---

## 1. Objective

v0.2.0 proved the system could extract, gate, and score safely. v0.3.0 turns the rule store into an **ecosystem** — adapters for real frameworks (LangGraph/CrewAI/PydanticAI), a rule lifecycle (specificity → outcomes → retirement → supersession), packs users install, MCP security for remote fleets, OTEL observability, and a cost/latency story. The M7 field test must prove that this ecosystem works **on real models with real frameworks across sessions**, not just in unit and Docker isolation.

Three things v0.3.0 must prove that v0.2.0 could not:

1. **Adapters capture from real framework runs** — not just `@watch` decorator unit tests, but a LangGraph/CrewAI/PydanticAI agent that actually fails, the trajectory is captured through the adapter, a rule is extracted, and the rule fires on the next run.
2. **The lifecycle closes the loop over multiple sessions** — rules accumulate specificity and outcome data, stale rules retire, superseded rules chain, and the **cross-session repeat-failure rate drops ≥50%** after CauterRule intervention (#445/#496).
3. **Packs are installable and replay-honest** — an operator installs `pack-git`/`pack-docker`/`pack-testing`/`pack-deploy`, the pack rules replay against the field-test corpus, and certification + safety gates block a deliberately-unsafe pack.

If any of these fail, v0.3.0 is not ready for release.

---

## 2. Test Phases

Executed sequentially. Each bucket has entry/exit criteria.

| Bucket | Name | Issues | Dependencies |
|--------|------|--------|-------------|
| 0 | Plan + Runner + Corpus | #625, #629, #635 | M4-M6 merged |
| 1 | Pre-Field Validation (hermetic) | #629 (validation suites) | Bucket 0 |
| 2 | Adapter Conformance | #629 (adapter block) | Bucket 1 |
| 3 | Lifecycle + Cross-Session | #663, #496 | Bucket 1 |
| 4 | Pack Ecosystem | #629 (pack block) | Bucket 1 |
| 5 | Model Sweeps | #648, #650 | Buckets 1-4 |
| 6 | Measurements | #653, #491, #493 | Bucket 5 |
| 7 | MCP Security + OTEL (field) | #629 (mcp/otel blocks) | Bucket 5 |
| 8 | Reporting + Known Issues | #667, #671 | Buckets 1-7 |

---

## 3. Corpus — What Trajectories to Test With

### 3.1 Corpus Sources (v0.2.0 baseline + v0.3.0 additions)

The v0.3.0 field test inherits the v0.2.0 corpus (720 trajectories) and adds new trajectories covering the M4-M6 surface. The new trajectories are the gap #635 closes.

| Source | Location | v0.2.0 | v0.3.0 | What's New |
|--------|----------|--------|--------|------------|
| Field-test corpus (curated) | `field-test/corpus/` | 394 | 394 + **adapter trajectories** | LangGraph/CrewAI/PydanticAI agent runs |
| Public corpus | `corpus/public/` | 160 | 160 + **pack fixtures** | Pack-replay fixtures for the 4 official packs |
| **Adapter corpus (NEW)** | `field-test/corpus/adapters/` | 0 | **≥60** | 20 per adapter × 3 frameworks (failure → capture → rule) |
| **Lifecycle corpus (NEW)** | `field-test/corpus/lifecycle/` | 0 | **≥40** | Stale (10), harmful (10), superseded (10), outcome-evolving (10) |
| **Pack-replay corpus (NEW)** | `field-test/corpus/packs/` | 0 | **≥40** | 10 per official pack (docker/deploy/testing/python) — replay against pack rules |
| **MCP/OTEL corpus (NEW)** | `field-test/corpus/mcp/` | 0 | **≥20** | report_failure payloads (valid + malformed + abusive) for schema/rate-limit field testing |
| **Cost corpus (NEW)** | `field-test/corpus/cost/` | 0 | **1000** | Fixed 1k-trajectory sample for $/1k measurement (#486/#653) |
| Reference corpus (expanded) | `corpus/public/` | 230 phrasings | **500+** (#489) | Diverse phrasings for matcher robustness |

**Target total:** ~1,750+ trajectories (up from 720). The 1000-trajectory cost corpus is a fixed sample reused across all models for the $/1k measurement.

### 3.2 Corpus Metadata (v0.2.0 fields + v0.3.0 additions)

Every v0.2.0 field remains required. v0.3.0 adds:

- `framework` — `langgraph` | `crewai` | `pydanticai` | `decorator` | `none` (for adapter trajectories)
- `pack` — pack name when the trajectory is a pack-replay fixture (`pack-git`, `pack-docker`, etc.)
- `lifecycle_stage` — `fresh` | `stale` | `harmful` | `superseded` | `outcome-evolving` (for lifecycle corpus)
- `session_id` — for cross-session trajectories (links trajectories across sessions to measure repeat-failure reduction)

Asserted by an updated `tests/corpus/test_field_test_metadata.py` before any sweep.

### 3.3 Sweep Corpus Allocation

| Sweep | Corpora | Trajectories | Est. Cost |
|-------|---------|-------------|-----------|
| Local OMLX (#648) | adapter, lifecycle, pack-replay, golden, failures/positive, successes, failures/negative, nearmiss, adversarial | ~250 | $0 (local) |
| Cloud OpenRouter (#650) | above + public/domains + cost corpus | ~1,250 | ~$5-15 per model |
| Cross-session (#663) | lifecycle + a 5-session trajectory set | ~40 | $0 (local, 5 sequential sessions) |
| Human review (#493) | sampled N per verdict bucket from sweep | ~40 (sampled) | $0 (human time) |

---

## 4. New Tests in v0.3.0

### 4.1 Pre-Field Validation Suites (#629)

The hermetic non-LLM CI suite expands from v0.2.0's ~1275 to include all M4-M6 additions. New validation suites added to the runner:

| Suite | Targets | Issue | What's New |
|-------|---------|-------|------------|
| `adapter_conformance` | `tests/adapter_conformance/` | #540 (M4) | Per-adapter conformance harness |
| `lifecycle` | `tests/lifecycle/` | #512 (M4) | specificity/outcome/retirement/supersession |
| `packs` | `tests/packs/` | #479/#481 (M5) | create/install/publish/cert/safety |
| `mcp_security` | `tests/mcp/test_security.py` | #601 (M6) | auth/rate-limit/schema (already 60 tests) |
| `otel_exporter` | `tests/integrations/test_otel_exporter.py` | #588 (M6) | mock-collector E2E |
| `corpus_cli` | `tests/cli/test_corpus_cli.py` | #606 (M6) | add/list/validate/lint/build/export |
| `benchmark_cli` | `tests/cli/test_benchmark_cli.py`, `benchmarks/` | #605/#606 (M6) | benchmark list/run/--compare + 15 hot-path benchmarks |

`scripts/run-field-test.py --run-validation` runs all; `--validation-suite <name>` runs one.

### 4.2 Adapter Conformance Field Test (Bucket 2 — NEW, M4)

**Purpose:** prove each adapter captures from a real framework run and the captured trajectory round-trips through extraction → replay → injection.

For each adapter (langgraph, crewai, pydanticai, decorator):

1. Run a minimal agent that fails (e.g., a LangGraph node raises, a CrewAI task errors).
2. Verify the adapter captures the trajectory (via `@watch`/`inject()`/adapter-specific hook).
3. Run extraction on the captured trajectory → candidate rule.
4. Run replay against the candidate → verdict.
5. Re-run the agent with the rule injected → verify the rule fires (matches the task) and the failure is prevented or surfaced.

**Pass criteria:**
- All 3 framework adapters capture a real failure (not a mock) → trajectory written.
- Captured trajectory passes redaction (no secrets).
- Extraction produces a candidate with specificity ≥ moderate.
- Rule fires on re-run (matcher match score ≥ threshold).

### 4.3 Lifecycle + Cross-Session Field Test (Bucket 3 — NEW, M4 + #663/#496)

**Purpose:** prove the lifecycle closes the loop over multiple sessions and the repeat-failure rate drops ≥50%.

**Protocol (per #663):**
1. Establish a baseline: run 5 sessions against the lifecycle corpus **without** CauterRule intervention → record the repeat-failure rate (same failure class recurring across sessions).
2. Enable CauterRule: run the same 5 sessions **with** extraction + promotion → rules accumulate.
3. Measure: per-rule outcomes (prevented/broke/neutral), specificity scores, and the repeat-failure rate in sessions 4-5 vs the baseline.
4. Verify retirement: stale rules (no hits in 5 sessions) auto-retire; harmful rules (broke ≥1) retire.
5. Verify supersession: a rule replaced by a more-specific one chains (`superseded_by` set, history viewable).

**Pass criteria:**
- **Cross-session repeat-failure reduction ≥50%** (#445/#496) — the headline v0.3.0 metric.
- Auto-retirement fires on stale + harmful rules.
- Supersession chains are queryable (`cauterule history <id>` shows the chain).
- Specificity distribution: <10% generic triggers.

### 4.4 Pack Ecosystem Field Test (Bucket 4 — NEW, M5)

**Purpose:** prove packs install, replay honestly, and the certification + safety gates block unsafe packs.

1. Install each official pack from GitHub: `pack install pack-git`, `pack-docker`, `pack-testing`, `pack-deploy`.
2. `pack list` shows all 4; `pack tree` resolves dependencies.
3. Replay each pack's rules against the pack-replay corpus → measure prevented/broke/neutral per pack.
4. **Certification gate:** install a pack with a deliberately-failing cert → blocked (exit ≠0, clear message).
5. **Safety gate:** install a pack with safety score < threshold → blocked.
6. `pack create` from the field-test rule store → produces a shippable pack (pack.yaml + rules).
7. `share <rule-id> as gist` → produces a gist URL with provenance (network-dependent; mock the API in CI).

**Pass criteria:**
- 4 official packs install and replay with ≥1 prevented failure each.
- Cert + safety gates block the two deliberately-unsafe packs.
- `pack create` produces a valid pack.yaml.

### 4.5 Model Sweeps (Bucket 5 — #648, #650)

Same 4 models from v0.2.0 for regression comparison, plus the cost corpus:

| Model | Type | Purpose |
|-------|------|---------|
| Llama-3.2-3B-Instruct-4bit | Local OMLX | Local default regression |
| Qwen3-4B-Instruct-2507-4bit | Local OMLX | Secondary local comparator |
| openai/gpt-4o-mini | Cloud OpenRouter | Cheap cloud baseline |
| meta-llama/llama-3.1-8b-instruct | Cloud OpenRouter | Strongest cost-effective |

**Preflight gates model selection** before each sweep (#486): `cauterule preflight --corpus <path>` aborts on FAIL, prints cost estimate, enforces `--max-cost` cap.

### 4.6 MCP Security + OTEL Field Test (Bucket 7 — NEW, M6)

**MCP security (remote mode, #601):** the docker field test already proved auth/rate-limit/schema over a mapped port. The field test adds a **real agent driving the MCP server**:

1. Start `cauterule mcp --transport http --auth-mode bearer` with a token.
2. Connect a real MCP client (the official `mcp` SDK ClientSession) with the bearer token.
3. Drive `list_rules`/`get_rule`/`get_matching_rules`/`report_failure` over the remote transport.
4. Verify an unauthenticated client is rejected (401 payload); an abusive client (burst) is rate-limited (429 payload); a malformed `report_failure` is schema-rejected (400 payload).

**OTEL exporter (#588):** start a real OTLP collector (Jaeger or Tempo via `docker compose`), configure `[otel]` in `cauterule.toml`, run a sweep, verify the 4 span types (`rule.match`/`rule.promote`/`rule.retire`/`replay.verdict`) arrive with correct attributes. Verify emit failure is non-fatal (kill the collector mid-run → pipeline continues).

### 4.7 Benchmark + Perf-Regression (Bucket 1 — #605)

The 15 pytest-benchmark hot paths run as a validation suite (`benchmarks/`). The field test additionally verifies the **perf-regression CI** (`scripts/compare_benchmarks.py` against `.benchmarks/main.json`) catches a deliberate regression (revert the #P3-B5 budget fix → CI fails >15%).

---

## 5. New Methodology in v0.3.0

### 5.1 Adapter Conformance Harness (#540)

Per-adapter: a minimal failing agent → capture → extract → replay → re-run-with-injection. The harness lives in `tests/adapter_conformance/` and is reused as a validation suite AND a field-test block.

### 5.2 Lifecycle Measurement (#663)

The cross-session protocol (§4.3) is new. The runner (`scripts/run-field-test.py`) gains a `--cross-session` mode: runs N sessions sequentially, persists the rule store between sessions, and computes the repeat-failure rate delta (baseline vs intervention).

### 5.3 Pack Replay Scoring

Pack rules replay against the pack-replay corpus using the same `classify_outcome` + safety-adjusted scoring as v0.2.0. A pack "prevents" a failure if its rule matches AND the trajectory's expected outcome is `should_extract`. A pack "breaks" if it matches a `should_silence` trajectory.

### 5.4 Cost Measurement (#653, #486)

The fixed 1000-trajectory cost corpus runs once per model. Per-model metrics:
- Cost per candidate = total_cost / candidates_produced
- Cost per promoted rule = total_cost / rules_promoted
- **$/1k trajectories** = (input+output tokens × price) / 1000 — the headline #486 metric
- Pre-extraction gate savings = dropped_trajectories × cost_per_request

The results feed the tiering table (local = $0, cheap cloud, flagship) already shipped in `preflight --cost-table`.

### 5.5 Human-vs-Replay Agreement (#493, deferred M2 → now)

After each sweep, sample N candidates per verdict bucket (pass/inconclusive/fail). Reviewer scores trigger specificity, directive actionability, safety, and replay-vs-human agreement. `replay_vs_human_agreement = matches / total_reviewed`. Promotion gate requires human approval if agreement <0.8.

### 5.6 Fix 8 Recovery Exclusion Re-run (#491, deferred M2 → now)

Re-run the v0.1.0 "Fix 8" (recovery exclusion) on the 2 OMLX local models. v0.1.0 measured this on cloud only; v0.3.0 re-runs on local OMLX to verify the exclusion holds on the local model tier.

### 5.7 Inherited v0.2.0 Methodology

Pre-extraction gate (#428), replay matcher (#417), inconclusive attribution (#419), trigger specificity (#424), safety scoring (#421/#418), harness health (#430) — all unchanged from v0.2.0 §5. The v0.3.0 runner reuses these scoring functions.

---

## 6. New Thresholds in v0.3.0

### 6.1 Release Thresholds (v0.2.0 inherited + v0.3.0 new)

| Threshold | Target | Source | Validated By |
|-----------|--------|--------|--------------|
| `successes` pass rate | 0% | v0.2.0 | sweep |
| `failures/negative` pass rate | 0% | v0.2.0 | sweep |
| `nearmiss` precision | ≥90% | v0.2.0 | sweep |
| `golden` pass rate | ≥70% | v0.2.0 | sweep |
| `failures/positive` pass rate | ≥50% | v0.2.0 | sweep |
| Curated inconclusive | <15% | v0.2.0 | sweep |
| Raw inconclusive | <40% | v0.2.0 | sweep |
| Generic triggers | <10% | v0.2.0 | sweep |
| **Cross-session repeat-failure reduction** | **≥50%** | **#445/#496** | **#663 protocol (§4.3)** |
| **Adapter capture rate** | **3/3 frameworks** | **#540** | **Bucket 2 (§4.2)** |
| **Pack replay** | **4/4 packs, ≥1 prevented each** | **#479** | **Bucket 4 (§4.4)** |
| **Pack cert/safety gate** | **2/2 unsafe blocked** | **#481** | **Bucket 4 (§4.4)** |
| **MCP unauth/burst/malformed rejected** | **100%** | **#601** | **Bucket 7 (§4.6)** |
| **OTEL span types emitted** | **4/4** | **#588** | **Bucket 7 (§4.6)** |
| **Human-vs-replay agreement** | **documented; human gate if <0.8** | **#493** | **Bucket 6** |

### 6.2 Cost Thresholds (#486)

| Model tier | $/1k trajs | Expected p95 extract | Target tier role |
|-----------|-----------|----------------------|------------------|
| local (Llama-3.2-3B, Qwen3-4B) | ~$0 | ~1.0-1.1s | iteration/regression |
| cheap cloud (gpt-4o-mini) | ~$1.60 | ~1.2s | PR/release gate |
| flagship (gpt-4o) | ~$20 | ~2.5s | calibration/disputed |

Measured values recorded in `docs/field-test/v0.3.0/cost-measurement.md` (#653); the measured table must match `preflight --cost-table` output.

---

## 7. New Scoring in v0.3.0

### 7.1 Safety-Adjusted Ranking (formula — v0.2.0, reused verbatim)

```
safety_adjusted_pass = total_pass - successes_pass - failures_negative_pass
safety_violation_rate = (successes_pass + failures_negative_pass) / total_pass
wrong_decision_rate = new_fail / (new_pass + new_fail)   # for model-pair upgrade
```

All models ranked by **both** raw-total and safety-adjusted; the report shows both rankings and flags any inversion.

### 7.2 Pack Replay Score (NEW)

```
pack_prevented = # pack-rule matches on should_extract trajectories
pack_broke     = # pack-rule matches on should_silence trajectories
pack_score     = pack_prevented / (pack_prevented + pack_broke)   if any matches, else 0
```

Target: pack_score ≥0.5 for each official pack and ≥1 prevented per pack.

### 7.3 Cross-Session Delta (NEW)

```
repeat_failure_rate(sessions) = repeat_failures / total_failures   # same failure_class recurring
reduction = 1 - (rate_intervention_sessions_4_5 / rate_baseline_sessions_4_5)
```

Target: reduction ≥0.50 (#445/#496).

### 7.4 Cost Scoring (v0.2.0 #447 formula, reused)

```
cost_per_candidate     = total_cost / candidates_produced
cost_per_promoted_rule = total_cost / rules_promoted
cost_per_1k_trajs      = (input_tokens × in_price + output_tokens × out_price) / (trajs / 1000)
gate_savings           = dropped_trajectories × cost_per_request
```

### 7.5 Comparison to v0.2.0 Baseline (NEW — methodology)

1. Load the v0.2.0 per-corpus summaries from `field-test/results/0.2.0/{corpus}/{model}/{date}/summary.json`.
2. Re-run the same corpora with the same 4 models in v0.3.0.
3. `scripts/run-field-test.py --regression-v020` emits a per-corpus delta table (pass rate, inconclusive rate, specificity distribution, silence rate) v0.3.0 vs v0.2.0.
4. Any v0.3.0 metric **worse** than v0.2.0 by >5pp fails the regression check and must be root-caused in the report (#667).

---

## 8. Models to Test

Same 4 models as v0.2.0 (regression comparison), swept on the v0.3.0 corpora:

| Model | Type | Tier | Config | Purpose |
|-------|------|------|--------|---------|
| Llama-3.2-3B-Instruct-4bit | Local OMLX | local | `--llm-provider openai --llm-base-url http://localhost:8000/v1 --llm-model llama-3.2-3b-instruct` | Local default regression |
| Qwen3-4B-Instruct-2507-4bit | Local OMLX | local | same, model `qwen3-4b-instruct` | Secondary local comparator |
| openai/gpt-4o-mini | Cloud OpenRouter | cheap cloud | `--llm-base-url https://openrouter.ai/api/v1` | Cheap cloud baseline |
| meta-llama/llama-3.1-8b-instruct | Cloud OpenRouter | cheap cloud | same | Strongest cost-effective |

- Optional flagship anchor (gpt-4o) for the cost table only, not the full sweep.
- Model-specific overrides via `--model-config models.yaml` (#629): per-model temperatures, extraction passes, max-cost.
- **Preflight gates every sweep** (#486): `cauterule preflight --corpus <path> --max-cost <cap>` — aborts on FAIL; the Qwen3.5-4B 3-4x-slower incident from v0.1.0 is the canonical reason this gate exists.

---

## 9. Runner and Harness Changes (#629)

`scripts/run-field-test.py` gains:

| Flag | Purpose | Issue |
|------|---------|-------|
| `--cross-session` | Run N sessions sequentially, persist store, compute repeat-failure delta (§7.3) | #663 |
| `--adapter` | Adapter conformance block (per framework or --all) | #540 |
| `--pack` | Pack ecosystem block (install/replay/cert/safety) | #479/#481 |
| `--mcp-security` | MCP remote security block (real agent + bearer) | #601 |
| `--otel` | OTEL emit block (real collector) | #588 |
| `--cost-corpus` | 1k-trajectory cost measurement (§7.4) | #653 |
| `--human-review` | Sample candidates for human agreement scoring | #493 |
| `--model-config` | Multi-model YAML config (per-model overrides) | #629 |
| `--regression-v020` | Delta table vs v0.2.0 baseline (§7.5) | #629 |

New validation suites added to `VALIDATION_SUITES` (§4.1): `adapter_conformance`, `lifecycle`, `packs`, `mcp_security`, `otel_exporter`, `corpus_cli`, `benchmark_cli`. Results output to `field-test/0.3.0/` (docker results already at `field-test/0.3.0/docker/`).

---

## 10. Acceptance Criteria

### 10.1 Pre-Field Validation (Bucket 1)
- [ ] Hermetic CI suite passes (all M4-M6 additions)
- [ ] 15 benchmarks green; perf-regression CI catches a deliberate regression
- [ ] Adapter conformance suite passes (3 frameworks import + capture)
- [ ] Lifecycle suite passes (specificity/outcome/retirement/supersession)
- [ ] Pack suite passes (create/install/cert/safety)
- [ ] MCP security suite passes (60 tests)
- [ ] OTEL exporter suite passes (mock collector)

### 10.2 Adapter + Lifecycle + Packs (Buckets 2-4)
- [ ] 3 framework adapters capture a real failure → rule fires on re-run
- [ ] Cross-session repeat-failure reduction ≥50%
- [ ] Auto-retirement fires on stale + harmful rules
- [ ] Supersession chains queryable
- [ ] 4 official packs install + replay (≥1 prevented each)
- [ ] Cert + safety gates block 2 unsafe packs

### 10.3 Model Sweeps (Bucket 5)
- [ ] Local OMLX sweep complete (2 models, safety-adjusted scoring)
- [ ] Cloud sweep complete (2 models, decision economics)
- [ ] Safety corpora: 100% silence on successes + failures/negative; ≥90% nearmiss precision
- [ ] Golden ≥70%, failures/positive ≥50%

### 10.4 Measurements (Bucket 6)
- [ ] $/1k trajs + p50/p95 latency recorded per model; matches `preflight --cost-table`
- [ ] Human-vs-replay agreement documented per corpus
- [ ] Fix 8 recovery exclusion re-run on OMLX (2 models)

### 10.5 MCP Security + OTEL (Bucket 7)
- [ ] Real MCP client drives all 4 tools over HTTP with bearer auth
- [ ] Unauth → 401; burst → 429; malformed → 400 (payload-level)
- [ ] OTEL: 4 span types arrive at a real collector with correct attributes
- [ ] OTEL emit failure non-fatal (collector killed mid-run → pipeline continues)

### 10.6 Reporting (Bucket 8)
- [ ] Field test report published (#667) with all sections (§12 deliverables)
- [ ] Known issues documented (#671) using the template (Appendix B)
- [ ] Regression table vs v0.2.0 baseline included (§7.5)

---

## 11. Release Gate (v0.3.0)

| Check | Threshold | Source |
|-------|-----------|--------|
| v0.2.0 release thresholds (all) | per v0.2.0 §11 | inherited |
| Cross-session repeat-failure reduction | ≥50% | #445/#496 |
| Adapter capture | 3/3 frameworks | #540 |
| Pack replay + gates | 4 packs replay, 2 unsafe blocked | #479/#481 |
| MCP remote security | unauth/burst/malformed rejected | #601 |
| OTEL span emission | 4/4 span types | #588 |
| Cost/latency published | $/1k + tiering | #486 |
| Docker field test | 153 tests pass | #641/#642 (closed) |
| Human-vs-replay agreement | documented | #493 |
| Corpus expansion | 500+ phrasings | #489 |
| Multi-env validation | macOS + Linux + Docker | #658 (closed) |

---

## 12. Deliverables

| Artifact | Issue | Location |
|----------|-------|----------|
| Field test plan | #625 | `docs/field-test/v0.3.0/field-test-plan.md` (this) |
| Runner updates | #629 | `scripts/run-field-test.py` |
| Corpus update | #635 | `field-test/corpus/adapters/`, `lifecycle/`, `packs/`, `mcp/`, `cost/` |
| Docker plan + results | #641/#642 | `docs/field-test/v0.3.0/docker-test-plan.md`, `docker-test-results.md` (closed) |
| Raw results | #648/#650 | `docs/field-test/v0.3.0/field-test-raw-results.md` |
| Cross-session results | #663 | `docs/field-test/v0.3.0/cross-session-results.md` |
| Cost measurement | #653 | `docs/field-test/v0.3.0/cost-measurement.md` |
| Human agreement | #493 | `docs/field-test/v0.3.0/human-agreement.md` |
| Field test report | #667 | `docs/field-test/v0.3.0/FIELD_TEST_REPORT.md` |
| Known issues | #671 | `field-test/v0.3.0/known-issues.md` (template: Appendix B) |

---

## 13. How This Plan Maps to the M1-M6 Surface

| M1-M6 area | Field test plan § | M7 issue |
|------------|-------------------|----------|
| M1-M3 critical fixes + gates | §4.1 validation suites, §14 corpus | #629 |
| M4 adapters (LangGraph/CrewAI/PydanticAI/@watch) | §4.2, §5.1 | #629, #540 |
| M4 lifecycle (specificity/outcomes/retirement/supersession) | §4.3, §5.2, §7.3 | #663, #496 |
| M5 packs (create/install/publish/cert/safety) | §4.4, §5.3, §7.2 | #629, #479/#481 |
| M5 DX (observe/badge/webhook/scenarios) | §4.1 suites; docker plan §13 | #629 |
| M6 corpus CLI + benchmark CLI + perf CI | §4.1, §4.7 | #605/#606 (closed) |
| M6 MCP security (auth/rate-limit/schema) | §4.6 | #601, #676 (docker closed) |
| M6 OTEL exporter | §4.6 | #588 |
| M6 cost/latency + preflight | §6.2, §7.4, §8 | #486, #653 |
| M6 Docker hardening | docker-test-plan.md (closed) | #524/#607/#641/#642 (closed) |
| Deferred M2: corpus 500+, Fix 8 OMLX, human agreement, cross-session | §5.5-§5.6, §4.3, §14 | #489, #491, #493, #496 |

---

## 14. Corpus Plan (#635)

### 14.1 Corpus Inventory

Total: **~1,750+ trajectories** across 27 sources (v0.2.0's 20 + 7 new).

| Source | Count | Expected Outcome | Gate Mode | Sweep Role |
|--------|-------|-----------------|-----------|------------|
| successes | 60 | `should_silence` | strict | Safety validation |
| failures/positive | 30 | `should_extract` | relaxed | Extraction quality |
| failures/negative | 50 | `should_silence` | strict | Safety validation |
| nearmiss | 50 | `should_reject` | strict | Precision testing |
| noisy | 5 | `should_extract` | relaxed | Robustness |
| corrections | 5 | `should_extract` | relaxed | Human correction |
| golden | 10 | `should_extract` | relaxed | Benchmark acceptance |
| raw/ci | 110 | mixed | strict | Inconclusive rate |
| raw/opencode | 25 | mixed | strict | Inconclusive rate |
| raw/synthetic | 145 | mixed | strict | Inconclusive rate |
| raw/sibling-repos | 10 | mixed | strict | Cross-repo transfer |
| raw/corrections | 5 | mixed | strict | Raw corrections |
| raw/cross-session | 5 | mixed | strict | Cross-session |
| public/golden | 10 | `should_extract` | relaxed | Gold-family benchmark |
| public/counterexample | 20 | `should_reject` | relaxed | Rejection testing |
| public/nearmiss | 20 | `should_reject` | relaxed | Precision testing |
| public/staleness | 10 | `should_reject` | relaxed | Staleness detection |
| public/synthetic | 50 | mixed | relaxed | Shareable benchmark |
| public/domains | 50 | mixed | relaxed | Per-domain coverage |
| public/adversarial | 50 | `should_reject` | strict | Security testing |
| **adapters/langgraph (NEW)** | **20** | `should_extract` | relaxed | Adapter capture |
| **adapters/crewai (NEW)** | **20** | `should_extract` | relaxed | Adapter capture |
| **adapters/pydanticai (NEW)** | **20** | `should_extract` | relaxed | Adapter capture |
| **lifecycle (NEW)** | **40** | mixed (stale/harmful/superseded/outcome-evolving) | strict | Lifecycle + cross-session |
| **packs (NEW)** | **40** | `should_extract` | relaxed | Pack replay |
| **mcp (NEW)** | **20** | mixed (valid/malformed/abusive) | strict | MCP security field |
| **cost (NEW)** | **1000** | mixed | relaxed | $/1k measurement |

Reference corpus expansion: 230 → 500+ diverse phrasings (#489) folded into `public/synthetic` + `public/domains`.

### 14.2 Sweep Corpus Allocation

| Sweep | Corpora | Trajectories | Est. Cost |
|-------|---------|-------------|-----------|
| Local OMLX (#648) | adapters, lifecycle, packs, golden, failures/positive, successes, failures/negative, nearmiss, adversarial | ~380 | $0 |
| Cloud OpenRouter (#650) | above + public/domains + cost corpus | ~1,430 | ~$5-15/model |
| Cross-session (#663) | lifecycle + 5-session set | ~40 | $0 (local) |
| Human review (#493) | sampled per verdict bucket | ~40 | $0 (human time) |

### 14.3 Expected Outcomes Tied to Release Thresholds

| Corpus | Expected Outcome | Release Threshold | Validated By |
|--------|-----------------|-------------------|--------------|
| successes | 100% silence (gate drops) | 0% pass | sweep |
| failures/negative | 100% silence | 0% pass | sweep |
| nearmiss | ≥90% precision | ≥90% | sweep |
| golden | ≥70% pass | ≥70% | #648/#650 |
| failures/positive | ≥50% pass | ≥50% | #648/#650 |
| curated (all) | <15% inconclusive | <15% | sweep |
| raw (all) | <40% inconclusive | <40% | sweep |
| adversarial | 0 promoted | 0 promoted | §4.1 suite |
| adapters | capture → extract → fire | 3/3 frameworks | §4.2 |
| lifecycle | stale/harmful retire; supersession chains | ≥50% reduction | §4.3 |
| packs | ≥1 prevented per pack | 4/4 packs | §4.4 |
| mcp | valid accepted; malformed/abusive rejected | 100% | §4.6 |
| cost | cost table matches preflight | documented | §7.4 |

### 14.4 Domain Balance

New corpora cover the 8 canonical domains (git, python, docker, ci, shell, browser_automation, research, support), ≥5 per safety corpus, unchanged from v0.2.0 §14.4. Adapter corpora add 5 framework-domain trajectories per framework. Lifecycle corpora distribute stale/harmful/superseded/outcome-evolving 10/10/10/10 across domains.

### 14.5 Metadata Validation

All trajectories validated by an updated `tests/corpus/test_field_test_metadata.py`:

- v0.2.0 fields: `trajectory_id`, `timestamp`, `task`, `steps`, `success`, `domain`, `quality_label`, `tags`, `failure_point`, `failure_class`, `severity`, `expected_outcome`, `expected_outcome_rationale`
- **v0.3.0 additions:** `framework` (adapters), `pack` (packs), `lifecycle_stage` (lifecycle), `session_id` (cross-session)

Gate verification (v0.2.0 parity): successes 60/60 dropped, failures/negative 50/50 dropped, nearmiss 0/50 dropped.

---

## 15. Methodology

### 15.1 Test Harness

**Runner:** `scripts/run-field-test.py` (v0.3.0 updated, §9). Output to `field-test/0.3.0/`. Per-run artifacts: `meta.json`, `preflight.json`, `results.jsonl`, `summary.json`, `harness_health.json` + new: `cross-session-delta.json`, `pack-replay.json`, `cost.json`.

### 15.2 Extraction Pipeline (v0.2.0 + v0.3.0 additions)

1. **Preflight** — provider + corpus + **cost estimate + `--max-cost` cap** (#486). Abort on FAIL.
2. **Gate** — strict on successes/failures-negative/nearmiss/adversarial/mcp-malformed; relaxed on golden/failures-positive/adapters/packs/cost.
3. **LLM extraction** — multi-pass (default 2, temps 0.2 + 0.5).
4. **Replay testing** — corpus-aware thresholds (0.70 curated, 0.45 raw, 0.40 cross-repo).

### 15.3 Scoring

Per-trajectory outcome: `classify_outcome(...)` → silence | parse_failure | rejected | accepted (v0.2.0). Safety: `score_safety_trajectory` / `safety_summary` (v0.2.0). Ranking + pack + cross-session formulas: §7.

### 15.4 Specificity Scoring (v0.2.0)

`score_specificity(trigger)` → specific | moderate | generic; generic <10% target; distribution reported per corpus.

### 15.5 Inconclusive Attribution (v0.2.0)

`attribute_inconclusive(...)` → broad_trigger | matcher_gap | corpus_mismatch | ambiguous_evidence; aggregated per corpus and per model.

### 15.6 Harness Health (v0.2.0)

Parse rate ≥70% hard gate; completion ratio per-corpus range; model results gated on `health.passed`.

### 15.7 Adapter Conformance Protocol (NEW)

Per §4.2: real framework failure → adapter capture → redaction check → extraction → replay → re-run with injection → rule fires. Runs once per framework on local OMLX.

### 15.8 Cross-Session Protocol (NEW)

Per §4.3: 5 sessions baseline (no CauterRule) → 5 sessions with intervention, store persisted between sessions → §7.3 delta. `session_id` links trajectories across sessions.

### 15.9 Human Review Sampling (v0.2.0 #425 + #493)

Sample N per verdict bucket; reviewer scores specificity/actionability/safety/agreement; `replay_vs_human_agreement = matches / total_reviewed`; human gate if <0.8.

### 15.10 Cost Measurement (v0.2.0 #447 + #486)

Fixed 1000-trajectory corpus per model; §7.4 formulas; results feed `preflight --cost-table` and the tiering table (§6.2).

### 15.11 Multi-Environment Validation (procedure — #658, closed)

| Environment | Procedure | Evidence |
|-------------|-----------|----------|
| macOS (local) | Full fast suite + docker-marked suite via Docker Desktop (Apple Silicon/arm64) | `field-test/0.3.0/docker/docker-results.jsonl` |
| Linux | CI runner (amd64): fast suite + docker suite | CI logs; junit `docker-junit.xml` |
| Docker | `scripts/docker_field_test.sh` — 18-stage plan (hardened image, compose profiles, MCP http, multi-arch readiness) | `docker-test-results.md` (closed #641/#642) |

Cross-env parity asserted: same test selection (`-m docker`), same results dir pattern, same junit schema.

### 15.12 Environment Summary

| Environment | Purpose | LLM |
|-------------|---------|-----|
| macOS (local) | OMLX sweeps, adapters, cross-session, TUI, OTEL | OMLX (free) |
| Linux (CI/Docker) | Cloud sweeps, multi-env, MCP security | OpenRouter (paid) |
| Docker | Full suite + compose + multi-arch | Mock (hermetic) |

### 15.13 Success Criteria

A v0.3.0 sweep is successful if it meets all v0.2.0 criteria (v0.2.0 §15.10) PLUS:
1. Cross-session repeat-failure reduction ≥50%.
2. Adapter capture 3/3 frameworks.
3. Pack replay 4/4 packs (≥1 prevented each); 2/2 unsafe blocked.
4. MCP unauth/burst/malformed rejected; OTEL 4/4 span types.
5. Cost/latency published per model, matching `preflight --cost-table`.

---

## Appendix A — Docker Test Scenarios (summary; full detail in docker-test-plan.md, closed)

| Scenario | Expected Outcome | Status |
|----------|-----------------|--------|
| Build & hardening (non-root, git, healthcheck, OCI labels, .dockerignore) | all assertions pass | ✅ closed |
| Compose profiles (name:, no dead port, mcp baked in) | bare up starts nothing; profiled services work | ✅ closed |
| Corpus/benchmark/pack/adapter/lifecycle CLIs in-container | round-trips OK | ✅ closed |
| MCP stdio + HTTP bearer auth (401/400/429 payloads) | all rejection paths + happy path | ✅ closed |
| OTEL emit non-fatal on bad endpoint | command returns control | ✅ closed |
| Preflight cost table + --max-cost | table prints; cap enforced | ✅ closed |
| Rule/pack persistence across containers | A → B survival | ✅ closed |
| Multi-arch readiness, image size, resource/network limits | documented/asserted | ✅ closed |

## Appendix B — Known Issues Template (#671)

```markdown
## KI-<n>: <title>
**Severity:** blocker | high | medium | low
**Area:** adapters | lifecycle | packs | mcp | otel | corpus | benchmark | cost | docker | core
**Symptom:** <what was observed in the field>
**Reproduction:** <command + corpus + model>
**Workaround:** <operator-facing mitigation, if any>
**Assignee:** <who>
**Status:** open | fixed | deferred (target milestone)
