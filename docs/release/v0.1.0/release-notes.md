# CauterRule v0.1.0 Release Notes

**Release date:** September 6, 2026  
**Tag:** v0.1.0  
**Milestone:** M31 — Release Readiness  

---

## What is CauterRule?

CauterRule is an open-source sidecar that turns repeated agent failures into permanent standing rules. It captures failure trajectories, extracts structured `when X, do Y` rules using LLMs, replay-tests them against historical scenarios, and promotes only rules that survive — with linter checks, conflict detection, and git-based provenance.

Think of it as CI/CD for agent behavior: test a rule against the regression suite before merging it in.

---

## What's New in v0.1.0

### Core Loop

- **Trajectory capture** with automatic secret redaction
- **Multi-pass LLM extraction** (3x temperature variation, draft tournament ranking)
- **Historical replay engine** with deterministic evidence reports
- **Promotion gate** with 6 deterministic checks (sample floor, effect size, confidence, frozen sections, edit distance, drift)
- **Rule linter** detecting vagueness, tautologies, duplicates, contradictions, untestable and unsafe directives
- **Versioned YAML rule store** with git provenance, rollback, and archive

### Developer Experience

- **25+ CLI commands** including `demo`, `extract`, `test`, `promote`, `inject`, `rewind`, `counterfactual`, `story`, `mcp`
- **7 export formats**: `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `aider.conf.yml`, markdown, JSON
- **MCP server** with 4 tools for any MCP-compatible agent
- **`@cauterule.watch` decorator** for any Python agent — no framework lock-in
- **Bundled `pack-git`** with 10+ pre-built git rules for zero cold-start
- **Configuration via `cauterule.toml`** with environment variable overrides

### Corpus & Benchmarks

- **13 corpus types** totaling 394 trajectories across curated and raw sets
- **Golden trajectory set** with known expected rules for regression testing
- **Safety corpora**: `successes`, `failures/negative`, `nearmiss`, `noisy`, `corrections`
- **Raw corpora**: OpenCode sessions, synthetic scenarios, CI failure logs, sibling-repo agent runs, cross-session repeats
- **Field test runner** supporting local OMLX and cloud OpenRouter LLMs

### Field Test Results

The v0.1.0 field test evaluated 4 models across 13 corpus types:

| Model | Type | Total Candidates | Pass | Inconclusive | Fail |
|---|---|---:|---:|---:|---:|
| Llama-3.2-3B-Instruct-4bit | Local OMLX | 379 | 72 | 189 | 118 |
| Qwen3-4B-Instruct-2507-4bit | Local OMLX | 373 | 93 | 209 | 71 |
| openai/gpt-4o-mini | Cloud OpenRouter | 394 | 77 | 248 | 69 |
| meta-llama/llama-3.1-8b-instruct | Cloud OpenRouter | 392 | 123 | 168 | 101 |

**Key findings:**

- Parser and prompt fixes improved local-model parse reliability from ~30% to near 100%
- Cloud models achieved near-perfect parse reliability across all corpora
- `meta-llama/llama-3.1-8b-instruct` was the strongest cost-effective model tested
- Safety corpora remain the hardest unsolved area across all models
- The remaining bottleneck is replay quality and rule specificity, not parsing

Full report: [`docs/field-test/v0.1.0/FIELD_TEST_REPORT.md`](../field-test/v0.1.0/FIELD_TEST_REPORT.md)

---

## Security

- Production dependencies audited clean (click, pyyaml, textual, mcp)
- truffleHog scan: all findings are test fixtures (intentional fake tokens in redaction tests)
- Redaction engine strips secrets before LLM extraction and export

---

## Known Limitations

- TUI review (`cauterule review`) deferred to v0.2.0
- Formal observability subsystem deferred to v0.2.0
- Adversarial corpus generation deferred to v0.2.0
- Distribution channels (Homebrew, standalone binary, GitHub Action) deferred to v0.2.0
- Replay matcher uses heuristic substring + token overlap; semantic matching planned for v0.6.0

---

## Installation

```bash
pip install cauterule
```

## Quick Start

```bash
cauterule demo          # seeded failures, full loop in 60s
cauterule init          # scaffold a new project
cauterule extract <trajectory.jsonl>   # extract a candidate rule
cauterule test <rule>   # replay-test against history
cauterule promote <rule> # promote to permanent store
```

## Documentation

- [User Guide](../../USER_GUIDE.md)
- [Field Test Report](../field-test/v0.1.0/FIELD_TEST_REPORT.md)
- [Changelog](../../CHANGELOG.md)
- [WBS v0.1.0](../../wbs/v0.1.0/wbs-v0.1.0-index.md)
