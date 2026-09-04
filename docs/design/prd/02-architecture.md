# PRD 02: Architecture

## System Architecture

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
       │                        ▼                         ▼
       │                 ┌──────────────┐          ┌───────────────────┐
       │                 │ Rule Linter  │          │ Promotion Gate    │
       │                 │ + Validate   │          │ (auto/hybrid/human)│
       │                 └──────────────┘          └───────────────────┘
       │                                                   │
       ▼                                                   ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Rule Injection  │ <── │ Standing-Rules   │ <── │ Conflict Detect  │
│ + Explanations  │     │ Store (YAML+git) │     │ + Consolidation  │
│ + Templates     │     │ + Tags + Packs   │     │ + Specificity     │
└─────────────────┘     └──────────────────┘     └───────────────────┘
       │                        │                         │
       ▼                        ▼                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Export / Import │     │ Corpus & Bench   │     │ Observability     │
│ cursorrules     │     │ Tiered + Gold    │     │ Metrics + Report  │
│ CLAUDE.md       │     │ Counterexample   │     │ Health + Coverage │
│ AGENTS.md       │     │ Scale + Adversarial│    │ Learning Journal  │
└─────────────────┘     └──────────────────┘     └───────────────────┘
```

## Components

### 1. Trajectory Capture + Redaction
Structured logging of every failure — steps taken, tool calls, outputs, and point of failure. Output: JSONL files. Secrets, tokens, and sensitive paths are redacted before LLM extraction via configurable patterns and auto-detection.

### 2. Rule Extractor (Multi-Pass)
LLM that reads a trajectory and proposes candidate standing rules in *when X, do Y* form. Multi-pass extraction runs 3x with temperature variation; draft tournaments rank all candidates by replay evidence. Supports dry-run mode and human correction capture ("next time do X" → candidate rule).

### 3. Historical Replay Engine + Visualization
Tests each candidate against prior trajectories. Produces evidence reports with precision, recall, and verdict. Includes Failure Time Machine (step-by-step replay with rule overlay), "what if?" simulation, and replay diff (before/after comparison). Deterministic on same inputs.

### 4. Rule Linter + Validator
Validates candidate and existing rules for vagueness, tautologies, duplicates, contradictions, and untestable directives. `cauterule validate` checks rule store integrity (orphaned refs, missing provenance, broken links).

### 5. Promotion Gate
Evidence threshold layer. Produces pass/fail reports. Three modes: `auto` (promote on pass), `human-review` (require approval), `hybrid` (auto for high-confidence, review for low). Integrates with the rule linter — unsafe directives are blocked before promotion.

### 6. Standing-Rules Store
Versioned, provenance-tracked repository of promoted rules (YAML in git). Each rule has source failure, replay evidence, promotion date, tags, taxonomy, and status. Supports rule packs, archiving, rollback, and consolidation.

### 7. Rule Injection + Explanations
On future tasks, matching standing rules are injected into context before execution. Structured matching by trigger pattern, tool name, error type, context clauses, and tags. Specificity ordering. LLM-generated explanations of why a rule fires. Rule templating for common patterns.

### 8. Conflict Detection + Consolidation
Pairwise comparison of triggers. Flags direct contradictions and specificity overlaps. Specificity scoring for precedence ordering. Consolidation merges overlapping triggers and deduplicates.

### 9. Export / Import
Export rules to `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `aider.conf.yml`, markdown, JSON. Import from `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, and chat history (parse corrections given to agents).

### 10. MCP Server
Exposes rules as MCP tools: `get_matching_rules`, `get_rule`, `list_rules`, `report_failure`. Any MCP-compatible agent (Claude, etc.) consumes rules without code changes. Stdio + HTTP transport.

### 11. Corpus & Benchmarks
Tiered corpus (tiny/small/medium/large), domain-specific corpora, gold rule families, counterexample/near-miss/staleness/redaction corpora. Public synthetic corpus + private local corpus mode. Model bake-off and prompt bake-off harnesses.

### 12. Observability
Metrics CLI, reports, learning journal, failure pattern leaderboard, coverage gap detector, rule coverage score, counterfactual report, health report. Per-rule hit tracking and outcome tracking.

### 13. CLI / TUI / MCP
Full CLI surface (25+ commands), TUI rule browser (`cauterule review`) with evidence cards and batch review, MCP server launcher (`cauterule mcp`).

## Data Flow

1. Agent fails → Trajectory Capture + Redaction writes JSONL
2. Failure clustering groups similar failures → one extraction per cluster
3. Rule Extractor (multi-pass) reads trajectory → produces N candidates
4. Draft Tournament: all candidates replay-tested, ranked by evidence
5. Best candidate → Rule Linter validates quality and safety
6. Linter-passed candidate → Promotion Gate → pass/fail decision
7. Pass → Conflict Detection checks against existing rules
8. No conflicts → Standing-Rules Store (YAML, git commit)
9. Conflicts → flagged for human review or auto-resolved by specificity
10. Future task → Rule Injection → matching rules + explanations in context
11. (Background) Rule hits tracked → metrics, coverage, learning journal