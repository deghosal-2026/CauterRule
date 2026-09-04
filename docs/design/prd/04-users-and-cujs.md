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

### CUJ 1: Install and See Value in 5 Minutes

1. User installs `cauterule`
2. User runs `cauterule demo`
3. The demo replays seeded failures, extracts candidate rules, replay-tests them, and promotes the winners
4. User sees the promoted rules fire on the next simulated run
5. User leaves with a concrete "this works" moment in under five minutes

### CUJ 2: Add CauterRule to an Existing Agent

1. User adds `@cauterule.watch` to an existing Python agent function
2. User runs a normal task with no framework migration
3. A failure is captured automatically as a structured trajectory
4. CauterRule extracts, tests, and proposes a standing rule
5. User can adopt learning without rewriting the agent architecture

### CUJ 3: Extract a Rule from Failure

1. Agent fails on a task
2. User inspects the extracted candidate rule
3. User sees the trajectory, failure class, and rule reasoning
4. User decides to replay-test, revise, or discard the candidate

### CUJ 4: Human Correction Becomes Permanent Knowledge

1. Agent fails and the user gives a direct correction: "next time, do X"
2. CauterRule converts that correction into a candidate rule in *when X, do Y* form
3. The candidate is replay-tested against historical failures and successes
4. If it survives, the rule is promoted into the permanent store
5. The next session starts with that lesson available instead of losing it in chat

### CUJ 5: Review Promotion Evidence

1. Candidate rule has been replay-tested
2. User sees the evidence report: which failures it would have prevented, which successes it would have broken, and the final verdict
3. User promotes or rejects with annotation
4. User can compare multiple candidate rules if the draft tournament produced several options

### CUJ 6: Debug a Historical Failure with the Time Machine

1. User runs `cauterule rewind <trajectory>` on a past failed run
2. The original trajectory is replayed step by step
3. User overlays a candidate or promoted rule onto the same run
4. The system shows exactly where the outcome would have changed
5. User gains confidence that the rule fixes a real problem instead of sounding plausible

### CUJ 7: See Rules in Action on a New Task

1. Agent starts a new task
2. Matching standing rules are injected into context
3. User sees which rules matched and why
4. Agent avoids a previous failure pattern
5. User sees the rule provenance and hit count update after the run

### CUJ 8: Find Coverage Gaps in Agent Knowledge

1. User runs `cauterule health`, `cauterule metrics`, or the coverage report
2. User sees repeated failure classes with weak or missing rule coverage
3. User identifies domains like `docker/network` or `git/push` that need more rules
4. User uses that gap analysis to prioritize future learning work

### CUJ 9: Export Learned Rules Back into Existing Tooling

1. User exports promoted rules to `CLAUDE.md`, `.cursorrules`, `AGENTS.md`, or another supported format
2. Existing agent tools immediately benefit from learned rules with no workflow migration
3. User keeps familiar tooling while gaining replay-tested behavioral knowledge

### CUJ 10: Measure Whether the Agent Is Actually Improving

1. User runs `cauterule counterfactual` or `cauterule report`
2. The system estimates how many past failures would have been avoided by the current rule set
3. User sees repeat-failure rate, top rules, weak coverage areas, and rule effectiveness trends
4. User shares the report with teammates or stakeholders as evidence of improvement

### CUJ 11: Manage and Trust the Rule Store

1. User browses all promoted rules
2. User sees provenance, tags, hit rate, outcome history, and conflict status per rule
3. User retires, supersedes, or consolidates stale rules
4. User validates the rule store before production use
