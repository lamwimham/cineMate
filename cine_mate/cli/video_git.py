"""
CineMate CLI — Video Git Commands
Provides `cinemate history` and `cinemate diff` commands.
"""

import asyncio
from pathlib import Path
from typing import Optional

import click

from cine_mate.core.store import Store


# ── Terminal formatting helpers ───────────────────────────────────────────

# Status emoji map
STATUS_EMOJI = {
    "completed": "✅",
    "failed": "❌",
    "running": "🔄",
    "pending": "⏳",
    "paused": "⏸️",
    "cancelled": "🚫",
}


def _color_status(status: str) -> str:
    """Color-code status for terminal output."""
    colors = {
        "completed": "\033[92m",  # green
        "failed": "\033[91m",     # red
        "running": "\033[93m",    # yellow
        "pending": "\033[90m",    # gray
        "cancelled": "\033[90m",
    }
    reset = "\033[0m"
    color = colors.get(status, "")
    emoji = STATUS_EMOJI.get(status, "")
    return f"{color}{emoji} {status}{reset}" if color else f"{emoji} {status}"


def _format_table(header: list[str], rows: list[list[str]], col_widths: Optional[list[int]] = None):
    """Print a simple terminal table."""
    if not col_widths:
        col_widths = [len(h) for h in header]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(cells):
        return "  ".join(
            cell.ljust(col_widths[i]) if i < len(col_widths) else cell
            for i, cell in enumerate(cells)
        )

    click.echo(fmt_row(header))
    click.echo("  ".join("-" * w for w in col_widths))
    for row in rows:
        click.echo(fmt_row(row))


# ── History Command ───────────────────────────────────────────────────────

async def cmd_history(
    db_path: Optional[str] = None,
    limit: int = 20,
    branch: Optional[str] = None,
    run_id: Optional[str] = None,
):
    """Show run history (Video Git log)."""

    project_root = Path.cwd()
    actual_db_path = Path(db_path) if db_path else project_root / "cinemate.db"

    if not actual_db_path.exists():
        click.echo("No database found. Run 'cinemate create' first.")
        return

    store = Store(actual_db_path)
    await store.init_db()

    if run_id:
        # Show details for a specific run
        run = await store.get_run(run_id)
        if not run:
            click.echo(f"Run '{run_id}' not found.")
            return

        click.echo(f"\n{'=' * 60}")
        click.echo(f"Run Details: {run.run_id}")
        click.echo(f"{'=' * 60}")
        click.echo(f"  Commit:    {run.commit_msg or '(no message)'}")
        click.echo(f"  Status:    {_color_status(run.status.value)}")
        click.echo(f"  Branch:    {run.branch_name or 'main'}")
        click.echo(f"  Parent:    {run.parent_run_id or '(root)'}")
        click.echo(f"  Created:   {run.created_at.isoformat()}")
        click.echo("")

        # Node details
        nodes = await store.list_node_executions_for_run(run_id)
        if nodes:
            click.echo("  Nodes:")
            for node in nodes:
                emoji = STATUS_EMOJI.get(node.status.value, "")
                retry = f" (x{node.retry_count})" if node.retry_count > 0 else ""
                error = f" — {node.error_msg}" if node.error_msg else ""
                click.echo(f"    {emoji} {node.node_id:20s} {node.status.value}{retry}{error}")
        else:
            click.echo("  (no node executions recorded)")

        click.echo(f"\n{'=' * 60}")
    else:
        # Show run history
        runs = await store.list_runs(limit=limit, branch=branch)

        click.echo(f"\n{'=' * 60}")
        title = f"Run History"
        if branch:
            title += f" (branch: {branch})"
        click.echo(f"{title}")
        click.echo(f"{'=' * 60}")

        if not runs:
            click.echo("  No runs found.")
            click.echo(f"{'=' * 60}")
            return

        # Table header
        header = ["Status", "Run ID", "Commit", "Branch", "Created"]
        rows = []
        for run in runs:
            status_str = _color_status(run.status.value)
            commit = (run.commit_msg or "(no message)")[:35]
            branch_name = run.branch_name or "main"
            created = run.created_at.strftime("%Y-%m-%d %H:%M")
            rows.append([status_str, run.run_id, commit, branch_name, created])

        _format_table(header, rows, col_widths=[12, 22, 37, 10, 17])
        click.echo(f"\n  Total: {len(runs)} runs shown")
        click.echo(f"{'=' * 60}")


# ── Diff Command ──────────────────────────────────────────────────────────

async def cmd_diff(
    db_path: Optional[str] = None,
    run_id: Optional[str] = None,
    parent_run_id: Optional[str] = None,
):
    """Show differences between two runs (Video Git diff)."""

    project_root = Path.cwd()
    actual_db_path = Path(db_path) if db_path else project_root / "cinemate.db"

    if not actual_db_path.exists():
        click.echo("No database found. Run 'cinemate create' first.")
        return

    store = Store(actual_db_path)
    await store.init_db()

    # Get the target run
    if not run_id:
        # Use the most recent run
        runs = await store.list_runs(limit=1)
        if not runs:
            click.echo("No runs found.")
            return
        run_id = runs[0].run_id

    target_run = await store.get_run(run_id)
    if not target_run:
        click.echo(f"Run '{run_id}' not found.")
        return

    # Determine comparison run
    if parent_run_id:
        base_run = await store.get_run(parent_run_id)
    elif target_run.parent_run_id:
        base_run = await store.get_run(target_run.parent_run_id)
    else:
        click.echo(f"Run '{run_id}' has no parent. Use --parent to specify a comparison run.")
        return

    if not base_run:
        click.echo(f"Parent run '{target_run.parent_run_id}' not found.")
        return

    # Get node executions for both runs
    target_nodes = await store.list_node_executions_for_run(run_id)
    base_nodes = await store.list_node_executions_for_run(base_run.run_id)

    target_map = {n.node_id: n for n in target_nodes}
    base_map = {n.node_id: n for n in base_nodes}

    # Compute diff
    all_node_ids = sorted(set(target_map.keys()) | set(base_map.keys()))

    click.echo(f"\n{'=' * 60}")
    click.echo(f"Diff: {base_run.run_id} -> {target_run.run_id}")
    click.echo(f"{'=' * 60}")
    click.echo(f"  Base:  {base_run.commit_msg or '(no message)'}")
    click.echo(f"  Target: {target_run.commit_msg or '(no message)'}")
    click.echo("")

    if not all_node_ids:
        click.echo("  No nodes to compare.")
        click.echo(f"{'=' * 60}")
        return

    # Table
    header = ["Node", "Base Status", "Target Status", "Change"]
    rows = []
    for node_id in all_node_ids:
        base_node = base_map.get(node_id)
        target_node = target_map.get(node_id)

        base_status = base_node.status.value if base_node else "(new)"
        target_status = target_node.status.value if target_node else "(deleted)"

        # Determine change type
        if base_node and not target_node:
            change = "🗑️  deleted"
        elif not base_node and target_node:
            change = "➕ added"
        elif base_node.status != target_node.status:
            change = "🔄 changed"
        else:
            change = "➖ same"

        base_col = _color_status(base_status) if base_status != "(new)" else "\033[90m(new)\033[0m"
        target_col = _color_status(target_status) if target_status != "(deleted)" else "\033[90m(deleted)\033[0m"

        rows.append([node_id, base_col, target_col, change])

    _format_table(header, rows, col_widths=[20, 15, 15, 15])

    # Summary
    added = sum(1 for r in rows if "added" in r[3])
    deleted = sum(1 for r in rows if "deleted" in r[3])
    changed = sum(1 for r in rows if "changed" in r[3])
    same = sum(1 for r in rows if "same" in r[3])

    click.echo(f"\n  Summary: {added} added, {deleted} deleted, {changed} changed, {same} same")
    click.echo(f"{'=' * 60}")


# ── Branches Command ──────────────────────────────────────────────────────

async def cmd_branches(db_path: Optional[str] = None):
    """List all branches in the Video Git history."""

    project_root = Path.cwd()
    actual_db_path = Path(db_path) if db_path else project_root / "cinemate.db"

    if not actual_db_path.exists():
        click.echo("No database found. Run 'cinemate create' first.")
        return

    store = Store(actual_db_path)
    await store.init_db()

    async with __import__("aiosqlite").connect(actual_db_path) as db:
        db.row_factory = __import__("aiosqlite").Row
        async with db.execute(
            "SELECT branch_name, COUNT(*) as cnt, MAX(created_at) as latest "
            "FROM pipeline_runs GROUP BY branch_name ORDER BY latest DESC"
        ) as cursor:
            rows = await cursor.fetchall()

    click.echo(f"\n{'=' * 60}")
    click.echo("Branches")
    click.echo(f"{'=' * 60}")

    if not rows:
        click.echo("  No branches found.")
        click.echo(f"{'=' * 60}")
        return

    header = ["Branch", "Runs", "Latest"]
    table_rows = []
    for row in rows:
        branch = row["branch_name"] or "main"
        latest = row["latest"]
        table_rows.append([branch, str(row["cnt"]), latest])

    _format_table(header, table_rows, col_widths=[15, 8, 20])
    click.echo(f"\n  Total: {len(rows)} branches")
    click.echo(f"{'=' * 60}")
