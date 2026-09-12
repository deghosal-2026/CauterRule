# PRD 08: Risks

## R1: Overfitting vs. Underfitting

**Risk:** Extracting a rule too narrow (overfit — only matches the exact failure) or too broad (underfit — fires everywhere, breaks everything).
**Mitigation:** The replay harness catches both cases. Overfit rules fail to help on other past failures. Underfit rules break past successes. Both are rejected. Multi-pass extraction + draft tournament reduces both by picking the best of N candidates rather than the first.
**Resolved in v0.3.0 (near-miss false passes):** The near-miss penalty, self-match exclusion, and recovery gate reduced non-applicable-rule false passes from 5–7 per model to 0–1 (near-miss precision 86–90% → 98–100%).
**Severity:** Medium

## R2: Historical Replay Quality

**Risk:** Testing against a sparse or biased history produces false confidence. A rule passes the test but fails in production because the test suite was shallow.
**Mitigation:** Tiered corpus (tiny/small/medium/large). Insufficient history detection warns when replay count is below threshold. Counterexample and near-miss corpora stress-test replay precision. Gold rule families avoid overfitting the benchmark to one phrasing.
**Resolved in v0.3.0 (reference corpus too small):** Reference pool expanded 230 → 444 and scoped to the source domain (#708), lifting recall 2–3× (0.087 → 0.170–0.228) by reducing the denominator to ~10–30 relevant failures. A residual paraphrase gap remains (see R12).
**Severity:** High

## R3: Rule Conflicts at Scale

**Risk:** As the rule store grows, rules contradict each other. Same trigger X says both do Y and do not-Y.
**Mitigation:** Conflict detection with precedence and specificity ordering (v0.1.0). Consolidation merges overlapping triggers. Contradiction stress tests verify >=90% detection recall. Direct contradictions flagged for human review.
**Severity:** Medium

## R4: Curriculum of Failure

**Risk:** The quality of extracted lessons is bounded by the diversity of failures the agent actually sees. If the agent always fails the same way, it learns narrow rules.
**Mitigation:** Coverage gap detector identifies domains with repeated failures but no matching rules. Bundled rule packs (`pack-git`) provide baseline coverage without local learning. Public synthetic corpus expands failure diversity for testing.
**Severity:** Low (design limitation, partially mitigated)

## R5: LLM Extraction Quality

**Risk:** The LLM produces plausible but incorrect rules — it invents a trigger that didn't cause the failure.
**Mitigation:** The replay harness is the safety net. Bad rules are caught before promotion. Multi-pass extraction with temperature variation. Draft tournament picks the best candidate by evidence, not by confidence alone. Confidence calibration tracks whether extractor confidence correlates with replay outcomes.
**Severity:** Medium

## R6: MCP Server Attack Surface

**Risk:** Exposing rules via MCP server opens the system to unauthorized access or injection from remote clients.
**Mitigation:** MCP server supports stdio (local) and HTTP (remote) transports. Remote mode requires authentication. `report_failure` endpoint validates trajectory schema before processing. Rate limiting on extraction requests.
**Resolved in v0.3.0 (MCP auth untested over HTTP):** The Docker field test found an HTTP auth-bypass bug (#601) — the auth guard silently treated remote requests as local stdio. Fixed via the official `mcp` SDK `Context` API; bearer auth, rate limiting, and schema validation now cover remote mode.
**Severity:** Low (v0.1.0 defaults to local stdio)

## R7: Export Leakage

**Risk:** Exporting rules to `.cursorrules`, `CLAUDE.md`, or other formats may leak secret paths, tokens, or internal notes embedded in rule provenance.
**Mitigation:** Export pipeline runs the same redaction as trajectory capture. Instruction leakage tests verify no secrets survive export. Provenance fields are configurable for export (strip/keep).
**Severity:** Medium

## R8: Corpus Bias

**Risk:** The public synthetic corpus is biased toward certain failure types, domains, or toolchains. Rules tested against a biased corpus may not generalize.
**Mitigation:** Domain-specific corpora (coding, DevOps, research, support, browser automation). Trajectory quality labels (clear, ambiguous, multi-causal, misleading, operator-induced). Human vs LLM lesson comparison validates benchmark quality. Corpus contribution guide enables community expansion.
**Resolved in v0.3.0 (corpus coverage narrow):** Corpus expanded from 22 to 40 sources (adapters, lifecycle, packs, mcp, otel, cost, browser, bugsinpy, lifecycle-infra, reference-expansion, adversarial vectors), with a 444-trajectory reference pool.
**Severity:** Medium

## R9: Scale Ceiling

**Risk:** YAML + git may not scale to 10k+ rules or 100k+ trajectories without performance degradation.
**Mitigation:** Scale tests measure replay throughput, injection latency, conflict detection time, and storage churn at 100/1k/10k rules. Incremental indexing benchmarks ensure add-one-rule cost stays small. If YAML + git breaks, the upgrade path is a local index file (SQLite or similar) with git still as the versioning layer.
**Severity:** Low (v0.1.0 targets 1k rules, not 10k)

## R10: Cost Explosion

**Risk:** Multi-pass extraction + draft tournaments + replay testing may make the LLM cost per promoted rule too high for casual use.
**Mitigation:** Cost benchmarks track cost per extracted candidate, cost per promoted rule, and cost per prevented repeat failure. Dry-run mode shows what would be extracted without making an LLM call. Bundled packs provide rules with zero LLM cost. Local models (Ollama) supported for cost-sensitive environments.
**Severity:** Medium

## R11: Adversarial Trajectory Manipulation

**Risk:** A malicious actor crafts a trajectory that produces a rule that looks helpful on replay but introduces a subtle vulnerability or backdoor.
**Mitigation:** Rule linter catches unsafe directives. Data poisoning simulation tests. Provenance chain requires source trajectory reference. Human-review mode for high-stakes environments. Pack certification baseline defines minimum safety checks.
**Severity:** Medium

---

## Open Risks Carried into v0.4.0

The following risks remain open after the v0.3.0 field test.

## R12: Matcher Paraphrase Gap

**Risk:** The token-F1 matcher cannot bridge paraphrases between LLM-extracted triggers and reference-trajectory phrasings even with semantic matching at a 20% blend weight. Golden pass rate is 40–50% (target ≥70%), failures/positive 8–10% (target ≥50%), and curated inconclusive ~75% (target <15%).
**Mitigation:** Raise the semantic blend weight (0.3–0.4), bridge trigger paraphrases, and expand adapter/CI reference vocabulary. Report: `docs/field-test/v0.3.0/FIELD_TEST_REPORT.md`.
**Severity:** High

## R13: Broad-Trigger Penalty Blocking

**Risk:** The safety-first broad-trigger penalty marks candidates that break any success as inconclusive, which blocks legitimate high-precision candidates and depresses failures/positive pass rate.
**Mitigation:** Calibrate the penalty against the near-miss tolerance band; distinguish narrow breakage from broad-trigger breakage by specificity and overlap fraction.
**Severity:** Medium

## R14: Cross-Session Measurement Not Run

**Risk:** The cross-session repeat-failure reduction protocol (target ≥50%) has tooling but no measured result, so the durability of promoted rules across fresh sessions is unproven.
**Mitigation:** Run the 5-session baseline/intervention protocol with `scripts/cross_session.py` and publish the result. Tracked #663/#496.
**Severity:** Medium

## R15: Human-vs-Replay Agreement Not Scored

**Risk:** The human-agreement gate (replay vs reviewer, threshold 0.80) has a sampler and scorer but no reviewer-scored sample, so the trustworthiness of replay-only promotion is unverified.
**Mitigation:** Fill and score the review sample with `scripts/human_agreement.py` before relaxing the human gate. Tracked #493.
**Severity:** Medium

## R16: OMLX Local Models Unusable

**Risk:** Local OMLX models hung on `raw/ci` and ran 5–10× slower, so the local/offline path could not complete a full sweep and remains unvalidated.
**Mitigation:** Per-trajectory watchdog + quarantine landed (#713); cloud runs are the reference. Local model viability is deferred and must be re-validated for offline users.
**Severity:** Low

## R17: OpenSSF Scorecard Posture

**Risk:** The project scores 3.8/10 on the OpenSSF Scorecard, below the posture expected for a security-sensitive tool that handles agent trajectories and secrets.
**Mitigation:** Remediate branch protection, signed releases, dependency pinning, and security policy gaps. Tracked #713.
**Severity:** Medium