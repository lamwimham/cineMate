"""
Tests for CineMate CLI Video Git commands (history, diff, branches).
Covers terminal output formatting, Store integration, and edge cases.
"""

import pytest
import tempfile
from pathlib import Path
from click.testing import CliRunner

from cine_mate.cli.main import cli
from cine_mate.cli.video_git import (
    cmd_history,
    cmd_diff,
    cmd_branches,
    _color_status,
    _format_table,
)
from cine_mate.core.store import Store
from cine_mate.core.models import PipelineRun, RunStatus, NodeExecution, NodeStatus


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
async def populated_store():
    """Provide a Store with multiple runs and node executions."""
    db_path = Path(tempfile.mktemp(suffix=".db"))
    store = Store(db_path)
    await store.init_db()

    # Run 1: single scene (3 nodes)
    run1 = PipelineRun(
        run_id="run_001",
        parent_run_id=None,
        branch_name="main",
        commit_msg="Cyberpunk city",
        status=RunStatus.COMPLETED,
    )
    await store.create_run(run1)
    for node_id in ["script", "image", "video"]:
        await store.upsert_node_execution(NodeExecution(
            id=f"exec_run_001_{node_id}",
            run_id="run_001",
            node_id=node_id,
            status=NodeStatus.SUCCEEDED,
        ))

    # Run 2: ad pipeline (4 nodes), child of run_001
    run2 = PipelineRun(
        run_id="run_002",
        parent_run_id="run_001",
        branch_name="main",
        commit_msg="Product ad",
        status=RunStatus.COMPLETED,
    )
    await store.create_run(run2)
    for node_id in ["hook", "demo", "cta", "compose"]:
        await store.upsert_node_execution(NodeExecution(
            id=f"exec_run_002_{node_id}",
            run_id="run_002",
            node_id=node_id,
            status=NodeStatus.SUCCEEDED,
        ))

    # Run 3: failed run on a different branch
    run3 = PipelineRun(
        run_id="run_003",
        parent_run_id=None,
        branch_name="experiment",
        commit_msg="Failed attempt",
        status=RunStatus.FAILED,
    )
    await store.create_run(run3)
    await store.upsert_node_execution(NodeExecution(
        id="exec_run_003_video",
        run_id="run_003",
        node_id="video",
        status=NodeStatus.FAILED,
        error_msg="API timeout",
    ))

    yield store

    if db_path.exists():
        db_path.unlink()


# =============================================================================
# CLI Entry Tests
# =============================================================================

class TestVideoGitCliCommands:
    """Test CLI command registration."""

    def test_history_in_help(self, runner):
        """History command appears in help."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "history" in result.output

    def test_diff_in_help(self, runner):
        """Diff command appears in help."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "diff" in result.output

    def test_branches_in_help(self, runner):
        """Branches command appears in help."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "branches" in result.output


# =============================================================================
# History Command Tests
# =============================================================================

class TestHistoryCommand:
    """Test the `cinemate history` command."""

    def test_history_shows_runs(self, runner, populated_store):
        """History lists all runs."""
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "history",
        ])

        assert result.exit_code == 0
        assert "Run History" in result.output
        assert "run_001" in result.output
        assert "run_002" in result.output
        assert "run_003" in result.output
        assert "Cyberpunk city" in result.output
        assert "Product ad" in result.output
        assert "Failed attempt" in result.output

    def test_history_filters_by_branch(self, runner, populated_store):
        """History filters runs by branch."""
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "history",
            "--branch", "experiment",
        ])

        assert result.exit_code == 0
        assert "run_003" in result.output
        assert "run_001" not in result.output

    def test_history_limits_results(self, runner, populated_store):
        """History respects --limit flag."""
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "history",
            "--limit", "1",
        ])

        assert result.exit_code == 0
        assert "Total: 1 runs shown" in result.output

    def test_history_shows_run_details(self, runner, populated_store):
        """History --run shows detailed node info."""
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "history",
            "--run", "run_001",
        ])

        assert result.exit_code == 0
        assert "Run Details: run_001" in result.output
        assert "Cyberpunk city" in result.output
        assert "script" in result.output
        assert "image" in result.output
        assert "video" in result.output

    def test_history_missing_run(self, runner, populated_store):
        """History reports missing run."""
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "history",
            "--run", "nonexistent",
        ])

        assert result.exit_code == 0
        assert "not found" in result.output

    def test_history_no_database(self, runner):
        """History reports missing database."""
        result = runner.invoke(cli, [
            "--db-path", "/tmp/nonexistent_cinemate.db",
            "history",
        ])

        assert result.exit_code == 0
        assert "No database found" in result.output


# =============================================================================
# Diff Command Tests
# =============================================================================

class TestDiffCommand:
    """Test the `cinemate diff` command."""

    def test_diff_shows_changes(self, runner, populated_store):
        """Diff shows node-level changes between runs."""
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "diff",
            "run_002",
            "--parent", "run_001",
        ])

        assert result.exit_code == 0
        assert "Diff: run_001 -> run_002" in result.output
        assert "Cyberpunk city" in result.output
        assert "Product ad" in result.output
        # run_002 has different nodes than run_001
        assert "hook" in result.output
        assert "script" in result.output

    def test_diff_shows_summary(self, runner, populated_store):
        """Diff includes change summary."""
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "diff",
            "run_002",
            "--parent", "run_001",
        ])

        assert result.exit_code == 0
        assert "Summary:" in result.output
        assert "added" in result.output
        assert "deleted" in result.output

    def test_diff_no_parent_no_arg(self, runner, populated_store):
        """Diff reports when run has no parent and no --parent given."""
        # run_001 has no parent
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "diff",
            "run_001",
        ])

        assert result.exit_code == 0
        assert "has no parent" in result.output

    def test_diff_missing_run(self, runner, populated_store):
        """Diff reports missing run."""
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "diff",
            "nonexistent",
        ])

        assert result.exit_code == 0
        assert "not found" in result.output

    def test_diff_no_database(self, runner):
        """Diff reports missing database."""
        result = runner.invoke(cli, [
            "--db-path", "/tmp/nonexistent_cinemate.db",
            "diff",
        ])

        assert result.exit_code == 0
        assert "No database found" in result.output


# =============================================================================
# Branches Command Tests
# =============================================================================

class TestBranchesCommand:
    """Test the `cinemate branches` command."""

    def test_branches_shows_all_branches(self, runner, populated_store):
        """Branches lists all branches."""
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "branches",
        ])

        assert result.exit_code == 0
        assert "Branches" in result.output
        assert "main" in result.output
        assert "experiment" in result.output

    def test_branches_shows_run_counts(self, runner, populated_store):
        """Branches shows correct run counts per branch."""
        result = runner.invoke(cli, [
            "--db-path", str(populated_store.db_path),
            "branches",
        ])

        assert result.exit_code == 0
        assert "Total: 2 branches" in result.output

    def test_branches_no_database(self, runner):
        """Branches reports missing database."""
        result = runner.invoke(cli, [
            "--db-path", "/tmp/nonexistent_cinemate.db",
            "branches",
        ])

        assert result.exit_code == 0
        assert "No database found" in result.output


# =============================================================================
# Formatting Helper Tests
# =============================================================================

class TestFormattingHelpers:
    """Test terminal formatting helpers."""

    def test_color_status_completed(self):
        """Completed status has green color and checkmark."""
        result = _color_status("completed")
        assert "completed" in result
        assert "\033[92m" in result  # green

    def test_color_status_failed(self):
        """Failed status has red color."""
        result = _color_status("failed")
        assert "failed" in result
        assert "\033[91m" in result  # red

    def test_color_status_unknown(self):
        """Unknown status returns plain text."""
        result = _color_status("unknown_status")
        assert "unknown_status" in result

    def test_format_table_outputs_header(self):
        """Format table includes header row."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            _format_table(["A", "B"], [["1", "2"]], col_widths=[5, 5])
        output = f.getvalue()

        assert "A" in output
        assert "B" in output
        assert "1" in output
        assert "2" in output
