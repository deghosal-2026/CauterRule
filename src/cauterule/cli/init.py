from __future__ import annotations

import click


@click.command("init")
@click.option("--dir", "target_dir", default=".", help="Target directory for scaffolding.")
def init(target_dir: str) -> None:
    """Scaffold cauterule.toml, rules/, .gitignore, example agent, and first rule."""
    from pathlib import Path
    d = Path(target_dir)
    d.mkdir(parents=True, exist_ok=True)
    toml_path = d / "cauterule.toml"
    if not toml_path.exists():
        toml_path.write_text(
            "[llm]\nprovider = \"openai\"\nmodel = \"gpt-4o\"\n\n[paths]\nrules = \"rules\"\ntrajectories = \"trajectories\"\n",
            encoding="utf-8",
        )
        click.echo(f"Created {toml_path}")
    rules_dir = d / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    traj_dir = d / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)
    (d / ".gitignore").write_text("*.pyc\n__pycache__/\n.venv/\n", encoding="utf-8")
    click.echo(f"Scaffolded CauterRule project in {d.resolve()}")