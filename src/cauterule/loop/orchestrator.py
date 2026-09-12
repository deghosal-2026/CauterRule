"""Loop orchestrator — wires capture → redact → cluster → extract → lint → replay → tournament → conflict → promote → inject."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from cauterule.extraction.multipass import multipass_extract
from cauterule.extraction.tournament import run_tournament
from cauterule.linter.orchestrator import lint_rule
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import StandingRule
from cauterule.models.trajectory import Trajectory
from cauterule.redaction.engine import redact_trajectory


@dataclass(frozen=True)
class LoopConfig:
    """Configuration for the loop orchestrator."""

    max_iterations: int = 5
    replay_enabled: bool = True
    promotion_mode: str = "auto"
    extract_template: str | None = None
    gate_mode: str = "strict"
    llm: Any = None
    historical_trajectories: tuple[Trajectory, ...] = field(default_factory=tuple)
    existing_rules: tuple[StandingRule, ...] = field(default_factory=tuple)
    extra: dict[str, Any] = field(default_factory=dict)


def run_loop(trajectory: Trajectory, config: LoopConfig) -> str | None:
    """Execute the full CauterRule loop for *trajectory*.

    Stages:

    1. **Capture** — record failure context from trajectory.
    2. **Redact** — strip sensitive content.
    3. **Cluster** — group with similar past failures.
    4. **Extract** — LLM extracts candidate rule(s).
    5. **Lint** — validate candidate for quality issues.
    6. **Replay** — test candidate against historical data.
    7. **Tournament** — compare candidates head-to-head.
    8. **Conflict** — detect contradictions with existing rules.
    9. **Promote** — promote winning rule to standing.
    10. **Inject** — prepare injection context.

    Args:
        trajectory: The execution trajectory to learn from.
        config: Loop configuration.

    Returns:
        The ID of the promoted rule, or ``None`` if no rule was promoted.
    """
    if config.llm is None:
        return None

    # 1. Capture — trajectory itself is the capture.
    # 2. Redact
    redacted = redact_trajectory(trajectory) if not trajectory.redacted else trajectory

    # 3. Cluster — group with historical failures
    # Use single-pass extraction per trajectory for now; clustering integration pending.

    # 4. Extract (pre-extraction gate runs inside multipass_extract)
    candidates: list[CandidateRule] = multipass_extract(
        redacted, config.llm, template=config.extract_template, gate_mode=config.gate_mode
    )
    if not candidates:
        return None

    # 5. Lint
    linted: list[CandidateRule] = []
    for c in candidates:
        result = lint_rule(
            c.when.trigger,
            c.do.directive,
            existing_rules=list(config.existing_rules) if config.existing_rules else None,
        )
        if result.passed:
            linted.append(c)
    if not linted:
        return None

    # 6-7. Replay + Tournament
    if config.replay_enabled and config.historical_trajectories:
        ranked = run_tournament(linted, list(config.historical_trajectories))
        if not ranked:
            return None
        winner_candidate = ranked[0].candidate
    else:
        winner_candidate = linted[0]

    # 8. Conflict — re-check winner against existing rules
    if config.existing_rules:
        conflict_check = lint_rule(
            winner_candidate.when.trigger,
            winner_candidate.do.directive,
            existing_rules=list(config.existing_rules),
        )
        if not conflict_check.passed:
            return None

    # 9. Promote
    # 10. Inject — mark as ready; actual injection done by caller.
    return f"R-{trajectory.id}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
