"""
Tests for CineMate CLI commands.
Covers create, loop, and status commands with mock execution.
"""

import pytest
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner

from cine_mate.cli.main import cli
from cine_mate.cli.commands import (
    _mock_intent_parser,
    _build_dag_from_json,
    mock_executor,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_db():
    """Provide a temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def temp_data_dir():
    """Provide a temporary data directory."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


# =============================================================================
# CLI Entry Point Tests
# =============================================================================

class TestCliEntryPoint:
    """Test the main CLI entry point."""

    def test_help_shows_commands(self, runner):
        """Help output shows all subcommands."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "create" in result.output
        assert "loop" in result.output
        assert "status" in result.output
        assert "AI Video Production OS" in result.output

    def test_version(self, runner):
        """Version flag shows 0.1.0."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_no_subcommand_shows_help(self, runner):
        """Running without subcommand shows help."""
        result = runner.invoke(cli)
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_mock_flag_available(self, runner):
        """Mock flag is available in help."""
        result = runner.invoke(cli, ["--help"])
        assert "--mock" in result.output
        assert "--no-mock" in result.output


# =============================================================================
# Create Command Tests
# =============================================================================

class TestCreateCommand:
    """Test the `cinemate create` command."""

    def test_create_single_scene(self, runner, temp_db, temp_data_dir):
        """Create command processes a single-scene prompt."""
        result = runner.invoke(cli, [
            "--db-path", str(temp_db),
            "--data-dir", str(temp_data_dir),
            "create",
            "赛博朋克城市夜景",
        ])

        assert result.exit_code == 0
        assert "DAG plan received" in result.output
        assert "node_script" in result.output
        assert "node_image" in result.output
        assert "node_video" in result.output
        assert "Completed successfully" in result.output
        assert "Nodes executed: 3/3" in result.output

    def test_create_ad_pipeline(self, runner, temp_db, temp_data_dir):
        """Create command detects ad keyword and builds branching DAG."""
        result = runner.invoke(cli, [
            "--db-path", str(temp_db),
            "--data-dir", str(temp_data_dir),
            "create",
            "产品广告耳机",
        ])

        assert result.exit_code == 0
        assert "node_hook" in result.output
        assert "node_demo" in result.output
        assert "node_cta" in result.output
        assert "node_compose" in result.output
        assert "Nodes executed: 4/4" in result.output

    def test_create_with_style(self, runner, temp_db, temp_data_dir):
        """Create command accepts --style option."""
        result = runner.invoke(cli, [
            "--db-path", str(temp_db),
            "--data-dir", str(temp_data_dir),
            "create",
            "赛博朋克视频",
            "--style", "style-cyberpunk",
        ])

        assert result.exit_code == 0
        assert "Style: style-cyberpunk" in result.output

    def test_creates_database(self, runner, temp_data_dir):
        """Create command creates the SQLite database."""
        db_path = Path(tempfile.mktemp(suffix=".db"))
        assert not db_path.exists()

        try:
            runner.invoke(cli, [
                "--db-path", str(db_path),
                "--data-dir", str(temp_data_dir),
                "create",
                "测试视频",
            ])

            assert db_path.exists()
        finally:
            if db_path.exists():
                db_path.unlink()

    def test_creates_data_directory(self, runner, temp_db, temp_data_dir):
        """Create command creates the data directory."""
        nested_dir = temp_data_dir / "nested"
        runner.invoke(cli, [
            "--db-path", str(temp_db),
            "--data-dir", str(nested_dir),
            "create",
            "测试视频",
        ])

        assert nested_dir.exists()


# =============================================================================
# Status Command Tests
# =============================================================================

class TestStatusCommand:
    """Test the `cinemate status` command."""

    def test_status_empty(self, runner, temp_db, temp_data_dir):
        """Status shows empty state before any runs."""
        result = runner.invoke(cli, [
            "--db-path", str(temp_db),
            "--data-dir", str(temp_data_dir),
            "status",
        ])

        assert result.exit_code == 0
        assert "System Status" in result.output
        assert "Database:" in result.output
        assert "Data directory:" in result.output
        assert "Skills directory:" in result.output

    def test_status_shows_runs(self, runner, temp_db, temp_data_dir):
        """Status shows run count after creation."""
        # Create a run first
        runner.invoke(cli, [
            "--db-path", str(temp_db),
            "--data-dir", str(temp_data_dir),
            "create",
            "测试视频",
        ])

        # Check status
        result = runner.invoke(cli, [
            "--db-path", str(temp_db),
            "--data-dir", str(temp_data_dir),
            "status",
        ])

        assert result.exit_code == 0
        assert "Runs: 1" in result.output


# =============================================================================
# Mock Intent Parser Tests
# =============================================================================

class TestMockIntentParser:
    """Test the mock intent parser logic."""

    def test_single_scene_default(self):
        """Default prompt generates single-scene DAG."""
        result = _mock_intent_parser("A beautiful sunset")

        assert result["intent"] == "single_scene"
        assert len(result["nodes"]) == 3

        node_ids = {n["id"] for n in result["nodes"]}
        assert "node_script" in node_ids
        assert "node_image" in node_ids
        assert "node_video" in node_ids

    def test_ad_detection(self):
        """Ad keywords trigger ad workflow."""
        result = _mock_intent_parser("Product ad for headphones")

        assert result["intent"] == "product_ad"
        assert len(result["nodes"]) == 4

        node_ids = {n["id"] for n in result["nodes"]}
        assert "node_hook" in node_ids
        assert "node_demo" in node_ids
        assert "node_cta" in node_ids
        assert "node_compose" in node_ids

    def test_ad_detection_chinese(self):
        """Chinese ad keywords detected."""
        result = _mock_intent_parser("产品广告耳机")

        assert result["intent"] == "product_ad"

    def test_multi_scene_detection(self):
        """Multi-scene keywords trigger branching DAG."""
        result = _mock_intent_parser("Multiple scenes video")

        assert result["intent"] == "multi_scene"
        assert len(result["nodes"]) == 6

    def test_multi_scene_detection_chinese(self):
        """Chinese multi-scene keywords detected."""
        result = _mock_intent_parser("多个场景的视频")

        assert result["intent"] == "multi_scene"

    def test_nodes_have_parents(self):
        """DAG nodes correctly reference parents."""
        result = _mock_intent_parser("A beautiful sunset")

        # First node has no parents
        assert result["nodes"][0]["parents"] == []

        # Subsequent nodes depend on predecessors
        node_parents = {n["id"]: n["parents"] for n in result["nodes"]}
        assert "node_script" in node_parents["node_image"]
        assert "node_image" in node_parents["node_video"]

    def test_nodes_have_params(self):
        """DAG nodes include prompt params."""
        result = _mock_intent_parser("Cyberpunk city")

        for node in result["nodes"]:
            if "params" in node:
                assert "prompt" in node["params"]


# =============================================================================
# DAG Builder Tests
# =============================================================================

class TestDagBuilder:
    """Test DAG construction from intent parser JSON."""

    def test_build_linear_dag(self):
        """Builds correct DAG from linear node list."""
        dag_json = {
            "nodes": [
                {"id": "a", "type": "script_gen", "parents": []},
                {"id": "b", "type": "text_to_image", "parents": ["a"]},
                {"id": "c", "type": "image_to_video", "parents": ["b"]},
            ],
        }

        dag = _build_dag_from_json(dag_json)

        assert len(dag.graph.nodes()) == 3
        assert "a" in dag.graph.nodes()
        assert "b" in dag.graph.nodes()
        assert "c" in dag.graph.nodes()

        # Check edges
        assert dag.graph.has_edge("a", "b")
        assert dag.graph.has_edge("b", "c")

    def test_build_branching_dag(self):
        """Builds correct DAG from branching node list."""
        dag_json = {
            "nodes": [
                {"id": "hook", "type": "text_to_video", "parents": []},
                {"id": "demo", "type": "image_to_video", "parents": []},
                {"id": "compose", "type": "video_compose", "parents": ["hook", "demo"]},
            ],
        }

        dag = _build_dag_from_json(dag_json)

        assert dag.graph.has_edge("hook", "compose")
        assert dag.graph.has_edge("demo", "compose")

    def test_node_config_includes_type(self):
        """Node config includes type for executor routing."""
        dag_json = {
            "nodes": [
                {"id": "a", "type": "script_gen", "parents": [], "params": {"prompt": "test"}},
            ],
        }

        dag = _build_dag_from_json(dag_json)
        config = dag.node_configs.get("a", {})

        assert config["type"] == "script_gen"
        assert config["prompt"] == "test"


# =============================================================================
# Mock Executor Tests
# =============================================================================

class TestMockExecutor:
    """Test the mock executor function."""

    @pytest.mark.asyncio
    async def test_script_gen_output(self):
        """Mock executor returns text for script_gen."""
        result = await mock_executor("node_script", {"type": "script_gen", "prompt": "test"})

        assert result["status"] == "success"
        assert result["result"]["type"] == "text"
        assert result["cost"] == 0.0

    @pytest.mark.asyncio
    async def test_text_to_image_output(self):
        """Mock executor returns image for text_to_image."""
        result = await mock_executor("node_img", {"type": "text_to_image", "prompt": "sunset"})

        assert result["status"] == "success"
        assert result["result"]["type"] == "image"

    @pytest.mark.asyncio
    async def test_image_to_video_output(self):
        """Mock executor returns video for image_to_video."""
        result = await mock_executor("node_vid", {"type": "image_to_video"})

        assert result["status"] == "success"
        assert result["result"]["type"] == "video"

    @pytest.mark.asyncio
    async def test_unknown_node_type(self):
        """Mock executor handles unknown node types."""
        result = await mock_executor("node_unknown", {"type": "unknown_type"})

        assert result["status"] == "success"
        assert result["result"]["type"] == "unknown"
