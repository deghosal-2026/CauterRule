# Pack Replay Score — CauterRule v0.3.0

**Issues:** #479/#481 · **Plan:** §5.3/§7.2 · **Match threshold:** 0.70

| Pack | Rules | Replays | Prevented | Broke | Neutral | Score | Meets ≥0.5 |
|------|-------|---------|-----------|-------|---------|-------|------------|
| pack-git | 10 | 0 | 0 | 0 | 0 | 0.00 | ❌ |
| pack-docker | 10 | 20 | 13 | 0 | 7 | 1.00 | ✅ |
| pack-deploy | 10 | 20 | 14 | 0 | 6 | 1.00 | ✅ |
| pack-testing | 10 | 20 | 15 | 0 | 5 | 1.00 | ✅ |
| pack-python | 10 | 20 | 14 | 0 | 6 | 1.00 | ✅ |

**Summary:** 4/4 packs with replay fixtures meet the ≥1-prevented and score ≥0.5 gate.
Packs without replay fixtures (create-only, not scored): pack-git.
