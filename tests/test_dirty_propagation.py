import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from cine_mate.core.store import Store
from cine_mate.core.models import PipelineRun, RunStatus
from cine_mate.engine.dag import PipelineDAG
from cine_mate.engine.orchestrator import Orchestrator
from pathlib import Path

async def mock_executor(node_id: str, config: dict) -> dict:
    print(f"  -> Executing {node_id}...")
    await asyncio.sleep(0.05)
    return {"result": "mock_output"}

async def test_dirty_propagation():
    """
    Scenario:
    Run 1: A -> B -> C (All run)
    Run 2: Parent is Run 1. Change B.
    Expected:
    - A is Reused (Skipped)
    - B is Re-run (Dirty)
    - C is Re-run (Dirty, downstream of B)
    """
    db_path = Path("/tmp/cinemate_dirty_test.db")
    if db_path.exists():
        db_path.unlink()
        
    store = Store(db_path)
    await store.init_db()

    # Define DAG: A -> B -> C
    dag = PipelineDAG()
    dag.add_node("node_A", "script", {"prompt": "v1"})
    dag.add_node("node_B", "img", {"prompt": "v1"})
    dag.add_node("node_C", "vid", {"prompt": "v1"})
    dag.add_edge("node_A", "node_B")
    dag.add_edge("node_B", "node_C")

    # 1. Execute Run 1
    run1 = PipelineRun(run_id="run_v1", status=RunStatus.RUNNING)
    orch1 = Orchestrator(store, run1, dag, mock_executor)
    await orch1.execute()
    print("\n--- Run 1 Completed ---")

    # 2. Setup Run 2 (Dirty Propagation)
    # Modify config for B
    dag.add_node("node_B", "img", {"prompt": "v2_modified"})
    
    run2 = PipelineRun(run_id="run_v2", parent_run_id="run_v1", status=RunStatus.RUNNING)
    orch2 = Orchestrator(store, run2, dag, mock_executor)
    
    # Manually trigger dirty analysis for test verification
    changed_nodes = {"node_B"}
    impact = dag.analyze_impact(changed_nodes)
    
    print(f"\n[Analysis] Changed: {changed_nodes}")
    print(f"  - Dirty Nodes (to re-run): {sorted(impact['dirty_nodes'])}")
    print(f"  - Reusable Nodes (to skip): {sorted(impact['reusable_nodes'])}")
    
    # Assertions for Dirty Analysis
    assert "node_A" in impact["reusable_nodes"]
    assert "node_B" in impact["dirty_nodes"]
    assert "node_C" in impact["dirty_nodes"] # Downstream
    
    # 3. Execute Run 2
    print("\n--- Starting Run 2 (Resume) ---")
    await orch2.execute()
    
    # 4. Verify DB State
    # Node A should be SKIPPED
    node_a = await store.get_node_execution("run_v2", "node_A")
    assert node_a.status.value == "skipped", f"Expected A to be skipped, got {node_a.status.value}"
    print(f"✅ Node A Status: {node_a.status.value} (Reused)")

    # Node B should be SUCCEEDED
    node_b = await store.get_node_execution("run_v2", "node_B")
    assert node_b.status.value == "succeeded"
    print(f"✅ Node B Status: {node_b.status.value} (Re-run)")
    
    print("✅ Dirty Propagation Test Passed")

asyncio.run(test_dirty_propagation())