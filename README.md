# CauterRule

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/pypi-v0.3.0-blue)](https://pypi.org/project/cauterule/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000)](https://github.com/astral-sh/ruff)
[![Type checked](https://img.shields.io/badge/mypy-strict-blue)](https://github.com/python/mypy)
[![Coverage](https://img.shields.io/badge/coverage-84%25-yellow)](https://github.com/deghosal-2026/CauterRule/actions)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/14464/badge)](https://www.bestpractices.dev/projects/14464)
[![Field Test](https://img.shields.io/badge/field%20test-v0.3.0%20%7C%20packs%20%2B%20adapters%20%2B%20lifecycle-brightgreen)](docs/field-test/v0.3.0/FIELD_TEST_REPORT.md)
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
| No OSS tool ships a corpus or benchmarks | 13 corpus types, 394 trajectories (v0.1.0) + 160 public trajectories (v0.2.0), golden set, safety corpora, public domain corpora, adversarial/staleness/counterexample corpora, field test runner |

---

## Quick Start

```bash
pip install cauterule
# With LLM providers (OpenAI, Anthropic, LiteLLM, Ollama-over-HTTP):
pip install cauterule[llm]
# With OpenTelemetry export:
pip install cauterule[otel]
# Everything:
pip install cauterule[all]

# Run the demo — seeded failures, full loop in 60s
cauterule demo

# Extract a rule from a trajectory
cauterule extract trajectory.jsonl

# Replay-test a candidate rule
cauterule test R-001

# Promote to the permanent store
cauterule promote R-001

# Browse rules
cauterule list
cauterule health
cauterule validate

# Export rules to your agent's format
cauterule export --format agents
```

---

## What's Shipped in v0.2.0

### Core Loop
- Trajectory capture with secret redaction
- Multi-pass LLM extraction (3x, temperature variation, draft tournament)
- Failure clustering — one extraction per failure cluster, not per failure
- Historical replay engine with deterministic evidence reports
- Promotion gate — auto, human-review, or hybrid mode
- Rule linter (vagueness, tautology, duplicate, contradiction, untestable, unsafe)
- Conflict detection and rule consolidation
- Versioned YAML rule store with git provenance

### CLI (25+ Commands)
- `cauterule init` | `demo` | `extract` (`--dry-run`) | `test` (`--ci`) | `promote` | `inject` | `list` | `show` | `search`
- `cauterule audit` | `diff` | `retire` | `history` | `conflicts` | `health` | `validate`
- `cauterule counterfactual` | `story` | `explain` | `config` | `metrics` | `report` | `pack list` | `pack info`
- `cauterule export` (`--format agents`) | `import` | `rewind` (Failure Time Machine) | `cauterule mcp` (MCP server)
- **NEW** `cauterule review` — TUI review interface with confidence-ordered queue
- **NEW** `cauterule observe` — observability metrics and learning journal
- **NEW** `cauterule corpus` — add/list/validate/lint/build/export trajectory corpora
- **NEW** `cauterule benchmark` — list/run performance benchmarks

### Replay Engine
- Replay harness with evidence reports (failures prevented, successes broken, precision, recall, verdict)
- "What if?" mode — apply a hypothetical rule and simulate the outcome
- Failure Time Machine — `cauterule rewind <trajectory>` with rule overlay
- Rule Draft Tournament — generate candidates, replay all, rank, promote the winner

### Rule Store
- YAML rule files with provenance metadata and tags
- Auto-classified failure taxonomy (`git/push`, `python/import`, `docker/network`)
- Git-based versioning, rollback, archive directory
- Rule consolidation — merge overlapping triggers

### Rule Injection
- Structured matching by trigger, tool, error type, context, tags, taxonomy
- Specificity ordering — more specific rules injected first
- Rule explanations, templating (retry, verify-then-act, check-preconditions)
- Context budget optimizer, preflight mode

### Rule Packs (Bundled)
- `pack-git` — 10+ pre-built git rules (push, merge, rebase, conflicts)
- Zero cold-start: rules work out of the box, zero LLM cost

### Export & Import (Day-One Interop)
- Export to `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `aider.conf.yml`, markdown, JSON
- Import from `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, and chat history

### MCP Server
- 4 tools: `get_matching_rules`, `get_rule`, `list_rules`, `report_failure`
- Any MCP-compatible agent (Claude, etc.) consumes rules with zero code changes

### Custom Agent Adapter
- `@cauterule.watch` decorator — wrap any agent function, auto-captures trajectories on failure
- `cauterule.inject()` context manager — prep context with matching rules before task execution
- Works with any Python agent — no framework lock-in

### Corpus & Field Test Infrastructure
- 13 corpus types totaling 394 trajectories (curated + raw, v0.1.0)
- v0.2.0 public corpus: 160 trajectories (golden families ×10, domain-specific ×50, counterexample ×20, near-miss ×20, staleness ×10, synthetic ×50)
- All public trajectories annotated with `expected_outcome` and `expected_outcome_rationale` for ground-truth verification
- **NEW** 6 adversarial corpora (staleness, counterexample, noise injection, prompt injection, redaction bypass, near-miss escalation)
- **NEW** Pre-extraction gate with corpus validation, annotations, preflight, and harness health checks

### NEW in v0.2.0

- **TUI review interface** — confidence-ordered review queue, filtering, approval/rejection workflows
- **Observability subsystem** — hit counters, coverage scoring, learning journal, metrics export
- **Adversarial corpus generation** — 6 corpora testing rule robustness
- **Distribution channels** — Docker image, standalone binary, GitHub Action, webhook notifications, OpenTelemetry export
- **Benchmark leaderboard** — determinism, acceptance, rejection, bake-off, mutation, calibration, ablation suites
- **Pack certification baseline** — rule pack validation harness with safety scoring
- **Safety-adjusted ranking** — broad-trigger penalty, silence scoring, trigger specificity metrics
- **Human review workflow** — sampling strategies, review queue management, TUI integration
- **Scale and reliability tests** — latency, memory, conflict detection, concurrency

### Configuration
- `cauterule.toml` — LLM provider, model, thresholds, mode, paths, redaction patterns
- Environment variable support — `CAUTERULE_LLM_PROVIDER`, `CAUTERULE_MODEL`, etc.
- LLM provider abstraction — OpenAI, Anthropic, Ollama, LiteLLM
- Promotion mode — auto, human-review, hybrid

---

## Field Test Results

The v0.2.0 field test expanded on v0.1.0 with safety-adjusted model rankings, adversarial corpora, and 160 additional public trajectories:

Key findings:
- Parser and prompt fixes improved local-model parse reliability from ~30% to near 100%
- Safety-adjusted ranking surfaces broad-trigger penalties and wrong-decision rates
- Adversarial corpora expose rule staleness, counterexamples, and redaction bypass
- Safety corpora remain the hardest unsolved area across all models

Full reports:
- v0.1.0: [`docs/field-test/v0.1.0/FIELD_TEST_REPORT.md`](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md)
- v0.2.0: [`docs/field-test/v0.2.0/FIELD_TEST_REPORT.md`](docs/field-test/v0.2.0/FIELD_TEST_REPORT.md)

---

## Architecture

```
                         ┌──────────────────────────────────────────┐
                         │              CLI / MCP                    │
                         │  cauterule demo | extract | mcp          │
                         └──────┬───────────────────────────┬───────┘
                                │                           │
                                ▼                           ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Trajectory      │ ──> │ Rule Extractor   │ ──> │ Historical Replay │
│ Capture + Redact│     │ (multi-pass LLM) │     │ Engine + Viz      │
└─────────────────┘     └──────────────────┘     └───────────────────┘
       │                        │                         │
       ▼                        ▼                         ▼
┌─────────────────┐     ┌──────────────┐          ┌───────────────────┐
│ Rule Injection  │ <── │ Standing-Rules│ <── ─── │ Promotion Gate    │
│ + Explanations  │     │ Store (YAML)  │     │   │ + Linter + Conflicts│
└─────────────────┘     └──────┬───────┘     │
                               │             │
                               ▼             ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Export / Import │     │ Corpus & Field   │     │ Basic Observability│
│ 7 formats       │     │ Test Runner      │     │ Metrics + Report  │
│ MCP server      │     │ 394 trajectories │     │ Health + Validate │
└─────────────────┘     └──────────────────┘     └───────────────────┘
```

---

## Roadmap

| Version | Theme | Key Deliverable |
|---------|-------|-----------------|
| **v0.1.0** ✅ | Core Loop + DX | Full loop, 25+ CLI commands, MCP, export/import, packs, corpus, field tests |
| **v0.2.0** ✅ | Distribution + Polish | TUI review, observability, corpus infra (160 public trajs), 12 benchmarks, adversarial corpora, Docker, binary, GitHub Action, webhook, OTEL |
| **v0.3.0** | Rule Pack Ecosystem | pack install/create/publish, official packs (docker, deploy, testing, python) |
| **v0.4.0** | Deep Integrations | AgentObservatory, AgentEvalForge, LangSmith/Phoenix |
| **v0.5.0** | Observability & Analytics | Web dashboard, trend lines, weekly digest |
| **v0.6.0** | Advanced Retrieval | Semantic matching, hybrid matching, rule embedding index |
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
- [Field Test Report (v0.2.0)](docs/field-test/v0.2.0/FIELD_TEST_REPORT.md)
- [Field Test Report (v0.1.0)](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md)
- [Release Notes (v0.2.0)](docs/release/v0.2.0/release-notes.md)
- [Release Notes (v0.1.0)](docs/release/v0.1.0/release-notes.md)
- [Changelog](CHANGELOG.md)
- [Docs Index](docs/README.md)
- [PRD: Why](docs/design/prd/01-why.md)
- [Architecture](docs/design/prd/02-architecture.md)
- [WBS v0.1.0](docs/wbs/v0.1.0/wbs-v0.1.0-index.md)

---

## License

MIT — see [LICENSE](LICENSE).