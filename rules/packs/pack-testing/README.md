# pack-testing

> Rules for flaky tests, coverage gates, mocks, snapshots and async timeouts.

`cauterule pack install <repo>@<version>`

## Symptoms → rules

| Symptom you see | Rule | Fix in brief |
|---|---|---|
| Pass/fail with no code change | R-TEST-001 | Quarantine + tracking issue |
| Network-dependent flakes | R-TEST-002 | Retry with backoff or replay fixtures |
| Coverage below gate | R-TEST-003 | Write the missing tests |
| Over-mocked seam | R-TEST-004 | Mock your boundary, contract-test |
| Blind snapshot update | R-TEST-005 | Review each diff deliberately |
| `coroutine was never awaited` | R-TEST-006 | Await + explicit timeout |
| Green solo, red in suite | R-TEST-007 | Isolate fixtures, bisect |
| Date/timezone failures | R-TEST-008 | Freeze time, assert UTC |
| Red under `-n auto` | R-TEST-009 | Unique dirs/ports/DBs per worker |
| Growing skip count | R-TEST-010 | Audit skips, expire or fix |

## Rules (10)

| Rule | Trigger | Fixtures |
|---|---|---|
| R-TEST-001 | flaky flip | ✅ 2 |
| R-TEST-002 | network flakes | ✅ 2 |
| R-TEST-003 | coverage gate | ✅ 2 |
| R-TEST-004 | mock boundary | ✅ 2 |
| R-TEST-005 | snapshot update | ✅ 2 |
| R-TEST-006 | async hang | ✅ 2 |
| R-TEST-007 | order dependence | ✅ 2 |
| R-TEST-008 | time dependence | ✅ 2 |
| R-TEST-009 | parallel collision | ✅ 2 |
| R-TEST-010 | skip accumulation | ✅ 2 |

## Certification

Run `cauterule test --pack pack-testing` to re-certify.
