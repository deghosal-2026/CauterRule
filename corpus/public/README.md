# Public Synthetic Corpus

This directory contains publicly distributable synthetic trajectory JSONL files
for testing and benchmarking CauterRule.

## File Format

Each `.jsonl` file contains one JSON object per line, where each object
represents a serialized `Trajectory` (see `src/cauterule/models/trajectory.py`).

## Naming Convention

```
<domain>-<scenario>-<tier>.jsonl
```

Examples:
- `coding-fix-sort-tiny.jsonl`
- `devops-deploy-small.jsonl`

## Schema Version

Current schema: 1.0 (see `CORPUS_SCHEMA_VERSION` in format.py)