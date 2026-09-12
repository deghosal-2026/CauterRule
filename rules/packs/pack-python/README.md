# pack-python

> Rules for Python imports, venvs, pip resolver and install failures.

`cauterule pack install <repo>@<version>`

## Symptoms → rules

| Symptom you see | Rule | Fix in brief |
|---|---|---|
| `ModuleNotFoundError` after pip install | R-PY-001 | `python -m pip` with the running interpreter |
| Installs land in system python | R-PY-002 | Create + activate a venv |
| `ResolutionImpossible` | R-PY-003 | Relax the over-tight pin |
| Stale installed copy shadows repo | R-PY-004 | Editable install |
| CI breaks on new releases | R-PY-005 | Pin direct deps + lockfile |
| Build fails on interpreter | R-PY-006 | Match `requires-python` |
| Local file shadows stdlib | R-PY-007 | Rename + clear bytecode |
| Missing headers at build | R-PY-008 | OS package or binary wheel |
| Notebook ≠ terminal imports | R-PY-009 | Register venv kernel |
| Imports depend on cwd | R-PY-010 | `python -m` + editable install |

## Rules (10)

| Rule | Trigger | Fixtures |
|---|---|---|
| R-PY-001 | ModuleNotFoundError | ✅ 2 |
| R-PY-002 | venv not active | ✅ 2 |
| R-PY-003 | resolver conflict | ✅ 2 |
| R-PY-004 | stale installed copy | ✅ 2 |
| R-PY-005 | unpinned deps | ✅ 2 |
| R-PY-006 | wrong interpreter | ✅ 2 |
| R-PY-007 | stdlib shadowing | ✅ 2 |
| R-PY-008 | system libs missing | ✅ 2 |
| R-PY-009 | kernel mismatch | ✅ 2 |
| R-PY-010 | cwd imports | ✅ 2 |

## Certification

Run `cauterule test --pack pack-python` to re-certify.

## Contributing trajectories

Harvest real `ModuleNotFoundError` trajectories from agent runs and append them
to `tests/replay_pack-python.jsonl` with the matching `rule_id` — this feeds
the tiered corpus.
