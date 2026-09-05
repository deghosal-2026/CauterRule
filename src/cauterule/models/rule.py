"""StandingRule data model.

Defines the structured *when X, do Y* rule with provenance and lifecycle
fields per ``docs/design/standing-rule-format-design.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Status = Literal["active", "retired", "superseded"]
_VALID_STATUSES: frozenset[str] = frozenset({"active", "retired", "superseded"})


def _require_nonblank(value: str, name: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{name} must be a non-blank string")


def _require_confidence(value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"confidence must be in [0.0, 1.0], got {value}")


@dataclass(frozen=True)
class RuleWhen:
    """Condition that triggers a rule."""

    trigger: str
    context: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_nonblank(self.trigger, "when.trigger")
        for c in self.context:
            _require_nonblank(c, "when.context item")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict."""
        d: dict[str, Any] = {"trigger": self.trigger}
        if self.context:
            d["context"] = list(self.context)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RuleWhen:
        """Create from a dict produced by :meth:`to_dict`."""
        trigger = data.get("trigger", "")
        context = tuple(data.get("context", []))
        return cls(trigger=trigger, context=context)


@dataclass(frozen=True)
class RuleDo:
    """Directive to follow when the rule fires."""

    directive: str
    because: str | None = None

    def __post_init__(self) -> None:
        _require_nonblank(self.directive, "do.directive")
        if self.because is not None and not self.because.strip():
            raise ValueError("do.because must be non-blank if provided")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict."""
        d: dict[str, Any] = {"directive": self.directive}
        if self.because is not None:
            d["because"] = self.because
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RuleDo:
        """Create from a dict produced by :meth:`to_dict`."""
        return cls(directive=data.get("directive", ""), because=data.get("because"))


@dataclass(frozen=True)
class ReplayEvidence:
    """Evidence from historical replay testing."""

    failures_prevented: tuple[str, ...] = field(default_factory=tuple)
    successes_broken: tuple[str, ...] = field(default_factory=tuple)
    precision: float = 0.0
    recall: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.precision <= 1.0:
            raise ValueError(f"precision must be in [0.0, 1.0], got {self.precision}")
        if not 0.0 <= self.recall <= 1.0:
            raise ValueError(f"recall must be in [0.0, 1.0], got {self.recall}")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict."""
        return {
            "failures_prevented": list(self.failures_prevented),
            "successes_broken": list(self.successes_broken),
            "precision": self.precision,
            "recall": self.recall,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReplayEvidence:
        """Create from a dict produced by :meth:`to_dict`."""
        return cls(
            failures_prevented=tuple(data.get("failures_prevented", [])),
            successes_broken=tuple(data.get("successes_broken", [])),
            precision=float(data.get("precision", 0.0)),
            recall=float(data.get("recall", 0.0)),
        )


@dataclass(frozen=True)
class Provenance:
    """Full provenance chain for a promoted rule."""

    source_trajectory: str
    extracted_by: str
    extract_timestamp: str
    extraction_pass: int
    draft_tournament_rank: int | None = None
    replay_evidence: ReplayEvidence | None = None
    promotion_commit: str | None = None
    promotion_mode: str | None = None

    def __post_init__(self) -> None:
        _require_nonblank(self.source_trajectory, "provenance.source_trajectory")
        _require_nonblank(self.extracted_by, "provenance.extracted_by")
        _require_nonblank(self.extract_timestamp, "provenance.extract_timestamp")
        if self.extraction_pass < 1:
            raise ValueError(f"extraction_pass must be >=1, got {self.extraction_pass}")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict."""
        d: dict[str, Any] = {
            "source_trajectory": self.source_trajectory,
            "extracted_by": self.extracted_by,
            "extract_timestamp": self.extract_timestamp,
            "extraction_pass": self.extraction_pass,
        }
        if self.draft_tournament_rank is not None:
            d["draft_tournament_rank"] = self.draft_tournament_rank
        if self.replay_evidence is not None:
            d["replay_evidence"] = self.replay_evidence.to_dict()
        if self.promotion_commit is not None:
            d["promotion_commit"] = self.promotion_commit
        if self.promotion_mode is not None:
            d["promotion_mode"] = self.promotion_mode
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Provenance:
        """Create from a dict produced by :meth:`to_dict`."""
        ev = data.get("replay_evidence")
        return cls(
            source_trajectory=data.get("source_trajectory", ""),
            extracted_by=data.get("extracted_by", ""),
            extract_timestamp=data.get("extract_timestamp", ""),
            extraction_pass=int(data.get("extraction_pass", 1)),
            draft_tournament_rank=data.get("draft_tournament_rank"),
            replay_evidence=ReplayEvidence.from_dict(ev) if isinstance(ev, dict) else None,
            promotion_commit=data.get("promotion_commit"),
            promotion_mode=data.get("promotion_mode"),
        )


@dataclass(frozen=True)
class StandingRule:
    """A promoted standing rule with full lifecycle metadata."""

    id: str
    when: RuleWhen
    do: RuleDo
    confidence: float
    provenance: Provenance
    status: Status
    promoted_at: str
    hit_count: int = 0
    last_match: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    taxonomy: str | None = None
    template: str | None = None
    pack: str | None = None

    def __post_init__(self) -> None:
        _require_nonblank(self.id, "id")
        _require_confidence(self.confidence)
        _require_nonblank(self.promoted_at, "promoted_at")
        if self.status not in _VALID_STATUSES:
            raise ValueError(f"status must be one of {_VALID_STATUSES}, got {self.status}")
        if self.hit_count < 0:
            raise ValueError(f"hit_count must be >=0, got {self.hit_count}")
        for t in self.tags:
            _require_nonblank(t, "tags item")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict for YAML/JSON persistence."""
        d: dict[str, Any] = {
            "id": self.id,
            "when": self.when.to_dict(),
            "do": self.do.to_dict(),
            "confidence": self.confidence,
            "provenance": self.provenance.to_dict(),
            "status": self.status,
            "promoted_at": self.promoted_at,
            "hit_count": self.hit_count,
        }
        if self.last_match is not None:
            d["last_match"] = self.last_match
        if self.tags:
            d["tags"] = list(self.tags)
        if self.taxonomy is not None:
            d["taxonomy"] = self.taxonomy
        if self.template is not None:
            d["template"] = self.template
        if self.pack is not None:
            d["pack"] = self.pack
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StandingRule:
        """Create from a dict produced by :meth:`to_dict`."""
        return cls(
            id=data.get("id", ""),
            when=RuleWhen.from_dict(data.get("when", {})),
            do=RuleDo.from_dict(data.get("do", {})),
            confidence=float(data.get("confidence", 0.0)),
            provenance=Provenance.from_dict(data.get("provenance", {})),
            status=data.get("status", "active"),
            promoted_at=data.get("promoted_at", ""),
            hit_count=int(data.get("hit_count", 0)),
            last_match=data.get("last_match"),
            tags=tuple(data.get("tags", [])),
            taxonomy=data.get("taxonomy"),
            template=data.get("template"),
            pack=data.get("pack"),
        )
