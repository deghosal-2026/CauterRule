# PRD 05: Features

## Feature Pillars

CauterRule is built on five pillars that make it a compelling, differentiated OSS project:

| Pillar | What it delivers |
|--------|-----------------|
| **Self-Improving Loop** | The extract → test → promote cycle that no other agent memory tool offers |
| **Framework Adapters** | Plug into any agent framework — LangGraph, CrewAI, PydanticAI, custom loops |
| **Rule Packs** | Pre-built, shareable rule collections — npm for agent behavioral knowledge |
| **DX & Observability** | CLI, TUI, replay dashboard, metrics — see your agent's knowledge compound |
| **Community & Extensibility** | MCP server, marketplace, webhook integrations — make rules a first-class artifact |

---

## v0.1.0 — Core Loop + First-Class DX (The "Wow" Release)

> **Goal:** Ship a complete, usable, impressive system on day one. Not just the loop — the loop *plus* the developer experience that makes people want to use it and show it off. The "wow" moment: `pip install cauterule && cauterule demo` — watch an agent fail, extract a rule, replay-test it, promote it, and see it fire on the next run — all in 60 seconds.

### Core Loop

- [ ] **Trajectory capture** on failure with structured logging (JSONL)
- [ ] **LLM extraction** of candidate standing rules (*when X, do Y*) with structured output parsing
- [ ] **Historical replay testing** — replay candidate against past failures + past successes
- [ ] **Promotion gate** with pass/fail evidence report (precision, recall, verdict)
- [ ] **Standing-rules store** in versioned YAML files with full provenance
- [ ] **Rule injection** into context on future matching tasks (structured matching)
- [ ] **Rule lifecycle** — promote, retire, supersede with git-committed history

### CLI (Full Surface)

- [ ] `cauterule demo` — seeded failure history, 10 rules extracted → tested → promoted in <60s
- [ ] `cauterule extract <trajectory>` — extract a candidate rule from a trajectory file
- [ ] `cauterule test <rule>` — replay-test a candidate against history, print evidence report
- [ ] `cauterule promote <rule>` — promote a tested rule to the store (git commit)
- [ ] `cauterule inject <task>` — show which rules would fire for a given task
- [ ] `cauterule list` — browse all promoted rules (table: id, trigger, status, hits)
- [ ] `cauterule show <rule-id>` — full provenance view (source failure → evidence → promotion)
- [ ] `cauterule retire <rule-id>` — retire a rule with reason (git commit)
- [ ] `cauterule history` — git-log-style timeline of all promotions and retirements
- [ ] `cauterule config` — view/edit configuration (LLM provider, thresholds, mode)

### Replay Engine

- [ ] **Replay harness** — load historical trajectories, simulate rule application, score outcome
- [ ] **Evidence report** — failures prevented, successes broken, precision, recall, verdict
- [ ] **Replay visualization** — step-by-step view of how a rule would have changed a past trajectory
- [ ] **"What if?" mode** — apply a hypothetical rule to a trajectory and see the simulated outcome
- [ ] **Replay diff** — before/after comparison of agent behavior with and without a rule
- [ ] **Insufficient history detection** — warn when replay count is below threshold

### Rule Store

- [ ] **YAML rule files** — one rule per file, with provenance metadata
- [ ] **Index file** — `rules/index.yaml` with all rules, statuses, summaries
- [ ] **Git-based versioning** — every promotion/retirement is a git commit with conventional message
- [ ] **Rollback** — `git revert` any promotion; rule store stays consistent
- [ ] **Archive directory** — retired/superseded rules moved to `rules/archived/`

### Rule Injection

- [ ] **Structured matching** — match by trigger pattern, tool name, error type, context clauses
- [ ] **Specificity ordering** — more specific rules injected first
- [ ] **Injection format** — clean markdown block injected into agent context
- [ ] **Injection preview** — `cauterule inject <task>` shows what would be injected without running
- [ ] **No-match graceful degradation** — if no rules match, agent runs without standing-rule context

### Export & Import (Day-One Interop)

- [ ] **Export to `.cursorrules`** — `cauterule export --format cursor` — drop-in for Cursor
- [ ] **Export to `CLAUDE.md`** — `cauterule export --format claude` — drop-in for Claude Code
- [ ] **Export to `AGENTS.md`** — `cauterule export --format agents` — drop-in for any agent
- [ ] **Export to markdown** — `cauterule export --format markdown` — human-readable rule doc
- [ ] **Export to JSON** — `cauterule export --format json` — machine-readable
- [ ] **Import from `.cursorrules` / `CLAUDE.md` / `AGENTS.md`** — convert existing conventions to testable rules

### Custom Agent Adapter

- [ ] **`@cauterule.watch` decorator** — wrap any agent function: auto-captures trajectories on failure
- [ ] **`cauterule.inject()` context manager** — prep context with matching rules before task execution
- [ ] **Adapter docs** — "Add CauterRule to your agent in 5 lines"
- [ ] Works with any Python agent — no framework lock-in for v0.1.0

### Observability (Lite)

- [ ] `cauterule metrics` — CLI summary: rules promoted, replay precision, repeat-failure rate, rule store size
- [ ] `cauterule report` — generate a markdown report (rules, evidence, metrics) for sharing
- [ ] Per-rule hit counter — how many times each rule has matched
- [ ] Last-match timestamp per rule

### Sample & Demo

- [ ] **Seeded failure history** — 10+ pre-built trajectories (git failures, docker failures, deploy failures)
- [ ] **`cauterule demo`** — runs the full loop on seeded data, prints a narrated walkthrough
- [ ] **Example agent** — a toy agent in `examples/` that fails, learns, and succeeds on the second try
- [ ] **Rule store example** — `examples/rules/` showing 10 promoted rules with full provenance

### Configuration

- [ ] **`cauterule.toml`** config file — LLM provider, model, thresholds, mode, paths
- [ ] **Environment variable support** — `CAUTERULE_LLM_PROVIDER`, `CAUTERULE_MODEL`, etc.
- [ ] **LLM provider abstraction** — OpenAI, Anthropic, local (Ollama), any LiteLLM-compatible
- [ ] **Promotion mode** — `auto` (promote on pass), `human-review` (require approval), `hybrid` (auto for high-confidence, review for low)
- [ ] **Replay thresholds** — `conservative`, `balanced` (default), `aggressive`

### Quality & OSS Hygiene

- [ ] **`pyproject.toml`** — installable via `pip install cauterule`
- [ ] **Type-checked** — mypy strict, zero errors
- [ ] **Linted** — ruff, zero warnings
- [ ] **Tested** — pytest, ≥80% coverage on core modules
- [ ] **CI** — GitHub Actions: lint, type-check, test on every PR
- [ ] **`CONTRIBUTING.md`** — how to contribute, adapter spec, rule pack format
- [ ] **`CHANGELOG.md`** — conventional commits, Keep a Changelog format
- [ ] **`SECURITY.md`** — security policy, threat model summary

---

## v0.1.1 — Framework Adapters (The "Plug In" Release)

> **Goal:** Make CauterRule work with the frameworks people already use. This is what makes it adoptable, not just interesting.

- [ ] **LangGraph adapter** — trajectory capture as a graph node, rule injection as state prep
- [ ] **CrewAI adapter** — trajectory capture as a crew callback, rule injection as task context
- [ ] **PydanticAI adapter** — trajectory capture as a tool wrapper, rule injection as system prompt
- [ ] **Custom loop adapter** — enhanced `@cauterule.watch` with async support and streaming
- [ ] Adapter spec + docs — "Write your own adapter in 50 lines"
- [ ] `cauterule init --adapter langgraph` — scaffold a new project with CauterRule wired in

---

## v0.2.0 — Intelligence & Rule Lifecycle (The "Grows Up" Release)

> **Goal:** Rules aren't just created — they live, conflict, retire, and consolidate. This is what makes the rule store a managed asset, not a junk drawer.

### Rule Lifecycle
- [ ] Rule conflict detection (direct contradiction + specificity conflict)
- [ ] Specificity scoring and precedence ordering
- [ ] Per-rule outcome tracking (hit rate, would-have-failed-without-it rate)
- [ ] Rule retirement workflow (stale, underperforming, superseded)
- [ ] Rule consolidation — merge similar rules, deduplicate overlapping triggers
- [ ] Supersession chain — R-012 supersedes R-005, with full history

### Review & Human-in-the-Loop
- [ ] **TUI rule browser** — `cauterule review` opens a rich terminal UI for browsing, approving, rejecting rules
- [ ] Evidence summary cards — "This rule would have prevented 3 failures, broken 0 successes"
- [ ] Human annotation capture on failures (tag, comment, categorize)
- [ ] Batch review mode — review 10 candidates in one session
- [ ] `cauterule audit` — full provenance trail for any rule (git log + replay evidence)

---

## v0.3.0 — Rule Packs & Sharing (The "Community" Release)

> **Goal:** Rules are shareable artifacts. Pre-built packs for common agent tasks. This is what turns CauterRule from a tool into an ecosystem.

### Rule Packs
- [ ] **Rule pack format** — a bundle of rules with metadata (name, version, description, author)
- [ ] **Official packs**:
  - `cauterule/pack-git` — rules for git operations (push, merge, rebase, conflicts)
  - `cauterule/pack-docker` — rules for container builds, compose, networking
  - `cauterule/pack-deploy` — rules for deployment failures (k8s, CI/CD, rollback)
  - `cauterule/pack-testing` — rules for test failures (flaky tests, coverage, mocking)
- [ ] `cauterule pack install <name>` — install a rule pack from GitHub
- [ ] `cauterule pack create` — scaffold a new pack from your agent's rule store
- [ ] `cauterule pack publish` — publish a pack as a GitHub release
- [ ] Pack versioning with semantic versioning (major/minor/patch)
- [ ] Pack dependency resolution — pack A depends on pack B

---

## v0.4.0 — MCP Server & Integrations (The "Plumbing" Release)

> **Goal:** Rules are a first-class artifact accessible to any agent, any tool, any platform. MCP makes rules universally consumable.

### MCP Server
- [ ] **CauterRule MCP server** — expose rules as MCP tools:
  - `get_matching_rules(task)` — returns rules matching a task
  - `get_rule(id)` — returns a single rule with full provenance
  - `list_rules(filter)` — browse the rule store
  - `report_failure(trajectory)` — trigger extraction from an MCP client
- [ ] Any MCP-compatible agent (Claude, etc.) can consume rules without code changes
- [ ] MCP transport: stdio (local) + HTTP (remote)

### Integrations
- [ ] **Webhook on promotion** — notify Slack/Discord/GitHub when a rule is promoted
- [ ] **GitHub Action** — `cauterule/action` — run extraction on CI failures, promote rules via PR
- [ ] **AgentObservatory integration** — production failure detection triggers extraction
- [ ] **AgentEvalForge integration** — synthetic scenario generation for replay testing
- [ ] **DecisionJournal integration** — decision log feeds historical scenarios

---

## v0.5.0 — Observability & Analytics (The "Dashboard" Release)

> **Goal:** See your agent's knowledge compound. Metrics, dashboards, and insights that prove the system is working.

### Replay Dashboard
- [ ] **Web dashboard** (FastAPI + React) — visualize:
  - Rule store growth over time
  - Replay precision/recall per rule
  - Hit rate heatmap (which rules fire most)
  - Failure recurrence rate (is it dropping?)
  - Rule conflict graph (visual)
- [ ] `cauterule dashboard` — launch local dashboard server
- [ ] Export dashboard as static HTML for sharing

### Metrics & Telemetry
- [ ] `cauterule metrics` — enhanced with trend lines (rule store growth, precision over time)
- [ ] Per-rule outcome tracking with trend lines
- [ ] "Rules that prevented a failure this week" — weekly digest
- [ ] `cauterule report` — generate a markdown report for stakeholders

---

## v0.6.0 — Advanced Extraction & Retrieval (The "Smarter" Release)

> **Goal:** Better extraction, better matching. Move from structured matching to semantic understanding.

### Semantic Retrieval
- [ ] Embedding-based rule matching — semantic similarity between task and rule triggers
- [ ] Hybrid matching — structured + semantic, with configurable weights
- [ ] Rule embedding index — local vector store for fast retrieval
- [ ] `cauterule match --semantic` — test matching without running the full loop

### Advanced Extraction
- [ ] Multi-pass extraction — extract 3 candidate rules per failure, test all, promote the best
- [ ] Cross-failure pattern detection — "this is the 4th failure of this type, extract a stronger rule"
- [ ] Rule templating — common rule patterns (retry, verify-then-act, check-preconditions)
- [ ] Extraction confidence calibration — track extractor accuracy over time, adjust thresholds

---

## v0.7.0 — Multi-Agent & Cross-Agent Transfer (The "Fleet" Release)

> **Goal:** Rules learned by one agent benefit the fleet. Transfer, share, and govern rules across agents.

- [ ] **Cross-agent rule transfer** — export rules from agent A, import to agent B with context adaptation
- [ ] **Shared rule registry** — a central rule store that multiple agents read from
- [ ] **Rule governance** — approval workflows for shared rules (agent A proposes, human approves, fleet adopts)
- [ ] **Agent profiles** — rules scoped by agent type, environment, and task domain
- [ ] **Rule federation** — combine rules from multiple agents, deduplicate, resolve conflicts
- [ ] `cauterule fleet` — manage rules across multiple agent deployments

---

## Backlog (Future / Exploratory)

Features being considered but not yet scheduled:

- [ ] **Rule A/B testing** — run two rule variants in production, compare outcomes
- [ ] **Rule auto-tuning** — LLM refines rule triggers based on hit/miss data
- [ ] **Rule explanations** — LLM generates a human-readable explanation of why a rule fired
- [ ] **Rule inheritance** — child agents inherit parent rules with overrides
- [ ] **Rule rollback dashboard** — visualize what happens when a rule is retired
- [ ] **Rule pack marketplace** — community-submitted packs with ratings and reviews
- [ ] **Federated learning** — agents share anonymized failure patterns without sharing trajectories
- [ ] **Rule DSL** — a domain-specific language for writing rules by hand that are test-compatible
- [ ] **Rule testing in CI** — `cauterule test --ci` — run replay tests as part of your CI pipeline
- [ ] **Rule provenance graph** — interactive graph showing the full lineage of every rule

---

## Version Summary

| Version | Theme | Key Deliverable |
|---------|-------|-----------------|
| **v0.1.0** | Core Loop + First-Class DX | Extract → test → promote + CLI + replay + export/import + adapter + demo |
| **v0.1.1** | Framework Adapters | LangGraph, CrewAI, PydanticAI adapters |
| **v0.2.0** | Intelligence | Conflict detection, retirement, TUI review |
| **v0.3.0** | Rule Packs | Pre-built, shareable rule collections |
| **v0.4.0** | MCP & Integrations | Rules as MCP tools, GitHub Action, webhooks |
| **v0.5.0** | Observability | Dashboard, metrics, replay visualization |
| **v0.6.0** | Advanced Retrieval | Semantic matching, multi-pass extraction |
| **v0.7.0** | Multi-Agent | Cross-agent transfer, fleet governance |

---

## What Makes v0.1.0 Exciting as OSS

| Hook | Why it gets engagement |
|------|----------------------|
| **"My agent wrote its own rules"** | The demo is visceral — watch a failure become a tested rule in 60 seconds |
| **`.cursorrules` / `CLAUDE.md` export** | Drop-in compatibility with tools people already use — zero migration friction |
| **Import existing conventions** | Turn your static `CLAUDE.md` into tested, provenance-tracked rules |
| **`@cauterule.watch` decorator** | Add learning to any agent in 5 lines — no framework lock-in |
| **Replay visualization** | See exactly how a rule would have changed a past failure — visual proof it works |
| **"What if?" mode** | Apply a hypothetical rule to history before promoting — test before you trust |
| **Full CLI surface** | 10+ commands on day one — not a toy, a usable tool |
| **`cauterule report`** | Generate a shareable markdown report — show your boss the agent is learning |