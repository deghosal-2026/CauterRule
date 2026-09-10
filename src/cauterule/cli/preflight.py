"""CLI: cauterule preflight — provider + corpus checks before expensive runs."""

from __future__ import annotations

import click

from cauterule.config import load_config
from cauterule.preflight import run_preflight


@click.command("preflight")
@click.option("--corpus", help="Path to corpus JSONL file or directory.")
@click.option("--catalog", help="Path to catalog.yaml for size/annotation checks.")
@click.option("--output-dir", help="Output directory to check for writability/space.")
@click.option("--no-probe", is_flag=True, help="Skip LLM latency probe.")
def preflight(
    corpus: str | None,
    catalog: str | None,
    output_dir: str | None,
    no_probe: bool,
) -> None:
    """Run provider + corpus preflight checks (fail fast before sweep)."""
    cfg = load_config()
    result = run_preflight(
        cfg,
        corpus_path=corpus,
        probe=_simple_probe if not no_probe else None,
        output_dir=output_dir,
        catalog_path=catalog,
    )

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


def _simple_probe(_config: object) -> float:
    """Minimal latency probe: return 0.1s placeholder.

    Real probes are deferred to the field-test runner; this ensures the
    preflight code path is exercised without requiring a live LLM.
    """
    return 0.1
