# CauterRule

**Automated standing-rule extraction from agent failures.**

Every agent fails. CauterRule ensures they never make the *same* failure twice.

After every failure, CauterRule:
1. **Extracts** a structured *when X, do Y* standing rule from the execution trajectory (multi-pass with draft tournament)
2. **Tests** that candidate rule against historical scenarios (past failures + past successes — deterministic replay)
3. **Promotes** only rules that survive replay into the agent's permanent rule store (with linter, conflict detection, provenance)

No more corrections dying in chat. No more hand-written standing rules. No more vague reflection paragraphs nobody re-reads. Rules are actionable, tested, and permanent.

**Status:** v0.1.0 — Field test complete. [Read the full report](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md).

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
| No OSS tool ships a corpus or benchmarks | 13 corpus types, 394 trajectories, golden set, safety corpora, field test runner |

---

## Quick Start

```bash
pip install cauterule

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

## What's Shipped in v0.1.0

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
- `cauterule rewind` (Failure Time Machine) | `cauterule mcp` (MCP server)

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
- 13 corpus types totaling 394 trajectories (curated + raw)
- Golden trajectory set with known expected rules
- Safety corpora: `successes`, `failures/negative`, `nearmiss`, `noisy`, `corrections`
- Raw corpora: OpenCode sessions, synthetic scenarios, CI failure logs, sibling-repo runs
- Field test runner supporting local OMLX and cloud OpenRouter LLMs
- 844+ deterministic tests passing, 104 Docker tests passing

### Configuration
- `cauterule.toml` — LLM provider, model, thresholds, mode, paths, redaction patterns
- Environment variable support — `CAUTERULE_LLM_PROVIDER`, `CAUTERULE_MODEL`, etc.
- LLM provider abstraction — OpenAI, Anthropic, Ollama, LiteLLM
- Promotion mode — auto, human-review, hybrid

---

## Field Test Results

The full v0.1.0 field test evaluated 4 models across 13 corpus types (394 trajectories):

| Model | Type | Candidates | Pass | Inconclusive | Fail |
|---|---|---:|---:|---:|---:|
| Llama-3.2-3B-Instruct-4bit | Local OMLX | 379 | 72 | 189 | 118 |
| Qwen3-4B-Instruct-2507-4bit | Local OMLX | 373 | 93 | 209 | 71 |
| openai/gpt-4o-mini | Cloud OpenRouter | 394 | 77 | 248 | 69 |
| meta-llama/llama-3.1-8b-instruct | Cloud OpenRouter | 392 | 123 | 168 | 101 |

Key findings:
- Parser and prompt fixes improved local-model parse reliability from ~30% to near 100%
- `meta-llama/llama-3.1-8b-instruct` was the strongest cost-effective model tested
- Safety corpora remain the hardest unsolved area across all models

Full report: [`docs/field-test/v0.1.0/FIELD_TEST_REPORT.md`](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md)

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
| **v0.2.0** | Distribution + Polish | TUI review, observability, adversarial corpora, Homebrew, GitHub Action, webhook, OTEL |
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
- [Field Test Report](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md)
- [Release Notes](docs/release/v0.1.0/release-notes.md)
- [Changelog](CHANGELOG.md)
- [Docs Index](docs/README.md)
- [PRD: Why](docs/design/prd/01-why.md)
- [Architecture](docs/design/prd/02-architecture.md)
- [WBS v0.1.0](docs/wbs/v0.1.0/wbs-v0.1.0-index.md)

---

## License

MIT — see [LICENSE](LICENSE).