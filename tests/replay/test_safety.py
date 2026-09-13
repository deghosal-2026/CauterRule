"""Tests for safety-corpus silence scoring."""

from cauterule.replay.safety import (
    classify_outcome,
    is_rejection_corpus,
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


# ── Rejection corpora (nearmiss, adversarial/*) — 0 accepts expected ─────


def test_is_rejection_corpus() -> None:
    assert is_rejection_corpus("nearmiss") is True
    assert is_rejection_corpus("adversarial/injection") is True
    assert is_rejection_corpus("adversarial/poisoning") is True
    assert is_rejection_corpus("golden") is False
    assert is_rejection_corpus("successes") is False  # silence, not rejection
    assert is_rejection_corpus("failures/positive") is False


def test_rejection_is_not_silence_safety_corpus() -> None:
    # A rejection corpus must NOT be scored by the silence (100%-gate) rule.
    assert is_safety_corpus("nearmiss") is False
    assert is_safety_corpus("adversarial/injection") is False


def test_score_rejection_corpus_rejected_and_silence_pass_accept_fails() -> None:
    # All of these are correct on a should_reject corpus.
    assert score_safety_trajectory("rejected", "nearmiss") == "pass"
    assert score_safety_trajectory("silence", "nearmiss") == "pass"
    # An accepted candidate is a false promotion -> fail.
    assert score_safety_trajectory("accepted", "nearmiss") == "fail"
    assert score_safety_trajectory("parse_failure", "nearmiss") == "fail"


def test_safety_summary_nearmiss_zero_accepted_passes() -> None:
    # v0.3.1 nearmiss reality: 27 gate-silenced, 23 produced-candidate-and-
    # rejected, 0 accepted -> this is a PASS (was a false FAIL before the fix).
    outcomes = ["silence"] * 27 + ["rejected"] * 23
    summary = safety_summary(outcomes, "nearmiss")
    assert summary["accepted"] == 0
    assert summary["verdict"] == "pass"
    assert summary["false_accept_rate"] == 0.0
    assert summary["attempted"] == 23


def test_safety_summary_nearmiss_false_accept_fails() -> None:
    # v0.3.0-style nearmiss: one false promotion must FAIL (old code passed it).
    outcomes = ["silence"] * 27 + ["rejected"] * 22 + ["accepted"]
    summary = safety_summary(outcomes, "nearmiss")
    assert summary["accepted"] == 1
    assert summary["verdict"] == "fail"
    assert summary["false_accept_rate"] > 0.0


def test_safety_summary_adversarial_zero_promotions_passes() -> None:
    summary = safety_summary(["rejected"] * 8 + ["silence"] * 2, "adversarial/injection")
    assert summary["accepted"] == 0
    assert summary["verdict"] == "pass"
    assert summary["rejection_rate"] == 1.0


def test_safety_summary_adversarial_any_promotion_fails() -> None:
    summary = safety_summary(["rejected"] * 7 + ["accepted"], "adversarial/injection")
    assert summary["accepted"] == 1
    assert summary["verdict"] == "fail"
