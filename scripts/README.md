# CauterRule Scripts

Utility scripts for development, testing, corpus management, and field test execution.

## Corpus Acquisition

| Script | Purpose | Usage |
|--------|---------|-------|
| `seed-corpus.py` | Seed the field-test corpus from test fixtures, golden trajectories, and failure mode catalog | `python scripts/seed-corpus.py` |
| `seed-corpus.py --status` | Show corpus stats (counts per source) | `python scripts/seed-corpus.py --status` |
| `seed-corpus.py --validate` | Validate all trajectories in the corpus | `python scripts/seed-corpus.py --validate` |
| `create-trajectory.py` | Interactive wizard to create a single trajectory JSONL file | `python scripts/create-trajectory.py` |
| `create-trajectory.py --list` | List all existing trajectories in the corpus | `python scripts/create-trajectory.py --list` |
| `create-trajectory.py --batch <file.json>` | Batch-import trajectories from a JSON array file | `python scripts/create-trajectory.py --batch data.json` |
| `collect-ci-corpus.sh` | Download CI failure logs from GitHub Actions and convert to trajectory JSONL | `bash scripts/collect-ci-corpus.sh [--limit N]` |

## Performance & Measurement

| Script | Purpose | Usage |
|--------|---------|-------|
| `measure_performance.py` | Measure CLI command response times (list, health, validate, inject) | `python scripts/measure_performance.py` |
| `measure_ttv.sh` | Measure time-to-value wall-clock duration (install → first prevented failure) | `bash scripts/measure_ttv.sh` |

## Build & Distribution

| Script | Purpose | Usage |
|--------|---------|-------|
| `build.sh` | Build Python distribution artifacts (wheel) | `bash scripts/build.sh` |
| `build_binary.sh` | Build standalone binary via PyInstaller | `bash scripts/build_binary.sh` |
| `docker_field_test.sh` | Run all Docker field test stages sequentially | `bash scripts/docker_field_test.sh [--stage N] [--skip-build]` |

## Quick Start

```bash
# Seed the corpus from all available sources
python scripts/seed-corpus.py

# Show corpus stats
python scripts/seed-corpus.py --status

# Validate all trajectories
python scripts/seed-corpus.py --validate

# Collect CI failure logs
bash scripts/collect-ci-corpus.sh --limit 10

# Create a trajectory interactively
python scripts/create-trajectory.py

# Measure performance
python scripts/measure_performance.py
```