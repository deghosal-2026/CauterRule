"""Evidence report builder."""

from __future__ import annotations

from cauterule.models.candidate import CandidateRule
from cauterule.models.evidence import EvidenceReport
from cauterule.models.trajectory import Trajectory
from cauterule.replay.attribution import attribute_inconclusive
from cauterule.replay.scorer import compute_scores
from cauterule.replay.simulator import simulate


def build_evidence_report(
    candidate: CandidateRule,
    trajectories: list[Trajectory],
    threshold: float | None = None,
) -> EvidenceReport:
    """Build an :class:`EvidenceReport` for *candidate* against *trajectories*.

    Args:
        candidate: The candidate rule.
        trajectories: Reference trajectories to test against.
        threshold: Matcher threshold. If None, uses DEFAULT_THRESHOLD (0.6).
            Use :func:`threshold_for_corpus` from matcher.py for corpus-aware tuning.
    """
    prevented: list[str] = []
    broken: list[str] = []
    near_misses: list[str] = []
    trace: list[dict[str, str]] = []

    total_failures = sum(1 for t in trajectories if not t.success)

    kwargs = {}
    if threshold is not None:
        kwargs["threshold"] = threshold

    for traj in trajectories:
        outcome = simulate(candidate, traj, **kwargs)
        trace.append({"trajectory_id": traj.id, "outcome": outcome})
        if outcome == "prevented":
            prevented.append(traj.id)
        elif outcome == "broken":
            broken.append(traj.id)
        elif outcome == "near_miss":
            near_misses.append(traj.id)

    precision, recall, verdict = compute_scores(
        prevented=len(prevented),
        broken=len(broken),
        total_failures=total_failures,
        total_successes=len(trajectories) - total_failures,
    )

    # If insufficient history, override verdict to inconclusive (handled elsewhere too)
    if len(trajectories) < 3:
        verdict = "inconclusive"

    report = EvidenceReport(
        failures_prevented=tuple(prevented),
        successes_broken=tuple(broken),
        near_misses=tuple(near_misses),
        precision=precision,
        recall=recall,
        verdict=verdict,  # type: ignore[arg-type]
        replay_trace=tuple(trace),
    )
    if report.verdict == "inconclusive":
        reason = attribute_inconclusive(candidate, trajectories, report)
        object.__setattr__(report, "inconclusive_reason", reason)
    return report
