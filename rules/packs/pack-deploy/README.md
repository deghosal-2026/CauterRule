# pack-deploy

> Rules for Kubernetes, rollout/rollback, CI/CD and secret-mount failures.

`cauterule pack install <repo>@<version>` (pulls `pack-docker` automatically)

## Symptoms → rules

| Symptom you see | Rule | Fix in brief |
|---|---|---|
| CrashLoopBackOff | R-DEPLOY-001 | Previous-container logs first |
| ImagePullBackOff | R-DEPLOY-002 | Fix tag + pull secret |
| Traffic hits starting pods | R-DEPLOY-003 | Add readinessProbe |
| Evicted / unschedulable | R-DEPLOY-004 | Set requests + limits |
| Rollout timeout | R-DEPLOY-005 | `rollout undo`, then fix forward |
| Flaky CI step | R-DEPLOY-006 | Retry-with-backoff + quarantine |
| Empty env in pod | R-DEPLOY-007 | Fix secret reference + namespace |
| Restarts on cold start | R-DEPLOY-008 | startupProbe / initialDelaySeconds |
| Empty endpoints | R-DEPLOY-009 | Align selector + targetPort |
| Helm pending-upgrade | R-DEPLOY-010 | `helm rollback` first |

## Rules (10)

| Rule | Trigger | Fixtures |
|---|---|---|
| R-DEPLOY-001 | CrashLoopBackOff | ✅ 2 |
| R-DEPLOY-002 | ImagePullBackOff | ✅ 2 |
| R-DEPLOY-003 | missing readiness probe | ✅ 2 |
| R-DEPLOY-004 | missing resources | ✅ 2 |
| R-DEPLOY-005 | stalled rollout | ✅ 2 |
| R-DEPLOY-006 | flaky CI step | ✅ 2 |
| R-DEPLOY-007 | secret not mounted | ✅ 2 |
| R-DEPLOY-008 | liveness kills slow start | ✅ 2 |
| R-DEPLOY-009 | selector mismatch | ✅ 2 |
| R-DEPLOY-010 | helm pending-upgrade | ✅ 2 |

## Certification

Run `cauterule test --pack pack-deploy` to re-certify.
