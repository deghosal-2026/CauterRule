from cauterule.extraction.fallback import check_fallback


def test_fallback_no_candidate() -> None:
    result = check_fallback(candidate_available=False, error="LLM failed")
    assert result.needs_review
    assert "LLM failed" in result.reason
    result2 = check_fallback(candidate_available=False)
    assert result2.needs_review
    assert "no candidate" in result2.reason


def test_fallback_warnings_confidence() -> None:
    result = check_fallback(candidate_available=True, warnings=["confidence 0.50 below 0.6"])
    assert result.needs_review
    assert "confidence" in result.reason


def test_fallback_warnings_tautological() -> None:
    result = check_fallback(
        candidate_available=True, warnings=["tautological: when and do are identical"]
    )
    assert result.needs_review


def test_fallback_warnings_other() -> None:
    result = check_fallback(
        candidate_available=True, warnings=["candidate does not reference trajectory"]
    )
    assert not result.needs_review
    assert result.reason == "ok"


def test_fallback_error() -> None:
    result = check_fallback(candidate_available=True, error="some error")
    assert result.needs_review
    assert "some error" in result.reason


def test_fallback_ok() -> None:
    result = check_fallback(candidate_available=True)
    assert not result.needs_review
    assert result.reason == "ok"
