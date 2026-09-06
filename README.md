# CauterRule

**Automated standing-rule extraction from agent failures.**

Every agent fails. CauterRule ensures they never make the *same* failure twice.

After every failure, CauterRule:
1. **Extracts** a structured *when X, do Y* standing rule from the execution trajectory (multi-pass with draft tournament)
2. **Tests** that candidate rule against historical scenarios (past failures + past successes — deterministic replay)
3. **Promotes** only rules that survive replay into the agent's permanent rule store (with linter, conflict detection, provenance)

No more corrections dying in chat. No more 134 hand-written standing rules. No more vague reflection paragraphs nobody re-reads. Rules are actionable, tested, and permanent.

**Status:** v0.1.0 — Field test complete. [Read the full report](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md).

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

**Status:** v0.1.0 released. [Field test report](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md). [Release notes](docs/release/v0.1.0/release-notes.md).

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
- `cauterule audit` | `diff` | `review` (TUI) | `retire` | `history` | `conflicts` | `health` | `validate`
- `cauterule counterfactual` | `story` | `explain` | `config` | `metrics` | `report` | `pack list` | `pack info`
- `cauterule rewind` (Failure Time Machine) | `cauterule mcp` (MCP server)

### Replay Engine
- Replay harness with evidence reports (failures prevented, successes broken, precision, recall, verdict)
- Replay visualization — step-by-step view of how a rule changes a past trajectory
- Failure Time Machine — `cauterule rewind <trajectory>` with rule overlay
- "What if?" mode — apply a hypothetical rule and simulate the outcome
- Replay diff — before/after comparison of agent behavior with and without a rule
- Insufficient history detection — warns when replay count is below threshold
- Rule Draft Tournament — generate 3-5 candidates, replay all, rank, promote the winner

### Rule Store
- YAML rule files with provenance metadata and tags
- Auto-classified failure taxonomy (`git/push`, `python/import`, `docker/network`)
- Git-based versioning, rollback, archive directory
- Rule consolidation — merge overlapping triggers
- Rule linter — validates for vagueness, tautologies, duplicates, contradictions, untestable directives

### Rule Injection
- Structured matching by trigger, tool, error type, context, tags, taxonomy
- Specificity ordering — more specific rules injected first
- Rule explanations — LLM generates human-readable explanation of why a rule fires
- Rule templating — retry, verify-then-act, check-preconditions
- Context budget optimizer — rank and compress rules to fit token limits
- Lesson portfolio optimizer — if only N rules can be injected, choose the set that maximizes expected failure prevention
- Preflight mode — predict likely failures and recommend rules before a task
- No-match graceful degradation

### Rule Packs (Bundled)
- `pack-git` — 10-15 pre-built git rules (push, merge, rebase, conflicts, hooks)
- Zero cold-start: rules work out of the box, zero LLM cost

### Export & Import (Day-One Interop)
- Export to `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `aider.conf.yml`, markdown, JSON
- Import from `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, and chat history

### MCP Server
- 4 tools: `get_matching_rules`, `get_rule`, `list_rules`, `report_failure`
- Any MCP-compatible agent (Claude, etc.) consumes rules with zero code changes
- Stdio (local) + HTTP (remote) transport
- `cauterule mcp` — launch the server

### Integrations
- GitHub Action — `cauterule/action` — extraction on CI failures, promote via PR
- Webhook on promotion — notify Slack/Discord/GitHub
- OpenTelemetry — emit rule hit/promotion/extraction events
- GitHub badge — "CauterRule: N rules learned" (shields.io-style)

### Distribution
- PyPI — `pip install cauterule`
- Homebrew — `brew install cauterule`
- Docker — `docker run cauterule demo`
- Standalone binary — `curl install` for non-Python users

### Custom Agent Adapter
- `@cauterule.watch` decorator — wrap any agent function, auto-captures trajectories on failure
- `cauterule.inject()` context manager — prep context with matching rules before task execution
- Adapter docs — "Add CauterRule to your agent in 5 lines"
- Works with any Python agent — no framework lock-in

### TUI Review
- `cauterule review` — rich terminal UI (textual/rich) for browsing, approving, rejecting candidates
- Evidence summary cards — "This rule would have prevented 3 failures, broken 0 successes"
- Rule confidence cards — confidence, failures prevented, successes broken, last hit, tags
- Human annotation capture — tag, comment, categorize failures before extraction
- Batch review mode — review 10 candidates in one session
- Filter by tag, status, confidence

### Observability
- `cauterule metrics` — CLI summary: rules promoted, replay precision, repeat-failure rate, store size
- `cauterule report` — generate markdown report for sharing
- Per-rule hit counter and last-match timestamp
- Failure pattern leaderboard — most common failure classes, most prevented, top gaps
- Coverage gap detector — domains with repeated failures but no matching rules
- Rule coverage score — weighted blend of coverage %, precision %, stale-rule %
- Domain coverage score — how well current rules cover failure classes across domains
- Failure-class coverage score — % of recurring failure classes with at least one validated rule
- Coverage frontier — identify the next most valuable domain to learn
- Learning journal — auto-generated markdown log of each failure → rule → replay → promotion
- Monthly learning report — rules learned, failures reduced, coverage gaps found

### Sample & Demo
- Seeded failure history — 10+ pre-built trajectories (git, docker, deploy, python, shell, CI, env)
- Scenario library — curated scenarios for immediate testing
- `cauterule demo` — narrated walkthrough of the full loop
- Example agent — toy agent that fails, learns, succeeds on the second try
- Example rule store — 10 promoted rules with full provenance
- Bundled pack-git demo — rules working out of the box
- Human correction capture demo — "next time do X" → candidate → replay → promote
- `cauterule init` templates — scaffold a new project
- Public demo corpus — reproducible data set with screenshots, recordings, expected outputs
- Animated demo GIF in README

### Field Test Program
- Single-agent coding field test — repeat-failure reduction over one week
- Long-horizon task field test — 20-50 step tasks, late-stage failures
- Noisy trajectory field test — retries, irrelevant calls, distractions
- Human-in-the-loop field test — auto vs human promotion comparison
- Cold-start field test — time to first useful rule from zero
- Cross-session memory field test — failure in session 1, rule applied in session 2
- Regression field test — old rules still pass after model/prompt changes
- Multi-environment field test — macOS, Linux, CI container

### Corpus & Benchmarks
- Tiered corpus: tiny (25), small (100), medium (1k), large (10k+) — balanced success/failure
- Domain-specific corpora — coding, DevOps, research, support, browser automation
- Trajectory quality labels — clear, ambiguous, multi-causal, misleading, operator-induced
- Gold rule families — multiple acceptable abstractions per benchmark scenario
- Counterexample corpus — plausible rules that should be rejected
- Near-miss corpus — scenarios that look similar but should not trigger
- Staleness corpus — historical failures that no longer matter
- Redaction corpus — trajectories with secrets, validates sanitization
- Public synthetic corpus + private local corpus mode
- Model bake-off harness — compare GPT, Claude, local models
- Prompt bake-off harness — compare extractor prompt variants
- Ablation studies — no clustering vs clustering, single-pass vs multi-pass, tags vs no tags
- Human vs LLM lesson comparison — manually written rules vs extracted rules

### Scale & Reliability
- Replay throughput benchmarks — candidates processed per minute
- Injection latency benchmarks — p50 <100ms, p95 <500ms on `small` corpus
- Conflict explosion benchmarks — 100/1k/10k rules, <5s at 1k
- Storage churn benchmarks — YAML + git under frequent promote/retire
- Concurrent ingestion — multiple failures at once, queue, dedup, consistent promotion
- LLM cost benchmarks — cost per extracted candidate, per promoted rule, per prevented failure
- Memory footprint benchmarks — <1GB RAM on `small` corpus
- Incremental indexing benchmarks — <1s per new rule at 1k rules
- Replay determinism tests — same candidate + same corpus = same report
- Extractor stability tests — repeat extraction, bounded variance
- Confidence calibration — extractor confidence correlates with replay outcomes

### Safety & Adversarial Testing
- Prompt injection corpus — >=90% of injection attempts fail
- Misleading root-cause corpus — extractor avoids superficial lessons
- Contradiction stress tests — >=90% detection recall
- Unsafe directive corpus — >=95% blocked by linter or gate
- Data poisoning simulation — poisoned trajectories caught by replay
- Instruction leakage tests — no secrets survive export

### Coverage & Optimization
- Domain coverage score — how well rules cover failure classes across domains
- Failure-class coverage score — % of recurring classes with a validated rule
- Coverage frontier — next most valuable area to learn
- Lesson portfolio optimizer — maximize expected failure prevention with N rules
- Context budget optimizer — prioritize and compress injected rules to fit token limits

### Community & Ecosystem
- Corpus contribution guide — submit anonymized or synthetic trajectories
- Official benchmark leaderboard — publish model + prompt results
- Pack certification baseline — minimum safety, replay, and provenance checks
- Monthly learning report — auto-generated report of rules learned, failures reduced, coverage gaps
- Public demo corpus — reproducible data set with screenshots, recordings, expected outputs

### Configuration
- `cauterule.toml` — LLM provider, model, thresholds, mode, paths, redaction patterns, extraction passes/temperatures
- Environment variable support — `CAUTERULE_LLM_PROVIDER`, `CAUTERULE_MODEL`, etc.
- LLM provider abstraction — OpenAI, Anthropic, Ollama, LiteLLM
- Promotion mode — auto, human-review, hybrid
- Replay thresholds — conservative, balanced, aggressive
- Extraction config — passes (default 3), temperatures, confidence threshold

### Quality & OSS Hygiene
- `pyproject.toml` — installable via `pip install cauterule`
- Type-checked — mypy strict, zero errors
- Linted — ruff, zero warnings
- Tested — pytest, >=80% coverage on core modules (exit gate: >95%)
- CI — GitHub Actions: lint, type-check, test on every PR
- `CONTRIBUTING.md` — how to contribute, adapter spec, rule pack format, corpus guide
- `CHANGELOG.md` — conventional commits, Keep a Changelog format
- `SECURITY.md` — security policy, threat model summary, adversarial coverage

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

## Quick Start

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

## Field Test Results

The full v0.1.0 field test evaluated 4 models (2 local OMLX, 2 cloud) across 13 corpus types totaling 394 trajectories. Key findings:

- **Parser and prompt fixes** dramatically improved benchmark reliability
- **Local 3B-4B models** are now viable for internal regression tracking
- **Cloud models** (especially `meta-llama/llama-3.1-8b-instruct`) provide stronger quality ceilings
- **Safety corpora** (`successes`, `failures/negative`, `nearmiss`) remain the hardest unsolved area

Read the full report: [`docs/field-test/v0.1.0/FIELD_TEST_REPORT.md`](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md)

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

- [User Guide](docs/USER_GUIDE.md)
- [Field Test Report](docs/field-test/v0.1.0/FIELD_TEST_REPORT.md)
- [Release Notes](docs/release/v0.1.0/release-notes.md)
- [Changelog](CHANGELOG.md)
- [Docs Index](docs/README.md)
- [PRD: Why](docs/design/prd/01-why.md)
- [Feature Breakdown](docs/design/prd/05-features.md)
- [Architecture](docs/design/prd/02-architecture.md)
- [Design Decisions](docs/design/design-decisions.md)
- [Roadmap](docs/design/prd/09-roadmap.md)
- [Success Metrics](docs/design/prd/07-success-metrics.md)
- [Risks](docs/design/prd/08-risks.md)
- [WBS v0.1.0](docs/wbs/v0.1.0/wbs-v0.1.0-index.md)

---

## License

MIT — see [LICENSE](LICENSE).