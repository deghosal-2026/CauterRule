# Design Decisions

## DD-01: Standing Rule Format — *when X, do Y*

**Status:** Accepted
**Context:** Rules must be actionable, falsifiable, and testable. Prose reflection paragraphs are not.
**Decision:** Encode every rule as a structured `when X, do Y` pair with optional `because Z` provenance, tags, taxonomy, template, and confidence.
**Consequences:** Rules are machine-parseable, individually testable via replay, and injectable into context on match. Human readability is preserved. Tags and taxonomy enable filtering and coverage analysis. Templates ensure consistency.

## DD-02: YAML for Rule Store

**Status:** Accepted
**Context:** Rules need to be human-readable, version-controlled in git, and machine-parseable.
**Decision:** Store rules as YAML files, one rule per entry, with provenance metadata (source failure, replay evidence, promotion date, extraction pass, draft tournament rank).
**Consequences:** Git provides versioning, diff, and rollback for free. YAML is readable by both humans and parsers. Scale ceiling exists but is mitigated by indexing at 1k+ rules.

## DD-03: JSONL for Trajectory Capture

**Status:** Accepted
**Context:** Execution trajectories are structured, append-only logs that need to be analyzable line by line.
**Decision:** Store trajectories as JSONL files — one JSON object per step (tool call, output, state). Include metadata: failure class, quality label, domain, severity, tags, environment, redaction flag.
**Consequences:** Streamable, append-friendly, compatible with most log analysis tools. Each line is independently parseable. Metadata enables clustering, coverage analysis, and corpus tiering.

## DD-04: Local-First with Git-Based Versioning

**Status:** Accepted
**Context:** The system should work offline, without external dependencies, for OSS adoption.
**Decision:** All data lives in local files (JSONL, YAML). Git is the versioning layer. No database required.
**Consequences:** Zero infrastructure to start. Collaboration happens through git remotes. No lock-in. Scale ceiling mitigated by incremental indexing.

## DD-05: LLM Extraction with Structured Output

**Status:** Accepted
**Context:** Extracting a general rule from one specific failure requires generalization, which requires an LLM.
**Decision:** Use an LLM call (local or API) with structured output parsing to produce candidate rules. The prompt includes the trajectory and asks for *when X, do Y* form. Multi-pass extraction (3x with temperature variation) produces N candidates; draft tournaments rank them by replay evidence.
**Consequences:** Extraction quality depends on LLM capability. Local models may underperform API models. Multi-pass + tournament reduces single-pass bias. Dry-run mode saves cost.

## DD-06: Historical Replay as Regression Testing

**Status:** Accepted
**Context:** A candidate rule must be verified before promotion — it should help on past failures and not break past successes.
**Decision:** Replay each candidate against all historical trajectories (both failures and successes). A rule passes if it would have prevented >=1 past failure and broken 0 past successes. Replay is deterministic on same inputs.
**Consequences:** Regression-test metaphor is intuitive. False confidence from sparse history is a risk (see Risk 2). Counterexample and near-miss corpora stress-test precision.

## DD-07: Single-Agent First, Cross-Agent Later

**Status:** Accepted
**Context:** Cross-agent rule transfer adds significant complexity (different contexts, different tool sets).
**Decision:** v0.1.0 focuses on a single agent's loop. Cross-agent transfer is deferred to v0.7.0.
**Consequences:** Simpler initial architecture. Later versions will need a rule normalization layer.

## DD-08: Promotion Gate Supports Three Modes

**Status:** Accepted
**Context:** Fully automated promotion is risky for production agents. Human review is valuable for high-stakes rules. But requiring human review for everything is too slow.
**Decision:** The promotion gate operates in three modes: `auto` (promote on pass), `human-review` (require approval), `hybrid` (auto for high-confidence, review for low). Linter and conflict detection run before the gate in all modes.
**Consequences:** Flexible adoption. Low-risk environments can fully automate; production environments can require human sign-off. Hybrid mode balances speed and safety.

## DD-09: Structured Matching (Not Semantic Embedding) for v0.1.0

**Status:** Accepted
**Context:** Rule injection needs to match the current task against standing rules. Semantic embedding is powerful but adds complexity.
**Decision:** v0.1.0 uses structured matching — match against trigger conditions by keyword, tool name, error type, pattern, tags, and taxonomy. Semantic retrieval is deferred to v0.6.0.
**Consequences:** Simpler initial implementation. May miss some matches that embedding would catch. Upgrade path is clear.

## DD-10: Trajectory Redaction Before Extraction

**Status:** Accepted
**Context:** Execution traces may contain API keys, tokens, or proprietary logic. Sending these to an LLM API is a security risk.
**Decision:** All trajectories are redacted before LLM extraction. Configurable patterns + auto-detection of common secret formats. `redacted: true` flag on trajectory metadata.
**Consequences:** Secrets never reach the LLM. Redaction corpus validates 100% success rate. No data exfiltration risk for local-first users.

## DD-11: MCP Server in v0.1.0

**Status:** Accepted
**Context:** Exposing rules via MCP makes them consumable by any MCP-compatible agent (Claude, etc.) with zero code changes. This is a major differentiator and adoption hook.
**Decision:** Ship the MCP server in v0.1.0 with 4 tools: `get_matching_rules`, `get_rule`, `list_rules`, `report_failure`. Stdio (local) + HTTP (remote) transport.
**Consequences:** Any MCP-compatible agent gets rules immediately. Increases v0.1.0 scope but the MCP SDK makes this ~200 lines.

## DD-12: Bundled Rule Pack in v0.1.0

**Status:** Accepted
**Context:** Cold start is a problem — users install the tool but have zero rules. Bundled packs provide value on day one.
**Decision:** Ship `pack-git` (10-15 pre-built git rules) with `pip install cauterule`. Pack rules are read-only, have full provenance (bundled, not extracted), and work with zero LLM cost.
**Consequences:** Rules work out of the box. Zero cold start for git operations. Sets the pattern for community packs in v0.3.0.

## DD-13: Export/Import in v0.1.0

**Status:** Accepted
**Context:** Users already have `.cursorrules`, `CLAUDE.md`, `AGENTS.md` files. CauterRule needs to interop with these from day one.
**Decision:** v0.1.0 exports to `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `aider.conf.yml`, markdown, JSON. Imports from `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, and chat history.
**Consequences:** Zero migration friction. Users can try CauterRule and export back to their existing tools. Import converts static conventions into testable rules.

## DD-14: Failure Clustering Before Extraction

**Status:** Accepted
**Context:** Extracting one rule per failure produces many near-identical rules for similar failures.
**Decision:** Cluster failures by failure class, tool sequence similarity, and error message similarity before extraction. One extraction per cluster.
**Consequences:** Fewer, more general rules. Less rule store clutter. Cross-failure pattern detection is a natural extension.

## DD-15: Draft Tournament for Candidate Selection

**Status:** Accepted
**Context:** Single-pass extraction picks the first candidate, which may not be the best.
**Decision:** Multi-pass extraction produces N candidates (typically 3-5). All are replay-tested. The draft tournament ranks them by precision > recall > confidence > specificity. The winner is promoted.
**Consequences:** Better rules. The system feels intelligent, not just automated. If top 2 are within 5%, both are held for human review.

## DD-16: Tiered Corpus as a First-Class Artifact

**Status:** Accepted
**Context:** Without a test corpus, the system cannot be benchmarked or trusted.
**Decision:** Ship a tiered corpus (tiny/small/medium/large) with v0.1.0. Include domain-specific corpora, gold rule families, counterexample, near-miss, staleness, and redaction corpora. Public synthetic corpus + private local corpus mode.
**Consequences:** Reproducible benchmarks. Model bake-off harness. Community can contribute scenarios. The project is measurable, not just "cool idea."

## DD-17: Rule Linter Before Promotion

**Status:** Accepted
**Context:** Rules can be vague, tautological, duplicative, contradictory, or untestable. Promoting bad rules degrades the store.
**Decision:** The rule linter runs before the promotion gate. Vague, tautological, duplicate, contradictory, untestable, and unsafe rules are blocked.
**Consequences:** Rule store quality stays high. Unsafe directives are caught before promotion. Linter precision target: >=80% of findings are genuinely useful.

## DD-18: Context Budget Optimizer

**Status:** Accepted
**Context:** Agents have limited context windows. Injecting too many rules bloats context and may hurt performance.
**Decision:** When a context budget is specified, rules are ranked by specificity, hit count, last match, and confidence. Rules are injected in rank order until the budget is exhausted. Lower-ranked rules are compressed or omitted.
**Consequences:** Injection stays within token limits. Most relevant rules are prioritized. Portfolio optimizer can choose the optimal set of N rules to maximize protection.