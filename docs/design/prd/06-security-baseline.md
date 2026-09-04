# PRD 06: Security Baseline

## Threat Model

### T1: Injection via Trajectory Content
- A malicious trajectory could contain prompt-injection payloads aimed at the rule extractor LLM
- **Mitigation:** Structured output parsing with schema validation; output is constrained to *when X, do Y* form. Prompt injection corpus tests resistance (target: >=90% of injection attempts fail to alter valid extractor output)

### T2: Unauthorized Rule Promotion
- A compromised agent could promote harmful rules
- **Mitigation:** Promotion gate supports human-review and hybrid modes; all promotions are git-committed with provenance. Rule linter blocks unsafe directives (target: >=95% block rate)

### T3: Sensitive Data in Trajectories
- Execution traces may contain API keys, tokens, or proprietary logic
- **Mitigation:** Trajectory redaction strips secrets before LLM extraction via configurable patterns + auto-detection. Redaction corpus validates 100% success rate. Trajectories are local-first; no data leaves the filesystem unless explicitly configured.

### T4: Instruction Leakage via Export
- Exported rules (`CLAUDE.md`, `.cursorrules`, etc.) may leak secret paths, tokens, or internal notes
- **Mitigation:** Export pipeline runs the same redaction as trajectory capture. Instruction leakage tests verify no secrets survive export.

### T5: Data Poisoning
- Corrupted or fabricated trajectories attempt to poison rule promotion
- **Mitigation:** Data poisoning simulation tests. Provenance chain requires source trajectory reference. Replay harness catches poisoned candidates if they fail on real history.

### T6: Misleading Root Cause
- Visible failure differs from actual root cause; extractor grabs superficial lessons
- **Mitigation:** Misleading root-cause corpus tests. Multi-pass extraction with temperature variation reduces single-pass bias. Draft tournament picks the best candidate, not just the first.

### T7: Contradiction at Scale
- Intentionally or accidentally generated conflicting rules
- **Mitigation:** Conflict detection with precedence and specificity ordering. Contradiction stress tests verify >=90% detection recall. Direct contradictions flagged for human review.

## Design Principles

- **Local-first by default:** No cloud dependency, no data exfiltration risk
- **Git as audit trail:** Every promotion is a git commit with full provenance
- **Human-in-the-loop option:** Promotion gate can require human approval (hybrid mode)
- **Minimal dependencies:** Python standard library + LLM API (local or remote)
- **Redaction before extraction:** Secrets never reach the LLM
- **Linter before promotion:** Unsafe or low-quality rules never enter the store
- **Validate before trust:** `cauterule validate` checks store integrity before production use

## Adversarial Testing Coverage (v0.1.0)

| Corpus | What it tests | Target |
|--------|--------------|--------|
| Prompt injection | Extractor output manipulation | >=90% resistance |
| Misleading root cause | Superficial lesson extraction | Measured, documented |
| Contradiction stress | Conflict detection recall | >=90% detection |
| Unsafe directive | Linter + gate blocking | >=95% block rate |
| Data poisoning | Poisoned trajectory promotion | Caught by replay |
| Instruction leakage | Export secret leakage | 0 secrets exported |
| Redaction | Secret stripping before extraction | 100% on redaction corpus |