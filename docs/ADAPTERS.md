# CauterRule Adapters & Rule Lifecycle

CauterRule meets agents where they live: a generic decorator for custom
loops and first-class adapters for LangGraph, CrewAI, and PydanticAI — all
passing a shared conformance harness.  This document covers each adapter
(hookup, capture semantics, injection semantics, redaction), the conformance
contract, and the rule-lifecycle policies (specificity, outcomes, retirement,
supersession, auto-promotion tuning).

---

## 1. Adapter overview

| Adapter | Module | Capture | Injection |
|---------|--------|---------|-----------|
| Custom loop (decorator) | `adapter/decorator.py` | per call (sync/async/gen) | `inject()` / `ainject()` |
| LangGraph | `adapter/langgraph.py` | per failed node | `inject_rules(state)` |
| CrewAI | `adapter/crewai.py` | per task (wrapper or callbacks) | `inject_crew_rules(...)` |
| PydanticAI | `adapter/pydanticai.py` | per `Agent.run()` | `inject_system_rules(...)` |

All adapters are **duck-typed**: they import cleanly when the framework is
not installed (`HAS_LANGGRAPH` / `HAS_CREWAI` / `HAS_PYDANTIC_AI` flags) and
work against faithful fakes for tests.

---

## 2. Custom-loop adapter (`@watch`, `inject`/`ainject`)

### Capture — `@watch`

```python
from cauterule.adapter import watch


# sync
@watch(base_dir="trajectories", redact_keys={"api_key", "token"})
def my_agent(prompt: str) -> str: ...


# async
@watch(base_dir="trajectories")
async def my_async_agent(prompt: str) -> str: ...


# generators / async-generators are supported (first-step capture,
# final failure step on error)
```

- On success a `success=True` trajectory is written; on exception a
  `success=False` trajectory is written and the exception is re-raised.
- `redact_keys`: kwarg keys placeholdered to `[REDACTED]` **before** the step
  input is stringified, so secrets never reach disk (the full
  `redact_trajectory` pass still runs after enrichment).

### Injection — `inject` / `ainject`

```python
from cauterule.adapter import inject, ainject
import cauterule as cr

with inject(task, rules=cr.load_rules(), tool="git", error="...") as matched:
    prompt = base + render(matched)

async with ainject(task, rules=cr.load_rules(), max_rules=5) as matched:
    ...
```

Uses the **real** matcher (`injection/matcher.py`, specificity ordering,
budget from `injection/budget.py`) — identical to the CLI path.  Supported
context kwargs: `tool`, `error`, `tags`, `taxonomy`; budget: `max_rules`,
`max_tokens`.

---

## 3. LangGraph adapter

```python
from cauterule.adapter.langgraph import inject_rules, capture_node_error, langgraph_node


# Pre-step injection
def my_node(state: dict) -> dict:
    state = inject_rules(state, task="sync billing records")
    ...


# Decorator with automatic capture + injection
@langgraph_node(task="sync billing records", base_dir="trajectories")
def my_node(state: dict) -> dict: ...
```

- **Capture**: `capture_node_error(node, state_in, state_out, exc)` maps a
  failed node to an input step (redacted state) + error step, enriches,
  redacts, writes.
- **Injection**: `inject_rules` returns a copy of `state` with
  `state["cauterule_rules"]` set to matched rule texts (budget-ordered).

## 4. CrewAI adapter

```python
from cauterule.adapter.crewai import CrewaiTracer, inject_crew_rules

tracer = CrewaiTracer(task_desc="reconcile invoices", base_dir="trajectories")

# Style A — explicit wrapper
with tracer.task("reconcile invoices", agent_role="accountant"):
    crew.kickoff()

# Style B — callback listeners
crew.tasks_handlers = [tracer.on_task_complete, tracer.on_tool_error]

# Injection into a Task description
description = "Reconcile invoices.\n" + inject_crew_rules("reconcile invoices")
```

- **Capture**: one trajectory per task run; tool calls via
  `tracer.record_tool(...)`, failure recorded with the exception.
- **Injection**: `inject_crew_rules` renders a `"Standing rules (learned from
  past failures):\n1. ..."` block to append to `Task(description=...)`.

## 5. PydanticAI adapter

```python
import asyncio
from cauterule.adapter.pydanticai import watch_run, inject_system_rules


# Option A — decorate the driver
@watch_run(task="answer billing question", base_dir="trajectories")
async def run_agent(prompt: str):
    return await agent.run(prompt)


# Option B — explicit system-prompt injection
rules_text = inject_system_rules("answer billing question")
result = await agent.run(prompt, system_prompt=(base_system + rules_text))
```

- **Capture**: one trajectory per `Agent.run()` (not per streamed chunk);
  retries/`ModelRetry` surfaces as repeated steps.  Async-first with a sync
  fallback.
- **Injection**: `inject_system_rules` returns a compact system-prompt block.

---

## 6. Conformance harness (`tests/adapter_conformance/`)

Every adapter must pass the shared kit:

- **no-repeat**: fail twice → 2 trajectories → third run with injection handling
  succeeds.
- **redaction**: a secret (`api_key=sk-secret-...`) in task/tool I/O never
  appears in the written trajectory.
- **success capture**: success path writes a `success=True` trajectory.
- **schema valid**: written trajectories carry `id`, `task`, and steps.

Adding an adapter = add one driver fixture in
`tests/adapter_conformance/conftest.py` (a fake failing agent plus
last_trajectory plumbing) and it is automatically in the parametrized suite.

---

## 7. Scaffolding

```bash
cauterule init --dir my_project --adapter langgraph   # | crewai | pydanticai | custom | none
```

Creates `cauterule.toml`, `rules/` (with a starter `R-001.yaml`), and an
example file per adapter (`agent_<adapter>_example.py`).

---

## 8. Rule lifecycle (M4)

The store is self-maintaining via four policies (all in `cauterule/lifecycle/`):

| Policy | Module | CLI |
|--------|--------|-----|
| Outcome tracking | `observe/outcomes.py` | `cauterule metrics --rule <id>`, `show <id> --outcomes` |
| Specificity scoring | `lifecycle/specificity.py` | `list` spec column, `list --sort spec`, `metrics --lowest-spec` |
| Auto-retirement | `lifecycle/retire.py` | `cauterule audit` (dry-run), `audit --apply --yes` |
| Supersession chains | `lifecycle/supersede.py` | `show <id> --history`, `health` supersession section |
| Auto-promotion tuning | `lifecycle/tune.py` | `promote --show-cutoffs` |

### Outcomes (`#542`)

Each rule persists:

```
prevented_count, broke_count, neutral_count,
last_outcome, last_outcome_at,
outcome_trend: [1, 0, -1, ...]   # capped at 50, +1/-1/0
```

Append-only log at `<rules>/outcomes/<rule-id>.jsonl` keyed by
`(trajectory_id, rule_id)` makes recording idempotent — replay-cache hits do
not double-count.

### Specificity (`#541`)

A 0..1 score combining trigger breadth + outcome precision, stored on the
rule (`specificity` + `specificity_inputs`) and recomputed on each outcome /
promotion / audit.  The reference "broad" threshold is 0.3.

### Retirement (`#543`)

`RetirementPolicy` with `harmful_window`, `harmful_ratio`, `stale_days`,
`stale_specificity`, `min_evidence`.  Dry-run by default; `audit --apply`
retires harmful (broke>prevented) and stale (idle + low-specificity) rules,
writing an audit log to `<rules>/outcomes/retirements.jsonl`.

### Supersession (`#544`)

`chain()`, `heads()`, `dangling()`, `cycles()`, `orphan_middles()` helpers —
cycle-guarded and depth-capped.  `show --history` renders the
`v1 (superseded) → v2 (superseded) → v3 (active)` lineage.  The validator
enforces: `superseded` requires `superseded_by`; `retired` must not carry one.

### Auto-promotion tuning (`#545`)

`learn_cutoffs(rules)` buckets active rules by specificity decile, computes
each bucket's empirical prevented-rate, and sets learned `min_quality` /
`min_specificity` cutoffs with floor/ceiling guardrails, a
`min_evidence` cold-start gate (`source="default"` below it), and a human
`--force` override.  `promote --show-cutoffs` prints learned vs default.