from cauterule.replay.scorer import compute_scores


def test_prevented_all() -> None:
    prec, rec, verdict = compute_scores(prevented=5, broken=0, total_failures=5, total_successes=5)
    assert prec == 1.0
    assert rec == 1.0
    assert verdict == "pass"


def test_mixed() -> None:
    prec, _rec, verdict = compute_scores(prevented=3, broken=1, total_failures=5, total_successes=5)
    assert prec == 0.75
    # #724: a net-positive rule (broken <= prevented, precision >= 0.5) passes.
    assert verdict == "pass"


def test_net_positive_broad_rule_passes() -> None:
    """#724: the F-001 case — prevents 5, breaks 3, precision 0.625 -> pass."""
    prec, _rec, verdict = compute_scores(
        prevented=5, broken=3, total_failures=8, total_successes=8
    )
    assert prec == 0.625
    assert verdict == "pass"


def test_dangerously_broad_still_fails() -> None:
    """#724: broken > prevented stays fail (safety preserved)."""
    _prec, _rec, verdict = compute_scores(
        prevented=3, broken=4, total_failures=8, total_successes=8
    )
    assert verdict == "fail"


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
    """#724: >2 near-misses take precedence; broken<=prevented alone no longer
    forces inconclusive, so the near-miss guard is what keeps this inconclusive."""
    _prec, _rec, verdict = compute_scores(
        prevented=3,
        broken=1,
        total_failures=5,
        total_successes=5,
        near_misses=5,
    )
    assert verdict == "inconclusive"  # near_misses>2 path


def test_detailed_reasons() -> None:
    from cauterule.replay.scorer import compute_scores_detailed

    assert compute_scores_detailed(5, 0, 5, 5, 0)[3] == "pass"
    assert compute_scores_detailed(0, 0, 5, 5, 0)[3] == "no_signal"
    assert compute_scores_detailed(3, 4, 8, 8, 0)[3] == "blocked_by_broken"
    assert compute_scores_detailed(5, 0, 5, 5, 3)[3] == "blocked_by_near_miss"
