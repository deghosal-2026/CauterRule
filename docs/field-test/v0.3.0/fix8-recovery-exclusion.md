# Fix 8 Recovery-Exclusion Re-run — CauterRule v0.3.0

**Issue:** #491 · **Plan:** §5.6 · **Tier:** local (gate-level, hermetic)

| Corpus | Recovered-expected | Excluded | Extracted (false) | Exclusion rate | Meets ≥0.5 |
|--------|--------------------|----------|-------------------|----------------|------------|
| field-test/corpus/curated/nearmiss | 50 | 27 | 23 | 0.540 | ✅ |
| corpus/public/nearmiss | 20 | 20 | 0 | 1.000 | ✅ |
| field-test/corpus/raw/cross-session | 0 | 0 | 0 | 0.000 | ❌ |

**Overall:** 47/70 recovered trajectories excluded (0.671); ✅ holds on local tier.
