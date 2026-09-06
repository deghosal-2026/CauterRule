# CauterRule v0.1.0 Field-Test Corpus

**Generated:** 2026-09-06T01:17:29Z
**Version:** 1.0

## Directory Layout

```
corpus/
├── raw/                 # Original captured trajectories
│   ├── opencode/        # From OpenCode sessions (25)
│   ├── synthetic/       # Generated scenarios (~145)
│   ├── ci/              # GitHub Actions CI logs (110)
│   ├── sibling-repos/   # Cursor + Claude agent runs (10)
│   ├── corrections/     # Manual correction transcripts (5)
│   └── cross-session/   # Cross-session repeat failures (5)
├── curated/             # Cleaned, labeled, validated
│   ├── failures/        # 30 positive + 10 negative failure trajectories
│   ├── successes/       # 20 success trajectories
│   ├── nearmiss/        # 10 near-miss scenarios
│   ├── noisy/           # 5 noisy/misleading trajectories
│   └── corrections/     # 5 human-correction examples
├── golden/              # 10 golden trajectories (regression anchor)
├── catalog.yaml         # Master catalog
└── README.md            # This file
```

## Naming Convention

```
<type>-<nnn>-<domain>-<scenario>.jsonl
type: F (failure), S (success), N (nearmiss), M (noisy), C (correction), G (golden)
```
