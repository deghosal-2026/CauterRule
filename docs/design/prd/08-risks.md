# PRD 08: Risks

## R1: Overfitting vs. Underfitting

**Risk:** Extracting a rule too narrow (overfit — only matches the exact failure) or too broad (underfit — fires everywhere, breaks everything).
**Mitigation:** The replay harness catches both cases. Overfit rules fail to help on other past failures. Underfit rules break past successes. Both are rejected. Multi-pass extraction + draft tournament reduces both by picking the best of N candidates rather than the first.
**Severity:** Medium

## R2: Historical Replay Quality

**Risk:** Testing against a sparse or biased history produces false confidence. A rule passes the test but fails in production because the test suite was shallow.
**Mitigation:** Tiered corpus (tiny/small/medium/large). Insufficient history detection warns when replay count is below threshold. Counterexample and near-miss corpora stress-test replay precision. Gold rule families avoid overfitting the benchmark to one phrasing.
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
**Severity:** Low (v0.1.0 defaults to local stdio)

## R7: Export Leakage

**Risk:** Exporting rules to `.cursorrules`, `CLAUDE.md`, or other formats may leak secret paths, tokens, or internal notes embedded in rule provenance.
**Mitigation:** Export pipeline runs the same redaction as trajectory capture. Instruction leakage tests verify no secrets survive export. Provenance fields are configurable for export (strip/keep).
**Severity:** Medium

## R8: Corpus Bias

**Risk:** The public synthetic corpus is biased toward certain failure types, domains, or toolchains. Rules tested against a biased corpus may not generalize.
**Mitigation:** Domain-specific corpora (coding, DevOps, research, support, browser automation). Trajectory quality labels (clear, ambiguous, multi-causal, misleading, operator-induced). Human vs LLM lesson comparison validates benchmark quality. Corpus contribution guide enables community expansion.
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