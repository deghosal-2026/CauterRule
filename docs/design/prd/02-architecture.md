# PRD 02: Architecture

## System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Trajectory      │ ──> │ Rule Extractor   │ ──> │ Historical Replay │
│ Capture         │     │ (LLM)            │     │ Engine            │
└─────────────────┘     └──────────────────┘     └───────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Rule Injection  │ <── │ Standing-Rules   │ <── │ Promotion Gate    │
│ (context prep)  │     │ Store (versioned)│     │ (evidence check)  │
└─────────────────┘     └──────────────────┘     └───────────────────┘
```

## Components

### 1. Trajectory Capture
Structured logging of every failure — steps taken, tool calls, outputs, and point of failure. Output: JSONL files.

### 2. Rule Extractor
LLM that reads a trajectory and proposes a candidate standing rule in *when X, do Y* form. Includes the specific failure it addresses and the reasoning.

### 3. Historical Replay Engine
Tests each candidate against prior trajectories. Answers: "Would this rule have helped on past failures? Would it have broken past successes?"

### 4. Promotion Gate
Evidence threshold layer. Produces a pass/fail report. Can operate in auto-promote or human-review mode.

### 5. Standing-Rules Store
Versioned, provenance-tracked repository of promoted rules (YAML in git). Each rule has source failure, replay evidence, promotion date, and status.

### 6. Rule Injection
On future tasks, matching standing rules are injected into context before execution. The agent starts with accumulated wisdom.

## Data Flow

1. Agent fails → Trajectory Capture writes JSONL
2. Trigger fires → Rule Extractor reads trajectory → produces candidate rule
3. Candidate → Historical Replay Engine → produces evidence report
4. Evidence → Promotion Gate → pass/fail decision
5. Pass → Standing-Rules Store (YAML, git commit)
6. Future task → Rule Injection → matching rules in context