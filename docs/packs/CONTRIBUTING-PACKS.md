# Contributing Community Packs

How to author, test, certify, and publish a Cauterule rule pack.

## Naming

- Pack directory and manifest: `pack-<domain>` (lowercase, digits, hyphens).
- Rule ids: `R-<NS>-NNN` namespaced per pack (`R-DOCKER-001`, `R-PY-001`).
  Never reuse another pack's namespace.

## Rule minimums

- At least 10 rules per official-quality pack.
- Every rule ships **at least 2 replay fixtures** (canonical trajectory +
  paraphrased agent phrasing) in `tests/replay_<name>.jsonl`.
- Every rule carries full provenance (`source_trajectory`, `extracted_by`,
  `extract_timestamp`, `extraction_pass`) and a taxonomy label.
- Per-rule precision bar: **>= 0.85** on the domain corpus before `1.0.0`.

## Certification bar

- `certify_pack()` must pass (manifest, replay evidence, provenance).
- Pack safety score **>= 70** (default `min_safety_score`); over-broad
  triggers and unsafe directives drag the score and block install/publish.

## Semver policy for rules

- `major`: rule removals, trigger narrowing that drops coverage, manifest
  format change.
- `minor`: new rules, new optional deps.
- `patch`: rule text fixes, provenance/metadata fixes.
- `publish --bump` suggests the bump from the rule-list diff (warn-only).

## Submission checklist

1. `cauterule pack create <name> --from-tag <tag>` — scaffold.
2. `cauterule test --pack <name>` — replay suite green.
3. `cauterule pack publish --dry-run` — cert + README lint clean.
4. Docs: symptom-index README per the schema below.
5. `cauterule pack publish` — ship the GitHub release.

## Pack README schema

```markdown
# pack-<name>
> One-line blurb.

## Symptoms → rules
| Symptom you see | Rule | Fix in brief |

## Rules (N)
| Rule | Trigger | Fixtures |

## Install / Upgrade / Pinning
## Certification (score, date, re-run command)
## Contributing trajectories
## Changelog
```

## Marketplace preview fields

`pack.yaml` accepts an optional `marketplace` block (`categories`,
`keywords`, `homepage`). `rating`, `downloads`, and `reviews_url` are
**service-owned**: publish rejects hand-set values. No fake stats, from day one.

## Review

Submission review SLA: best effort by maintainers; packs that stay green
against `test --pack` plus cert keep their certified badge.
