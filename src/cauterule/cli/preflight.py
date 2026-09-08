"""CLI: cauterule preflight — provider + corpus checks before expensive runs."""

from __future__ import annotations

import click

from cauterule.config import load_config
from cauterule.preflight import run_preflight


@click.command("preflight")
@click.option("--corpus", help="Path to corpus JSONL file or directory.")
@click.option(
    "--cost-per-request",
    default=0.01,
    show_default=True,
    help="Cost per LLM request in USD for estimate.",
)
def preflight(corpus: str | None, cost_per_request: float) -> None:
    """Run provider + corpus preflight checks (fail fast before sweep)."""
    cfg = load_config()
    result = run_preflight(cfg, corpus_path=corpus, cost_per_request_usd=cost_per_request)

    for check in result.provider_checks:
        status = "PASS" if check.passed else "FAIL"
        msg = f"  [{status}] {check.name}: {check.message}"
        if check.latency_s is not None:
            msg += f" ({check.latency_s:.1f}s)"
        click.echo(msg)

    for check in result.corpus_checks:
        status = "PASS" if check.passed else "FAIL"
        click.echo(f"  [{status}] {check.name}: {check.message}")

    if result.cost_estimate_usd is not None:
        click.echo(f"Estimated cost: ${result.cost_estimate_usd:.2f}")

    if result.passed:
        click.echo("Preflight: PASS — ready to run.")
    else:
        click.echo("Preflight: FAIL — fix issues before running.")
        raise click.ClickException("Preflight checks failed")  # noqa: TRY003
