"""
CineMate Engine Tools for AgentScope
Maps the CineMate Core Engine to AgentScope Toolkit functions.

Design Goals:
1. Async-compatible (align with copaw's Async Infra).
2. Simple interfaces for easy Agent parsing.
3. Type-hinted for JSON schema generation.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from agentscope.tool import Toolkit, ToolResponse

from cine_mate.core.store import Store
from cine_mate.core.models import PipelineRun, RunStatus
from cine_mate.engine.dag import PipelineDAG
from cine_mate.engine.orchestrator import Orchestrator


class EngineTools:
    """
    Manager class for CineMate Engine Tools.
    Maintains the Store instance and provides methods for the Agent.
    """

    def __init__(self, store_path: str = "./cinemate.db"):
        self.store = Store(store_path)
        # We assume a standard DAG config for the tool, 
        # or pass it dynamically. For now, simple pipeline.
        
    async def init_db(self):
        await self.store.init_db()

    # --- Tool Functions ---

    async def create_video(
        self, 
        prompt: str, 
        style: Optional[str] = None,
        parent_run_id: Optional[str] = None
    ) -> ToolResponse:
        """
        Create a new video pipeline run or fork an existing one.
        
        Args:
            prompt: The user's natural language request.
            style: Optional style/skill to apply (e.g., "wong-kar-wai").
            parent_run_id: If forking, the ID of the run to modify.
        """
        run_id = f"run_{asyncio.get_event_loop().time():.0f}" # Simple ID generation for now
        commit_msg = prompt
        
        run = PipelineRun(
            run_id=run_id,
            parent_run_id=parent_run_id,
            commit_msg=commit_msg,
            status=RunStatus.PENDING
        )
        
        # For MVP, we just record the request. Real execution is triggered by Orchestrator.
        # In a real tool, we would call Orchestrator here.
        await self.store.create_run(run)
        
        result = {
            "run_id": run_id,
            "status": "created",
            "message": f"Pipeline {run_id} created successfully. Prompt queued."
        }
        return ToolResponse(content=[{"type": "text", "text": json.dumps(result, indent=2)}])

    async def get_run_status(self, run_id: str) -> ToolResponse:
        """
        Get the status and progress of a specific run.
        
        Args:
            run_id: The ID of the run to query.
        """
        run = await self.store.get_run(run_id)
        if not run:
            return ToolResponse(content=[{"type": "text", "text": json.dumps({"error": "Run not found"})}])
        
        # Fetch node execution statuses for progress
        nodes = await self.store.find_stuck_executions() # Just a placeholder for now
        # Real implementation would fetch all nodes for this run
        
        result = {
            "run_id": run.run_id,
            "status": run.status.value,
            "parent": run.parent_run_id,
            "created_at": run.created_at.isoformat()
        }
        return ToolResponse(content=[{"type": "text", "text": json.dumps(result, indent=2)}])

    async def get_run_list(self) -> ToolResponse:
        """List recent video runs."""
        # Placeholder for store.list_runs()
        result = {"runs": ["list", "of", "run_ids"]}
        return ToolResponse(content=[{"type": "text", "text": json.dumps(result, indent=2)}])


def register_engine_tools(toolkit: Toolkit, store_path: str = "./cinemate.db") -> EngineTools:
    """
    Registers CineMate engine tools with an AgentScope Toolkit.
    """
    manager = EngineTools(store_path)
    
    # Register methods as tools
    toolkit.register_tool_function(manager.create_video)
    toolkit.register_tool_function(manager.get_run_status)
    toolkit.register_tool_function(manager.get_run_list)
    
    return manager
