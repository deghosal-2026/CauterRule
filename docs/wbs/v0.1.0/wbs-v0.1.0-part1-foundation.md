# v0.1.0 — WBS Part 1: Foundation & Data Models

**Milestones:** M1-M3

## M1: Project Scaffold

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 1.1 | Initialize project structure | `pyproject.toml`, `src/cauterule/__init__.py` | `pip install -e .` works | ⬜ |
| 1.2 | Set up ruff config | `.ruff.toml` | `ruff check` clean | ⬜ |
| 1.3 | Set up mypy config | `mypy.ini` | `mypy src/` zero errors | ⬜ |
| 1.4 | Configure structured logging | `src/cauterule/log.py` | JSON logging with levels | ⬜ |
| 1.5 | Add CI workflow | `.github/workflows/ci.yaml` | lint + type-check + test on PR | ⬜ |

### M1 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M1 complete`
- [ ] Push to main

## M2: Core Data Models

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 2.1 | Define `StandingRule` dataclass | `src/cauterule/models/rule.py` | Full schema: id, when, do, tags, taxonomy, template, confidence, provenance, status, hit_count, last_match, pack | ⬜ |
| 2.2 | Define `Trajectory` + `Step` dataclasses | `src/cauterule/models/trajectory.py` | Full schema: id, timestamp, task, steps, failure_point, failure_class, success, quality_label, domain, severity, tags, agent_config, environment, redacted | ⬜ |
| 2.3 | Define `CandidateRule` dataclass | `src/cauterule/models/candidate.py` | when, do, confidence, reasoning, extraction_pass, template | ⬜ |
| 2.4 | Define `EvidenceReport` dataclass | `src/cauterule/models/evidence.py` | failures_prevented, successes_broken, near_misses, precision, recall, verdict, replay_trace | ⬜ |
| 2.5 | Define `PromotionDecision` dataclass | `src/cauterule/models/decision.py` | verdict, evidence_summary, approver, linter_warnings, conflicts | ⬜ |
| 2.6 | Define `ConflictReport` dataclass | `src/cauterule/models/conflict.py` | type, rules, trigger, resolution, specificity_scores | ⬜ |

### M2 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M2 complete`
- [ ] Push to main

## M3: Serialization & Config

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 3.1 | YAML serialization for rules | `src/cauterule/serialization/rule_yaml.py` | `StandingRule` ↔ YAML file, round-trip | ⬜ |
| 3.2 | JSONL serialization for trajectories | `src/cauterule/serialization/trajectory_jsonl.py` | `Trajectory` ↔ JSONL, streamable | ⬜ |
| 3.3 | Config dataclass + `cauterule.toml` parser | `src/cauterule/config.py` | LLM provider, model, thresholds, mode, paths, redaction patterns, extraction passes/temperatures | ⬜ |
| 3.4 | Environment variable support | `src/cauterule/config.py` | `CAUTERULE_LLM_PROVIDER`, `CAUTERULE_MODEL`, etc. override config | ⬜ |
| 3.5 | LLM provider abstraction | `src/cauterule/llm/provider.py` | OpenAI, Anthropic, Ollama, LiteLLM — unified interface | ⬜ |
| 3.6 | LLM provider factory | `src/cauterule/llm/factory.py` | `get_llm(config)` returns provider instance | ⬜ |

### M3 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M3 complete`
- [ ] Push to main
