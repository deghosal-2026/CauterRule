"""EvidenceReport data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Verdict = Literal["pass", "fail", "inconclusive"]
_VALID_VERDICTS: frozenset[str] = frozenset({"pass", "fail", "inconclusive"})


@dataclass(frozen=True)
class EvidenceReport:
    """Report from replay-testing a candidate against history."""

    failures_prevented: tuple[str, ...] = field(default_factory=tuple)
    successes_broken: tuple[str, ...] = field(default_factory=tuple)
    near_misses: tuple[str, ...] = field(default_factory=tuple)
    precision: float = 0.0
    recall: float = 0.0
    verdict: Verdict = "inconclusive"
    replay_trace: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not 0.0 <= self.precision <= 1.0:
            raise ValueError(f"precision must be in [0.0, 1.0], got {self.precision}")
        if not 0.0 <= self.recall <= 1.0:
            raise ValueError(f"recall must be in [0.0, 1.0], got {self.recall}")
        if self.verdict not in _VALID_VERDICTS:
            raise ValueError(f"verdict must be one of {_VALID_VERDICTS}, got {self.verdict}")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict."""
        return {
            "failures_prevented": list(self.failures_prevented),
            "successes_broken": list(self.successes_broken),
            "near_misses": list(self.near_misses),
            "precision": self.precision,
            "recall": self.recall,
            "verdict": self.verdict,
            "replay_trace": list(self.replay_trace),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceReport:
        """Create from a dict produced by :meth:`to_dict`."""
        return cls(
            failures_prevented=tuple(data.get("failures_prevented", [])),
            successes_broken=tuple(data.get("successes_broken", [])),
            near_misses=tuple(data.get("near_misses", [])),
            precision=float(data.get("precision", 0.0)),
            recall=float(data.get("recall", 0.0)),
            verdict=data.get("verdict", "inconclusive"),
            replay_trace=tuple(data.get("replay_trace", [])),
        )
