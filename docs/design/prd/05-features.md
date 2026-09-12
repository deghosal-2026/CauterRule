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
- [ ] **Trajectory redaction** — strip API keys, tokens, secrets before LLM extraction (configurable patterns + auto-detect)
- [ ] **LLM extraction** of candidate standing rules (*when X, do Y*) with structured output parsing
- [ ] **Multi-pass extraction** — run extraction 3x with temperature variation, test all candidates, promote the best
- [ ] **Failure clustering** — group similar failures, extract one rule per cluster instead of one per failure
- [ ] **Historical replay testing** — replay candidate against past failures + past successes
- [ ] **Promotion gate** with pass/fail evidence report (precision, recall, verdict)
- [ ] **Standing-rules store** in versioned YAML files with full provenance
- [ ] **Rule injection** into context on future matching tasks (structured matching)
- [ ] **Rule lifecycle** — promote, retire, supersede with git-committed history

### CLI (Full Surface)

- [ ] `cauterule init` — scaffold a new project: `cauterule.toml`, `rules/` dir, `.gitignore`, example agent, first rule
- [ ] `cauterule demo` — seeded failure history, 10 rules extracted → tested → promoted in <60s
- [ ] `cauterule extract <trajectory>` — extract a candidate rule from a trajectory file
- [ ] `cauterule extract --dry-run` — show what would be extracted without making an LLM call (saves cost)
- [ ] `cauterule test <rule>` — replay-test a candidate against history, print evidence report
- [ ] `cauterule test --ci` — CI-friendly output (exit codes, JUnit XML) for pipeline integration
- [ ] `cauterule promote <rule>` — promote a tested rule to the store (git commit)
- [ ] `cauterule inject <task>` — show which rules would fire for a given task
- [ ] `cauterule list` — browse all promoted rules (table: id, trigger, status, hits, tags)
- [ ] `cauterule show <rule-id>` — full provenance view (source failure → evidence → promotion)
- [ ] `cauterule search <query>` — full-text search across all rules (triggers, directives, tags)
- [ ] `cauterule audit <rule-id>` — full provenance trail (git log + replay evidence + hit history)
- [ ] `cauterule diff <rule-id>` — show what changed between two versions of a rule (git diff wrapper)
- [ ] `cauterule review` — TUI rule browser (browse, approve, reject candidates with evidence cards)
- [ ] `cauterule retire <rule-id>` — retire a rule with reason (git commit)
- [ ] `cauterule history` — git-log-style timeline of all promotions and retirements
- [ ] `cauterule conflicts` — detect and list rule conflicts (direct contradictions + specificity overlaps)
- [ ] `cauterule health` — rule store health report (coverage, stale rules, conflicts, avg effectiveness)
- [ ] `cauterule validate` — check rule store integrity (no orphaned refs, missing provenance, broken links)
- [ ] `cauterule counterfactual` — "if you had these rules N days ago, you'd have avoided X failures"
- [ ] `cauterule story` — generate a narrative blog post of your agent's learning journey (shareable)
- [ ] `cauterule explain <rule-id>` — LLM generates a human-readable explanation of why a rule fires and when
- [ ] `cauterule config` — view/edit configuration (LLM provider, thresholds, mode)
- [ ] `cauterule pack list` — list installed rule packs
- [ ] `cauterule pack info <name>` — show pack contents and metadata

### Replay Engine

- [ ] **Replay harness** — load historical trajectories, simulate rule application, score outcome
- [ ] **Evidence report** — failures prevented, successes broken, precision, recall, verdict
- [ ] **Replay visualization** — step-by-step view of how a rule would have changed a past trajectory
- [ ] **Failure Time Machine** — `cauterule rewind <trajectory>` replays a failed run step by step, then overlays what changes if a selected rule existed
- [ ] **"What if?" mode** — apply a hypothetical rule to a trajectory and see the simulated outcome
- [ ] **Replay diff** — before/after comparison of agent behavior with and without a rule
- [ ] **Insufficient history detection** — warn when replay count is below threshold
- [ ] **Rule Draft Tournament** — generate 3-5 candidate rules for one failure, replay all of them, rank them, and show why the winner won

### Rule Store

- [ ] **YAML rule files** — one rule per file, with provenance metadata and tags
- [ ] **Rule tagging** — `tags: [git, docker, deploy]` field for organization and filtering
- [ ] **Auto-classified failure taxonomy** — every trajectory labeled like `git/push`, `python/import`, `docker/network`, and rules inherit taxonomy tags
- [ ] **Index file** — `rules/index.yaml` with all rules, statuses, summaries, tags
- [ ] **Git-based versioning** — every promotion/retirement is a git commit with conventional message
- [ ] **Rollback** — `git revert` any promotion; rule store stays consistent
- [ ] **Archive directory** — retired/superseded rules moved to `rules/archived/`
- [ ] **Conflict detection** — pairwise comparison of triggers, flag direct contradictions and specificity overlaps
- [ ] **Rule consolidation** — detect and merge overlapping triggers, deduplicate similar rules
- [ ] **Rule linter** — validate rules for vagueness, tautologies, duplicates, contradictions, and untestable directives

### Rule Injection

- [ ] **Structured matching** — match by trigger pattern, tool name, error type, context clauses, tags
- [ ] **Specificity ordering** — more specific rules injected first
- [ ] **Injection format** — clean markdown block injected into agent context
- [ ] **Injection preview** — `cauterule inject <task>` shows what would be injected without running
- [ ] **No-match graceful degradation** — if no rules match, agent runs without standing-rule context
- [ ] **Rule explanations** — LLM generates a human-readable explanation of why a rule fired and when it applies
- [ ] **Rule templating** — common rule patterns (retry, verify-then-act, check-preconditions) as reusable templates

### Rule Packs (Bundled)

- [ ] **Rule pack format** — bundle of rules with metadata (name, version, description, author)
- [ ] **Bundled `pack-git`** — 10-15 pre-built git rules shipped with `pip install cauterule` (push, merge, rebase, conflicts, hooks)
- [ ] `cauterule pack list` — list installed packs
- [ ] `cauterule pack info <name>` — show pack contents
- [ ] Rules work out of the box — zero cold start, zero LLM cost for bundled rules

### Export & Import (Day-One Interop)

- [ ] **Export to `.cursorrules`** — `cauterule export --format cursor` — drop-in for Cursor
- [ ] **Export to `CLAUDE.md`** — `cauterule export --format claude` — drop-in for Claude Code
- [ ] **Export to `AGENTS.md`** — `cauterule export --format agents` — drop-in for any agent
- [ ] **Export to `.windsurfrules`** — `cauterule export --format windsurf` — drop-in for Windsurf
- [ ] **Export to `aider.conf.yml`** — `cauterule export --format aider` — drop-in for Aider
- [ ] **Export to markdown** — `cauterule export --format markdown` — human-readable rule doc
- [ ] **Export to JSON** — `cauterule export --format json` — machine-readable
- [ ] **Import from `.cursorrules` / `CLAUDE.md` / `AGENTS.md`** — convert existing conventions to testable rules
- [ ] **Import from chat history** — parse past chat corrections given to agents, convert to candidate rules

### MCP Server

- [ ] **CauterRule MCP server** — expose rules as MCP tools:
  - `get_matching_rules(task)` — returns rules matching a task
  - `get_rule(id)` — returns a single rule with full provenance
  - `list_rules(filter)` — browse the rule store
  - `report_failure(trajectory)` — trigger extraction from an MCP client
- [ ] Any MCP-compatible agent (Claude, etc.) can consume rules without code changes
- [ ] MCP transport: stdio (local) + HTTP (remote)
- [ ] `cauterule mcp` — launch the MCP server

### Integrations

- [ ] **GitHub Action** — `cauterule/action` — run extraction on CI failures, promote rules via PR
- [ ] **Webhook on promotion** — notify Slack/Discord/GitHub when a rule is promoted (configurable URL)
- [ ] **OpenTelemetry** — emit rule hit/promotion/extraction events to any OTel-compatible platform
- [ ] **GitHub badge** — "CauterRule: 42 rules learned" — embeddable in your repo README (shields.io-style)

### Distribution

- [ ] **PyPI** — `pip install cauterule`
- [ ] **Homebrew formula** — `brew install cauterule` (massive adoption boost on macOS)
- [ ] **Docker image** — `docker run cauterule demo` (zero-install trial)
- [ ] **Standalone binary** — `curl install` for non-Python users (via PyInstaller/shiv)

### Custom Agent Adapter

- [ ] **`@cauterule.watch` decorator** — wrap any agent function: auto-captures trajectories on failure
- [ ] **`cauterule.inject()` context manager** — prep context with matching rules before task execution
- [ ] **Adapter docs** — "Add CauterRule to your agent in 5 lines"
- [ ] Works with any Python agent — no framework lock-in for v0.1.0

### TUI Review

- [ ] **`cauterule review`** — rich terminal UI (textual/rich) for browsing, approving, rejecting candidates
- [ ] **Evidence summary cards** — "This rule would have prevented 3 failures, broken 0 successes"
- [ ] **Rule confidence cards** — compact cards with confidence, failures prevented, successes broken, last hit, tags
- [ ] **Human annotation capture** — tag, comment, categorize failures before extraction
- [ ] **Batch review mode** — review 10 candidates in one session
- [ ] **Filter by tag, status, confidence** — narrow the review queue

### Observability (Lite)

- [ ] `cauterule metrics` — CLI summary: rules promoted, replay precision, repeat-failure rate, rule store size
- [ ] `cauterule report` — generate a markdown report (rules, evidence, metrics) for sharing
- [ ] Per-rule hit counter — how many times each rule has matched
- [ ] Last-match timestamp per rule
- [ ] **Failure pattern leaderboard** — most common failure classes, most prevented failures, top missing coverage areas
- [ ] **Coverage gap detector** — identify domains with repeated failures but no matching rules yet
- [ ] **Rule coverage score** — single score summarizing failure coverage %, replay safety %, and stale-rule %
- [ ] **Learning journal** — auto-generate a markdown log of each failure, extracted rule, replay result, and promotion outcome

### Sample & Demo

- [ ] **Seeded failure history** — 10+ pre-built trajectories (git failures, docker failures, deploy failures)
- [ ] **Scenario library** — curated scenarios for git, Python, shell, Docker, CI, and env-var failures so users can test immediately
- [ ] **`cauterule demo`** — runs the full loop on seeded data, prints a narrated walkthrough
- [ ] **Example agent** — a toy agent in `examples/` that fails, learns, and succeeds on the second try
- [ ] **Rule store example** — `examples/rules/` showing 10 promoted rules with full provenance
- [ ] **Bundled `pack-git` demo** — show rules working out of the box with zero setup
- [ ] **Human correction capture demo** — user types "next time do X," system turns it into a candidate rule, replay-tests it, and promotes it if valid

### Field Test Program

- [ ] **Single-agent coding field test** — run CauterRule against a coding agent on real repo tasks and measure repeat-failure reduction over one week
- [ ] **Long-horizon task field test** — evaluate tasks with 20-50 steps to confirm rules still help when failures occur late in trajectories
- [ ] **Noisy trajectory field test** — inject retries, irrelevant tool calls, and distractions to verify the extractor still finds the right lesson
- [ ] **Human-in-the-loop field test** — compare auto-promotion vs review-gated promotion for precision, trust, and operator load
- [ ] **Cold-start field test** — start from zero learned rules and measure time to first useful rule and first prevented repeat failure
- [ ] **Cross-session memory field test** — fail in one session and verify the promoted rule still fires correctly in a fresh session later
- [ ] **Regression field test** — previously promoted rules must still pass after extractor prompt or model changes
- [ ] **Multi-environment field test** — run the same scenarios on macOS, Linux, and CI containers to expose environment-specific lessons

### Corpus & Benchmarks

- [ ] **Tiered corpus** — `tiny` (25), `small` (100), `medium` (1k), and `large` (10k+) trajectory sets for local dev, CI, and scale testing
- [ ] **Domain-specific corpora** — coding, DevOps, research, support, and browser-automation trajectory families
- [ ] **Balanced success/failure corpus** — maintain both failure and success trajectories so replay measures regressions, not just fixes
- [ ] **Trajectory metadata schema** — each trajectory labeled with task type, toolchain, failure class, severity, domain, and tags
- [ ] **Trajectory quality labels** — clear failure, ambiguous failure, multi-causal failure, misleading failure, operator-induced failure
- [ ] **Public synthetic corpus** — shareable open corpus with no secrets for reproducible benchmarking
- [ ] **Private local corpus mode** — let users point CauterRule at their own local traces without uploading data anywhere
- [ ] **Gold rule families** — benchmark accepts multiple valid abstractions, not a single exact phrasing
- [ ] **Counterexample corpus** — trajectories where plausible-looking rules should be rejected
- [ ] **Near-miss corpus** — scenarios that look similar but should not trigger the rule
- [ ] **Staleness corpus** — historical failures that no longer matter, used to validate retirement behavior
- [ ] **Redaction corpus** — trajectories containing secrets, tokens, internal URLs, and private paths to validate sanitization

### Scale & Reliability Tests

- [ ] **Replay throughput benchmarks** — measure candidates processed per minute with and without caching across corpus sizes
- [ ] **Rule matching latency benchmarks** — track p50, p95, and p99 pre-task injection latency
- [ ] **Conflict explosion benchmarks** — test naive pairwise conflict detection at 100, 1k, and 10k rules
- [ ] **Storage churn benchmarks** — simulate frequent promotion and retirement to validate YAML + git as a long-lived backend
- [ ] **Concurrent failure ingestion** — process multiple failures at once and verify queueing, deduplication, and promotion consistency
- [ ] **LLM cost benchmarks** — cost per extracted rule, cost per promoted rule, and cost per prevented repeat failure
- [ ] **Memory footprint benchmarks** — RAM usage for replay, matching, and indexing under growing corpora
- [ ] **Incremental indexing benchmarks** — time to add one new rule into a large rule store without full reindexing
- [ ] **Replay determinism tests** — same candidate and same corpus should produce identical evidence reports
- [ ] **Extractor stability tests** — repeated extraction on the same trajectory should show bounded variance

### Safety & Adversarial Testing

- [ ] **Prompt injection corpus** — malicious trajectory content tries to manipulate extractor output
- [ ] **Misleading root-cause corpus** — visible failure differs from actual root cause; extractor must avoid shallow lessons
- [ ] **Contradiction stress tests** — intentionally generate conflicting rules and verify precedence + conflict handling
- [ ] **Unsafe directive corpus** — candidate rules suggesting dangerous actions must be blocked by linter or promotion gate
- [ ] **Data poisoning simulation** — corrupted or fabricated trajectories attempt to poison rule promotion
- [ ] **Instruction leakage tests** — exports must not leak secret paths, tokens, or private notes

### Advanced Evaluation

- [ ] **Model bake-off harness** — compare GPT, Claude, local models, and LiteLLM providers on the same corpus
- [ ] **Prompt bake-off harness** — compare extractor prompt variants by replay pass rate, not just readability
- [ ] **Rule mutation testing** — slightly perturb a good rule and verify replay catches degraded variants
- [ ] **Ablation studies** — no clustering vs clustering, single-pass vs multi-pass, tags vs no tags, etc.
- [ ] **Confidence calibration** — verify extractor confidence scores correlate with real replay outcomes
- [ ] **Human vs LLM lesson comparison** — compare manually written standing rules to extracted rules on the same failures

### Coverage & Optimization

- [ ] **Domain coverage score** — how well current rules cover failure classes across domains
- [ ] **Failure-class coverage score** — percent of recurring failure classes with at least one validated rule
- [ ] **Coverage frontier** — identify the next most valuable domain or failure family to learn based on recurrence and missing coverage
- [ ] **Lesson portfolio optimizer** — if only N rules can be injected, choose the set that maximizes expected failure prevention
- [ ] **Context budget optimizer** — prioritize and compress injected rules to fit token limits without losing critical protection

### Community & Ecosystem

- [ ] **Corpus contribution guide** — contributors can submit anonymized or synthetic trajectories in a standard format
- [ ] **Official benchmark leaderboard** — publish model and prompt results on the public corpus
- [ ] **Pack certification baseline** — define minimum safety, replay, and provenance checks for official rule packs
- [ ] **Monthly learning report** — auto-generate a report of rules learned, failures reduced, and coverage gaps found
- [ ] **Public demo corpus** — reproducible demo data set with screenshots, recordings, and expected outputs

### Configuration

- [ ] **`cauterule.toml`** config file — LLM provider, model, thresholds, mode, paths, redaction patterns
- [ ] **Environment variable support** — `CAUTERULE_LLM_PROVIDER`, `CAUTERULE_MODEL`, etc.
- [ ] **LLM provider abstraction** — OpenAI, Anthropic, local (Ollama), any LiteLLM-compatible
- [ ] **Promotion mode** — `auto` (promote on pass), `human-review` (require approval), `hybrid` (auto for high-confidence, review for low)
- [ ] **Replay thresholds** — `conservative`, `balanced` (default), `aggressive`
- [ ] **Extraction config** — passes (default 3), temperature variation, confidence threshold

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

## v0.2.0 — Rule Lifecycle Management (The "Grows Up" Release)

> **Goal:** Deepen rule lifecycle management with outcome tracking, specificity scoring, and automated retirement. The rule store becomes a self-maintaining asset.

- [ ] **Specificity scoring** — automatic scoring of rule specificity (context count, trigger precision, error subtype)
- [ ] **Per-rule outcome tracking** — hit rate, would-have-failed-without-it rate, effectiveness score
- [ ] **Automated retirement** — auto-flag stale rules (no hits in N days), underperforming rules (hit but still failed)
- [ ] **Supersession chains** — R-012 supersedes R-005, with full history and automatic context migration
- [ ] **Rule auto-promotion tuning** — adjust promotion thresholds based on historical accuracy data

---

## v0.3.0 — Hardening & Ecosystem (The "Trustworthy" Release)

> **Goal:** Make CauterRule trustworthy at the seams — no silent data corruption, no phantom gates — and grow it into an ecosystem: adapters for real frameworks, a full rule lifecycle, installable packs, and corpus/benchmark infrastructure. **Shipped 2026-09-12.**

### Framework Adapters

- [ ] **LangGraph adapter** — trajectory capture as a graph node, rule injection as state prep
- [ ] **CrewAI adapter** — trajectory capture as a crew callback, rule injection as task context
- [ ] **PydanticAI adapter** — trajectory capture as a tool wrapper, rule injection as system prompt
- [ ] **Generic `@watch` / `inject`** — async-capable capture decorator + rule-injection context manager for custom loops
- [ ] **Adapter conformance harness** — verifies every adapter emits capture/injection in the same shape

### Rule Lifecycle & Safety

- [ ] **Per-rule outcome tracking** — prevented / broke / neutral outcomes
- [ ] **Specificity scoring** — context count, trigger precision, error subtype
- [ ] **Supersession chains** — R-012 supersedes R-005 with full history
- [ ] **Automated retirement** — stale and underperforming rules
- [ ] **Quarantine** — isolate suspect rules pending review
- [ ] **Auto-promotion tuning** — thresholds adjust from historical accuracy
- [ ] **Model-level safety judgment** — pre-extraction gate v2 suppresses unsafe/non-failure extractions

### Pack Ecosystem

- [ ] **Official packs** — `pack-python`, `pack-testing`, `pack-deploy`, `pack-docker`
- [ ] `cauterule pack install <name>` — install a rule pack from GitHub
- [ ] `cauterule pack create` — scaffold a new pack from your agent's rule store
- [ ] `cauterule pack publish` — publish a pack as a GitHub release
- [ ] **Pack versioning** — semantic versioning (major/minor/patch)
- [ ] **Pack dependency resolution** — pack A depends on pack B
- [ ] **Pack certification** — baseline safety, replay, and provenance checks
- [ ] `cauterule share <rule-id>` — publish a single rule as a GitHub gist with full provenance

### Reliability & MCP Hardening

- [ ] **Atomic store writes** — no partial YAML on crash
- [ ] **Path-traversal guards** — pack and rule paths stay inside the store
- [ ] **Duplicate / conflict detection** — minimum-fraction overlap, consolidation via specificity
- [ ] **Recursive per-file YAML loading** — nested pack/store directories load reliably
- [ ] **MCP hardening** — bearer auth over HTTP, rate limiting, request schema validation
- [ ] **Extraction changes** — prompt narrowed to name error codes, broad aliases (#492) removed, quality gate no longer discarded

### Corpus & Benchmark Infrastructure

- [ ] `cauterule corpus` — manage tiered and domain corpora
- [ ] `cauterule bench` — benchmark runs plus a public leaderboard
- [ ] `cauterule observe` — runtime observation surface
- [ ] **OpenTelemetry exporter** — rule hit/promotion/extraction events
- [ ] **Release automation** — version bump, packaging, publish

### Field Test v0.3.0

- [ ] 40 corpora × 2 cloud models (gpt-4o-mini, llama-3.1-8b), 4,768 runs
- [ ] Near-miss precision 98–100% (was 86–90%), adversarial promotions 0, 100% safety silence
- [ ] Recall 0.170–0.228 (was 0.087, 2–3×) with a 444-trajectory domain-scoped reference pool
- [ ] Known gaps: golden 40–50%, failures/positive 8–10%, inconclusive ~75%

---

## v0.4.0 — Matcher Quality, Measurement & Integrations (The "Sharp" Release)

> **Goal:** Close the extraction-quality gap left by v0.3.0 (matcher paraphrases) and finish the trust story (measurement + security posture), then land deep integrations.

### Matcher Quality
- [ ] **Paraphrase bridging** — raise the semantic blend weight (0.3–0.4) and bridge trigger/reference phrasings
- [ ] **Adapter / CI reference vocabulary** — fix the `matcher_gap` corpora (adapters, raw/ci)

### Measurement & Security Posture
- [ ] **Cross-session repeat-failure measurement** — run the 5-session protocol (#663/#496)
- [ ] **Human-vs-replay agreement scoring** — fill and score the reviewer sample (#493)
- [ ] **OpenSSF Scorecard remediation** — branch protection, signed releases, dependency pinning (#713)

### Integrations
- [ ] **AgentObservatory integration** — production failure detection triggers extraction
- [ ] **AgentEvalForge integration** — synthetic scenario generation for replay testing
- [ ] **DecisionJournal integration** — decision log feeds historical scenarios
- [ ] **LangSmith / Phoenix** — send rule events to observability platforms
- [ ] **Rule testing in CI pipelines** — `cauterule test --ci` as a GitHub Actions step with PR annotations

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
| **v0.1.0** | Core Loop + First-Class DX | Full loop, CLI (24+ commands), replay + visualization, export/import, MCP server, bundled pack-git, `@cauterule.watch` adapter, TUI review, corpus, benchmarks, scale tests, field tests, adversarial tests, distribution |
| **v0.1.1** | Framework Adapters | LangGraph, CrewAI, PydanticAI adapters |
| **v0.2.0** | Rule Lifecycle Management | Specificity scoring, outcome tracking, automated retirement, supersession chains, auto-promotion tuning |
| **v0.3.0** | Hardening & Ecosystem | Adapters (LangGraph/CrewAI/PydanticAI/`@watch`), rule lifecycle + safety, official packs + install/create/publish/certification, MCP hardening, reliability fixes, corpus/benchmark CLI + leaderboard, OTEL, release automation |
| **v0.4.0** | Matcher Quality, Measurement & Integrations | Paraphrase bridging + semantic weight, cross-session measurement, human agreement, OpenSSF Scorecard, deep integrations |
| **v0.5.0** | Observability & Analytics | Web dashboard, replay visualization, trend lines, weekly digest, failure recurrence tracking |
| **v0.6.0** | Advanced Retrieval | Semantic matching, hybrid matching, rule embedding index, cross-failure pattern detection |
| **v0.7.0** | Multi-Agent | Cross-agent transfer, shared registry, rule governance, agent profiles, rule federation |

---

## What Makes v0.1.0 Exciting as OSS

| Hook | Why it gets engagement |
|------|----------------------|
| **"My agent wrote its own rules"** | The demo is visceral — watch a failure become a tested rule in 60 seconds |
| **`.cursorrules` / `CLAUDE.md` export** | Drop-in compatibility with tools people already use — zero migration friction |
| **Import existing conventions** | Turn your static `CLAUDE.md` into tested, provenance-tracked rules |
| **`@cauterule.watch` decorator** | Add learning to any agent in 5 lines — no framework lock-in |
| **Replay visualization** | See exactly how a rule would have changed a past failure — visual proof it works |
| **Failure Time Machine** | Debug history like a movie and overlay alternate outcomes with specific rules |
| **"What if?" mode** | Apply a hypothetical rule to history before promoting — test before you trust |
| **Rule Draft Tournament** | Shows the system choosing the best lesson, not just the first lesson |
| **Full CLI surface** | 10+ commands on day one — not a toy, a usable tool |
| **`cauterule report`** | Generate a shareable markdown report — show your boss the agent is learning |
| **Coverage gap detector** | Turns rule-building into measurable coverage, like tests for agent behavior |
| **Learning journal** | Produces a living artifact people can read, share, and publish |
