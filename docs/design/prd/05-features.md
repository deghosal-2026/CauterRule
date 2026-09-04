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

## v0.1.0 — Core Loop (The "Wow" Release)

> **Goal:** A complete extract → test → promote loop that runs on any agent. The "wow" moment: watch your agent fail, extract a rule, replay-test it, and promote it — all in one command.

### Must-Have
- [ ] Trajectory capture on failure with structured logging (JSONL)
- [ ] LLM extraction of candidate standing rules (*when X, do Y*)
- [ ] Historical replay testing (past failures + past successes)
- [ ] Promotion gate with pass/fail evidence report
- [ ] Standing-rules store in versioned YAML files with provenance
- [ ] Rule injection into context on future matching tasks
- [ ] **One-command demo**: `cauterule demo` — seeded failure history, 10 rules extracted → tested → promoted in <60 seconds
- [ ] **CLI**: `cauterule extract`, `cauterule test`, `cauterule promote`, `cauterule inject`, `cauterule list`

### Nice-to-Have
- [ ] Streaming extraction (watch the LLM extract a rule in real-time)
- [ ] `cauterule show <rule-id>` — full provenance view (source failure → evidence → promotion)

---

## v0.1.1 — Framework Adapters (The "Plug In" Release)

> **Goal:** Make CauterRule work with the frameworks people already use. This is what makes it adoptable, not just interesting.

- [ ] **LangGraph adapter** — trajectory capture as a graph node, rule injection as state prep
- [ ] **CrewAI adapter** — trajectory capture as a crew callback, rule injection as task context
- [ ] **PydanticAI adapter** — trajectory capture as a tool wrapper, rule injection as system prompt
- [ ] **Custom loop adapter** — decorator-based: `@cauterule.watch` on any agent function
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

### Export & Import
- [ ] Export rules as system prompt fragments (markdown, JSON, YAML)
- [ ] Export rules as `.clinerules` / `.cursorrules` format — drop-in for existing tools
- [ ] Import rules from `.cursorrules` / `CLAUDE.md` / `AGENTS.md` — convert existing conventions to tested rules
- [ ] `cauterule export --format cursor` / `--format claude` / `--format markdown`

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
- [ ] `cauterule metrics` — CLI summary: rules promoted, replay precision, repeat-failure rate
- [ ] Per-rule outcome tracking with trend lines
- [ ] "Rules that prevented a failure this week" — weekly digest
- [ ] `cauterule report` — generate a markdown report for stakeholders

### Replay Visualization
- [ ] Replay timeline — step-by-step view of how a rule would have changed a past trajectory
- [ ] "What if?" mode — apply a hypothetical rule to a trajectory and see the simulated outcome
- [ ] Replay diff — before/after comparison of agent behavior with and without a rule

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
| **v0.1.0** | Core Loop | Extract → test → promote in one command |
| **v0.1.1** | Framework Adapters | Plug into LangGraph, CrewAI, PydanticAI |
| **v0.2.0** | Intelligence | Conflict detection, retirement, TUI review |
| **v0.3.0** | Rule Packs | Pre-built, shareable rule collections |
| **v0.4.0** | MCP & Integrations | Rules as MCP tools, GitHub Action, webhooks |
| **v0.5.0** | Observability | Dashboard, metrics, replay visualization |
| **v0.6.0** | Advanced Retrieval | Semantic matching, multi-pass extraction |
| **v0.7.0** | Multi-Agent | Cross-agent transfer, fleet governance |

---

## What Makes This Exciting as OSS

| Hook | Why it gets engagement |
|------|----------------------|
| **"My agent wrote its own rules"** | The demo is visceral — watch a failure become a tested rule in 60 seconds |
| **Rule Packs** | The npm-for-agent-knowledge angle — community can contribute and share |
| **MCP Server** | Any MCP-compatible agent (Claude, etc.) gets rules with zero code changes |
| **`.cursorrules` export** | Drop-in compatibility with tools people already use |
| **Framework adapters** | Works with what you have — LangGraph, CrewAI, PydanticAI |
| **Replay dashboard** | Visual proof the system works — see failures drop over time |
| **GitHub Action** | Rules promoted via PR — fits existing workflows |