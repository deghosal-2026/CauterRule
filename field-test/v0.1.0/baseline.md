# CauterRule v0.1.0 Baseline Metrics

Date: 2026-09-05
Status: Pre-field-test

| Metric | Value |
|--------|-------|
| Test suite | tests/: 844 |
| Source files | 198 |
| Rules in store | 0 |
| Milestones shipped | 25/32 |
| Coverage | 87% |

## Notes

- Tests exclude `--co` parsing of `tests/mcp/test_mcp.py` (missing `mcp<2` at baseline time; resolved post-baseline).
- Coverage run used `--cov=src/cauterule --cov-report=term-missing -m "not slow and not docker" --ignore=tests/mcp`.
- Coverage config omits `*/tui/*`, requires >95% (`fail_under=95`). Baseline 87% reflects uncovered CLI subcommands, mcp/server, integrations, and TUI paths.
- Source file count: 198 `.py` files under `src/cauterule/`.
- Rules in store: 0 (rule store initialized but empty at baseline).
- Milestones: 25 of 32 main-line milestones shipped per WBS tracking (M1-M20 exit-gate-complete; M21-M25 infrastructure built; M30.6 Docker field-test sub-milestone complete).