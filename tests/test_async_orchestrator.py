"""
Unit/Integration Test for AsyncOrchestrator
Verifies that nodes are submitted ONLY after dependencies are met.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from cine_mate.engine.dag import PipelineDAG
from cine_mate.engine.orchestrator import AsyncOrchestrator
from cine_mate.infra.schemas import NodeCompletedEvent, JobType

# Test DAG: A -> B -> C
# A has no deps.
# B depends on A.
# C depends on B.

dag_data = {
    "nodes": [
        {"id": "node_A", "type": "TEXT_TO_IMAGE", "params": {"prompt": "A"}},
        {"id": "node_B", "type": "IMAGE_TO_VIDEO", "params": {"prompt": "B"}},
        {"id": "node_C", "type": "VIDEO_EDIT", "params": {"prompt": "C"}}
    ],
    "edges": [
        {"from": "node_A", "to": "node_B"},
        {"from": "node_B", "to": "node_C"}
    ]
}

async def test_async_orchestrator_flow():
    print("--- Starting AsyncOrchestrator Flow Test ---")
    
    # 1. Setup DAG
    dag = PipelineDAG()
    for node in dag_data["nodes"]:
        dag.add_node(node["id"], node["type"], node["params"])
    for edge in dag_data["edges"]:
        dag.add_edge(edge["from"], edge["to"])
        
    print(f"DAG Nodes: {list(dag.graph.nodes())}")
    print(f"Edges: {list(dag.graph.edges())}")

    # 2. Mock Dependencies
    mock_queue = AsyncMock()
    mock_event_bus = AsyncMock()
    
    # Create Orchestrator
    orchestrator = AsyncOrchestrator(
        dag=dag, 
        queue=mock_queue, 
        event_bus=mock_event_bus, 
        run_id="test_run_001"
    )
    
    # 3. Mock Event Bus Subscribe to trigger events manually
    # The orchestrator will call subscribe. We capture the handler.
    captured_handler = None
    
    async def capture_subscribe(channel, handler):
        nonlocal captured_handler
        captured_handler = handler
        print(f"🎧 Orchestrator subscribed to '{channel}'")
        
    mock_event_bus.subscribe = capture_subscribe
    
    # 4. Start Execution (Run in background)
    task = asyncio.create_task(orchestrator.execute(timeout=5.0))
    
    # Give it a moment to submit initial nodes
    await asyncio.sleep(0.5)
    
    # 5. Verify: Node A should be submitted (In-degree 0)
    print("\n--- Verification Step 1: Initial Submission ---")
    calls = mock_queue.submit_job.call_args_list
    print(f"submit_job called {len(calls)} times")
    assert len(calls) == 1, "Should only submit Node A initially"
    
    call_args = calls[0].kwargs
    assert call_args["node_id"] == "node_A", "First node must be A"
    print(f"✅ Node A submitted correctly: {call_args['node_id']}")
    
    # 6. Simulate Node A Completion
    print("\n--- Verification Step 2: Simulate Node A Completion ---")
    event_a = NodeCompletedEvent(
        event_type="node_completed",
        run_id="test_run_001",
        node_id="node_A",
        payload={"result": "A_done"}
    )
    
    await captured_handler(event_a)
    await asyncio.sleep(0.5)
    
    # Verify: Node B should now be submitted
    calls = mock_queue.submit_job.call_args_list
    assert len(calls) == 2, "Should submit Node B after A completes"
    assert calls[1].kwargs["node_id"] == "node_B", "Second node must be B"
    print(f"✅ Node B submitted correctly after A completed")
    
    # 7. Simulate Node B Completion
    print("\n--- Verification Step 3: Simulate Node B Completion ---")
    event_b = NodeCompletedEvent(
        event_type="node_completed",
        run_id="test_run_001",
        node_id="node_B",
        payload={"result": "B_done"}
    )
    
    await captured_handler(event_b)
    await asyncio.sleep(0.5)
    
    # Verify: Node C should now be submitted
    calls = mock_queue.submit_job.call_args_list
    assert len(calls) == 3, "Should submit Node C after B completes"
    assert calls[2].kwargs["node_id"] == "node_C", "Third node must be C"
    print(f"✅ Node C submitted correctly after B completed")
    
    # 8. Simulate Node C Completion
    print("\n--- Verification Step 4: Simulate Node C Completion ---")
    event_c = NodeCompletedEvent(
        event_type="node_completed",
        run_id="test_run_001",
        node_id="node_C",
        payload={"result": "C_done"}
    )
    
    await captured_handler(event_c)
    
    # Wait for orchestrator to finish
    try:
        await asyncio.wait_for(task, timeout=2.0)
        print("✅ Orchestrator finished successfully!")
    except asyncio.TimeoutError:
        print("❌ Orchestrator timed out waiting for completion.")
        task.cancel()

    print("\n--- Final Summary ---")
    print(f"Total Jobs Submitted: {len(mock_queue.submit_job.call_args_list)}")
    print(f"Nodes Completed: {orchestrator.completed_nodes}")

if __name__ == "__main__":
    asyncio.run(test_async_orchestrator_flow())
