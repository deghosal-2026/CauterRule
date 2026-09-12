# PRD 02: Architecture

## System Architecture

```
                         ┌──────────────────────────────────────────┐
                         │              CLI / TUI / MCP              │
                         │  cauterule demo | review | rewind | mcp  │
                         │  corpus | bench | observe | release      │
                         └──────┬───────────────────────────┬───────┘
                                │                           │
                                ▼                           ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Trajectory      │ ──> │ Rule Extractor   │ ──> │ Historical Replay │
│ Capture + Redact│     │ (multi-pass LLM) │     │ Engine + Viz      │
│ + Adapters      │     │ + Safety Judgment│     │ + Domain Scope    │
└─────────────────┘     └──────────────────┘     └───────────────────┘
       │                        │                         │
       │                        ▼                         ▼
       │                 ┌──────────────┐          ┌───────────────────┐
       │                 │ Rule Linter  │          │ Promotion Gate    │
       │                 │ + Validate   │          │ (auto/hybrid/human)│
       │                 └──────────────┘          │ safety-first      │
       │                                           └───────────────────┘
       │                                                   │
       ▼                                                   ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Rule Injection  │ <── │ Standing-Rules   │ <── │ Conflict Detect  │
│ + Explanations  │     │ Store (YAML+git) │     │ + Consolidation  │
│ + Templates     │     │ + Lifecycle      │     │ + Specificity     │
│ + Adapters      │     │ + Pack Ecosystem │     │ + Overlap fraction│
└─────────────────┘     └──────────────────┘     └───────────────────┘
       │                        │                         │
       ▼                        ▼                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Export / Import │     │ Corpus & Bench   │     │ Observability     │
│ cursorrules     │     │ CLI + Leaderboard│     │ Metrics + Report  │
│ CLAUDE.md       │     │ Tiered + Gold    │     │ Health + Coverage │
│ AGENTS.md       │     │ Adversarial/Scale│     │ Learning Journal  │
└─────────────────┘     └──────────────────┘     └───────────────────┘
```

## Components

### 1. Trajectory Capture + Redaction
Structured logging of every failure — steps taken, tool calls, outputs, and point of failure. Output: JSONL files. Secrets, tokens, and sensitive paths are redacted before LLM extraction via configurable patterns and auto-detection.

### 2. Rule Extractor (Multi-Pass)
LLM that reads a trajectory and proposes candidate standing rules in *when X, do Y* form. Multi-pass extraction runs 3x with temperature variation; draft tournaments rank all candidates by replay evidence. Supports dry-run mode and human correction capture ("next time do X" → candidate rule). v0.3.0 narrowed the extraction prompt to name concrete error codes, removed the broad matching aliases (#492), added model-level safety judgment, and stopped discarding the quality-gate result.

### 3. Historical Replay Engine + Visualization
Tests each candidate against prior trajectories. Produces evidence reports with precision, recall, and verdict. Includes Failure Time Machine (step-by-step replay with rule overlay), "what if?" simulation, and replay diff (before/after comparison). Deterministic on same inputs. v0.3.0 scopes the reference pool to the source trajectory's domain (#708), excludes the source trajectory from its own reference set, applies a near-miss penalty with a tolerance band (`near_misses <= 2 → pass if precision ≥ 0.5`), lowers the pass threshold 0.8 → 0.5, and adds an optional semantic-matching term (`0.5·token-F1 + 0.3·bigram + 0.2·semantic`).

### 4. Rule Linter + Validator
Validates candidate and existing rules for vagueness, tautologies, duplicates, contradictions, and untestable directives. `cauterule validate` checks rule store integrity (orphaned refs, missing provenance, broken links).

### 5. Promotion Gate
Evidence threshold layer. Produces pass/fail reports. Three modes: `auto` (promote on pass), `human-review` (require approval), `hybrid` (auto for high-confidence, review for low). Integrates with the rule linter — unsafe directives are blocked before promotion. v0.3.0 makes the gate safety-first: a broad-trigger penalty marks candidates that break successes as inconclusive, and an adversarial `should_reject` override (#714) forces candidates extracted from adversarial trajectories to fail regardless of replay score.

### 6. Standing-Rules Store
Versioned, provenance-tracked repository of promoted rules (YAML in git). Each rule has source failure, replay evidence, promotion date, tags, taxonomy, and status. Supports rule packs, archiving, rollback, and consolidation. v0.3.0 adds atomic writes, path-traversal guards, recursive per-file YAML loading, quarantine, and lifecycle state (active / retired / superseded / quarantined).

### 7. Rule Lifecycle
Outcome tracking (prevented / broke / neutral), specificity scoring, supersession chains, automated retirement, quarantine of suspect rules, and auto-promotion threshold tuning driven by historical accuracy.

### 8. Rule Injection + Explanations
On future tasks, matching standing rules are injected into context before execution. Structured matching by trigger pattern, tool name, error type, context clauses, and tags. Specificity ordering. LLM-generated explanations of why a rule fires. Rule templating for common patterns.

### 9. Conflict Detection + Consolidation
Pairwise comparison of triggers. Flags direct contradictions and specificity overlaps. Specificity scoring for precedence ordering. Consolidation merges overlapping triggers and deduplicates. v0.3.0 adds minimum-fraction overlap detection and consolidates overlapping rules via specificity, backed by recursive per-file YAML loading.

### 10. Export / Import
Export rules to `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `aider.conf.yml`, markdown, JSON. Import from `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, and chat history (parse corrections given to agents).

### 11. MCP Server
Exposes rules as MCP tools: `get_matching_rules`, `get_rule`, `list_rules`, `report_failure`. Any MCP-compatible agent (Claude, etc.) consumes rules without code changes. Stdio + HTTP transport. v0.3.0 hardens the server with bearer-token auth over HTTP, rate limiting, and request schema validation (the Docker field test found and fixed an auth-bypass bug, #601).

### 12. Framework Adapters
First-class adapters for LangGraph (capture node + state prep), CrewAI (crew callback + task context), PydanticAI (tool wrapper + system prompt), and the generic `@watch` / `inject` decorators for custom loops. A conformance harness verifies every adapter emits trajectory capture and rule injection in the same shape.

### 13. Pack Ecosystem
Install / create / publish / share rule packs. Packs carry semantic versioning, dependency resolution, and certification checks, plus the official `pack-python`, `pack-testing`, `pack-deploy`, and `pack-docker` collections.

### 14. Corpus & Benchmarks
Tiered corpus (tiny/small/medium/large), domain-specific corpora, gold rule families, counterexample/near-miss/staleness/redaction corpora. Public synthetic corpus + private local corpus mode. Model bake-off and prompt bake-off harnesses. v0.3.0 adds `cauterule corpus` and `cauterule bench` CLIs plus a public benchmark leaderboard.

### 15. Observability
Metrics CLI, `cauterule observe`, reports, learning journal, failure pattern leaderboard, coverage gap detector, rule coverage score, counterfactual report, health report. Per-rule hit tracking and outcome tracking. OTEL exporter for rule hit/promotion/extraction events.

### 16. CLI / TUI / MCP
Full CLI surface (25+ commands), TUI rule browser (`cauterule review`) with evidence cards and batch review, MCP server launcher (`cauterule mcp`), and release automation.

## Data Flow

1. Agent (or framework adapter) fails → Trajectory Capture + Redaction writes JSONL
2. Pre-extraction gate scans for a failure signal; the model-level safety judgment silences clean/adversarial trajectories (no LLM call)
3. Failure clustering groups similar failures → one extraction per cluster
4. Rule Extractor (multi-pass) reads trajectory → produces N candidates
5. Draft Tournament: all candidates replay-tested, ranked by evidence
6. Best candidate → Rule Linter validates quality and safety
7. Linter-passed candidate → Promotion Gate → safety-first pass/fail decision (broad-trigger penalty, adversarial override)
8. Pass → Conflict Detection checks against existing rules
9. No conflicts → Standing-Rules Store (YAML, git commit)
10. Conflicts → flagged for human review or auto-resolved by specificity/consolidation
11. Future task → Rule Injection → matching rules + explanations in context
12. (Background) Rule hits and outcomes tracked → specificity scoring, supersession/retirement/quarantine, metrics, coverage, learning journal