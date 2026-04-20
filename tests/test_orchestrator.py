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
    """Mock function simulating an API call."""
    print(f"  -> Executing {node_id} with config {config}...")
    await asyncio.sleep(0.1) # Simulate delay
    return {"result": f"fake_{node_id}_output"}

async def test_orchestrator():
    db_path = Path("/tmp/cinemate_orch_test.db")
    if db_path.exists():
        db_path.unlink()
        
    store = Store(db_path)
    await store.init_db()

    # 1. Define a simple DAG: A -> B -> C
    dag = PipelineDAG()
    dag.add_node("node_A", "script_gen", {"prompt": "Write a script"})
    dag.add_node("node_B", "img_gen", {"prompt": "Generate image from script"})
    dag.add_node("node_C", "vid_gen", {"prompt": "Animate image"})
    
    dag.add_edge("node_A", "node_B")
    dag.add_edge("node_B", "node_C")

    # 2. Create Run and Orchestrator
    run = PipelineRun(run_id="run_001", status=RunStatus.RUNNING)
    orch = Orchestrator(store, run, dag, mock_executor)

    # 3. Execute
    await orch.execute()
    
    # 4. Verify
    print("\n--- Verification ---")
    art_a = await store.get_artifact("run_001", "node_A")
    assert art_a is None # Mock executor didn't link artifacts yet
    
    # Check node statuses in DB
    node_b = await store.get_node_execution("run_001", "node_B")
    assert node_b.status.value == "succeeded"
    print("✅ Orchestrator Test Passed")

asyncio.run(test_orchestrator())