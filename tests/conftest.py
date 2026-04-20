"""
CineMate Test Configuration
Shared fixtures for all test modules.

Usage:
    pytest tests/                     # Run all tests
    pytest -m unit                    # Run unit tests only
    pytest -m integration             # Run integration tests only
    pytest --cov=cine_mate            # With coverage
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, Set

from cine_mate.core.store import Store
from cine_mate.core.models import (
    PipelineRun, NodeExecution, NodeStatus, RunStatus,
    NodeConfig, Artifact, BlobMetadata, ApiMode
)
from cine_mate.engine.dag import PipelineDAG
from cine_mate.engine.fsm import NodeFSM, NodeState
from cine_mate.engine.orchestrator import Orchestrator


# =============================================================================
# Async Event Loop
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Store Fixtures
# =============================================================================

@pytest.fixture
async def temp_db_path():
    """Provide a temporary database path that is cleaned up after test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
async def store(temp_db_path):
    """
    Provide a fresh Store instance with initialized schema.
    Uses in-memory SQLite for fast tests.
    """
    s = Store(temp_db_path)
    await s.init_db()
    yield s


@pytest.fixture
async def populated_store(store):
    """
    Store with pre-populated test data (Run + Nodes + Artifacts).
    """
    # Create a test run
    run = PipelineRun(
        run_id="test_run_001",
        parent_run_id=None,
        branch_name="main",
        commit_msg="Test run",
        status=RunStatus.COMPLETED
    )
    await store.create_run(run)

    # Create node executions
    for node_id in ["node_A", "node_B", "node_C"]:
        exec = NodeExecution(
            id=f"exec_test_run_001_{node_id}",
            run_id="test_run_001",
            node_id=node_id,
            status=NodeStatus.SUCCEEDED,
            config_snapshot=NodeConfig(prompt=f"test_prompt_{node_id}")
        )
        await store.upsert_node_execution(exec)

    # Create blob and artifact for node_A
    blob = BlobMetadata(
        blob_id="sha256_test_abc123",
        relative_path="objects/ab/c123.mp4",
        file_size_bytes=1024,
        mime_type="video/mp4"
    )
    await store.register_blob(blob)

    artifact = Artifact(
        id="art_test_run_001_node_A",
        run_id="test_run_001",
        node_id="node_A",
        blob_hash="sha256_test_abc123",
        metadata={"cost": 0.5},
        is_reused=False
    )
    await store.link_artifact(artifact)

    yield store


# =============================================================================
# DAG Fixtures
# =============================================================================

@pytest.fixture
def empty_dag():
    """Provide an empty PipelineDAG."""
    return PipelineDAG()


@pytest.fixture
def linear_dag():
    """
    Linear DAG: A -> B -> C
    Simple dependency chain for basic tests.
    """
    dag = PipelineDAG()
    dag.add_node("node_A", "script_gen", {"prompt": "Write a script"})
    dag.add_node("node_B", "img_gen", {"prompt": "Generate image"})
    dag.add_node("node_C", "vid_gen", {"prompt": "Animate image"})

    dag.add_edge("node_A", "node_B")
    dag.add_edge("node_B", "node_C")

    return dag


@pytest.fixture
def branching_dag():
    """
    Branching DAG: A -> B -> D
                      -> C -> D
    Two parallel branches converging at D.
    """
    dag = PipelineDAG()
    dag.add_node("node_A", "script_gen", {"prompt": "Write script"})
    dag.add_node("node_B", "img_gen_style1", {"prompt": "Style 1 image"})
    dag.add_node("node_C", "img_gen_style2", {"prompt": "Style 2 image"})
    dag.add_node("node_D", "video_concat", {"prompt": "Concat videos"})

    dag.add_edge("node_A", "node_B")
    dag.add_edge("node_A", "node_C")
    dag.add_edge("node_B", "node_D")
    dag.add_edge("node_C", "node_D")

    return dag


@pytest.fixture
def complex_dag():
    """
    Complex DAG with 10+ nodes for performance testing.
    Structure: Multi-level branching.
    """
    dag = PipelineDAG()

    # Level 1: Input
    dag.add_node("input_1", "text_to_image", {"prompt": "Scene 1"})
    dag.add_node("input_2", "text_to_image", {"prompt": "Scene 2"})
    dag.add_node("input_3", "text_to_image", {"prompt": "Scene 3"})

    # Level 2: Processing
    dag.add_node("proc_1", "image_to_video", {"duration": 5})
    dag.add_node("proc_2", "image_to_video", {"duration": 5})
    dag.add_node("proc_3", "image_to_video", {"duration": 5})

    dag.add_edge("input_1", "proc_1")
    dag.add_edge("input_2", "proc_2")
    dag.add_edge("input_3", "proc_3")

    # Level 3: Enhancement
    dag.add_node("enhance_1", "color_grade", {"style": "cinematic"})
    dag.add_node("enhance_2", "color_grade", {"style": "cinematic"})

    dag.add_edge("proc_1", "enhance_1")
    dag.add_edge("proc_2", "enhance_1")
    dag.add_edge("proc_3", "enhance_2")

    # Level 4: Output
    dag.add_node("output", "video_concat", {"transition": "crossfade"})

    dag.add_edge("enhance_1", "output")
    dag.add_edge("enhance_2", "output")

    return dag


# =============================================================================
# FSM Fixtures
# =============================================================================

@pytest.fixture
def fsm():
    """Provide a basic NodeFSM instance."""
    return NodeFSM(node_id="test_node_001")


@pytest.fixture
def fsm_with_retries():
    """FSM configured with custom max_retries."""
    return NodeFSM(node_id="test_node_002", max_retries=3)


# =============================================================================
# Orchestrator Fixtures
# =============================================================================

@pytest.fixture
async def mock_executor():
    """
    Mock executor function for Orchestrator tests.
    Simulates async API call with short delay.
    """
    async def executor(node_id: str, config: dict) -> dict:
        await asyncio.sleep(0.05)  # Simulate 50ms API call
        return {
            "result": f"mock_output_{node_id}",
            "status": "success",
            "cost": 0.1
        }
    return executor


@pytest.fixture
async def failing_executor():
    """
    Mock executor that always fails.
    Used for testing error handling.
    """
    async def executor(node_id: str, config: dict) -> dict:
        raise RuntimeError(f"Mock failure for {node_id}")
    return executor


@pytest.fixture
async def orchestrator(store, linear_dag, mock_executor):
    """
    Orchestrator with linear DAG and mock executor.
    Ready for basic execution tests.
    """
    run = PipelineRun(
        run_id="orch_test_run",
        status=RunStatus.RUNNING
    )
    orch = Orchestrator(store, run, linear_dag, mock_executor)
    yield orch


# =============================================================================
# Model Fixtures
# =============================================================================

@pytest.fixture
def sample_node_config():
    """Sample NodeConfig for testing."""
    return NodeConfig(
        model_name="kling-v2",
        prompt="A beautiful sunset",
        negative_prompt="blurry, low quality",
        seed=42,
        billing_mode=ApiMode.MANAGED
    )


@pytest.fixture
def sample_run():
    """Sample PipelineRun for testing."""
    return PipelineRun(
        run_id="sample_run_001",
        parent_run_id=None,
        branch_name="main",
        commit_msg="Initial generation",
        status=RunStatus.PENDING
    )


@pytest.fixture
def child_run():
    """
    Sample child run (has parent_run_id).
    For testing Video Git replay scenarios.
    """
    return PipelineRun(
        run_id="sample_run_002",
        parent_run_id="sample_run_001",
        branch_name="main",
        commit_msg="Modify scene 2",
        status=RunStatus.PENDING
    )


# =============================================================================
# Helper Functions (Not Fixtures)
# =============================================================================

def assert_valid_dag_json(data: Dict[str, Any]) -> bool:
    """
    Validate DAG JSON structure from Intent Parser.
    Returns True if valid, raises AssertionError otherwise.
    """
    assert "nodes" in data, "DAG must have 'nodes' field"
    assert isinstance(data["nodes"], list), "'nodes' must be a list"

    for node in data["nodes"]:
        assert "id" in node, "Each node must have 'id'"
        assert "type" in node, "Each node must have 'type'"
        assert "inputs" in node, "Each node must have 'inputs'"

    return True


def create_test_dag_from_json(data: Dict[str, Any]) -> PipelineDAG:
    """
    Create a PipelineDAG from Intent Parser JSON output.
    """
    dag = PipelineDAG()

    for node in data.get("nodes", []):
        dag.add_node(
            node["id"],
            node["type"],
            node.get("params", {})
        )

    for node in data.get("nodes", []):
        for input_id in node.get("inputs", []):
            dag.add_edge(input_id, node["id"])

    return dag


# =============================================================================
# Test Data
# =============================================================================

@pytest.fixture
def intent_test_cases():
    """
    Load test cases from test_cases_intent.json.
    """
    import json
    test_file = Path(__file__).parent / "test_cases_intent.json"
    if test_file.exists():
        with open(test_file) as f:
            return json.load(f)
    return {"cases": []}


# =============================================================================
# Mock Upstream Fixtures
# =============================================================================

@pytest.fixture
def mock_kling():
    """Provide Mock Kling API client."""
    from tests.mocks.upstream import MockKlingClient
    return MockKlingClient()


@pytest.fixture
def mock_runway():
    """Provide Mock Runway API client."""
    from tests.mocks.upstream import MockRunwayClient
    return MockRunwayClient()


@pytest.fixture
def mock_openai():
    """Provide Mock OpenAI API client."""
    from tests.mocks.upstream import MockOpenAIClient
    return MockOpenAIClient()


@pytest.fixture
def mock_factory():
    """Provide Mock Upstream Factory."""
    from tests.mocks.upstream import MockUpstreamFactory
    return MockUpstreamFactory