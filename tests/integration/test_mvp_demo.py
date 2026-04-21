"""
Integration tests for CineMate MVP End-to-End Demo.
Verifies the full pipeline: NL -> Intent -> DAG -> Orchestrator -> Mock Provider.
"""

import pytest
import tempfile
from pathlib import Path

from cine_mate.cli.commands import (
    _mock_intent_parser,
    _build_dag_from_json,
    mock_executor,
)
from cine_mate.core.store import Store
from cine_mate.core.models import PipelineRun, RunStatus
from cine_mate.engine.orchestrator import Orchestrator


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
async def temp_store():
    """Provide a fresh Store with initialized schema."""
    db_path = Path(tempfile.mktemp(suffix=".db"))
    store = Store(db_path)
    await store.init_db()
    yield store
    if db_path.exists():
        db_path.unlink()


# =============================================================================
# End-to-End Pipeline Tests
# =============================================================================

class TestEndToEndPipeline:
    """Full pipeline: NL -> Intent -> DAG -> Execute -> Verify."""

    @pytest.mark.asyncio
    async def test_single_scene_pipeline(self, temp_store):
        """Single scene prompt creates and executes 3-node DAG."""
        prompt = "赛博朋克城市夜景"

        # Intent parsing
        dag_json = _mock_intent_parser(prompt)
        assert dag_json["intent"] == "single_scene"
        assert len(dag_json["nodes"]) == 3

        # DAG construction
        dag = _build_dag_from_json(dag_json)
        assert len(dag.graph.nodes()) == 3

        # Execution
        run = PipelineRun(run_id="e2e_single", commit_msg=prompt, status=RunStatus.PENDING)
        orchestrator = Orchestrator(store=temp_store, run=run, dag=dag, executor_fn=mock_executor)
        await orchestrator.execute()

        final = await temp_store.get_run("e2e_single")
        assert final.status == RunStatus.COMPLETED
        assert len(orchestrator.completed_nodes) == 3

    @pytest.mark.asyncio
    async def test_ad_pipeline(self, temp_store):
        """Ad prompt creates and executes 4-node branching DAG."""
        prompt = "产品广告耳机"

        dag_json = _mock_intent_parser(prompt)
        assert dag_json["intent"] == "product_ad"
        assert len(dag_json["nodes"]) == 4

        dag = _build_dag_from_json(dag_json)
        assert len(dag.graph.nodes()) == 4

        run = PipelineRun(run_id="e2e_ad", commit_msg=prompt, status=RunStatus.PENDING)
        orchestrator = Orchestrator(store=temp_store, run=run, dag=dag, executor_fn=mock_executor)
        await orchestrator.execute()

        final = await temp_store.get_run("e2e_ad")
        assert final.status == RunStatus.COMPLETED

        # Verify compose node depends on all 3 upstream nodes
        assert dag.graph.has_edge("node_hook", "node_compose")
        assert dag.graph.has_edge("node_demo", "node_compose")
        assert dag.graph.has_edge("node_cta", "node_compose")

    @pytest.mark.asyncio
    async def test_multi_scene_pipeline(self, temp_store):
        """Multi-scene prompt creates and executes 6-node DAG."""
        prompt = "多个场景的视频"

        dag_json = _mock_intent_parser(prompt)
        assert dag_json["intent"] == "multi_scene"
        assert len(dag_json["nodes"]) == 6

        dag = _build_dag_from_json(dag_json)
        assert len(dag.graph.nodes()) == 6

        run = PipelineRun(run_id="e2e_multi", commit_msg=prompt, status=RunStatus.PENDING)
        orchestrator = Orchestrator(store=temp_store, run=run, dag=dag, executor_fn=mock_executor)
        await orchestrator.execute()

        final = await temp_store.get_run("e2e_multi")
        assert final.status == RunStatus.COMPLETED

        # Verify parallel branches: img1 -> vid1, img2 -> vid2
        assert dag.graph.has_edge("node_img1", "node_vid1")
        assert dag.graph.has_edge("node_img2", "node_vid2")


# =============================================================================
# Mock Provider Integration Tests
# =============================================================================

class TestMockProviderIntegration:
    """Verify Mock Provider returns traceable results."""

    @pytest.mark.asyncio
    async def test_mock_executor_returns_consistent_results(self):
        """Mock executor returns structured results for all node types."""
        node_types = [
            ("script_gen", "text"),
            ("text_to_image", "image"),
            ("image_to_video", "video"),
            ("text_to_video", "video"),
            ("video_compose", "video"),
            ("tts", "audio"),
        ]

        for node_type, expected_output_type in node_types:
            result = await mock_executor(f"node_{node_type}", {"type": node_type, "prompt": "test"})
            assert result["status"] == "success"
            assert result["result"]["type"] == expected_output_type
            assert result["cost"] == 0.0

    @pytest.mark.asyncio
    async def test_mock_executor_includes_node_context(self):
        """Mock executor includes node_id and prompt in output."""
        result = await mock_executor("test_node", {"type": "script_gen", "prompt": "custom prompt"})
        assert result["node_id"] == "test_node"
        assert "custom prompt" in result["result"]["output"]

    @pytest.mark.asyncio
    async def test_mock_executor_preserves_dag_flow(self, temp_store):
        """Full DAG execution via mock executor preserves node ordering."""
        dag_json = {
            "intent": "test",
            "nodes": [
                {"id": "a", "type": "script_gen", "parents": [], "params": {"prompt": "test"}},
                {"id": "b", "type": "text_to_image", "parents": ["a"], "params": {"prompt": "test"}},
                {"id": "c", "type": "image_to_video", "parents": ["b"]},
            ],
        }
        dag = _build_dag_from_json(dag_json)
        run = PipelineRun(run_id="flow_test", commit_msg="test", status=RunStatus.PENDING)

        orchestrator = Orchestrator(store=temp_store, run=run, dag=dag, executor_fn=mock_executor)
        await orchestrator.execute()

        # Verify all nodes completed
        assert "a" in orchestrator.completed_nodes
        assert "b" in orchestrator.completed_nodes
        assert "c" in orchestrator.completed_nodes


# =============================================================================
# Director Agent Integration (Mock Mode)
# =============================================================================

class TestDirectorAgentMockIntegration:
    """Verify Director Agent (mock mode) correctly integrates with EngineTools."""

    def test_mock_intent_produces_valid_dag_json(self):
        """Mock intent parser produces structurally valid DAG JSON."""
        prompts = ["test prompt", "产品广告", "多个场景"]
        for prompt in prompts:
            dag_json = _mock_intent_parser(prompt)
            assert "intent" in dag_json
            assert "nodes" in dag_json
            assert isinstance(dag_json["nodes"], list)
            for node in dag_json["nodes"]:
                assert "id" in node
                assert "type" in node
                assert "parents" in node

    def test_dag_json_roundtrips_through_builder(self):
        """DAG JSON can be built back into a PipelineDAG."""
        dag_json = _mock_intent_parser("test prompt")
        dag = _build_dag_from_json(dag_json)

        # Verify node count matches
        assert len(dag.graph.nodes()) == len(dag_json["nodes"])

        # Verify all edges exist
        for node in dag_json["nodes"]:
            for parent_id in node.get("parents", []):
                assert dag.graph.has_edge(parent_id, node["id"]), \
                    f"Missing edge {parent_id} -> {node['id']}"
