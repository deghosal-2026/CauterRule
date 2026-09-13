from typing import Any, cast

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen
from cauterule.models.trajectory import Step, Trajectory
from cauterule.replay.simulator import simulate


def _cand(trigger: str, context: tuple[str, ...] = ()) -> CandidateRule:
    return CandidateRule(
        when=RuleWhen(trigger=trigger, context=context), do=RuleDo(directive="d"), confidence=0.9
    )


def _traj(task: str, success: bool, error: str = "") -> Trajectory:
    steps = (Step(1, "bash", error=error),) if error else ()
    return Trajectory(id="T-001", timestamp="t", task=task, steps=steps, success=success)


def test_prevented() -> None:
    cand = _cand("git push")
    traj = _traj("git push fails", success=False, error="non-fast-forward")
    assert simulate(cand, traj) == "prevented"


def test_no_effect() -> None:
    cand = _cand("docker")
    traj = _traj("git push", success=False, error="non-fast-forward")
    assert simulate(cand, traj) == "no_effect"


def test_broken() -> None:
    cand = _cand("git push")
    traj = _traj("git push succeeds", success=True)
    assert simulate(cand, traj) == "broken"


def test_near_miss() -> None:
    cand = _cand("git push", context=("shared branch", "multiple contributors"))
    traj = _traj("git push on shared branch", success=False, error="non-fast-forward")
    assert simulate(cand, traj) == "near_miss"


def test_simulate_forwards_threshold_to_near_miss() -> None:
    # #764: a partial-context trajectory scoring below a stricter threshold is
    # not a match at all; the near-miss path must not use the hard-coded 0.60.
    from cauterule.replay.matcher import match_score

    cand = _cand("artifact upload failure", context=("artifact", "nonexistent-xyz"))
    traj = _traj("artifact upload", success=False)
    assert 0.6 <= match_score(cand, traj) < 0.7  # precondition
    assert simulate(cand, traj) == "near_miss"
    assert simulate(cand, traj, threshold=0.7) == "no_effect"


def _success_traj(task: str, failure_class: str | None) -> Trajectory:
    return Trajectory(
        id="T-002", timestamp="t", task=task, steps=(), success=True, failure_class=failure_class
    )


def test_recovery_exclusion_unrecoverable_is_broken() -> None:
    # #616: "recover" substring inside "unrecoverable" must not count as recovery.
    cand = _cand("git push")
    traj = _success_traj("git push origin main", "unrecoverable state corruption")
    assert simulate(cand, traj) == "broken"


def test_recovery_exclusion_exhausted_retry_is_broken() -> None:
    # #616: exhausted retries are the opposite of recovery.
    cand = _cand("git push")
    traj = _success_traj("git push origin main", "retry budget exhausted")
    assert simulate(cand, traj) == "broken"


def test_recovery_exclusion_template_is_broken() -> None:
    # #616: "temp" substring inside "template" must not count as recovery.
    cand = _cand("render")
    traj = _success_traj("render template", "template render error")
    assert simulate(cand, traj) == "broken"


def test_recovery_exclusion_nearest_is_broken() -> None:
    # #616: "near" substring inside "nearest" must not count as recovery.
    cand = _cand("replica")
    traj = _success_traj("replica unavailable", "nearest replica unavailable")
    assert simulate(cand, traj) == "broken"


def test_recovery_exclusion_nearmiss_label_not_circular() -> None:
    # #616: "nearmiss/*" category label must not match via "near" substring.
    cand = _cand("git push")
    traj = _success_traj("git push origin main", "nearmiss/coding")
    assert simulate(cand, traj) == "broken"


def test_recovery_exclusion_genuine_recovery_still_near_miss() -> None:
    # #616: exact recovery tokens still classify as near_miss.
    cand = _cand("git push")
    for fc in (
        "temporary",
        "git/push/temporary",
        "retry",
        "ci/retry",
        "recovered",
        "flaky",
        "test/flaky",
        "intermittent",
    ):
        traj = _success_traj("git push origin main", fc)
        assert simulate(cand, traj) == "near_miss", fc


def test_recovery_case_and_whitespace_insensitive() -> None:
    # Review: normalization covers case/whitespace variants.
    from cauterule.replay.simulator import is_recovery_class

    assert is_recovery_class(" Temporary ") is True
    assert is_recovery_class("CI/Retry") is True
    assert is_recovery_class("") is False
    assert is_recovery_class(None) is False


def test_recovery_non_string_input_safe() -> None:
    # Review: unvalidated JSONL may carry non-string failure_class.
    from cauterule.replay.simulator import is_recovery_class

    assert is_recovery_class(cast(Any, 123)) is False
    assert is_recovery_class(cast(Any, ["retry"])) is False


def test_recovery_bare_nearmiss_token_not_recovery() -> None:
    # Review: bare "nearmiss" is a category label, not a recovery signal.
    cand = _cand("git push")
    traj = _success_traj("git push origin main", "nearmiss")
    assert simulate(cand, traj) == "broken"


def test_failure_point_only_without_class() -> None:
    # Review: success + failure_point but no failure_class → broken.
    cand = _cand("git push")
    traj = Trajectory(
        id="T-003",
        timestamp="t",
        task="git push origin main",
        steps=(),
        success=True,
        failure_point="step_1",
    )
    assert simulate(cand, traj) == "broken"


def test_domain_mismatch_not_counted_as_prevented() -> None:
    # #487: trigger says "docker" but trajectory is a git failure — domain mismatch.
    cand = _cand("when docker build fails")
    traj = Trajectory(
        id="T-dm",
        timestamp="t",
        task="git push fails",
        steps=(Step(1, "bash", error="non-fast-forward"),),
        success=False,
        failure_class="git/push/non-fast-forward",
    )
    assert simulate(cand, traj) == "no_effect"


def test_domain_not_mismatched_when_same() -> None:
    # #487: same domain — prevented as usual.
    cand = _cand("when docker build fails with package not found")
    traj = Trajectory(
        id="T-dms",
        timestamp="t",
        task="docker build fails",
        steps=(Step(1, "bash", error="Package 'x' not found"),),
        success=False,
        failure_class="docker/build/package-not-found",
    )
    assert simulate(cand, traj) == "prevented"


# ---------------------------------------------------------------------------
# #723 — spurious 'broken' successes
# ---------------------------------------------------------------------------


def test_cross_domain_success_not_broken() -> None:
    # A git rule must not be "broken" by a docker success that shares a token.
    from cauterule.replay.matcher import match_score

    cand = _cand("docker build failed")
    traj = Trajectory(
        id="S-git",
        timestamp="t",
        task="git push failed docker build step",
        steps=(),
        success=True,
        failure_class="git/push",
    )
    assert match_score(cand, traj) >= 0.6  # precondition: it does match
    assert simulate(cand, traj) == "no_effect"


def test_borderline_success_not_broken() -> None:
    # Matches just above threshold but below threshold + margin -> no_effect.
    from cauterule.replay.matcher import match_score

    cand = _cand("artifact upload failure")
    traj = Trajectory(
        id="S-up", timestamp="t", task="artifact upload", steps=(), success=True
    )
    assert 0.6 <= match_score(cand, traj) < 0.7  # precondition
    assert simulate(cand, traj) == "no_effect"


def test_high_confidence_success_still_broken() -> None:
    cand = _cand("artifact upload failure")
    traj = Trajectory(
        id="S-up2",
        timestamp="t",
        task="artifact upload failure detected",
        steps=(),
        success=True,
    )
    assert simulate(cand, traj) == "broken"


def test_nm_retry_success_is_near_miss() -> None:
    cand = _cand("deploy timed out")
    traj = Trajectory(
        id="NM-024-deploy-timeout-retry",
        timestamp="t",
        task="deploy timed out",
        steps=(),
        success=True,
        failure_class="deploy/timeout",
    )
    assert simulate(cand, traj) == "near_miss"


def test_nm_rollback_success_is_near_miss() -> None:
    cand = _cand("kubectl rollout failed")
    traj = Trajectory(
        id="NM-039-kubectl-rollback",
        timestamp="t",
        task="kubectl rollout failed",
        steps=(),
        success=True,
        failure_class="k8s/deploy",
    )
    assert simulate(cand, traj) == "near_miss"


def test_exhausted_retry_task_still_broken() -> None:
    # Guard against over-broadening: retry tokens in failure_class were the #616
    # trap; a genuine success with no recovery id/task stays "broken".
    cand = _cand("git push")
    traj = _success_traj("git push origin main", "retry budget exhausted")
    assert simulate(cand, traj) == "broken"
