# Changelog

All notable changes to CauterRule are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v0.4.0

- Semantic matching in replay engine (sentence-transformer embeddings)
- Additional distribution channels
- Enhanced observability dashboards

## [0.3.0] - 2026-09-12

Hardening & Ecosystem — fixes critical data-integrity bugs found by the v0.2.0
field test, ships first-class framework adapters, rule lifecycle management, a
pack ecosystem, corpus/benchmark infrastructure, and a full field test.

### Added

- **Adapters (M4)**: LangGraph, CrewAI, and PydanticAI adapters with failure capture + rule injection; generic `@watch` decorator and `inject()` context manager GA; adapter conformance harness + docs page (#512, #534, #536-#538, #540)
- **Rule lifecycle (M4)**: per-rule outcome tracking (prevented/broke/neutral), per-rule specificity scoring, supersession chains (replaced-by graph), automated retirement policy for stale/harmful rules, outcome-learned auto-promotion thresholds, model-level safety judgment (pre-extraction gate v2) (#541-#545)
- **Pack ecosystem (M5)**: `pack install` from GitHub with pinning, `pack create` scaffold, `pack publish` + semver + dependency resolution, `share <rule-id>` as GitHub gist with provenance, official packs (pack-python, pack-testing, pack-deploy, pack-docker), pack certification + safety scoring on install, pack docs + marketplace stub, scenario library, examples/ (#479-#481, #547-#548, #554-#560, #581-#587, #602)
- **Infrastructure (M6)**: `cauterule corpus` CLI group, `cauterule benchmark` CLI + leaderboard, pytest-benchmark perf-regression CI, OpenTelemetry standalone exporter, cost/latency tiering guidance (#486, #588, #601, #605-#606)
- **MCP hardening (M3/M6)**: remote MCP bearer auth, per-client rate limiting, payload schema validation (#601, #611)
- **Field test (M7)**: execution across local + cloud models, latency benchmarks (extraction/replay/injection), cost report with tiered provider guidance, safety-adjusted ranking validation, human-vs-replay agreement measurement, expanded reference corpus, field test report publication (#489, #491, #493-#496, #524, #607, #625, #629, #635, #641-#642, #648, #650, #653, #658, #663, #667, #671, #673, #676-#712)
- **DX/infra (M5/M6)**: `cauterule observe` command, webhook-on-promotion (Slack/Discord/GitHub), auto-classified failure taxonomy on promote, GitHub rules-learned badge, standalone PyInstaller binary, Homebrew tap (#547, #554-#560)
- **Security scanning (M8)**: `.github/workflows/security-scan.yml` (truffleHog, pip-audit, custom secret regex, OpenSSF Scorecard SARIF), `scripts/security/secret_scan.py`, `.trufflehog-exclude-paths.txt` (#620)

### Changed

- **Calibration (M1)**: `calibration_loop.feed_calibration_data` promoted from no-op stub to a working, persisted implementation (#596)
- **Serde strictness (M1)**: `Step.from_dict`/`Trajectory.from_dict`/`StandingRule.from_dict` now require explicit fields instead of silently defaulting `step_number`/`success`/`status` (#497-#499)
- **Coverage (M2)**: restored from 86% to ≥95%; Qwen alias expansion (18 matcher gaps fixed); narrowed extraction prompt to name error codes; trigger-domain mismatch detection (#487-#488, #490, #492, #598-#600)
- **Conflict handling (M3)**: new duplicate conflict type + `detect_duplicates`, overlap min-fraction threshold, consolidation via `score_specificity()`, recursive per-file rule YAML loading (#517-#523, #525-#527, #608-#613)
- **Replay matcher (M3)**: fixed token_f1 degeneracy, removed dead `_MIN_TRIGGER_WORDS`, reconciled near-miss divergence (#608-#613)
- **Budget optimizer (M3)**: metadata/token/greedy fixes (#608-#613)
- **Docker/CI (M3)**: dockerignore, non-root user, git, healthcheck, compose profiles, port fixes (#517-#527)
- **Version**: bumped 0.2.0 → 0.3.0 across `pyproject.toml`, `__init__.py`, README, and fixtures (#626)

### Fixed

- **Trajectory loading (M1)**: `load_trajectories` skips-and-warns on malformed JSONL instead of aborting (#593)
- **Recovery exclusion (M1)**: fixed 8 unanchored substring matches in recovery-class exclusion (#497-#508)
- **LLM provider (M1)**: timeout/retry/config, prompt-injection, and webhook SSRF fixes; missing runtime deps (requests/litellm/opentelemetry) added (#497-#508)
- **Replay cache (M1)**: cache key now includes trajectory content + threshold (#497-#508)
- **Store (M1/M3)**: git rollback option-injection and silent-commit-failure fixes; path-traversal guard on rule IDs; durability (index/archive/atomicity/git-commit); per-file catch when one YAML is bad (#497-#508, #517-#527, #616)
- **Linter (M1)**: unsafe/vagueness/duplicate/contradiction blind spots closed (#497-#508)
- **Redaction (M1/M3)**: `redact_trajectory` completeness (keys/sets/tags/quality_label), `mark_redacted` now actually redacts content, added Slack/Stripe/high-entropy/private-key/api_key patterns (#497-#508, #608-#613)
- **Extraction (M1/M3)**: `_error_matches` always-True bug; extraction quality-gate result no longer discarded; gate holes (zero-signal, state-only, hardcoded quality) closed (#497-#508, #608-#613)
- **Evidence report (M3)**: verdict override + frozen dataclass fix; determinism corpus hash no longer discarded (#608-#613)
- **Preflight (M2)**: CLI latency/cost/output-dir fixes; `validate_annotations` + `validate_corpus_sizes` wired; `CORPUS_SCHEMA_VERSION` enforcement; public multi-line JSONL loader fix (#598-#600)

### Security

- **Scans (M8)**: truffleHog — 0 verified secrets; `pip-audit --strict` — 0 known vulnerabilities in production dependencies; custom secret regex — 0 unmarked matches; OpenSSF Scorecard 3.8/10 with structural remediation tracked in #713 (#620)
- **Threat model (M8)**: SECURITY.md updated for v0.3.0 — remote MCP auth/rate-limit/payload validation, adapter redaction-on-disk guarantees, pack checksums/certification, rule-lifecycle safety (#620, #640)
- **Redaction**: secret patterns extended (Slack, Stripe, high-entropy, private keys, generic API keys); export and adapter paths redact before persistence (#608-#613)
- **Fixtures**: 11 intentional-fake-credential test modules marked `SECURITY-FIXTURE` so scans can distinguish fixtures from real leaks (#620)
- **CI tokens**: top-level `permissions: contents: read` added to workflows (#620)

### Milestone issue index

- **M1 Critical Fixes** (#52): #497-#508, #593-#597, #616
- **M2 Field-Test Gates** (#53): #487, #488, #490, #492, #598-#600
- **M3 Reliability & Durability** (#54): #517-#523, #525-#527, #608-#613
- **M4 Adapters & Lifecycle** (#55): #512, #534, #536-#538, #540-#545
- **M5 Pack Ecosystem & DX** (#56): #479-#481, #547, #548, #554-#560, #581-#587, #602, #603
- **M6 Corpus, Benchmark & Infra** (#57): #486, #588, #601, #605, #606
- **M7 Field Test** (#62): #489, #491, #493-#496, #524, #607, #625, #629, #635, #641, #642, #648, #650, #653, #658, #663, #667, #671, #673, #676-#712
- **M8 Release Readiness** (#63): #604, #614, #615, #620, #622, #626, #630, #633, #637, #640, #645, #649, #654, #657, #661, #665, #668, #670, #674, #675

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

## [0.2.0] - 2026-09-07

### Added

- **TUI review interface** (`cauterule review`): confidence-ordered review queue, filtering by severity/origin/status, approval/rejection workflows, card-based navigation
- **Observability subsystem**: hit counters, coverage scoring, learning journal (`cauterule observe`), metrics export
- **Adversarial corpus generation**: 6 adversarial corpora (staleness, counterexample, noise injection, prompt injection, redaction bypass, near-miss escalation)
- **Distribution channels**: Docker image with multi-service compose, standalone binary build (`scripts/build_binary.sh`), GitHub Action, webhook notifications, OpenTelemetry export
- **Benchmark leaderboard**: determinism, acceptance, rejection, bake-off, mutation, calibration, and ablation test suites
- **Pack certification baseline**: rule pack validation harness with safety scoring
- **Safety-adjusted ranking**: broad-trigger penalty, silence scoring, trigger specificity metrics (`cauterule report --safety-adjusted`)
- **Pre-extraction gate**: corpus validation, annotations, preflight, harness health checks
- **Human review workflow**: sampling strategies, review queue management, TUI integration
- **Scale and reliability tests**: latency, memory, conflict detection, concurrency
- **Public domain corpora**: 160 public trajectories added to corpus infrastructure
- **Field test runner**: v0.2.0 field test with expanded model coverage and safety corpora

### Changed

- `cauterule report` now emits a header by default and supports `--safety-adjusted` for model ranking
- Replay scorer verdict logic refined: broad-but-fixable triggers (broken < prevented) now return "inconclusive" instead of "fail"
- Coverage gate set to 95% across all modules

### Field Test Results

- Expanded field test with safety-adjusted model rankings
- Full report: `docs/field-test/v0.2.0/`

### Known Limitations

- Replay matcher uses heuristic substring + token overlap; semantic matching planned for v0.6.0
- LLM-backed extraction requires API keys (OpenAI/Anthropic) for cloud models

### Security

- Redaction engine strips secrets before LLM extraction
- Export redaction strips secrets from exported rules
- Adversarial corpus coverage for prompt injection and redaction bypass

