# CauterRule

**Automated standing-rule extraction from agent failures.**

Every agent fails. CauterRule ensures they never make the *same* failure twice.

After every failure, CauterRule:
1. **Extracts** a structured *when X, do Y* standing rule from the execution trajectory (multi-pass with draft tournament)
2. **Tests** that candidate rule against historical scenarios (past failures + past successes — deterministic replay)
3. **Promotes** only rules that survive replay into the agent's permanent rule store (with linter, conflict detection, provenance)

No more corrections dying in chat. No more 134 hand-written standing rules. No more vague reflection paragraphs nobody re-reads. Rules are actionable, tested, and permanent.

---

## Why

The current state of "learning from mistakes" in agent systems is reflection-as-a-paragraph — prose that bloats the context window and is never read again. The manual alternative is 134 standing rules maintained by hand. Both are broken.

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
| No OSS tool ships a corpus or benchmarks | Tiered corpus, gold families, counterexample/near-miss/redaction/adversarial corpora |

---

## v0.1.0 Feature Set

**Status:** Pre-release / in development. 32 milestones, 241 tasks, 270+ issues.

### Core Loop
- Trajectory capture with secret redaction
- Multi-pass LLM extraction (3x, temperature variation, draft tournament)
- Failure clustering — one extraction per failure cluster, not per failure
- Historical replay engine with deterministic evidence reports
- Promotion gate — auto, human-review, or hybrid mode
- Rule linter (vagueness, tautology, duplicate, contradiction, untestable, unsafe)
- Conflict detection and rule consolidation
- Versioned YAML rule store with git provenance

### CLI & DX (25+ Commands)
- `cauterule demo` | `init` | `extract` | `test` | `promote` | `inject` | `list` | `show` | `search`
- `cauterule audit` | `diff` | `review` (TUI) | `retire` | `history` | `conflicts` | `validate` | `health`
- `cauterule counterfactual` | `story` | `explain` | `config` | `metrics` | `report` | `pack`
- `cauterule rewind` (Failure Time Machine) | `cauterule mcp` (MCP server)

### Interop
- Export to `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `aider.conf.yml`, markdown, JSON
- Import from `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, and chat history
- MCP server — 4 tools: `get_matching_rules`, `get_rule`, `list_rules`, `report_failure`
- `@cauterule.watch` decorator — add learning to any Python agent in 5 lines

### Bundled Rule Packs
- `pack-git` — 10-15 pre-built git rules (push, merge, rebase, conflicts, hooks)
- Zero cold-start: rules work out of the box, zero LLM cost

### Observability
- Metrics CLI, markdown reports, learning journal, failure pattern leaderboard
- Coverage gap detector, rule coverage score, domain coverage score
- Coverage frontier — identifies the next most valuable area to learn

### Corpus & Benchmarks
- Tiered corpus (tiny 25 / small 100 / medium 1k / large 10k+)
- Domain-specific corpora (coding, DevOps, research, support, automation)
- Gold rule families, counterexample/near-miss/staleness/redaction/adversarial corpora
- Model bake-off harness, prompt bake-off harness, ablation studies

### Scale & Safety
- Replay throughput, injection latency, conflict explosion, concurrent ingestion benchmarks
- 6 adversarial corpora (injection, misleading, contradiction, unsafe, poisoning, leakage)
- 8 field tests (coding, long-horizon, noisy, cold-start, cross-session, regression, multi-env, human-correction)

### Distribution
- `pip install cauterule`, Homebrew, Docker, standalone binary
- GitHub Action, webhook on promotion, OpenTelemetry, GitHub badge

---

## Roadmap

| Version | Theme | Key Deliverable |
|---------|-------|-----------------|
| **v0.1.0** | Core Loop + First-Class DX | Full loop, 25+ CLI commands, MCP, export/import, packs, corpus, benchmarks, field tests, adversarial tests, distribution |
| **v0.1.1** | Framework Adapters | LangGraph, CrewAI, PydanticAI adapters |
| **v0.2.0** | Rule Lifecycle Management | Specificity scoring, outcome tracking, automated retirement, supersession chains |
| **v0.3.0** | Rule Pack Ecosystem | pack install/create/publish, official packs (docker, deploy, testing, python) |
| **v0.4.0** | Deep Integrations | AgentObservatory, AgentEvalForge, DecisionJournal, LangSmith/Phoenix |
| **v0.5.0** | Observability & Analytics | Web dashboard, trend lines, weekly digest, failure recurrence tracking |
| **v0.6.0** | Advanced Retrieval | Semantic matching, hybrid matching, rule embedding index |
| **v0.7.0** | Multi-Agent | Cross-agent transfer, shared registry, rule governance, fleet management |

See [docs/design/prd/05-features.md](docs/design/prd/05-features.md) for the full feature breakdown.

---

## Quick Start (Coming Soon)

```bash
pip install cauterule

# Run the demo — seeded failures, 10 rules extracted → tested → promoted in 60s
cauterule demo

# Watch your own agent fail and learn
cauterule watch --agent my_agent.py

# Browse and manage rules
cauterule list          # browse promoted rules
cauterule review        # TUI for reviewing pending promotions
cauterule health        # rule store health report
cauterule counterfactual # "if you had these rules, you'd have avoided X failures"
cauterule story         # generate narrative of your agent's learning journey
```

---

## Architecture

```
                         ┌──────────────────────────────────────────┐
                         │              CLI / TUI / MCP              │
                         │  cauterule demo | review | rewind | mcp  │
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
│ + Templates     │     │ + Packs       │     │   └───────────────────┘
└─────────────────┘     └──────┬───────┘     │
                               │             │
                               ▼             ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Export / Import │     │ Corpus & Bench   │     │ Observability     │
│ 7 formats       │     │ Tiered + Gold    │     │ Metrics + Report  │
│ MCP server      │     │ Adversarial      │     │ Coverage + Health │
└─────────────────┘     └──────────────────┘     └───────────────────┘
```

---

## Related Ecosystem

CauterRule is the **learning layer** in an open-source agent infrastructure stack. These public repos from the same ecosystem are complementary:

| Project | Layer | How it relates |
|---------|-------|----------------|
| [planner-critic-engine](https://github.com/deghosal-2026/planner-critic-engine) | Prevention | Catches flawed plans *before* execution — reduces failures CauterRule needs to learn from |
| [agent-self-edit](https://github.com/deghosal-2026/agent-self-edit) | Prompt Learning | Twin learning engine — extracts *prompt edits* from failures. CauterRule extracts *standing rules*. Both run extract → test → promote |
| [agent-tooltrust](https://github.com/deghosal-2026/agent-tooltrust) | Tool Safety | Runtime permission engine — CauterRule's rules can feed into tool policy decisions |
| [agent-eval-forge](https://github.com/deghosal-2026/agent-eval-forge) | Evaluation | "pytest for agents" — could be the replay-testing backend for CauterRule's candidate rules |
| [agent-exec-trace](https://github.com/deghosal-2026/agent-exec-trace) | Observability | 40-detector anomaly engine — detects failures that trigger CauterRule's extraction pipeline |
| [ai-loopguard](https://github.com/deghosal-2026/ai-loopguard) | Circuit Breaker | Real-time failure handling — CauterRule encodes the lesson so the breaker isn't needed next time |

---

## Documentation

- [Docs Index](docs/README.md)
- [PRD: Why](docs/design/prd/01-why.md)
- [Feature Breakdown](docs/design/prd/05-features.md)
- [Architecture](docs/design/prd/02-architecture.md)
- [Design Decisions](docs/design/design-decisions.md)
- [Roadmap](docs/design/prd/09-roadmap.md)
- [Success Metrics](docs/design/prd/07-success-metrics.md)
- [WBS v0.1.0](docs/wbs/v0.1.0/wbs-v0.1.0-index.md)

---

## License

MIT — see [LICENSE](LICENSE).