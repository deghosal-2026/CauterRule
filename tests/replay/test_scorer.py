from cauterule.replay.scorer import compute_scores


def test_prevented_all() -> None:
    prec, rec, verdict = compute_scores(prevented=5, broken=0, total_failures=5, total_successes=5)
    assert prec == 1.0
    assert rec == 1.0
    assert verdict == "pass"


def test_mixed() -> None:
    prec, _rec, verdict = compute_scores(prevented=3, broken=1, total_failures=5, total_successes=5)
    assert prec == 0.75
    assert verdict == "inconclusive"  # broad but fixable: broken < prevented


def test_no_matches() -> None:
    prec, rec, verdict = compute_scores(prevented=0, broken=0, total_failures=5, total_successes=5)
    assert prec == 0.0
    assert rec == 0.0
    assert verdict == "inconclusive"


def test_no_failures() -> None:
    _prec, rec, verdict = compute_scores(prevented=0, broken=0, total_failures=0, total_successes=5)
    assert rec == 0.0
    assert verdict == "inconclusive"


def test_partial() -> None:
    prec, rec, verdict = compute_scores(prevented=2, broken=0, total_failures=5, total_successes=5)
    assert prec == 1.0
    assert rec == 0.4
    assert verdict == "pass"  # precision >= 0.8, no broken


def test_low_precision() -> None:
    prec, _rec, ver = compute_scores(prevented=1, broken=3, total_failures=5, total_successes=5)
    assert prec == 0.25
    assert ver == "fail"


def test_near_miss_downgrades_pass() -> None:
    """>2 near-miss matches is over-broad: downgrade from pass to inconclusive
    even with precision 1.0 (v0.3.0 tolerance band: <=2 NM passes)."""
    prec, _rec, verdict = compute_scores(
        prevented=5,
        broken=0,
        total_failures=5,
        total_successes=5,
        near_misses=3,
    )
    assert prec == 1.0
    assert verdict == "inconclusive"


def test_near_miss_tolerance_band_passes() -> None:
    """v0.3.0: 1-2 near-misses with precision>=0.5 still pass — a candidate
    that prevents more failures than it touches near-misses is a good rule."""
    prec, _rec, verdict = compute_scores(
        prevented=5,
        broken=0,
        total_failures=5,
        total_successes=5,
        near_misses=2,
    )
    assert prec == 1.0
    assert verdict == "pass"


def test_near_miss_tolerance_low_precision_stays_inconclusive() -> None:
    """1-2 near-misses but precision<0.5 -> inconclusive."""
    _prec, _rec, verdict = compute_scores(
        prevented=1,
        broken=3,
        total_failures=5,
        total_successes=5,
        near_misses=1,
    )
    assert verdict == "fail"  # broken>prevented takes precedence


def test_near_miss_zero_stays_pass() -> None:
    """near_misses=0 preserves the original pass verdict."""
    _prec, _rec, verdict = compute_scores(
        prevented=5,
        broken=0,
        total_failures=5,
        total_successes=5,
        near_misses=0,
    )
    assert verdict == "pass"


def test_near_miss_does_not_override_broken() -> None:
    """broken > 0 takes precedence over near_misses."""
    _prec, _rec, verdict = compute_scores(
        prevented=3,
        broken=1,
        total_failures=5,
        total_successes=5,
        near_misses=5,
    )
    assert verdict == "inconclusive"  # broken>0 path, not near-miss path
