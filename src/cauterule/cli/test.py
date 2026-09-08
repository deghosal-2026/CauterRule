from __future__ import annotations

import click
from pathlib import Path

from cauterule.serialization.trajectory_jsonl import load_trajectories
from cauterule.replay.report import build_evidence_report
from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import RuleDo, RuleWhen


@click.command("test")
@click.argument("rule")
@click.option("--ci", is_flag=True, help="Output JUnit XML.")
def test(rule: str, ci: bool) -> None:
    """Replay-test a candidate rule against historical failures."""
    from cauterule.store.manager import StoreManager
    store = StoreManager()
    candidate = store.get_rule(rule)
    if candidate:
        cand = CandidateRule(
            when=candidate.when,
            do=candidate.do,
            confidence=candidate.confidence,
            reasoning=candidate.provenance.source_trajectory,
        )
    else:
        click.echo(f"Rule {rule!r} not found in store.")
        return

    traj_path = Path("trajectories")
    if traj_path.is_dir():
        trajectories = []
        for f in traj_path.glob("*.jsonl"):
            trajectories.extend(load_trajectories(f))
    elif traj_path.with_suffix(".jsonl").is_file():
        trajectories = list(load_trajectories(traj_path.with_suffix(".jsonl")))
    else:
        trajectories = []

    if not trajectories:
        click.echo("No trajectories found for replay testing.")
        return

    report_ = build_evidence_report(cand, trajectories)
    click.echo(f"Testing rule: {rule}")
    click.echo(f"  Failures prevented: {len(report_.failures_prevented)}")
    click.echo(f"  Successes broken: {len(report_.successes_broken)}")
    click.echo(f"  Precision: {report_.precision:.2f}")
    click.echo(f"  Recall: {report_.recall:.2f}")
    click.echo(f"  Verdict: {report_.verdict}")
    if report_.verdict == "inconclusive" and report_.inconclusive_reason:
        click.echo(f"  Inconclusive reason: {report_.inconclusive_reason}")
    if report_.failures_prevented:
        click.echo(f"  Prevented: {', '.join(report_.failures_prevented)}")
    if report_.successes_broken:
        click.echo(f"  Broken: {', '.join(report_.successes_broken)}")