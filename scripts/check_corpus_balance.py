#!/usr/bin/env python3
"""Corpus source-balance check (#707).

Reports per-``source_repo`` success/failure counts across ``corpus/public`` and
flags failure-only sources (which leave the safety gate validated against a
narrower vocabulary than production traffic). Warns by default; ``--strict``
exits non-zero so CI can gate once the known gaps are closed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cauterule.corpus.balance import balance_violations, load_public_balance


def main() -> None:
    """Print per-source balance and flag failure-only sources."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-root", type=Path, default=None)
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any violation.")
    args = parser.parse_args()

    balances = load_public_balance(args.public_root)
    for balance in balances:
        mark = "ok" if balance.balanced else "FAILURE-ONLY"
        print(
            f"{balance.source}: successes={balance.successes} failures={balance.failures} [{mark}]"
        )

    violations = balance_violations(balances)
    if not violations:
        print("[ok] every source has both success and failure trajectories")
        return
    print(f"\n[warn] {len(violations)} unbalanced source(s):")
    for violation in violations:
        print(f"  - {violation}")
    if args.strict:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
