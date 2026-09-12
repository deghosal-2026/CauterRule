# Security Policy

## Supported Versions

| Version | Supported | Status |
|---------|-----------|--------|
| 0.3.x   | ✅        | Current release |
| 0.2.x   | ✅        | Maintenance (critical fixes only) |
| 0.1.x   | ❌        | Unsupported |
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
| Unauthenticated MCP access | MCP server (remote mode) | Bearer-token auth (`auth_mode="bearer"`) required off loopback; stdio stays local. Warns (does not silently allow) when auth is disabled on a non-loopback host (#601) |
| MCP request flooding | MCP server (remote mode) | Per-client token-bucket rate limiter returns HTTP 429 with `retry_after`; stdio calls bypass |
| Malformed MCP tool payloads | MCP server | `validate_report_failure` schema-checks payloads before extraction; 400 with field-level errors |
| Adapter-captured data leakage | Adapters (LangGraph/CrewAI/PydanticAI/generic) | Every adapter routes trajectory I/O through the same redaction engine before persistence; conformance kit asserts secrets are redacted on disk (#540) |
| Pack supply-chain tampering | Pack install | Packs carry checksums and are certified (safety/replay/provenance) before trust |

### v0.3.0 Additions

- **Remote MCP hardening** — bearer auth + per-client rate limiting + payload validation (#601)
- **Adapter conformance kit** — all adapters prove redaction-on-disk and no-repeat contracts (#540)
- **Rule lifecycle safety** — supersession/retirement/quarantine prevent stale rules from masquerading as active (#541-#545)
- **Pack certification** — checksums + safety/replay/provenance gates for installable packs
- **Durability fixes** — atomic store writes and path-traversal guards on rule IDs (#517-#527)

## Adversarial Coverage

Six adversarial corpora test rule robustness against known attack patterns:

1. **Prompt injection** — trajectories containing injection attempts; no rule should promote an injection directive
2. **Misleading root-cause** — plausible-but-wrong failure causes; extracted rules should fail replay
3. **Contradiction stress test** — conflicting directives; linter should flag contradictions
4. **Unsafe directive** — dangerous/destructive actions; promotion gate should reject
5. **Data poisoning simulation** — manipulated trajectories with false annotations; corpus validation should catch
6. **Instruction leakage** — system prompt fragments in trajectory; extracted rules should contain no prompt fragments

**M10 field test result:** all 6 adversarial corpora produced 0 promoted rules across all tested models.

**v0.3.0 (M7/M8) additions:** the adversarial set was extended with near-miss,
staleness, and counterexample corpora. Across all tested models the promotion
gate produced 0 unsafe promotions; near-miss matches downgrade the scorer
verdict from `pass` to `inconclusive` (tolerance band ≤2 near-misses with
precision ≥0.5). See `docs/field-test/v0.3.0/FIELD_TEST_REPORT.md`.

## Redaction Guarantees

The redaction engine strips secrets before LLM extraction and before export:

- **Built-in patterns:** AWS access keys, GitHub tokens, JWTs, generic API keys, passwords, Google API keys, Slack and Stripe tokens
- **Custom patterns:** configurable via `cauterule.toml` under `[redaction]`
- **Export redaction:** all export formats (`.cursorrules`, `CLAUDE.md`, `AGENTS.md`, etc.) run through redaction before writing
- **Adapter coverage:** generic `watch`/`inject` and framework adapters (LangGraph, CrewAI, PydanticAI) redact before persisting trajectories
- **Test fixtures:** redaction/adversarial test modules carry a `SECURITY-FIXTURE` marker; every token-like string in them is an intentional fake credential, not a real secret

## Security Scanning

Scans run in `.github/workflows/security-scan.yml` on push, PR, and weekly.

| Scan | Scope | Result (v0.3.0, 2026-09-12) |
|------|-------|------------------------------|
| truffleHog 3.97.4 | Full repo filesystem | 0 verified secrets; 7 unverified matches, all in `SECURITY-FIXTURE`-marked redaction/adversarial tests |
| Custom secret regex | Repo source, fixture-marker aware | 0 unmarked matches |
| pip-audit 2.10.1 (`--strict .`) | Production deps in `pyproject.toml` | 0 known vulnerabilities |
| pip-audit (venv, awareness) | Dev deps | 4 advisories in `pip` itself (build tool); non-blocking |
| OpenSSF Scorecard 5.5.0 | Repository posture | 3.8/10 — structural gaps tracked (see below) |

### OpenSSF Scorecard remediation

The aggregate score is below the ≥7/10 target. The remaining gaps are
structural for a young, single-maintainer repository and are tracked with
mitigation plans rather than silently accepted:

- **Branch protection / Code-Review / Contributors / Maintained** — require
  organizational history and review policy; track as project matures.
- **Dependency-Update-Tool** — dependabot config tracked by #615.
- **SAST** — CodeQL / static analysis tracked by #614.
- **Token-Permissions** — top-level `permissions: contents: read` added to
  `ci.yaml` and `security-scan.yml`.
- **Pinned-Dependencies** — pin GitHub Actions and base images by hash tracked
  by #614.
- **Fuzzing** — fuzzing integration tracked by #614.

## Contact

- GitHub Security Advisories: [Report a vulnerability](https://github.com/deghosal-2026/CauterRule/security)
- Maintainer: Debashish Ghosal
