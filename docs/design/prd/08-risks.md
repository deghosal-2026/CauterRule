# PRD 08: Risks

## R1: Overfitting vs. Underfitting

**Risk:** Extracting a rule too narrow (overfit — only matches the exact failure) or too broad (underfit — fires everywhere, breaks everything).
**Mitigation:** The replay harness catches both cases. Overfit rules fail to help on other past failures. Underfit rules break past successes. Both are rejected.
**Severity:** Medium

## R2: Historical Replay Quality

**Risk:** Testing against a sparse or biased history produces false confidence. A rule passes the test but fails in production because the test suite was shallow.
**Mitigation:** Track historical scenario diversity. Warn when replay count is below threshold. Support synthetic scenario generation (AgentEvalForge in v0.3+).
**Severity:** High

## R3: Rule Conflicts at Scale

**Risk:** As the rule store grows, rules contradict each other. Same trigger X says both do Y and do not-Y.
**Mitigation:** Conflict detection with precedence and specificity ordering (v0.2.0). Direct contradictions flagged for human review.
**Severity:** Medium (v0.1.0), Low (v0.2.0+)

## R4: Curriculum of Failure

**Risk:** The quality of extracted lessons is bounded by the diversity of failures the agent actually sees. If the agent always fails the same way, it learns narrow rules.
**Mitigation:** No architectural mitigation — this is an inherent limitation. Document as known constraint.
**Severity:** Low (design limitation, not bug)

## R5: LLM Extraction Quality

**Risk:** The LLM produces plausible but incorrect rules — it invents a trigger that didn't cause the failure.
**Mitigation:** The replay harness is the safety net. Bad rules are caught before promotion. Multiple extraction passes with temperature variation for robustness.
**Severity:** Medium