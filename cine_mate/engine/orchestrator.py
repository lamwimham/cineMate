"""
CineMate Pipeline Orchestrator
Ties together DAG, FSM, and Store to execute the pipeline.
Supports incremental execution (Video Git) and Event-Driven dependencies.
"""

import asyncio
import uuid
from typing import List, Set, Dict, Optional, Callable, Awaitable, Any

from cine_mate.core.models import (
    PipelineRun, NodeExecution, NodeStatus, RunStatus, NodeConfig, ApiMode
)
from cine_mate.core.store import Store
from cine_mate.engine.dag import PipelineDAG
from cine_mate.engine.fsm import NodeFSM, NodeState
from cine_mate.infra.schemas import NodeCompletedEvent

# Type alias for node execution function
NodeExecutorFn = Callable[[str, Dict], Awaitable[Dict]]

class Orchestrator:
    """
    Orchestrates the execution of a PipelineRun.
    Supports both direct execution and Event-Driven mode.
    """
    
    def __init__(
        self, 
        store: Store, 
        run: PipelineRun, 
        dag: PipelineDAG,
        executor_fn: NodeExecutorFn,
        event_bus: Optional[Any] = None  # EventBus instance for event-driven mode
    ):
        self.store = store
        self.run = run
        self.dag = dag
        self.executor_fn = executor_fn
        self.event_bus = event_bus
        
        # Initialize FSMs for all nodes
        self.fsms: Dict[str, NodeFSM] = {
            node_id: NodeFSM(node_id) 
            for node_id in dag.graph.nodes()
        }
        
        # Track completed nodes in this run
        self.completed_nodes: Set[str] = set()
        
        # Event-driven state
        self._event_subscribed = False
        self._completion_event = asyncio.Event()
    
    async def start_event_listening(self):
        """
        P0 #5: Start listening for events (public method for external use).
        
        Subscribe to node_completed and node_failed events,
        then start the background listener.
        """
        if self.event_bus and not self._event_subscribed:
            self.event_bus.subscribe("node_completed", self._on_node_completed)
            self.event_bus.subscribe("node_failed", self._on_node_failed)
            await self.event_bus.start_listening()
            self._event_subscribed = True
            print("🎧 [Orchestrator] Event listening started.")
    
    async def _on_node_failed(self, event: Any):
        """
        P0 #5: Event callback for node failure.
        Marks the node as failed and logs the error.
        """
        print(f"❌ [Event] Received node_failed for {event.node_id}")
        if event.node_id in self.fsms:
            self.fsms[event.node_id].state = NodeState.FAILED
        
        # For now, don't auto-retry. Log and wait for manual intervention.
        # TODO: Implement retry logic based on retry_count
        
    async def _on_node_completed(self, event: NodeCompletedEvent):
        """
        事件回调：节点完成后触发下游 (参考文档方案)
        
        This method is called when a node execution completes and publishes 
        a node_completed event to the EventBus.
        """
        self.completed_nodes.add(event.node_id)
        print(f"🎧 [Event] Received node_completed for {event.node_id}")
        
        # 找到下游节点
        children = list(self.dag.graph.successors(event.node_id))
        
        for child_id in children:
            # 检查所有父节点是否完成
            parents = list(self.dag.graph.predecessors(child_id))
            if all(p in self.completed_nodes for p in parents):
                print(f"🚀 [Event] Triggering downstream node: {child_id}")
                await self._submit_node(child_id)
        
        # 检查是否所有节点都完成了
        if len(self.completed_nodes) == len(self.dag.graph.nodes()):
            self._completion_event.set()
            
    async def _submit_node(self, node_id: str):
        """Submit a single node for execution."""
        if node_id in self.completed_nodes:
            return
            
        self.fsms[node_id].transition("schedule")
        self.fsms[node_id].transition("start")
        
        task = asyncio.create_task(self._execute_node(node_id))
        await task
        
    async def execute(self):
        """
        Execute the pipeline.
        Supports two modes:
        1. Event-Driven Mode (if event_bus is provided)
        2. Direct Execution Mode (default)
        """
        await self.store.create_run(self.run)
        self.run.status = RunStatus.RUNNING
        
        # 1. Identify Dirty/Reusable nodes
        changed_nodes = set()
        
        if self.run.parent_run_id:
            for node_id in self.dag.graph.nodes():
                current_config = self.dag.node_configs.get(node_id, {})
                parent_exec = await self.store.get_node_execution(self.run.parent_run_id, node_id)
                
                if parent_exec and parent_exec.config_snapshot:
                    parent_config = parent_exec.config_snapshot.model_dump(exclude_unset=True)
                    current_config_clean = {k: v for k, v in current_config.items() if v is not None}
                    
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
        if self.event_bus and not self._event_subscribed:
            await self._execute_event_driven(impact["dirty_nodes"])
        else:
            await self._execute_direct(impact["dirty_nodes"])
            
    async def _execute_event_driven(self, dirty_nodes: Set[str]):
        """
        Event-Driven Execution Mode.
        Submits nodes and waits for node_completed events to trigger downstream nodes.
        """
        print("🔄 Switching to Event-Driven Execution Mode...")
        
        # Subscribe to node_completed and node_failed events (P0 #5)
        await self.start_event_listening()
        
        # Submit initial nodes (nodes with no dependencies or all deps completed)
        initial_nodes = [
            n for n in dirty_nodes 
            if not list(self.dag.graph.predecessors(n)) or 
            all(p in self.completed_nodes for p in self.dag.graph.predecessors(n))
        ]
        
        print(f"📤 Submitting initial nodes: {initial_nodes}")
        for node_id in initial_nodes:
            await self._submit_node(node_id)
            
        # Wait for all nodes to complete
        if len(self.completed_nodes) < len(self.dag.graph.nodes()):
            print("⏳ Waiting for all nodes to complete via events...")
            await self._completion_event.wait()
            
        self.run.status = RunStatus.COMPLETED
        await self.store.update_run_status(self.run.run_id, RunStatus.COMPLETED)
        print(f"[Run {self.run.run_id}] Completed successfully (Event-Driven).")
        
    async def _execute_direct(self, dirty_nodes: Set[str]):
        """Direct Execution Mode (original behavior)."""
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
            
            # P0 #4: Publish node_completed event
            if self.event_bus:
                from cine_mate.infra.schemas import NodeCompletedEvent
                await self.event_bus.publish(NodeCompletedEvent(
                    run_id=self.run.run_id,
                    node_id=node_id,
                    payload={
                        "result": result,
                        "status": "succeeded"
                    }
                ))
            
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
            
            # P0 #4: Publish node_failed event
            if self.event_bus:
                from cine_mate.infra.schemas import NodeFailedEvent
                await self.event_bus.publish(NodeFailedEvent(
                    run_id=self.run.run_id,
                    node_id=node_id,
                    payload={
                        "error_code": "EXECUTION_ERROR",
                        "error_msg": str(e),
                        "retry_count": 0
                    }
                ))
            
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
