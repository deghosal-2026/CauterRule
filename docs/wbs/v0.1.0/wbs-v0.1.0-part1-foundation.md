# v0.1.0 — WBS Part 1: Foundation

**Milestones:** M1-M2  
**Issues:** 8

## M1: Project Scaffold

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 1.1 | Initialize project structure | `pyproject.toml`, `src/cauterule/` | Project installable via pip | ⬜ |
| 1.2 | Set up linting and typing | `.ruff.toml`, `mypy.ini` | CI passes ruff + mypy | ⬜ |
| 1.3 | Configure logging | `src/cauterule/log.py` | Structured JSON logging | ⬜ |
| 1.4 | Add CI workflow | `.github/workflows/ci.yaml` | Tests run on PR | ⬜ |

## M2: Standing Rule Data Model

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 2.1 | Define StandingRule dataclass | `src/cauterule/models/rule.py` | *when X, do Y* structure | ⬜ |
| 2.2 | Define Trajectory dataclass | `src/cauterule/models/trajectory.py` | Step-by-step execution trace | ⬜ |
| 2.3 | Define EvidenceReport dataclass | `src/cauterule/models/evidence.py` | Replay verdict + counts | ⬜ |
| 2.4 | Add YAML serialization | `src/cauterule/serialization.py` | Rules ↔ YAML, Trajectories ↔ JSONL | ⬜ |