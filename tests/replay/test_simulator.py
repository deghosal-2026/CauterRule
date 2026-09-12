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
