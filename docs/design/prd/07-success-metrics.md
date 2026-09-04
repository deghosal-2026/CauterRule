# PRD 07: Success Metrics

## Primary Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Rules extracted, tested, promoted per week | ≥5/week | Rule store git log |
| Replay precision | ≥90% | % of promoted rules that help without breaking prior successes |
| Repeat-failure rate | <10% failure recurrence | % of failures that match an existing rule's trigger condition |
| Time from failure to rule promotion | <5 minutes (auto) | Timestamps in provenance |

## Secondary Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Rule store growth without human intervention | Growing weekly | Git commit count |
| External interest | Stars, forks, issues | GitHub analytics |
| Community contributions | ≥2 external PRs/month | GitHub pull requests |

## Quality Gates

- Every promoted rule must have ≥1 historical failure it would have prevented
- Every promoted rule must have 0 historical successes it would have broken
- Every rule must include full provenance (source failure, replay evidence, promotion timestamp)