from cauterule.replay.scorer import compute_scores


def test_prevented_all() -> None:
    prec, rec, verdict = compute_scores(prevented=5, broken=0, total_failures=5, total_successes=5)
    assert prec == 1.0
    assert rec == 1.0
    assert verdict == "pass"


def test_mixed() -> None:
    prec, rec, verdict = compute_scores(prevented=3, broken=1, total_failures=5, total_successes=5)
    assert prec == 0.75
    assert verdict == "inconclusive"  # broad but fixable: broken < prevented


def test_no_matches() -> None:
    prec, rec, verdict = compute_scores(prevented=0, broken=0, total_failures=5, total_successes=5)
    assert prec == 0.0
    assert rec == 0.0
    assert verdict == "inconclusive"


def test_no_failures() -> None:
    prec, rec, verdict = compute_scores(prevented=0, broken=0, total_failures=0, total_successes=5)
    assert rec == 0.0
    assert verdict == "inconclusive"


def test_partial() -> None:
    prec, rec, verdict = compute_scores(prevented=2, broken=0, total_failures=5, total_successes=5)
    assert prec == 1.0
    assert rec == 0.4
    assert verdict == "pass"  # precision >= 0.8, no broken


def test_low_precision() -> None:
    prec, rec, ver = compute_scores(prevented=1, broken=3, total_failures=5, total_successes=5)
    assert prec == 0.25
    assert ver == "fail"


def test_near_miss_downgrades_pass() -> None:
    """A candidate that matches near-miss references is over-broad:
    downgrade from pass to inconclusive even with precision 1.0."""
    prec, rec, verdict = compute_scores(
        prevented=5, broken=0, total_failures=5, total_successes=5, near_misses=2,
    )
    assert prec == 1.0
    assert verdict == "inconclusive"


def test_near_miss_zero_stays_pass() -> None:
    """near_misses=0 preserves the original pass verdict."""
    prec, rec, verdict = compute_scores(
        prevented=5, broken=0, total_failures=5, total_successes=5, near_misses=0,
    )
    assert verdict == "pass"


def test_near_miss_does_not_override_broken() -> None:
    """broken > 0 takes precedence over near_misses."""
    prec, rec, verdict = compute_scores(
        prevented=3, broken=1, total_failures=5, total_successes=5, near_misses=5,
    )
    assert verdict == "inconclusive"  # broken>0 path, not near-miss path
