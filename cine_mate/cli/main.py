"""
CineMate CLI — Main Entry Point
Provides `cinemate create`, `cinemate loop`, `cinemate status` commands.

Default: Mock mode (no API key required for MVP).
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from cine_mate.cli.commands import (
    cmd_create,
    cmd_loop,
    cmd_status,
)


@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="cinemate")
@click.option("--db-path", default=None, help="Path to CineMate SQLite database.")
@click.option("--data-dir", default=None, help="Path to CineMate data directory (skills, CAS).")
@click.option("--mock/--no-mock", default=True, help="Use mock provider (default: True for MVP).")
@click.pass_context
def cli(ctx, db_path: Optional[str], data_dir: Optional[str], mock: bool):
    """CineMate — AI Video Production OS.

    Create videos from natural language descriptions.
    Default mode uses Mock providers (no API key needed).
    """
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = db_path
    ctx.obj["data_dir"] = data_dir
    ctx.obj["mock"] = mock

    # If no subcommand, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("prompt")
@click.option("--style", default=None, help="Apply a skill/style (e.g., cyberpunk).")
@click.option("--parent-run", default=None, help="Fork from an existing run ID.")
@click.pass_context
def create(ctx, prompt: str, style: Optional[str], parent_run: Optional[str]):
    """Create a video from a natural language description.

    Example:
        cinemate create "A cyberpunk city at night with neon lights"
        cinemate create "Product ad for headphones" --style workflow-short-ad
    """
    db_path = ctx.obj.get("db_path")
    data_dir = ctx.obj.get("data_dir")
    mock = ctx.obj.get("mock", True)

    asyncio.run(cmd_create(
        prompt=prompt,
        style=style,
        parent_run_id=parent_run,
        db_path=db_path,
        data_dir=data_dir,
        use_mock=mock,
    ))


@cli.command()
@click.pass_context
def loop(ctx):
    """Start interactive continuous conversation mode.

    In loop mode, you can have a back-and-forth conversation with the
    Director Agent to refine your video production plan.

    Type 'exit' or 'quit' to leave.
    """
    db_path = ctx.obj.get("db_path")
    data_dir = ctx.obj.get("data_dir")
    mock = ctx.obj.get("mock", True)

    asyncio.run(cmd_loop(
        db_path=db_path,
        data_dir=data_dir,
        use_mock=mock,
    ))


@cli.command()
@click.pass_context
def status(ctx):
    """Show CineMate system status."""
    db_path = ctx.obj.get("db_path")
    data_dir = ctx.obj.get("data_dir")

    asyncio.run(cmd_status(
        db_path=db_path,
        data_dir=data_dir,
    ))


def main():
    """CLI entry point (called from pyproject.toml script)."""
    cli(standalone_mode=False)


if __name__ == "__main__":
    main()
