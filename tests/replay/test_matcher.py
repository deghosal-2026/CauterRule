import pytest

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.matcher import (
    is_near_miss,
    match_detail,
    match_score,
    rule_matches,
)


def _cand(trigger: str, context: tuple[str, ...] = ()) -> CandidateRule:
    return CandidateRule(when=RuleWhen(trigger=trigger, context=context), do=RuleDo(directive="d"), confidence=0.9)


def _traj(task: str = "git push", error: str = "non-fast-forward", success: bool = False) -> Trajectory:
    return Trajectory(id="T-001", timestamp="t", task=task, steps=(Step(1, "bash", error=error),), success=success)


def test_matches_trigger() -> None:
    cand = _cand("git push")
    traj = _traj()
    assert rule_matches(cand, traj)


def test_no_match() -> None:
    cand = _cand("docker")
    assert not rule_matches(cand, _traj())


def test_empty_trigger() -> None:
    # Handled via rule_matches returning False, but CandidateRule validation
    # prevents empty trigger at construction. So we test via a non-matching trigger.
    cand = _cand("zzzzz_nonexistent")
    assert not rule_matches(cand, _traj())


def test_matches_context() -> None:
    cand = _cand("git push", context=("shared branch",))
    traj = _traj(task="git push on shared branch fails")
    assert rule_matches(cand, traj)
    traj2 = _traj(task="git push solo")
    assert not rule_matches(cand, traj2)


def test_case_insensitive() -> None:
    cand = _cand("Git Push")
    assert rule_matches(cand, _traj())


def test_near_miss() -> None:
    cand = _cand("git push", context=("shared branch", "multiple contributors"))
    traj = _traj(task="git push on shared branch")
    assert is_near_miss(cand, traj)
    assert not is_near_miss(_cand("git push"), _traj())
    assert not is_near_miss(_cand("docker"), _traj())
    # full context match is not near miss
    traj2 = _traj(task="git push on shared branch with multiple contributors")
    assert not is_near_miss(cand, traj2)


def test_semantic_paraphrase_match() -> None:
    # "non-fast-forward push is rejected" should match a trajectory whose
    # error text is phrased differently ("remote contains work").
    cand = _cand("when a non-fast-forward push is rejected")
    traj = _traj(
        task="deploy",
        error="Updates were rejected because the remote contains work that you do not have locally",
    )
    assert rule_matches(cand, traj)
    assert match_score(cand, traj) >= 0.5


def test_stemming_match() -> None:
    # "push fails" should match "push failed" via stemming.
    cand = _cand("git push fails")
    traj = _traj(task="git push failed", error="rejected")
    assert rule_matches(cand, traj)


def test_match_score_range() -> None:
    cand = _cand("git push")
    score = match_score(cand, _traj())
    assert 0.0 <= score <= 1.0
    assert score == 1.0  # exact substring


def test_match_score_no_match() -> None:
    cand = _cand("docker")
    assert match_score(cand, _traj()) < 0.5


def test_match_detail_contents() -> None:
    cand = _cand("git push")
    detail = match_detail(cand, _traj())
    assert detail["score"] == 1.0
    assert detail["exact_substring"] is True
    assert "git" in detail["matched_tokens"]
    assert detail["trigger_word_count"] == 2


def test_threshold_param() -> None:
    # Paraphrase matches at default threshold but not at a strict one.
    cand = _cand("when a non-fast-forward push is rejected")
    traj = _traj(
        task="deploy",
        error="Updates were rejected because the remote contains work that you do not have locally",
    )
    assert rule_matches(cand, traj, threshold=0.5)
    assert not rule_matches(cand, traj, threshold=0.99)


def test_qwen_alias_expansion() -> None:
    # #492: Qwen abstract triggers match through alias expansion.
    from cauterule.replay.matcher import DEFAULT_THRESHOLD, match_score
    cand = _cand("command fails with exit code")
    traj = Trajectory(id="T-q", timestamp="t", task="git push fails", steps=(Step(1, "bash", error="exit code 128"),), success=False, failure_class="git/push")
    score = match_score(cand, traj)
    assert score >= DEFAULT_THRESHOLD, f"alias score {score:.3f} < {DEFAULT_THRESHOLD}"


def test_domain_mismatch_detection() -> None:
    # #487: extract_trigger_domain and check_domain_mismatch.
    from cauterule.replay.matcher import check_domain_mismatch, extract_trigger_domain
    assert extract_trigger_domain("docker build fails") == "docker"
    assert extract_trigger_domain("git push fails") == "git"
    assert extract_trigger_domain("something unrelated") is None
    cand = _cand("docker build fails")
    traj = Trajectory(id="T-dm2", timestamp="t", task="git push fails", steps=(Step(1, "bash", error="err"),), success=False, failure_class="git/push")
    assert check_domain_mismatch(cand, traj) is True
    traj2 = Trajectory(id="T-dm3", timestamp="t", task="docker build fails", steps=(Step(1, "bash", error="err"),), success=False, failure_class="docker/build")
    assert check_domain_mismatch(cand, traj2) is False


# ---------------------------------------------------------------------------
# #517 — real F1, min-trigger-words floor, unified is_near_miss
# ---------------------------------------------------------------------------


def test_short_generic_trigger_rejected_without_context() -> None:
    # Single-word trigger "error" without context must be rejected (#517).
    cand = _cand("error")
    traj = _traj(task="something failed", error="fatal error occurred")
    assert not rule_matches(cand, traj)


def test_short_generic_trigger_accepted_with_context() -> None:
    cand = _cand("error", context=("fatal",))
    traj = Trajectory(
        id="T-ctx", timestamp="t", task="something fatal",
        steps=(Step(1, "bash", error="error occurred"),), success=False,
    )
    assert rule_matches(cand, traj)


def test_distinctive_two_word_trigger_accepted() -> None:
    cand = _cand("permission denied")
    traj = _traj(task="git push failed", error="permission denied to push")
    assert rule_matches(cand, traj)


def test_noisy_haystack_penalizes_score() -> None:
    # Same trigger hit in two haystacks: the noisier (larger) one scores lower.
    # Bypass exact-substring and alias floors so token-F1 path is exercised.
    cand = _cand("artifact upload failure")
    small_traj = Trajectory(
        id="T-sm", timestamp="t", task="artifact upload",
        steps=(Step(1, "bash", error="failure"),), success=False,
    )
    big_traj = Trajectory(
        id="T-lg", timestamp="t",
        task="artifact upload succeeded caching layer compressing archives",
        steps=(Step(1, "bash", error="failure pushing to registry after retry with fallback snapshot"),), success=False,
    )
    small_score = match_score(cand, small_traj)
    big_score = match_score(cand, big_traj)
    assert small_score >= big_score, f"noisy-haystack penalty: {small_score=} < {big_score=}"


def test_near_miss_respects_threshold_param() -> None:
    # is_near_miss(cand, traj, threshold=0.70) should agree with
    # rule_matches(cand, traj, threshold=0.70) — both must be False
    # for a low-score pair where old hardcoded 0.60 would have diverged.
    cand = _cand("docker build cache miss")
    traj = _traj(task="pipeline", error="layer already exists")
    assert not rule_matches(cand, traj, threshold=0.70)
    assert not is_near_miss(cand, traj, threshold=0.70)


def test_near_miss_include_input() -> None:
    cand = _cand("build failure", context=("dockerfile", "ci pipeline"))
    traj = Trajectory(
        id="T-inp", timestamp="t", task="docker build",
        steps=(Step(1, "bash", "check dockerfile syntax", error="failure"),),
        success=False,
    )
    assert is_near_miss(cand, traj, include_input=True)
    assert not is_near_miss(cand, traj, include_input=False)


# ---------------------------------------------------------------------------
# #694 — check_domain_mismatch must actually gate rule_matches
# ---------------------------------------------------------------------------


def test_rule_matches_rejects_cross_domain_match() -> None:
    cand = _cand("docker build failed")
    traj = Trajectory(
        id="T-cross", timestamp="t", task="docker build failed on push",
        steps=(Step(1, "bash", error="rejected"),), success=False,
        failure_class="git/push/rejected",
    )
    assert match_score(cand, traj) >= 0.6
    assert not rule_matches(cand, traj)


def test_rule_matches_allows_same_domain_match() -> None:
    cand = _cand("docker build failed")
    traj = Trajectory(
        id="T-same", timestamp="t", task="docker build failed",
        steps=(Step(1, "bash", error="exit 1"),), success=False,
        failure_class="docker/build",
    )
    assert rule_matches(cand, traj)


def test_check_domain_mismatch_is_invoked(monkeypatch: pytest.MonkeyPatch) -> None:
    import cauterule.replay.matcher as matcher

    calls = {"n": 0}
    real = matcher.check_domain_mismatch

    def spy(candidate: CandidateRule, trajectory: Trajectory) -> bool:
        calls["n"] += 1
        return real(candidate, trajectory)

    monkeypatch.setattr(matcher, "check_domain_mismatch", spy)
    rule_matches(_cand("git push"), _traj())
    assert calls["n"] == 1


def test_domain_mismatch_treats_related_domains_as_compatible() -> None:
    from cauterule.replay.matcher import check_domain_mismatch

    pip_traj = Trajectory(
        id="T-pip", timestamp="t", task="pip install fails",
        steps=(Step(1, "bash", error="dependency conflict"),), success=False,
        failure_class="python/pip/dependency-conflict",
    )
    assert check_domain_mismatch(_cand("pip install fails with conflict"), pip_traj) is False

    k8s_traj = Trajectory(
        id="T-k8s", timestamp="t", task="kubectl apply",
        steps=(Step(1, "bash", error="no matches for kind"),), success=False,
        failure_class="k8s/deploy/crd-not-found",
    )
    assert check_domain_mismatch(_cand("kubectl apply fails with CRD not found"), k8s_traj) is False

    ci_traj = Trajectory(
        id="T-ci", timestamp="t", task="deploy timed out",
        steps=(Step(1, "bash", error="timeout"),), success=False,
        failure_class="ci/deploy/timeout",
    )
    assert check_domain_mismatch(_cand("when CI deploy times out"), ci_traj) is False


def test_extract_trigger_domain_no_substring_false_positive() -> None:
    from cauterule.replay.matcher import extract_trigger_domain

    assert extract_trigger_domain("specificity scoring failed") is None
    assert extract_trigger_domain("capital letters rejected") is None
    assert extract_trigger_domain("deploy fails") == "deploy"


def test_trigger_prefilter_reason_categories() -> None:
    from cauterule.replay.matcher import trigger_prefilter_reason

    assert trigger_prefilter_reason(_cand("step_1")) == "degenerate"
    assert trigger_prefilter_reason(_cand("error")) == "generic"
    assert trigger_prefilter_reason(_cand("error", context=("fatal",))) is None
    assert trigger_prefilter_reason(_cand("distinctive failure signature")) is None


def test_context_matches_trajectory_domain_label() -> None:
    # #677: golden rules use domain labels (e.g. "devops") as context; a
    # context item equal to the trajectory's domain must satisfy it even when
    # the domain word is not present in the trajectory text.
    cand = _cand("no matches for kind", context=("devops",))
    traj = Trajectory(
        id="T-domain", timestamp="t", task="Deploy custom resource to Kubernetes cluster",
        steps=(Step(1, "bash", error="no matches for kind CustomResourceDefinition"),),
        success=False, failure_class="k8s/deploy/crd-not-found", domain="devops",
    )
    assert rule_matches(cand, traj)


def test_context_domain_label_does_not_match_other_domain() -> None:
    cand = _cand("no matches for kind", context=("devops",))
    traj = Trajectory(
        id="T-domain2", timestamp="t", task="Fetch data",
        steps=(Step(1, "bash", error="no matches for kind X"),),
        success=False, failure_class="api/x", domain="research",
    )
    assert not rule_matches(cand, traj)
