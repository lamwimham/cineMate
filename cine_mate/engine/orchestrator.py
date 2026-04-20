"""
CineMate Pipeline Orchestrator
Ties together DAG, FSM, and Store to execute the pipeline.
Supports incremental execution (Video Git).
"""

import asyncio
import uuid
from typing import List, Set, Dict, Optional, Callable, Awaitable

from cine_mate.core.models import (
    PipelineRun, NodeExecution, NodeStatus, RunStatus, NodeConfig, ApiMode
)
from cine_mate.core.store import Store
from cine_mate.engine.dag import PipelineDAG
from cine_mate.engine.fsm import NodeFSM, NodeState

# Type alias for node execution function
NodeExecutorFn = Callable[[str, Dict], Awaitable[Dict]]

class Orchestrator:
    """
    Orchestrates the execution of a PipelineRun.
    """
    
    def __init__(
        self, 
        store: Store, 
        run: PipelineRun, 
        dag: PipelineDAG,
        executor_fn: NodeExecutorFn
    ):
        self.store = store
        self.run = run
        self.dag = dag
        self.executor_fn = executor_fn
        
        # Initialize FSMs for all nodes
        self.fsms: Dict[str, NodeFSM] = {
            node_id: NodeFSM(node_id) 
            for node_id in dag.graph.nodes()
        }
        
        # Track completed nodes in this run
        self.completed_nodes: Set[str] = set()
        
    async def execute(self):
        """
        Execute the pipeline.
        If this is a replay (parent_run_id exists), it will reuse artifacts.
        """
        await self.store.create_run(self.run)
        self.run.status = RunStatus.RUNNING
        
        # 1. Identify Dirty/Reusable nodes
        changed_nodes = set()
        
        if self.run.parent_run_id:
            # Load parent run to compare configs
            # For this MVP, we assume the DAG structure is the same, only configs change.
            # We compare current DAG configs with what we *think* the parent had.
            # Ideally, we would store parent DAG configs in DB, but for now we compare against
            # the current DAG if we assume the "change" is what triggered the new run.
            
            # Heuristic for MVP:
            # If a node config differs from "default" (or if we explicitly mark it), it's dirty.
            # But a better way: The Orchestrator is passed the *new* DAG.
            # We need to know what the *old* DAG looked like.
            # Let's assume the Orchestrator receives the *changed* nodes in its constructor or 
            # we detect changes by checking if parent artifacts exist.
            
            # Simpler approach for MVP: 
            # Check if parent artifact exists. If not, it's dirty.
            # But we need to know if the config CHANGED.
            # Since we don't have full history storage of configs yet, 
            # let's add a `changed_nodes` parameter to the Orchestrator.
            pass 
        else:
            # Fresh run: everything is dirty
            changed_nodes = set(self.dag.graph.nodes())
            
        # Temporary Fix for Test: 
        # In a real app, we'd compare configs. Here we just assume the test passed the right DAG.
        # We will implement a basic diff check.
        
        # Check each node: if its config is different from "expected" (hardcoded or DB stored)
        # For now, let's look at the `dag.node_configs`.
        # If parent_run exists, we fetch parent artifacts. 
        # If parent artifact exists AND config matches (somehow), reuse.
        # Since we can't easily match config without history, let's assume the Caller tells us 
        # or we mark nodes.
        
        # IMPROVEMENT: Let's check if we can fetch parent node execution config.
        if self.run.parent_run_id:
            for node_id in self.dag.graph.nodes():
                current_config = self.dag.node_configs.get(node_id, {})
                parent_exec = await self.store.get_node_execution(self.run.parent_run_id, node_id)
                
                if parent_exec and parent_exec.config_snapshot:
                    parent_config = parent_exec.config_snapshot.model_dump(exclude_unset=True)
                    current_config_clean = {k: v for k, v in current_config.items() if v is not None}
                    
                    # DEBUG
                    print(f"  [Diff Check] Node {node_id}:")
                    print(f"    Parent: {parent_config}")
                    print(f"    Current: {current_config_clean}")
                    
                    if parent_config == current_config_clean:
                        pass # Reuse
                    else:
                        changed_nodes.add(node_id)
                else:
                    changed_nodes.add(node_id)
        else:
            changed_nodes = set(self.dag.graph.nodes())

        impact = self.dag.analyze_impact(changed_nodes)
        
        # 2. Process Reusable Nodes
        # If this is a child run, we copy artifacts from parent
        if self.run.parent_run_id:
            await self._reuse_artifacts(self.run.parent_run_id, impact["reusable_nodes"])
            for node_id in impact["reusable_nodes"]:
                self.completed_nodes.add(node_id)
                self.fsms[node_id].state = NodeState.SUCCEEDED
                await self.store.upsert_node_execution(
                    NodeExecution(
                        id=f"exec_{self.run.run_id}_{node_id}",
                        run_id=self.run.run_id,
                        node_id=node_id,
                        status=NodeStatus.SKIPPED
                    )
                )
                print(f"[Reuse] Node {node_id} reused from parent.")

        # 3. Execute Dirty Nodes
        while True:
            ready_nodes = self.dag.get_ready_nodes(self.completed_nodes)
            
            # Filter out already completed (reused) nodes
            active_ready = [n for n in ready_nodes if n not in self.completed_nodes]
            
            if not active_ready:
                if len(self.completed_nodes) == len(self.dag.graph.nodes()):
                    self.run.status = RunStatus.COMPLETED
                    await self.store.update_run_status(self.run.run_id, RunStatus.COMPLETED)
                    print(f"[Run {self.run.run_id}] Completed successfully.")
                    return
                else:
                    raise Exception("Deadlock: No ready nodes but not all completed.")
            
            # Execute ready nodes in parallel
            tasks = []
            for node_id in active_ready:
                self.fsms[node_id].transition("schedule")
                self.fsms[node_id].transition("start")
                
                task = asyncio.create_task(self._execute_node(node_id))
                tasks.append(task)
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for res in results:
                if isinstance(res, Exception):
                    print(f"[Error] {res}")
                    # Handle error: mark run as failed?
                    # For now, just log
                    
    async def _execute_node(self, node_id: str):
        """Execute a single node with FSM and Store updates."""
        fsm = self.fsms[node_id]
        node_config = self.dag.node_configs.get(node_id, {})
        
        exec_id = f"exec_{self.run.run_id}_{node_id}"
        
        try:
            # Update Store: EXECUTING
            await self.store.upsert_node_execution(
                NodeExecution(
                    id=exec_id,
                    run_id=self.run.run_id,
                    node_id=node_id,
                    status=NodeStatus.EXECUTING,
                    config_snapshot=NodeConfig(**node_config)
                )
            )
            
            # Call Executor Function (Mock API call)
            result = await self.executor_fn(node_id, node_config)
            
            # Update Store: SUCCEEDED
            fsm.transition("complete")
            fsm.transition("pass")
            await self.store.upsert_node_execution(
                NodeExecution(
                    id=exec_id,
                    run_id=self.run.run_id,
                    node_id=node_id,
                    status=NodeStatus.SUCCEEDED,
                    config_snapshot=NodeConfig(**node_config)
                )
            )
            
            self.completed_nodes.add(node_id)
            print(f"[Node {node_id}] Succeeded. Output: {result}")
            
        except Exception as e:
            fsm.state = NodeState.FAILED
            await self.store.upsert_node_execution(
                NodeExecution(
                    id=exec_id,
                    run_id=self.run.run_id,
                    node_id=node_id,
                    status=NodeStatus.FAILED,
                    error_msg=str(e),
                    config_snapshot=NodeConfig(**node_config)
                )
            )
            print(f"[Node {node_id}] Failed: {e}")
            raise e

    async def _reuse_artifacts(self, parent_run_id: str, reusable_nodes: List[str]):
        """Copy artifact references from parent run to current run."""
        for node_id in reusable_nodes:
            # Fetch parent artifact
            parent_art = await self.store.get_artifact(parent_run_id, node_id)
            if parent_art:
                # Create new artifact pointing to same blob
                new_art = parent_art.model_copy()
                new_art.id = f"art_{self.run.run_id}_{node_id}"
                new_art.run_id = self.run.run_id
                new_art.is_reused = True
                
                await self.store.link_artifact(new_art)
                print(f"[Reuse] Linked artifact for {node_id} -> {parent_art.blob_hash}")
