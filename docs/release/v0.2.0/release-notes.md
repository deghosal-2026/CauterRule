# CauterRule v0.2.0 Release Notes

**Release date:** September 7, 2026

CauterRule v0.2.0 is the **Distribution & Polish** release. It builds on the v0.1.0 core loop with a TUI review interface, full observability subsystem, adversarial corpus generation, expanded distribution channels, a benchmark leaderboard, and pack certification baseline.

---

## What's New

### TUI Review Interface (`cauterule review`)
- Confidence-ordered review queue — highest-impact rules surface first
- Filter by severity, origin, and status
- Approval/rejection workflows with keyboard-driven navigation
- Card-based UI built on Textual

### Observability Subsystem (`cauterule observe`)
- Hit counters — track how often each rule fires
- Coverage scoring — measure which failure classes are covered by rules
- Learning journal — narrative view of rule evolution over time
- Metrics export for external dashboards

### Adversarial Corpus Generation
Six adversarial corpora that stress-test rule robustness:

| Corpus | What It Tests |
|--------|---------------|
| Staleness | Rules that become outdated as codebases evolve |
| Counterexample | Cases where a correct rule produces wrong prevention |
| Noise Injection | Rule resilience to noisy/irrelevant trajectory content |
| Prompt Injection | Rules that prevent injection attacks vs. are exploited by them |
| Redaction Bypass | Whether rules leak or circumvent secret redaction |
| Near-Miss Escalation | Edge cases where near-misses should escalate to full failures |

### Distribution Channels
- **Docker** — multi-service `docker-compose.yaml` (demo, test, MCP) with healthchecks
- **Standalone binary** — `scripts/build_binary.sh` for PyInstaller-packaged binary
- **GitHub Action** — run `cauterule test --ci` in any CI workflow
- **Webhook notifications** — post promotion/rejection events to external services
- **OpenTelemetry export** — emit traces and metrics to any OTEL collector

### Benchmark Leaderboard
Seven deterministic benchmark suites:

1. **Determinism** — same input → same output, every time
2. **Acceptance** — valid trajectories produce valid rules
3. **Rejection** — invalid trajectories produce no rules
4. **Bake-off** — head-to-head model comparison
5. **Mutation** — small trajectory changes produce expected rule deltas
6. **Calibration** — confidence scores correlate with correctness
7. **Ablation** — each subsystem contributes measurable value

### Pack Certification Baseline
- Rule pack validation harness with safety scoring
- `pack-git` certified as the reference implementation

### Safety-Adjusted Ranking (`cauterule report --safety-adjusted`)
- Broad-trigger penalty — rules that break successes are penalized
- Silence scoring — rules that never fire are flagged
- Trigger specificity metrics — measure how targeted a rule's trigger is
- Decision economics — pairwise model comparison with wrong-decision rate

### Pre-Extraction Gate
- Corpus validation before extraction runs
- Annotation enforcement (`expected_outcome`, `expected_outcome_rationale`)
- Preflight checks and harness health verification

### Human Review Workflow
- Sampling strategies (random, confidence-stratified, severity-weighted)
- Review queue management with TUI integration
- Approval/rejection with audit trail

### Scale and Reliability Tests
- Latency benchmarks across corpus sizes
- Memory usage profiling
- Conflict detection at scale
- Concurrency safety verification

### Expanded Corpus
- 160 new public-domain trajectories added to v0.2.0 corpus
- All trajectories annotated with `expected_outcome` and `expected_outcome_rationale`
- 13 corpus types from v0.1.0 retained and extended

---

## Field Test Results

The v0.2.0 field test expanded on v0.1.0 with safety-adjusted model rankings and adversarial corpora.

Key findings:
- Parser and prompt fixes from v0.1.0 maintained near-100% parse reliability for cloud models
- Safety-adjusted ranking surfaces broad-trigger penalties and wrong-decision rates that total-pass rankings miss
- Adversarial corpora expose rule staleness, counterexamples, and redaction bypass edges
- Safety corpora (`successes`, `failures/negative`, `nearmiss`) remain the hardest unsolved area

Full report: [`docs/field-test/v0.2.0/FIELD_TEST_REPORT.md`](../../field-test/v0.2.0/FIELD_TEST_REPORT.md)

---

## Known Issues

- Replay matcher uses heuristic substring + token overlap; semantic matching is planned for v0.6.0
- LLM-backed extraction requires API keys (OpenAI/Anthropic) for cloud models
- TUI review interface requires a terminal with color support

---

## Upgrade Guide

### From v0.1.0 to v0.2.0

1. **Update the package:**
   ```bash
   pip install --upgrade cauterule
   ```

2. **Verify the version:**
   ```bash
   cauterule --version
   # cauterule, version 0.2.0
   ```

3. **New commands available:**
   ```bash
   cauterule review           # TUI review interface
   cauterule observe          # observability metrics
   cauterule report --safety-adjusted  # safety-adjusted model ranking
   ```

4. **Docker users:**
   ```bash
   docker compose up cauterule-demo
   ```

5. **No breaking changes** — all v0.1.0 commands, rule formats, and stores are fully compatible.

---

## Security

- Redaction engine strips secrets before LLM extraction
- Export redaction strips secrets from exported rules
- Adversarial corpus coverage for prompt injection and redaction bypass
- Production dependencies audited clean (click, pyyaml, textual, mcp)

---

## Contributors

- Debashish Ghosal

---

## Links

- [Changelog](../../../CHANGELOG.md)
- [Field Test Report (v0.2.0)](../../field-test/v0.2.0/FIELD_TEST_REPORT.md)
- [Documentation Index](../../README.md)
- [PyPI](https://pypi.org/project/cauterule/)
- [GitHub](https://github.com/deghosal-2026/CauterRule)
