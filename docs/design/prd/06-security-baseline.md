# PRD 06: Security Baseline

## Threat Model

### Injection via Trajectory Content
- A malicious trajectory could contain prompt-injection payloads aimed at the rule extractor LLM
- **Mitigation:** Structured output parsing with schema validation; output is constrained to *when X, do Y* form

### Unauthorized Rule Promotion
- A compromised agent could promote harmful rules
- **Mitigation:** Promotion gate supports human-review mode; all promotions are git-committed with provenance

### Sensitive Data in Trajectories
- Execution traces may contain API keys, tokens, or proprietary logic
- **Mitigation:** Trajectories are local-first; no data leaves the filesystem unless explicitly configured. Sanitization hooks for sensitive fields.

## Design Principles

- **Local-first by default:** No cloud dependency, no data exfiltration risk
- **Git as audit trail:** Every promotion is a git commit with full provenance
- **Human-in-the-loop option:** Promotion gate can require human approval
- **Minimal dependencies:** Python standard library + LLM API (local or remote)