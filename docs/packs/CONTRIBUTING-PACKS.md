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

## Pack format (`pack.yaml`)

A pack is a flat directory: `pack.yaml` at the root, flat `R-*.yaml` rule
files, a `README.md`, a `LICENSE`, and `tests/replay_<name>.jsonl`.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | `pack-<domain>`; must match `^[a-z0-9-]+$` |
| `version` | string | yes | Strict semver `MAJOR.MINOR.PATCH` |
| `description` | string | yes | Non-blank blurb |
| `author` | string | yes | Defaults to `git config user.name` on `pack create` |
| `rules` | list of rule ids | yes | At least one; ids must exist in the store |
| `license` | string | no | SPDX identifier (e.g. `MIT`) |
| `deps` | list of strings | no | Dependency specs (see below) |
| `cauterule` | string | no | Minimum Cauterule version |
| `checksum` | string | no | sha256 of the release asset, verified on install |
| `created_with` | string | no | Toolchain that scaffolded the pack, e.g. `cauterule 0.3.0` |
| `cert` | mapping | no | `{ required: true, min_score: <float> }` certification gate |
| `marketplace` | mapping | no | Optional `categories`, `keywords`, `homepage` |

`pack create` writes `pack.yaml` with `created_with: cauterule <version>` and
`cert: { required: true, min_score: 0.8 }`. A legacy `manifest.yaml` is also
written for compatibility; `pack.yaml` is preferred by the loader.

## Dependencies

```yaml
deps:
  - pack-docker >=1.0.0,<2.0.0
  - pack-testing ^0.4.0
```

Resolution is recorded in `packs.lock.yaml`; `cauterule pack tree <name>`
prints the resolved tree. Cycles and unsatisfiable constraints fail with an
actionable error naming both requirers. Prereleases (`-rc.N`) never satisfy an
unpinned install — pin them exactly.

## Certification & safety

Every `create` / `install` / `publish` runs two gates:

1. **`certify_pack()`** — manifest validity (safety), at least one rule
   (replay), and a non-empty `id` on every rule (provenance).
2. **Safety score (0–100)** — per-rule scan: unsafe directives cost 40 points
   each, broad triggers 22 each; the pack score is the mean of its rules.

The safety gate blocks the operation below the threshold. Precedence:
`--min-safety-score` flag > `[packs] min_safety_score` in `cauterule.toml` >
`70` (`DEFAULT_MIN_SAFETY_SCORE`).

- `cauterule pack create ... --cert/--no-cert` runs the cert gate on scaffold.
- `cauterule pack install ... --skip-cert` bypasses both gates **for CI only**;
  it is not recommended.
- `cauterule pack publish` applies the safety gate with **no override** — fix
  the rules or they will not ship.
- `cauterule pack info <name>` prints the cert status, safety score, and which
  rules drag the score down.

## Semver policy for rules

- `major`: rule removals, trigger narrowing that drops coverage, manifest
  format change.
- `minor`: new rules, new optional deps.
- `patch`: rule text fixes, provenance/metadata fixes.
- `publish --bump` suggests the bump from the rule-list diff (warn-only; the
  explicit `--bump` wins). Published versions are monotonic — you cannot
  re-publish a version or downgrade.

## Submission checklist

1. `cauterule pack create <name> --from-tag <tag>` — scaffold (`pack.yaml` +
   rules + replay fixtures + README).
2. Fill in real replay fixtures; `cauterule test --pack <name>` — replay suite
   green.
3. `cauterule pack publish --dry-run` — cert + safety + README lint clean
   (asset is built but not uploaded).
4. Docs: symptom-index README per the schema below.
5. `cauterule pack publish --bump minor` — tag `pack-<name>-vX.Y.Z` and create
   the GitHub release.

```bash
cauterule pack publish --dry-run                 # validate + cert + asset preview
cauterule pack publish --bump minor --repo owner/repo
cauterule pack publish --version 1.0.0 --notes NOTES.md --prerelease
```

`publish` rejects hand-set service-owned `marketplace` fields (`rating`,
`downloads`, `reviews_url`) and warns about missing README sections
(`Symptoms`, `Rules`, `Install`, `Certification`); the README check becomes a
hard gate in v0.4.0.

## Share a single rule

For one rule to a reviewer, skip the pack machinery:

```bash
cauterule share R-001                    # secret gist + PROVENANCE.json
cauterule share R-001 --public --yes     # public gist (confirms author-email exposure)
cauterule share R-001 --no-provenance    # rule YAML only
cauterule pack install <gist-url>        # import it back
```

The gist carries a `cauterule-share/1` provenance envelope
(`shared_by`, `shared_at`, `cauterule_version`, `source_pack`, `redacted`,
`upstream`). Secrets in the rule are redacted before upload; if anything
unredactable remains, `share` refuses. Requires `GH_TOKEN` (or a
`gh auth login` token).

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
