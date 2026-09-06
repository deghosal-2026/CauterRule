# v0.1.0 — WBS Part 11: Demo & Examples

**Milestones:** M29

> **Note:** M28 (Distribution) is merged into M31 (Release Readiness). See `wbs-v0.1.0-part13-release-readiness.md` for distribution tasks.

## M29: Demo & Examples

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 29.1 | Seeded failure history | `examples/trajectories/` | 10+ pre-built trajectories (git, docker, deploy, python, shell, CI, env) | ✅ |
| 29.2 | Scenario library | `examples/scenarios/` | Curated scenarios for git, Python, shell, Docker, CI, env-var failures | ✅ |
| 29.3 | Example agent | `examples/agent.py` | Toy agent that fails, learns, succeeds on second try | ✅ |
| 29.4 | Example rule store | `examples/rules/` | 10 promoted rules with full provenance | ✅ |
| 29.5 | Bundled pack-git demo | `examples/pack-git-demo.py` | Show rules working out of the box with zero setup | ✅ |
| 29.6 | Human correction capture demo | `examples/human-correction.py` | User types "next time do X" → candidate → replay → promote | ✅ |
| 29.7 | Animated demo GIF | `assets/demo.gif` | README demo animation | ➡️ v0.2.0 |
| 29.8 | `cauterule init` templates | `src/cauterule/cli/templates/` | Scaffold templates for new project | ✅ |
| 29.9 | Public demo corpus | `examples/demo-corpus/` | Reproducible demo data set with screenshots, recordings, and expected outputs | ✅ |
| 29.10 | Adapter docs | `docs/adapter-guide.md` | "Add CauterRule to your agent in 5 lines" — adapter spec and examples | ✅ |

### M29 Exit Gate

- [x] Run all tests: `pytest` — all pass
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M29 complete`
- [x] Push to main

> **Note:** M29 is complete. The animated demo GIF (29.7) is deferred to v0.2.0. Distribution tasks (M28) are merged into M31 (Release Readiness).
