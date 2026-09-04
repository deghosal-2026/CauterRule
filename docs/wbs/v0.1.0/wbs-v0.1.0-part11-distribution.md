# v0.1.0 — WBS Part 11: Distribution, Demo & Release

**Milestones:** M28-M30

## M28: Distribution

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 28.1 | PyPI publish config | `pyproject.toml` | `pip install cauterule` works | ⬜ |
| 28.2 | Homebrew formula | `dist/homebrew/cauterule.rb` | `brew install cauterule` works on macOS | ⬜ |
| 28.3 | Docker image | `Dockerfile`, `docker-compose.yaml` | `docker run cauterule demo` works | ⬜ |
| 28.4 | Standalone binary | `scripts/build_binary.sh` | PyInstaller/shiv bundling | ⬜ |
| 28.5 | GitHub badge endpoint | `src/cauterule/badge.py` | "CauterRule: N rules learned" shields.io-style | ⬜ |
| 28.6 | GitHub Action | `.github/action.yml`, `action/` | `cauterule/action` — extraction on CI failures, promote via PR | ⬜ |
| 28.7 | Webhook on promotion | `src/cauterule/integrations/webhook.py` | Notify Slack/Discord/GitHub (configurable URL) | ⬜ |
| 28.8 | OpenTelemetry exporter | `src/cauterule/integrations/otel.py` | Emit rule hit/promotion/extraction events | ⬜ |
| 28.9 | Official benchmark leaderboard | `src/cauterule/benchmark/leaderboard.py` | Publish model + prompt results on public corpus | ⬜ |
| 28.10 | Pack certification baseline | `src/cauterule/packs/certification.py` | Minimum safety, replay, and provenance checks for official rule packs | ⬜ |

### M28 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M28 complete`
- [ ] Push to main

## M29: Demo & Examples

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 29.1 | Seeded failure history | `examples/trajectories/` | 10+ pre-built trajectories (git, docker, deploy, python, shell, CI, env) | ⬜ |
| 29.2 | Scenario library | `examples/scenarios/` | Curated scenarios for git, Python, shell, Docker, CI, env-var failures | ⬜ |
| 29.3 | Example agent | `examples/agent.py` | Toy agent that fails, learns, succeeds on second try | ⬜ |
| 29.4 | Example rule store | `examples/rules/` | 10 promoted rules with full provenance | ⬜ |
| 29.5 | Bundled pack-git demo | `examples/pack-git-demo.py` | Show rules working out of the box with zero setup | ⬜ |
| 29.6 | Human correction capture demo | `examples/human-correction.py` | User types "next time do X" → candidate → replay → promote | ⬜ |
| 29.7 | Animated demo GIF | `assets/demo.gif` | README demo animation | ⬜ |
| 29.8 | `cauterule init` templates | `src/cauterule/cli/templates/` | Scaffold templates for new project | ⬜ |
| 29.9 | Public demo corpus | `examples/demo-corpus/` | Reproducible demo data set with screenshots, recordings, and expected outputs | ⬜ |
| 29.10 | Adapter docs | `docs/adapter-guide.md` | "Add CauterRule to your agent in 5 lines" — adapter spec and examples | ⬜ |

### M29 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M29 complete`
- [ ] Push to main

## M30: Release

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 30.1 | CONTRIBUTING.md | `CONTRIBUTING.md` | How to contribute, adapter spec, rule pack format, corpus guide | ⬜ |
| 30.2 | CHANGELOG.md | `CHANGELOG.md` | Conventional commits, Keep a Changelog format | ⬜ |
| 30.3 | SECURITY.md | `SECURITY.md` | Security policy, threat model summary, adversarial coverage | ⬜ |
| 30.4 | README.md | `README.md` | Updated with full v0.1.0 feature list, quick start, architecture | ⬜ |
| 30.5 | Release notes | `docs/release/v0.1.0/release-notes.md` | What's new, field test results, known issues, upgrade guide | ⬜ |
| 30.6 | Release gate check | `scripts/release_check.sh` | Verify all release gates pass (demo, precision, counterexample, redaction, validate, install) | ⬜ |

### M30 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M30 complete`
- [ ] Push to main
