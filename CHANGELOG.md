# Changelog

All notable changes to CauterRule are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-06

### Added

- **Core extraction loop**: trajectory capture, multi-pass LLM extraction (3x temperature variation), draft tournament ranking
- **Replay engine**: deterministic evidence reports, "What if?" mode, Failure Time Machine (`cauterule rewind`), replay diff visualization
- **Promotion gate**: auto, human-review, and hybrid modes with 6 deterministic checks (sample floor, effect size, confidence, frozen sections, edit distance, drift)
- **Rule linter**: vagueness, tautology, duplicate, contradiction, untestable, unsafe directive detection
- **Rule store**: versioned YAML with git provenance, rollback, archive, auto-classified failure taxonomy
- **Rule injection**: structured matching, specificity ordering, rule explanations, templating (retry, verify-then-act, check-preconditions), context budget optimizer, preflight mode
- **Rule packs**: bundled `pack-git` with 10+ pre-built git rules for zero cold-start
- **CLI**: 25+ commands including `init`, `demo`, `extract`, `test`, `promote`, `inject`, `list`, `audit`, `rewind`, `counterfactual`, `story`, `mcp`
- **Export/import**: 7 formats (`.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `aider.conf.yml`, markdown, JSON) with round-trip fidelity
- **MCP server**: 4 tools (`get_matching_rules`, `get_rule`, `list_rules`, `report_failure`) with stdio + HTTP transport
- **Custom agent adapter**: `@cauterule.watch` decorator and `cauterule.inject()` context manager for any Python agent
- **Corpus infrastructure**: 13 corpus types totaling 394 trajectories (curated + raw), including golden set, failures, successes, nearmiss, noisy, corrections, and raw CI/OpenCode/synthetic sets
- **Field test runner**: `scripts/run-field-test.py` supporting local OMLX and cloud OpenRouter LLMs with incremental result writing
- **Configuration**: `cauterule.toml` with env var overrides (`CAUTERULE_LLM_PROVIDER`, `CAUTERULE_MODEL`, `CAUTERULE_LLM_API_KEY`, `CAUTERULE_LLM_BASE_URL`)
- **Redaction engine**: built-in secret patterns (AWS keys, GitHub tokens, JWTs, API keys, passwords) with custom pattern support
- **CI integration**: JUnit XML output via `cauterule test --ci`

### Field Test Results

- Evaluated 4 models across 13 corpus types (394 trajectories total):
  - Local: `Llama-3.2-3B-Instruct-4bit`, `Qwen3-4B-Instruct-2507-4bit`
  - Cloud: `openai/gpt-4o-mini`, `meta-llama/llama-3.1-8b-instruct`
- Parser and prompt fixes improved local-model parse reliability from ~30% to near 100%
- Cloud models achieved near-perfect parse reliability across all corpora
- Safety corpora (`successes`, `failures/negative`, `nearmiss`) remain the hardest unsolved area
- Full report: `docs/field-test/v0.1.0/FIELD_TEST_REPORT.md`

### Known Limitations

- TUI review (`cauterule review`) deferred to v0.2.0
- Formal observability subsystem (hit counters, coverage scoring) deferred to v0.2.0
- Adversarial corpus generation deferred to v0.2.0
- Distribution channels (Homebrew, standalone binary, GitHub Action) deferred to v0.2.0
- Replay matcher uses heuristic substring + token overlap; semantic matching planned for v0.6.0

### Security

- Production dependencies audited clean (click, pyyaml, textual, mcp)
- truffleHog scan: all findings are test fixtures (intentional fake tokens in redaction tests)
- Redaction engine strips secrets before LLM extraction
- Export redaction strips secrets from exported rules

## [Unreleased]

### Planned for v0.2.0

- TUI review interface
- Observability subsystem (hit counters, coverage scoring, learning journal)
- Adversarial corpus generation
- Distribution channels (Homebrew, standalone binary, GitHub Action, webhook, OpenTelemetry)
- Benchmark leaderboard
- Pack certification baseline
