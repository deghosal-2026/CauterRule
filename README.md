# CauterRule

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/pypi-v0.3.0-blue)](https://pypi.org/project/cauterule/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000)](https://github.com/astral-sh/ruff)
[![Type checked](https://img.shields.io/badge/mypy-strict-blue)](https://github.com/python/mypy)
[![Coverage](https://img.shields.io/badge/coverage-87%25%20(deterministic%20subset)-yellow)](https://github.com/deghosal-2026/CauterRule/actions)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/14464/badge)](https://www.bestpractices.dev/projects/14464)
[![Field Test](https://img.shields.io/badge/field%20test-v0.3.0%20%7C%2098%E2%80%93100%25%20near-miss%20precision-brightgreen)](docs/field-test/v0.3.0/FIELD_TEST_REPORT.md)
[![Changelog](https://img.shields.io/badge/changelog-Keep%20a%20Changelog-%23E05735)](CHANGELOG.md)
[![Cauterule](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/deghosal-2026/Cauterule/main/badge.json)](docs/USER_GUIDE.md)

**Automated standing-rule extraction from agent failures.**

Every agent fails. CauterRule ensures they never make the *same* failure twice.

After every failure, CauterRule:
1. **Extracts** a structured *when X, do Y* standing rule from the execution trajectory (multi-pass with draft tournament)
2. **Tests** that candidate rule against historical scenarios (past failures + past successes — deterministic replay)
3. **Promotes** only rules that survive replay into the agent's permanent rule store (with linter, conflict detection, provenance)

No more corrections dying in chat. No more hand-written standing rules. No more vague reflection paragraphs nobody re-reads. Rules are actionable, tested, and permanent.

**Status:** v0.3.0 — Hardening & Ecosystem: critical fixes, adapters, rule lifecycle, pack ecosystem, corpus/benchmark infra, full field test.

---

## Why

The current state of "learning from mistakes" in agent systems is reflection-as-a-paragraph — prose that bloats the context window and is never read again. The manual alternative is standing rules maintained by hand. Both are broken.

CauterRule automates the extract → test → promote loop. Same pattern as CI/CD for code, but for agent behavior: test a rule against the historical regression suite before merging it in.

---

## What Makes It Different

| Existing | CauterRule |
|----------|-----------|
| Reflection produces prose nobody re-reads | Produces structured *when X, do Y* rules that are testable and injectable |
| Memory stores hold raw text (Letta/MemGPT) | Rules are tested against history before promotion — evidence-based, not append-only |
| Framework memory is unstructured (LangGraph) | Rules have provenance, versioning, conflict detection, linter, and retirement |
| Standing rules maintained by hand | The agent writes its own rules, tests them, and promotes only what survives |
| `.cursorrules` / `CLAUDE.md` are static files | Rules are living artifacts that grow from real failures, not guesses |
| No OSS tool ships a corpus or benchmarks | 40 corpora, 2,384 trajectories per model, 444 domain-scoped reference trajectories, golden set, safety corpora, public domain corpora, adversarial/staleness/counterexample corpora, corpus + benchmark + leaderboard CLI, field test runner |

---

## Installation

Pick any channel:

```bash
# PyPI (base)
pip install cauterule
# With LLM providers (OpenAI, Anthropic, LiteLLM, Ollama-over-HTTP):
pip install cauterule[llm]
# With semantic matching:
pip install "cauterule[matching]"
# With OpenTelemetry export:
pip install cauterule[otel]
# Everything:
pip install cauterule[all]

# Homebrew
brew install deghosal-2026/cauterule/cauterule

# Docker
docker pull ghcr.io/deghosal-2026/cauterule:v0.3.0
docker compose up cauterule-demo

# Standalone binary — download from the GitHub Release assets
# https://github.com/deghosal-2026/CauterRule/releases/tag/v0.3.0
```

---

## Quick Start

```bash
# Run the demo — seeded failures, full loop in 60s
cauterule demo

# Extract a rule from a trajectory
cauterule extract trajectory.jsonl

# Replay-test a candidate rule
cauterule test R-001

# Promote to the permanent store
cauterule promote R-001

# Browse rules and lifecycle state
cauterule list
cauterule audit
cauterule health
cauterule validate

# Export rules to your agent's format
cauterule export --format agents

# Install an official rule pack (GitHub + version pinning)
cauterule pack install deghosal-2026/cauterule-packs/pack-docker@v0.3.0

# Corpus + benchmark infrastructure
cauterule corpus list
cauterule benchmark run
```

Wrap any Python agent with the generic adapter, or use a framework adapter:

```python
from cauterule.adapter import watch, inject
from cauterule.store.manager import StoreManager


@watch(base_dir="trajectories", redact_keys={"api_key", "token"})
def my_agent(prompt: str) -> str: ...


with inject(task, rules=StoreManager().list_rules(status="active"), tool="git") as matched:
    prompt = base_prompt + render(matched)

# LangGraph
from cauterule.adapter.langgraph import inject_rules, langgraph_node


@langgraph_node(task="sync billing records", base_dir="trajectories")
def my_node(state: dict) -> dict: ...
```

See [Adapters & Rule Lifecycle](docs/ADAPTERS.md) for CrewAI and PydanticAI.

---

## What's Shipped in v0.3.0

### Core Loop
- Trajectory capture with secret redaction
- Multi-pass LLM extraction (temperature variation, draft tournament)
- Failure clustering — one extraction per failure cluster, not per failure
- Historical replay engine with deterministic evidence reports
- Promotion gate — auto, human-review, or hybrid mode
- Rule linter (vagueness, tautology, duplicate, contradiction, untestable, unsafe)
- Conflict detection and rule consolidation
- Versioned YAML rule store with git provenance

### Adapters (New in v0.3.0)
- First-class **LangGraph**, **CrewAI**, and **PydanticAI** adapters — capture failures and inject matching rules in-framework
- Generic `@watch` decorator and `inject()` / `ainject()` context manager GA
- One shared **conformance harness** holds every adapter to the same capture/injection/redaction contract
- Duck-typed: adapters import cleanly when the framework is not installed
- Docs: [Adapters & Rule Lifecycle](docs/ADAPTERS.md)

### Rule Lifecycle (New in v0.3.0)
- Per-rule **outcome tracking** — prevented / broke / neutral counters
- **Specificity scoring** feeds conflict consolidation and lifecycle decisions
- **Supersession chains** — replaced-by graph for evolving rules
- **Automated retirement** for stale and harmful rules
- **Outcome-learned auto-promotion** thresholds, plus model-level safety judgment
- `cauterule audit`, `cauterule retire`, `cauterule review`, `cauterule journal`

### CLI (40+ Commands)
- Core: `init` | `demo` | `extract` (`--dry-run`) | `test` (`--ci`) | `promote` | `inject` | `list` | `show` | `search`
- Lifecycle: `audit` | `retire` | `review` | `history` | `conflicts` | `diff` | `promote` | `journal`
- Diagnostics: `health` | `validate` | `preflight` | `harness-health` | `gaps` | `frontier`
- Analysis: `counterfactual` | `story` | `explain` | `metrics` | `report` | `taxonomy`
- Ecosystem: `pack` (`list`/`info`/`install`/`create`/`publish`) | `share` | `observe`
- Infra: `corpus` | `benchmark` | `leaderboard` | `otel` | `release`
- Integrations: `export` (`--format agents`) | `import` | `config` | `mcp` | `webhook` | `badge` | `rewind`

### Pack Ecosystem (New in v0.3.0)
- `pack install` from GitHub with version pinning
- `pack create` scaffold from a rule store; `pack publish` with semver + dependency resolution
- `share <rule-id>` publishes a single rule as a GitHub gist with provenance
- Official packs: `pack-python`, `pack-testing`, `pack-deploy`, `pack-docker`
- Pack **certification + safety scoring** on install
- Docs: [Contributing Packs](docs/packs/CONTRIBUTING-PACKS.md)

### Replay Engine
- Replay harness with evidence reports (failures prevented, successes broken, precision, recall, verdict)
- Domain-scoped reference pool — same-domain scoring, recall 2–3× v0.2.0
- Near-miss penalty, self-match exclusion, and recovery gate
- "What if?" mode — apply a hypothetical rule and simulate the outcome
- Failure Time Machine — `cauterule rewind <trajectory>` with rule overlay
- Rule Draft Tournament — generate candidates, replay all, rank, promote the winner

### Rule Store
- YAML rule files with provenance metadata and tags
- Auto-classified failure taxonomy (`git/push`, `python/import`, `docker/network`)
- Git-based versioning, rollback, archive directory, path-traversal guard
- Rule consolidation — merge overlapping triggers

### Rule Injection
- Structured matching by trigger, tool, error type, context, tags, taxonomy
- Specificity ordering — more specific rules injected first
- Rule explanations, templating (retry, verify-then-act, check-preconditions)
- Context budget optimizer, preflight mode

### Export & Import (Day-One Interop)
- Export to `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `aider.conf.yml`, markdown, JSON
- Import from `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, and chat history

### MCP Server (Hardened in v0.3.0)
- 4 tools: `get_matching_rules`, `get_rule`, `list_rules`, `report_failure`
- Remote HTTP mode: **bearer auth**, per-client **rate limiting**, and payload **schema validation**
- Any MCP-compatible agent (Claude, etc.) consumes rules with zero code changes
- Critical HTTP auth bug (#601) found by the Docker field test and fixed via the official `mcp` SDK `Context` API

### Corpus, Benchmark & Release Infrastructure (New in v0.3.0)
- `cauterule corpus` — add/list/validate/lint/build/export trajectory corpora
- `cauterule benchmark` + `cauterule leaderboard` — determinism, acceptance, rejection, bake-off, mutation, calibration, ablation suites
- 40 corpora / 2,384 trajectories per model; 444 domain-scoped reference trajectories
- pytest-benchmark perf-regression CI for hot paths
- `cauterule release check` — version consistency + publish guidance; tag-triggered `Release` workflow (build, `twine check`, TestPyPI/PyPI)
- OpenTelemetry standalone exporter (`cauterule otel`); cost/latency tiering guidance

### Observability
- `cauterule observe` — hit counters, coverage scoring, learning journal, metrics export
- Webhook-on-promotion (Slack / Discord / GitHub)
- OpenTelemetry spans for `rule.match`, `rule.promote`, `rule.retire`, `replay.verdict`
- Docs: [Observability](docs/observability.md)

### Configuration
- `cauterule.toml` — LLM provider, model, thresholds, mode, paths, redaction patterns
- Environment variable support — `CAUTERULE_LLM_PROVIDER`, `CAUTERULE_MODEL`, `CAUTERULE_SEMANTIC_MATCHING`, `CAUTERULE_QUARANTINE_IDS`
- LLM provider abstraction — OpenAI, Anthropic, Ollama, LiteLLM
- Promotion mode — auto, human-review, hybrid

### Security
- Remote MCP auth / rate-limit / payload validation; adapter redaction-on-disk; pack checksums/certification
- 0 verified secrets (truffleHog), 0 production vulnerabilities (pip-audit), custom secret regex clean
- OpenSSF Scorecard 3.8/10 with structural remediation tracked (#713)
- Details: [SECURITY.md](SECURITY.md)

---

## Field Test Results

The v0.3.0 field test ran **40 corpora × 2 cloud models (gpt-4o-mini, llama-3.1-8b) = 4,768 trajectory-runs**, with a 444-trajectory domain-scoped reference corpus.

Key findings:
- **Near-miss precision 98–100%** (was 86–90% in v0.2.0) — near-miss penalty + self-match exclusion + recovery gate
- **Adversarial promotions: 0** on both models (`should_reject` override)
- **100% safety silence** — 60/60 successes and 60/60 failures-negative gate-dropped
- **Recall improved 2–3×** (0.170 / 0.228 vs 0.087) after domain-scoping the reference pool (#708)
- **#601 MCP auth bug** caught by the Docker field test and fixed (unit-green, deployment-broken)
- **Known gap:** golden pass 40–50% (target ≥70%) and failures/positive 8–10% (target ≥50%) — the matcher's paraphrase limitation, targeted for v0.4.0

Full report: [`docs/field-test/v0.3.0/FIELD_TEST_REPORT.md`](docs/field-test/v0.3.0/FIELD_TEST_REPORT.md)

Prior reports:
- v0.2.0: [`docs/field-test/v0.2.0/FIELD_TEST_REPORT.md`](docs/field-test/v0.2.0/FIELD_TEST_REPORT.md)
- v0.1.0: [`docs/field-test/v0.1.0/FIELD_TEST_REPORT.md`](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md)

---

## Architecture

```
                         ┌───────────────────────────────────────────────┐
                         │                  CLI / MCP                     │
                         │ extract | test | promote | corpus | benchmark  │
                         │ pack | share | observe | retire | audit        │
                         └──────┬────────────────────┬──────────────┬─────┘
                                │                    │              │
                                ▼                    ▼              ▼
 ┌──────────────────┐   ┌───────────────┐   ┌───────────────┐  ┌──────────────┐
 │ Adapters         │──>│ Rule Extractor│──>│ Historical    │  │ Corpus &     │
 │ @watch/LangGraph │   │ (multi-pass)  │   │ Replay Engine │  │ Benchmark    │
 │ CrewAI/PydanticAI│   │               │   │ domain-scoped │  │ 40 corpora   │
 └──────────────────┘   └───────────────┘   └───────┬───────┘  └──────────────┘
                                                     │
                                                     ▼
 ┌──────────────────┐   ┌───────────────┐   ┌───────────────┐  ┌──────────────┐
 │ Rule Injection   │<──│ Standing-Rule │<──│ Promotion Gate│  │ Rule         │
 │ + Explanations   │   │ Store (YAML)  │   │ + Linter +    │  │ Lifecycle    │
 │ + Budget         │   │ + git prov.   │   │   Conflicts   │  │ outcomes/    │
 └──────────────────┘   └───────┬───────┘   └───────────────┘  │ retirement   │
                                │                              └──────────────┘
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
 ┌──────────────────┐   ┌───────────────┐  ┌───────────────────┐
 │ Pack Ecosystem   │   │ Export /      │  │ Observability     │
 │ install/create/  │   │ Import        │  │ OpenTelemetry +   │
 │ publish + share  │   │ 7 formats +MCP │  │ journal + metrics │
 └──────────────────┘   └───────────────┘  └───────────────────┘
```

---

## Known Limitations

- **Golden pass rate 40–50%** (target ≥70%) — the token-F1 matcher cannot bridge the paraphrase gap between LLM-extracted triggers and reference phrasings. Targeted for v0.4.0 matcher work.
- **Failures/positive pass rate 8–10%** (target ≥50%) — blocked by the broad-trigger penalty (`broken > 0`) and precision below 0.5. v0.4.0 matcher work.
- **Semantic matching is still maturing** — optional via `pip install "cauterule[matching]"`, but it contributes only a 0.2 weight to the score blend today. Raising the semantic weight is v0.4.0 work.
- **Cross-session repeat-failure reduction and human-vs-replay agreement** — tooling is ready; the measurement protocols have not been run.
- **Local OMLX models are unusable** (slow, hung on `raw/ci`) — use cloud models.
- **OpenSSF Scorecard 3.8/10** — structural gaps (branch protection, review, fuzzing, dependency pinning); remediation tracked in #713, #614, #615.
- **Replay matcher is still heuristic** (substring + token overlap + 0.2 semantic) — the embedding index is planned for a later release.
- **TUI review requires a color-capable terminal** — use the CLI commands otherwise.

---

## Roadmap

| Version | Theme | Key Deliverable |
|---------|-------|-----------------|
| **v0.1.0** ✅ | Core Loop + DX | Full loop, 25+ CLI commands, MCP, export/import, packs, corpus, field tests |
| **v0.2.0** ✅ | Distribution + Polish | TUI review, observability, corpus infra (160 public trajs), 12 benchmarks, adversarial corpora, Docker, binary, GitHub Action, webhook, OTEL |
| **v0.3.0** ✅ | Hardening & Ecosystem | Critical fixes, adapters (LangGraph/CrewAI/PydanticAI), rule lifecycle, pack ecosystem, corpus/benchmark infra, 40-corpus field test |
| **v0.4.0** | Intelligence & Scale | Matcher quality + paraphrase bridging, higher semantic weight, cross-session repeat-failure measurement, human-vs-replay agreement, deep integrations, observability dashboard, fleet support |
| **v0.5.0** | Observability & Analytics | Web dashboard, trend lines, weekly digest |
| **v0.6.0** | Advanced Retrieval | Rule embedding index, hybrid retrieval tuning |
| **v0.7.0** | Multi-Agent | Cross-agent transfer, shared registry, rule governance |

---

## Related Ecosystem

CauterRule is the **learning layer** in an open-source agent infrastructure stack:

| Project | Layer | How it relates |
|---------|-------|----------------|
| [planner-critic-engine](https://github.com/deghosal-2026/planner-critic-engine) | Prevention | Catches flawed plans *before* execution |
| [agent-self-edit](https://github.com/deghosal-2026/agent-self-edit) | Prompt Learning | Twin learning engine — extracts *prompt edits* from failures |
| [agent-tooltrust](https://github.com/deghosal-2026/agent-tooltrust) | Tool Safety | Runtime permission engine |
| [agent-eval-forge](https://github.com/deghosal-2026/agent-eval-forge) | Evaluation | "pytest for agents" |
| [ai-loopguard](https://github.com/deghosal-2026/ai-loopguard) | Circuit Breaker | Real-time failure handling |

---

## Documentation

- [User Guide](docs/USER_GUIDE.md)
- [Adapters & Rule Lifecycle](docs/ADAPTERS.md)
- [Observability](docs/observability.md)
- [Contributing Rule Packs](docs/packs/CONTRIBUTING-PACKS.md)
- [Field Test Report (v0.3.0)](docs/field-test/v0.3.0/FIELD_TEST_REPORT.md)
- [Field Test Report (v0.2.0)](docs/field-test/v0.2.0/FIELD_TEST_REPORT.md)
- [Field Test Report (v0.1.0)](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md)
- [Release Notes (v0.3.0)](docs/release/v0.3.0/release-notes.md)
- [Release Notes (v0.2.0)](docs/release/v0.2.0/release-notes.md)
- [Release Notes (v0.1.0)](docs/release/v0.1.0/release-notes.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Docs Index](docs/README.md)
- [PRD: Why](docs/design/prd/01-why.md)
- [Architecture](docs/design/prd/02-architecture.md)
- [WBS v0.3.0](docs/wbs/v0.3.0/wbs-v0.3.0-index.md)
- [WBS v0.1.0](docs/wbs/v0.1.0/wbs-v0.1.0-index.md)

---

## License

MIT — see [LICENSE](LICENSE).