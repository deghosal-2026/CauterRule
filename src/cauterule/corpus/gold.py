"""Gold rule families — curated trajectory-rule associations for evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field

from cauterule.models.rule import StandingRule
from cauterule.models.trajectory import Trajectory
from cauterule.serialization.trajectory_jsonl import load_trajectories


@dataclass(frozen=True)
class GoldRuleFamily:
    """A gold-standard scenario with trajectories and acceptable rules."""

    scenario_id: str
    trajectories: list[Trajectory] = field(default_factory=list)
    acceptable_rules: list[StandingRule] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.scenario_id or not self.scenario_id.strip():
            raise ValueError("scenario_id must be non-blank")


def load_gold_families(path: str) -> list[GoldRuleFamily]:
    """Load gold rule families from a directory of JSONL files.

    Each JSONL file in *path* is loaded as a single gold family. The filename
    (without extension) becomes the ``scenario_id``.

    Args:
        path: Directory path containing ``*.jsonl`` files, one per family.

    Returns:
        List of :class:`GoldRuleFamily` instances.
    """
    from pathlib import Path

    p = Path(path)
    if not p.is_dir():
        raise ValueError(f"Path must be a directory: {path}")

    families: list[GoldRuleFamily] = []
    for fpath in sorted(p.glob("*.jsonl")):
        trajectories = list(load_trajectories(fpath))
        scenario_id = fpath.stem
        families.append(GoldRuleFamily(scenario_id=scenario_id, trajectories=trajectories))
    return families
