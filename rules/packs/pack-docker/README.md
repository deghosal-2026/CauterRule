# pack-docker

> Rules for Docker build, compose, network, volume and registry failures.

`cauterule pack install <repo>@<version>`

## Symptoms → rules

| Symptom you see | Rule | Fix in brief |
|---|---|---|
| Rebuild reinstalls deps on each edit | R-DOCKER-001 | Copy requirements first, install, then copy source |
| Huge context upload, slow builds | R-DOCKER-002 | Add `.dockerignore` |
| App crashes before DB is ready | R-DOCKER-003 | Healthcheck + `service_healthy` |
| `port is already allocated` | R-DOCKER-004 | Remap ports or stop the squatter |
| `EACCES` writing to volume | R-DOCKER-005 | Align container user / chown |
| Exit 137 OOMKilled | R-DOCKER-006 | Raise memory limit, profile leaks |
| `unauthorized: authentication required` | R-DOCKER-007 | `docker login`, rotate token |
| CI runs stale image | R-DOCKER-008 | Pin versions, pull before up |
| Binary missing at runtime | R-DOCKER-009 | Fix `COPY --from` stage names |
| Image ballooned after apt install | R-DOCKER-010 | Single-layer install + cleanup |

## Rules (10)

| Rule | Trigger | Fixtures |
|---|---|---|
| R-DOCKER-001 | layer-cache bust | ✅ 2 |
| R-DOCKER-002 | build context too large | ✅ 2 |
| R-DOCKER-003 | depends_on without healthcheck | ✅ 2 |
| R-DOCKER-004 | host port conflict | ✅ 2 |
| R-DOCKER-005 | volume permission denied | ✅ 2 |
| R-DOCKER-006 | OOMKilled exit 137 | ✅ 2 |
| R-DOCKER-007 | registry auth failure | ✅ 2 |
| R-DOCKER-008 | stale latest tag | ✅ 2 |
| R-DOCKER-009 | multi-stage copy miss | ✅ 2 |
| R-DOCKER-010 | apt bloat | ✅ 2 |

## Certification

Run `cauterule test --pack pack-docker` to re-certify.
