# Design Decisions

## DD-01: Standing Rule Format — *when X, do Y*

**Status:** Accepted  
**Context:** Rules must be actionable, falsifiable, and testable. Prose reflection paragraphs are not.  
**Decision:** Encode every rule as a structured `when X, do Y` pair with optional `because Z` provenance. X is a condition (trigger pattern), Y is a directive (behavior change).  
**Consequences:** Rules are machine-parseable, individually testable via replay, and injectable into context on match. Human readability is preserved.

## DD-02: YAML for Rule Store

**Status:** Accepted  
**Context:** Rules need to be human-readable, version-controlled in git, and machine-parseable.  
**Decision:** Store rules as YAML files, one rule per entry, with provenance metadata (source failure, replay evidence, promotion date).  
**Consequences:** Git provides versioning, diff, and rollback for free. YAML is readable by both humans and parsers.

## DD-03: JSONL for Trajectory Capture

**Status:** Accepted  
**Context:** Execution trajectories are structured, append-only logs that need to be analyzable line by line.  
**Decision:** Store trajectories as JSONL files — one JSON object per step (tool call, output, state).  
**Consequences:** Streamable, append-friendly, compatible with most log analysis tools. Each line is independently parseable.

## DD-04: Local-First with Git-Based Versioning

**Status:** Accepted  
**Context:** The system should work offline, without external dependencies, for OSS adoption.  
**Decision:** All data lives in local files (JSONL, YAML). Git is the versioning layer. No database required.  
**Consequences:** Zero infrastructure to start. Collaboration happens through git remotes. No lock-in.

## DD-05: LLM Extraction with Structured Output

**Status:** Accepted  
**Context:** Extracting a general rule from one specific failure requires generalization, which requires an LLM.  
**Decision:** Use an LLM call (local or API) with structured output parsing to produce candidate rules. The prompt includes the trajectory and asks for *when X, do Y* form.  
**Consequences:** Extraction quality depends on LLM capability. Local models may underperform API models. Output is structured enough for automated processing.

## DD-06: Historical Replay as Regression Testing

**Status:** Accepted  
**Context:** A candidate rule must be verified before promotion — it should help on past failures and not break past successes.  
**Decision:** Replay each candidate against all historical trajectories (both failures and successes). A rule passes if it would have prevented ≥1 past failure and broken 0 past successes.  
**Consequences:** Regression-test metaphor is intuitive. False confidence from sparse history is a risk (see Risk 2).

## DD-07: Single-Agent First, Cross-Agent Later

**Status:** Accepted  
**Context:** Cross-agent rule transfer adds significant complexity (different contexts, different tool sets).  
**Decision:** v0.x focuses on a single agent's loop. Cross-agent transfer is deferred to v0.4+.  
**Consequences:** Simpler initial architecture. Later versions will need a rule normalization layer.

## DD-08: Promotion Gate Supports Human Review

**Status:** Accepted  
**Context:** Fully automated promotion is risky for production agents. Human review is valuable for high-stakes rules.  
**Decision:** The promotion gate produces an evidence report. It can operate in auto-promote or human-review mode based on configuration.  
**Consequences:** Flexible adoption. Low-risk environments can fully automate; production environments can require human sign-off.

## DD-09: Structured Matching (Not Semantic Embedding) for Rule Injection

**Status:** Accepted  
**Context:** Rule injection needs to match the current task against standing rules. Semantic embedding is powerful but adds complexity.  
**Decision:** Start with structured matching — match against trigger conditions by keyword, tool name, error type, and pattern. Semantic retrieval is deferred.  
**Consequences:** Simpler initial implementation. May miss some matches that embedding would catch. Upgrade path is clear.