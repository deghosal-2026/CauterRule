from cauterule.replay.scorer import compute_scores


def test_prevented_all() -> None:
    prec, rec, verdict = compute_scores(prevented=5, broken=0, total_failures=5, total_successes=5)
    assert prec == 1.0
    assert rec == 1.0
    assert verdict == "pass"


def test_mixed() -> None:
    prec, rec, verdict = compute_scores(prevented=3, broken=1, total_failures=5, total_successes=5)
    assert prec == 0.75
    assert verdict == "fail"


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
