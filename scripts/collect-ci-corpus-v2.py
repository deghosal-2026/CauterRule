"""Re-collect raw/ci trajectories keeping the failure region of the log (J11).

The v0.1.0-era collector stored the FIRST 2000 chars of ``gh run view --log``.
GitHub Actions logs start with runner boilerplate (image info, token
permissions), so the actual failure signature at the END of the log was
truncated out of the corpus. 99/110 raw/ci trajectories contained no failure
signal, so extractors produced generic "when CI fails with error" triggers and
the replay matcher had nothing to score against (77-83% no_signal).

This script re-fetches each existing trajectory's CI run (run id is encoded in
the filename ``<repo>-<run_id>.jsonl``) and rewrites the record in place with:

* ``steps[0].output``  — the TAIL of the log (failure region), clean log lines
* ``steps[0].error``   — the first real error line
* ``failure_point``    — same error line (<= 200 chars)
* ``failure_class``    — re-derived from the real log content

All other fields (trajectory_id, task, domain, tags, ...) are preserved so the
before/after sweep is a clean A/B on identical run ids.

Usage:
    python scripts/collect-ci-corpus-v2.py                # fix all, in place
    python scripts/collect-ci-corpus-v2.py --dry-run      # show plan, write nothing
    python scripts/collect-ci-corpus-v2.py --limit 3      # only first 3 files
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

CORPUS_DIR = Path("field-test/corpus/raw/ci")
ORG = "deghosal-2026"
TAIL_LINES = 120
OUTPUT_CHAR_CAP = 3000
SLEEP_SECONDS = 0.3

_ERROR_RE = re.compile(
    r"(error:|FAILED|failed|Error\b|E\d{3}|panic|Traceback|assert|eslint|ruff|tsc)", re.I
)
_BOILER_RE = re.compile(
    r"(GITHUB_TOKEN|runner version|Runner Image|Provisioner|Secret source|"
    r"##\[(group|endgroup)\]|Set up job|Post job|Commit:|Build Date|Worker ID)", re.I
)


def fetch_log(repo: str, run_id: int) -> str:
    """Fetch the full CI log for a run, clean of the job/step column prefixes."""
    out = subprocess.run(
        ["gh", "run", "view", str(run_id), "--repo", repo, "--log"],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        raise RuntimeError(f"gh failed for {repo}/{run_id}: {out.stderr.strip()[:200]}")
    lines = []
    for line in out.stdout.splitlines():
        parts = line.split("\t", 2)
        text = parts[2] if len(parts) == 3 else line
        # Drop the leading Actions timestamp ("2026-08-29T06:57:49.1234567Z ").
        text = re.sub(r"^\d{4}-\d{2}-\d{2}T[\d:.]+Z\s*", "", text)
        lines.append(text)
    return "\n".join(lines)


def tail_of(log: str) -> str:
    lines = log.splitlines()
    return "\n".join(lines[-TAIL_LINES:])[:OUTPUT_CHAR_CAP]


def derive_failure_class(log: str) -> str:
    low = log.lower()
    if "ruff" in low or "flake8" in low or "lint" in low:
        return "ci/lint"
    if "mypy" in low or "type check" in low or "type-check" in low:
        return "ci/typecheck"
    if "pytest" in low or "test failed" in low or "failed" in low:
        return "ci/test"
    if "docker" in low or "build failed" in low:
        return "ci/build"
    return "ci/failure"


def find_error_line(tail: str) -> str:
    for line in reversed(tail.splitlines()):
        clean = line.strip()
        if not clean:
            continue
        if _ERROR_RE.search(clean) and not _BOILER_RE.search(clean):
            return clean[:500]
    for line in reversed(tail.splitlines()):
        clean = line.strip()
        if clean and not _BOILER_RE.search(clean):
            return clean[:500]
    return "CI failure"


def has_real_signal(text: str) -> bool:
    return any(
        _ERROR_RE.search(line) and not _BOILER_RE.search(line) for line in text.splitlines()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-signal", action="store_true",
                        help="skip files whose stored output already carries a failure signal")
    args = parser.parse_args()

    files = sorted(CORPUS_DIR.glob("*.jsonl"))
    if args.limit:
        files = files[: args.limit]
    print(f"=== raw/ci re-collection: {len(files)} files ===")

    ok = fixed = 0
    for f in files:
        m = re.match(r"^(?P<repo>[a-z0-9-]+)-(?P<run>\d+)\.jsonl$", f.name)
        if not m:
            print(f"  [skip] {f.name} (no <repo>-<run_id> pattern)")
            continue
        repo, run_id = m.group("repo"), int(m.group("run"))
        rec = json.loads(f.read_text().splitlines()[0])
        full_repo = rec.get("source_repo") or f"{ORG}/{repo}"
        if args.skip_signal and has_real_signal(rec["steps"][0].get("output", "")):
            print(f"  [skip] {f.name} (already has failure signal)")
            continue
        try:
            log = fetch_log(full_repo, run_id)
        except Exception as exc:
            print(f"  [fail] {f.name}: {exc}")
            continue
        ok += 1
        tail = tail_of(log)
        error_line = find_error_line(tail)
        new_class = derive_failure_class(log)
        had_signal = has_real_signal(rec["steps"][0].get("output", ""))
        new_signal = has_real_signal(tail)

        if args.dry_run:
            print(f"  [dry] {f.name}: signal {had_signal}->{new_signal}, "
                  f"class {rec.get('failure_class')}->{new_class}, err={error_line[:80]!r}")
            continue

        rec["steps"][0]["output"] = tail
        rec["steps"][0]["error"] = error_line
        rec["failure_point"] = error_line[:200]
        rec["failure_class"] = new_class
        f.write_text(json.dumps(rec) + "\n")
        if had_signal and new_signal:
            fixed += 0
        elif new_signal:
            fixed += 1
        print(f"  [ok] {f.name}: class->{new_class}, signal={new_signal}, "
              f"err={error_line[:80]!r}")
        time.sleep(SLEEP_SECONDS)

    print(f"=== done: fetched {ok}/{len(files)}, newly-signal-bearing {fixed} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
