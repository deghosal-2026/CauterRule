# PRD 04: Users and Critical User Journeys

## Primary User

**Agent builders** running production agents who are tired of debugging the same failure twice and want a system that remembers.

## Secondary Users

- Platform teams maintaining a fleet of agents that need shared, transferable knowledge
- LLMOps engineers managing agent reliability and drift over time
- Teams using LangGraph, CrewAI, PydanticAI, or custom Python agent loops

## Not For

- Teams running one-off agents that never see repeat tasks
- Builders who only need a scratch pad for notes, not a tested rule system

## Critical User Journeys

### CUJ 1: Extract from Failure

1. Agent fails on a task
2. User inspects the extracted candidate rule
3. User sees the trajectory → rule reasoning
4. User decides to replay-test or discard

### CUJ 2: Review Promotion Evidence

1. Candidate rule has been replay-tested
2. User sees the evidence report: would help on X failures, would break Y successes
3. User promotes or rejects with annotation

### CUJ 3: See Rules in Action

1. Agent starts a new task
2. Matching standing rules are injected into context
3. Agent avoids a previous failure pattern
4. User sees the rule provenance in the trace

### CUJ 4: Manage Rule Store

1. User browses all promoted rules
2. User sees provenance, hit rate, outcome per rule
3. User retires or consolidates stale rules
4. User resolves detected conflicts