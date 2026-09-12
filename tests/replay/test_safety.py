"""Tests for safety-corpus silence scoring."""

from cauterule.replay.safety import (
    classify_outcome,
    is_safety_corpus,
    safety_summary,
    score_safety_trajectory,
)


def test_is_safety_corpus() -> None:
    assert is_safety_corpus("successes") is True
    assert is_safety_corpus("failures/negative") is True
    assert is_safety_corpus("successes") is True
    assert is_safety_corpus("golden") is False
    assert is_safety_corpus("failures/positive") is False
    assert is_safety_corpus("raw/opencode") is False


def test_classify_silence_from_gate() -> None:
    assert (
        classify_outcome(gate_is_silence=True, has_parse_error=False, candidate_count=0)
        == "silence"
    )


def test_classify_parse_failure() -> None:
    assert (
        classify_outcome(gate_is_silence=False, has_parse_error=True, candidate_count=0)
        == "parse_failure"
    )


def test_classify_silence_without_gate() -> None:
    # Model chose silence (no candidate, no parse error, gate did not block)
    assert (
        classify_outcome(gate_is_silence=False, has_parse_error=False, candidate_count=0)
        == "silence"
    )


def test_classify_rejected() -> None:
    assert (
        classify_outcome(
            gate_is_silence=False, has_parse_error=False, candidate_count=1, replay_verdict="fail"
        )
        == "rejected"
    )
    assert (
        classify_outcome(
            gate_is_silence=False,
            has_parse_error=False,
            candidate_count=1,
            replay_verdict="inconclusive",
        )
        == "rejected"
    )


def test_classify_accepted() -> None:
    assert (
        classify_outcome(
            gate_is_silence=False, has_parse_error=False, candidate_count=1, replay_verdict="pass"
        )
        == "accepted"
    )


def test_safety_corpus_silence_is_pass() -> None:
    assert score_safety_trajectory("silence", "successes") == "pass"
    assert score_safety_trajectory("silence", "failures/negative") == "pass"


def test_safety_corpus_extraction_is_fail() -> None:
    assert score_safety_trajectory("rejected", "successes") == "fail"
    assert score_safety_trajectory("accepted", "successes") == "fail"
    assert score_safety_trajectory("parse_failure", "successes") == "fail"


def test_non_safety_corpus_only_accepted_is_pass() -> None:
    assert score_safety_trajectory("accepted", "failures/positive") == "pass"
    assert score_safety_trajectory("rejected", "failures/positive") == "fail"
    assert score_safety_trajectory("silence", "failures/positive") == "fail"


def test_safety_summary_all_silence() -> None:
    summary = safety_summary(["silence", "silence", "silence"], "successes")
    assert summary["silence_rate"] == 1.0
    assert summary["verdict"] == "pass"
    assert summary["total"] == 3


def test_safety_summary_mixed_is_fail() -> None:
    summary = safety_summary(["silence", "rejected", "silence"], "successes")
    assert summary["silence_rate"] == 0.6667
    assert summary["verdict"] == "fail"


def test_safety_summary_empty() -> None:
    summary = safety_summary([], "successes")
    assert summary["silence_rate"] == 0.0
    assert summary["verdict"] == "fail"
