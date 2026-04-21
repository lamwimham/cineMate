"""
Tests for Orchestrator Event-Driven Mode (Sprint 2 Day 2)

Test Coverage:
- Event-driven execution mode
- start_event_listening()
- _on_node_completed() callback
- _on_node_failed() callback
- Node dependency triggering
- Completion event signaling
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from cine_mate.core.models import PipelineRun, RunStatus, NodeExecution, NodeStatus, NodeConfig
from cine_mate.core.store import Store
from cine_mate.engine.dag import PipelineDAG
from cine_mate.engine.orchestrator import Orchestrator
from cine_mate.engine.fsm import NodeState
from cine_mate.infra.schemas import NodeCompletedEvent, NodeFailedEvent


@pytest.fixture
def linear_dag():
    """Linear DAG: A -> B -> C."""
    dag = PipelineDAG()
    dag.add_node("node_A", "text_to_image", {"prompt": "A"})
    dag.add_node("node_B", "image_to_video", {"prompt": "B"})
    dag.add_node("node_C", "video_edit", {"prompt": "C"})
    dag.add_edge("node_A", "node_B")
    dag.add_edge("node_B", "node_C")
    return dag


@pytest.fixture
def branching_dag():
    """Branching DAG: A -> B -> D, A -> C -> D."""
    dag = PipelineDAG()
    dag.add_node("node_A", "text_to_image", {"prompt": "A"})
    dag.add_node("node_B", "image_to_video", {"prompt": "B"})
    dag.add_node("node_C", "image_to_video", {"prompt": "C"})
    dag.add_node("node_D", "video_concat", {"prompt": "D"})
    dag.add_edge("node_A", "node_B")
    dag.add_edge("node_A", "node_C")
    dag.add_edge("node_B", "node_D")
    dag.add_edge("node_C", "node_D")
    return dag


@pytest.fixture
async def mock_store():
    """Mock Store for orchestrator tests."""
    store = Mock(spec=Store)
    store.create_run = AsyncMock()
    store.update_run_status = AsyncMock()
    store.upsert_node_execution = AsyncMock()
    store.get_node_execution = AsyncMock(return_value=None)
    store.get_artifact = AsyncMock(return_value=None)
    store.link_artifact = AsyncMock()
    return store


@pytest.fixture
async def mock_executor():
    """Mock executor function."""
    async def executor(node_id: str, config: dict) -> dict:
        await asyncio.sleep(0.01)
        return {"result": f"output_{node_id}", "status": "success"}
    return executor


@pytest.fixture
async def mock_event_bus():
    """Mock EventBus for event-driven tests."""
    event_bus = Mock()
    event_bus.subscribe = Mock()
    event_bus.start_listening = AsyncMock()
    event_bus.publish = AsyncMock()
    return event_bus


class TestOrchestratorEventDrivenInit:
    """Test Orchestrator initialization with EventBus."""

    @pytest.mark.asyncio
    async def test_orchestrator_with_event_bus(self, mock_store, linear_dag, mock_executor, mock_event_bus):
        """Orchestrator accepts EventBus instance."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=mock_executor,
            event_bus=mock_event_bus,
        )

        assert orchestrator.event_bus == mock_event_bus
        assert orchestrator._event_subscribed is False

    @pytest.mark.asyncio
    async def test_orchestrator_without_event_bus(self, mock_store, linear_dag, mock_executor):
        """Orchestrator without EventBus uses direct mode."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=mock_executor,
            event_bus=None,
        )

        assert orchestrator.event_bus is None


class TestStartEventListening:
    """Test start_event_listening method."""

    @pytest.mark.asyncio
    async def test_subscribe_to_events(self, mock_store, linear_dag, mock_executor, mock_event_bus):
        """Orchestrator subscribes to node_completed and node_failed events."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=mock_executor,
            event_bus=mock_event_bus,
        )

        await orchestrator.start_event_listening()

        # Verify subscriptions
        assert mock_event_bus.subscribe.call_count == 2
        mock_event_bus.subscribe.assert_any_call("node_completed", orchestrator._on_node_completed)
        mock_event_bus.subscribe.assert_any_call("node_failed", orchestrator._on_node_failed)

        # Verify listening started
        mock_event_bus.start_listening.assert_called_once()
        assert orchestrator._event_subscribed is True

    @pytest.mark.asyncio
    async def test_double_subscribe_ignored(self, mock_store, linear_dag, mock_executor, mock_event_bus):
        """Double call to start_event_listening is ignored."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=mock_executor,
            event_bus=mock_event_bus,
        )

        await orchestrator.start_event_listening()
        await orchestrator.start_event_listening()

        # Should only subscribe once
        assert mock_event_bus.subscribe.call_count == 2

    @pytest.mark.asyncio
    async def test_no_subscribe_without_event_bus(self, mock_store, linear_dag, mock_executor):
        """No subscription if event_bus is None."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=mock_executor,
            event_bus=None,
        )

        await orchestrator.start_event_listening()

        # No error, no action
        assert orchestrator._event_subscribed is False


class TestOnNodeCompleted:
    """Test _on_node_completed callback."""

    @pytest.mark.asyncio
    async def test_node_added_to_completed(self, mock_store, linear_dag, mock_executor, mock_event_bus):
        """Completed node is added to completed_nodes set."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=mock_executor,
            event_bus=mock_event_bus,
        )

        event = NodeCompletedEvent(
            run_id="test_run",
            node_id="node_A",
            payload={"result": "success"}
        )

        await orchestrator._on_node_completed(event)

        assert "node_A" in orchestrator.completed_nodes

    @pytest.mark.asyncio
    async def test_downstream_triggered_after_completion(self, mock_store, linear_dag, mock_executor, mock_event_bus):
        """Downstream node is triggered after parent completes."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=mock_executor,
            event_bus=mock_event_bus,
        )

        # Start listening first
        await orchestrator.start_event_listening()

        # Simulate node_A completion
        event = NodeCompletedEvent(
            run_id="test_run",
            node_id="node_A",
            payload={"result": "success"}
        )

        with patch.object(orchestrator, '_submit_node', new_callable=AsyncMock) as mock_submit:
            await orchestrator._on_node_completed(event)

            # node_B (dependent on node_A) should be triggered
            mock_submit.assert_called_once_with("node_B")

    @pytest.mark.asyncio
    async def test_completion_event_set_when_all_done(self, mock_store, linear_dag, mock_executor, mock_event_bus):
        """Completion event is set when all nodes complete."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=mock_executor,
            event_bus=mock_event_bus,
        )

        # Mark all nodes as completed
        orchestrator.completed_nodes = {"node_A", "node_B", "node_C"}

        event = NodeCompletedEvent(
            run_id="test_run",
            node_id="node_C",
            payload={"result": "success"}
        )

        await orchestrator._on_node_completed(event)

        assert orchestrator._completion_event.is_set()


class TestOnNodeFailed:
    """Test _on_node_failed callback."""

    @pytest.mark.asyncio
    async def test_fsm_marked_failed(self, mock_store, linear_dag, mock_executor, mock_event_bus):
        """Node FSM state is set to FAILED on failure."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=mock_executor,
            event_bus=mock_event_bus,
        )

        event = NodeFailedEvent(
            run_id="test_run",
            node_id="node_A",
            payload={
                "error_code": "API_ERROR",
                "error_msg": "Timeout",
                "retry_count": 0
            }
        )

        await orchestrator._on_node_failed(event)

        assert orchestrator.fsms["node_A"].state == NodeState.FAILED


class TestBranchingDAGDependency:
    """Test dependency resolution in branching DAG."""

    @pytest.mark.asyncio
    async def test_convergence_node_not_triggered_early(self, mock_store, branching_dag, mock_executor, mock_event_bus):
        """Node D is not triggered until both B and C complete."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=branching_dag,
            executor_fn=mock_executor,
            event_bus=mock_event_bus,
        )

        await orchestrator.start_event_listening()

        with patch.object(orchestrator, '_submit_node', new_callable=AsyncMock) as mock_submit:
            # Only B completes (C still pending)
            orchestrator.completed_nodes.add("node_A")
            orchestrator.completed_nodes.add("node_B")

            event_b = NodeCompletedEvent(
                run_id="test_run",
                node_id="node_B",
                payload={"result": "success"}
            )

            await orchestrator._on_node_completed(event_b)

            # D should NOT be triggered (C not complete)
            mock_submit.assert_not_called()

            # Now C completes
            orchestrator.completed_nodes.add("node_C")

            event_c = NodeCompletedEvent(
                run_id="test_run",
                node_id="node_C",
                payload={"result": "success"}
            )

            await orchestrator._on_node_completed(event_c)

            # D should now be triggered
            mock_submit.assert_called_with("node_D")


class TestPublishNodeEvents:
    """Test Orchestrator publishes node events."""

    @pytest.mark.asyncio
    async def test_publish_node_completed_on_success(self, mock_store, linear_dag, mock_executor, mock_event_bus):
        """Orchestrator publishes node_completed event after successful execution."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=mock_executor,
            event_bus=mock_event_bus,
        )

        await orchestrator._execute_node("node_A")

        # Verify event published
        assert mock_event_bus.publish.called
        call_args = mock_event_bus.publish.call_args
        event = call_args[0][0]
        assert isinstance(event, NodeCompletedEvent)
        assert event.node_id == "node_A"

    @pytest.mark.asyncio
    async def test_publish_node_failed_on_error(self, mock_store, linear_dag, mock_event_bus):
        """Orchestrator publishes node_failed event on execution error."""
        run = PipelineRun(run_id="test_run", status=RunStatus.RUNNING)

        async def failing_executor(node_id: str, config: dict) -> dict:
            raise RuntimeError("API Error")

        orchestrator = Orchestrator(
            store=mock_store,
            run=run,
            dag=linear_dag,
            executor_fn=failing_executor,
            event_bus=mock_event_bus,
        )

        with pytest.raises(RuntimeError):
            await orchestrator._execute_node("node_A")

        # Verify event published
        assert mock_event_bus.publish.called
        call_args = mock_event_bus.publish.call_args
        event = call_args[0][0]
        assert isinstance(event, NodeFailedEvent)
        assert event.node_id == "node_A"