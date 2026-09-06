# Time-to-Value (TTV) Measurement — v0.1.0

Date: 2026-09-05
Tool: `scripts/measure_ttv.sh`

## Target Thresholds

| Phase | Measurement | Target | Result |
|-------|-------------|--------|--------|
| Install | `pip install` or binary download duration | <30s | — |
| Demo | Run `cauterule demo` or quickstart | <60s | — |
| First rule | Create, extract, or import first standing rule | <5 min | — |
| First prevented failure | Iterate until a rule fires & prevents a failure | <10 min | — |
| **Total TTV** | Cumulative from install to first prevented failure | **<15 min** | — |

## Measurement Method

Run `bash scripts/measure_ttv.sh` from a clean environment (fresh venv or no prior install).
The script records wall-clock time for each phase and reports pass/fail against the targets above.

## Acceptance Criteria

All five phases must meet their individual targets for the release to qualify.