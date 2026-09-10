"""Pre-extraction null-hypothesis gate.

Deterministic failure-signal check that runs *before* LLM invocation.
If the trajectory contains no unhandled exit code, no failed assertion,
and no schema violation in the raw telemetry, the gate drops the
candidate immediately without calling the LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from cauterule.models.trajectory import Step, Trajectory

GateMode = Literal["strict", "relaxed"]
SILENCE_REASON_NO_FAILURE = "no_failure_signal"
SILENCE_REASON_NEARMISS = "nearmiss_recovery_succeeded"
SILENCE_REASON_NO_SIGNAL_AND_FAILURE = "failure_without_signal"
_SILENCE_REASONS = frozenset(
    {SILENCE_REASON_NO_FAILURE, SILENCE_REASON_NEARMISS, SILENCE_REASON_NO_SIGNAL_AND_FAILURE}
)


@dataclass(frozen=True)
class GateResult:
    """Result of running the pre-extraction gate on a trajectory."""

    should_extract: bool
    reason: str | None = None
    failure_signals: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_silence(self) -> bool:
        return not self.should_extract and self.reason in _SILENCE_REASONS


def _step_shows_success(step: Step) -> bool:
    """Return True if *step* indicates success by output or state (#518).

    A non-zero exit_code is always a failure signal regardless of output
    or absence of assertions (code-review).  ``exit_code == 0`` counts as
    success ONLY when no assertion or schema violation is present.
    """
    if step.output and step.output.strip():
        return True
    state = step.state or {}
    exit_code = state.get("exit_code")
    if exit_code is not None:
        try:
            if int(exit_code) != 0:
                return False
            # exit_code 0 — still a failure if assertion/schema violated
            if state.get("assertion_failed") or state.get("schema_violation"):
                return False
            return True
        except (ValueError, TypeError):
            pass
    if state.get("assertion_failed") or state.get("schema_violation"):
        return False
    if step.error and step.error.strip():
        return False
    return True


def _detect_nearmiss_recovery(trajectory: Trajectory) -> bool:
    """Detect a near-miss pattern: first step fails, later step succeeds.

    A near-miss is a trajectory where:
    - At least one early step has an error or failure signal
    - A later step succeeds (has output, exit_code 0, or no error)
    - Overall trajectory success = True (retry/recovery succeeded)

    These should not produce rules — the failure was transient.

    State-only recovery is recognized (#518): a step whose retry succeeds
    via state change (``exit_code: 0``, no assertion/schema violation)
    with empty output still counts as recovery.
    """
    if not trajectory.success:
        return False
    if len(trajectory.steps) < 2:
        return False

    has_early_error = False
    has_later_success = False

    for i, step in enumerate(trajectory.steps):
        if step.error and step.error.strip():
            has_early_error = True
        elif has_early_error and _step_shows_success(step):
            has_later_success = True

    return has_early_error and has_later_success


def _detect_failure_signals(trajectory: Trajectory) -> list[str]:
    """Scan raw step telemetry for failure evidence.

    Returns a list of human-readable signal descriptions (empty = no signal).
    """
    signals: list[str] = []

    # 1. Non-zero exit codes from step state
    for step in trajectory.steps:
        state = step.state or {}
        exit_code = state.get("exit_code")
        if exit_code is not None:
            try:
                code = int(exit_code)
                if code != 0:
                    signals.append(f"step {step.step_number}: non-zero exit code {code}")
            except (ValueError, TypeError):
                pass

    # 2. Failed assertions
    for step in trajectory.steps:
        state = step.state or {}
        assertion = state.get("assertion_failed")
        if assertion:
            signals.append(f"step {step.step_number}: assertion failed ({assertion})")

    # 3. Schema violations
    for step in trajectory.steps:
        state = step.state or {}
        schema = state.get("schema_violation")
        if schema:
            signals.append(f"step {step.step_number}: schema violation ({schema})")

    # 4. Step error content (non-empty error = something went wrong)
    for step in trajectory.steps:
        if step.error and step.error.strip():
            signals.append(f"step {step.step_number}: error")

    # 5. Trajectory-level failure indicators
    if trajectory.failure_point:
        signals.append(f"failure_point: {trajectory.failure_point}")
    if trajectory.failure_class and trajectory.failure_class.strip():
        signals.append(f"failure_class: {trajectory.failure_class}")

    return signals


def run_gate(
    trajectory: Trajectory,
    mode: GateMode = "strict",
) -> GateResult:
    """Run the pre-extraction gate on *trajectory*.

    Args:
        trajectory: The execution trajectory to check.
        mode:
            - ``strict``: drop if no failure signal is present.
            - ``relaxed``: always proceed to extraction (gate does not block).

    Returns:
        ``GateResult`` with ``should_extract`` and optional reason.
    """
    signals = _detect_failure_signals(trajectory)

    if mode == "relaxed":
        return GateResult(should_extract=True, failure_signals=tuple(signals))

    if not signals:
        reason = (
            SILENCE_REASON_NO_SIGNAL_AND_FAILURE
            if not trajectory.success
            else SILENCE_REASON_NO_FAILURE
        )
        return GateResult(
            should_extract=False,
            reason=reason,
            failure_signals=(),
        )

    # Nearmiss detection: if trajectory has failure signals but overall
    # success=True AND shows recovery pattern (early error, later success),
    # drop it — the failure was transient and self-resolved.
    if trajectory.success and _detect_nearmiss_recovery(trajectory):
        return GateResult(
            should_extract=False,
            reason=SILENCE_REASON_NEARMISS,
            failure_signals=tuple(signals),
        )

    return GateResult(should_extract=True, failure_signals=tuple(signals))
