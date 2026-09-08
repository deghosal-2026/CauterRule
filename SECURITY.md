# Security Policy

## Supported Versions

| Version | Supported | Status |
|---------|-----------|--------|
| 0.2.x   | ✅        | Current release |
| 0.1.x   | ✅        | Maintenance (critical fixes only) |
| < 0.1   | ❌        | Unsupported |

## Reporting a Vulnerability

1. **Do not open a public issue.** Email security concerns to the maintainer via GitHub's private vulnerability reporting (`Security` → `Report a vulnerability`).
2. Include a description of the issue, reproduction steps, and affected versions.
3. You will receive acknowledgment within 72 hours.
4. Security fixes are prioritized and released as patch versions.

## Threat Model

### Attack Surfaces

CauterRule processes agent trajectories that may contain untrusted content (tool outputs, error messages, user prompts). The threat model assumes adversaries can influence trajectory content but cannot control the host environment.

| Threat | Surface | Mitigation |
|--------|---------|------------|
| Secret leakage in trajectories | Capture, extraction, export | Redaction engine strips secrets (AWS keys, GitHub tokens, JWTs, API keys, passwords) before LLM extraction and export |
| Prompt injection via trajectory content | LLM extraction | Pre-extraction gate filters junk trajectories; adversarial prompt-injection corpus validates resistance |
| Data poisoning — manipulated trajectories | Corpus, extraction | Corpus validation enforces annotations (`expected_outcome`, `expected_outcome_rationale`); adversarial corpora test detection |
| Instruction leakage — system prompt in rules | Extraction, store | Instruction leakage test verifies no system prompt fragments in extracted rules |
| Unsafe rule promotion | Promotion gate | Safety-first promotion gate: 6 deterministic checks (sample floor, effect size, confidence, frozen sections, edit distance, drift) |
| Webhook URL injection | Integrations | Webhook URLs validated via config; no user-controlled URL input at runtime |
| OTEL data exposure | Integrations | OpenTelemetry export is opt-in; event filtering strips sensitive fields |
| CI secret exposure | GitHub Action | Redaction runs before extraction; CI secrets never sent to LLM |

### v0.2.0 Additions

- **Pre-extraction gate** — prevents junk rules from clean trajectories
- **Safety-first promotion** — broad-trigger penalty prevents rules that break successes
- **Adversarial corpora** — validate resistance to prompt injection, data poisoning, redaction bypass
- **Instruction leakage test** — verifies no system prompt fragments in rules
- **Pack certification** — validates safety, replay, and provenance of official rule packs

## Adversarial Coverage

Six adversarial corpora test rule robustness against known attack patterns:

1. **Prompt injection** — trajectories containing injection attempts; no rule should promote an injection directive
2. **Misleading root-cause** — plausible-but-wrong failure causes; extracted rules should fail replay
3. **Contradiction stress test** — conflicting directives; linter should flag contradictions
4. **Unsafe directive** — dangerous/destructive actions; promotion gate should reject
5. **Data poisoning simulation** — manipulated trajectories with false annotations; corpus validation should catch
6. **Instruction leakage** — system prompt fragments in trajectory; extracted rules should contain no prompt fragments

**M10 field test result:** all 6 adversarial corpora produced 0 promoted rules across all tested models.

## Redaction Guarantees

The redaction engine strips secrets before LLM extraction and before export:

- **Built-in patterns:** AWS access keys, GitHub tokens, JWTs, generic API keys, passwords
- **Custom patterns:** configurable via `cauterule.toml` under `[redaction]`
- **Export redaction:** all export formats (`.cursorrules`, `CLAUDE.md`, `AGENTS.md`, etc.) run through redaction before writing
- **Test fixtures:** redaction tests use intentional fake tokens — these are not real secrets

## Security Scanning

- **truffleHog:** scans for secrets in the repository; all findings are test fixtures (intentional fake tokens)
- **pip-audit:** production dependencies audited clean (click, pyyaml, textual, mcp)
- **OpenSSF scorecard:** maintained as part of release readiness

## Contact

- GitHub Security Advisories: [Report a vulnerability](https://github.com/deghosal-2026/CauterRule/security)
- Maintainer: Debashish Ghosal
