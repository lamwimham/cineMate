"""
CineMate API Schemas (Pydantic V2)
Request/Response models for the FastAPI REST API.
Mirrors core data models with API-specific additions (e.g., pagination).
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# --- Enums ---

class RunStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatusEnum(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


# --- Request Schemas ---

class CreateRunRequest(BaseModel):
    """Request body for creating a new video pipeline run."""
    prompt: str = Field(..., description="Natural language video description")
    parent_run_id: Optional[str] = Field(None, description="Fork from existing run ID")
    branch_name: Optional[str] = Field("main", description="Git branch name")
    style: Optional[str] = Field(None, description="Skill/style to apply (e.g., 'cyberpunk')")


class UpdateRunRequest(BaseModel):
    """Request body for updating run status."""
    status: RunStatusEnum = Field(..., description="New run status")
    commit_msg: Optional[str] = Field(None, description="Update commit message")


# --- Response Schemas ---

class NodeStatusResponse(BaseModel):
    """Node execution status for a run."""
    node_id: str
    status: NodeStatusEnum
    retry_count: int = 0
    error_msg: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RunResponse(BaseModel):
    """PipelineRun response with summary info."""
    run_id: str
    parent_run_id: Optional[str] = None
    branch_name: Optional[str] = "main"
    commit_msg: Optional[str] = None
    status: RunStatusEnum
    node_count: int = 0
    completed_nodes: int = 0
    created_at: datetime

    @classmethod
    def from_core(cls, run, node_count: int = 0, completed_nodes: int = 0) -> "RunResponse":
        """Construct from core PipelineRun model."""
        return cls(
            run_id=run.run_id,
            parent_run_id=run.parent_run_id,
            branch_name=run.branch_name,
            commit_msg=run.commit_msg,
            status=RunStatusEnum(run.status.value),
            node_count=node_count,
            completed_nodes=completed_nodes,
            created_at=run.created_at,
        )


class RunDetailResponse(BaseModel):
    """Detailed run response with node-level info."""
    run_id: str
    parent_run_id: Optional[str] = None
    branch_name: Optional[str] = "main"
    commit_msg: Optional[str] = None
    status: RunStatusEnum
    nodes: List[NodeStatusResponse] = []
    created_at: datetime

    @classmethod
    def from_core(cls, run, nodes: list) -> "RunDetailResponse":
        """Construct from core PipelineRun + node executions."""
        return cls(
            run_id=run.run_id,
            parent_run_id=run.parent_run_id,
            branch_name=run.branch_name,
            commit_msg=run.commit_msg,
            status=RunStatusEnum(run.status.value),
            nodes=[
                NodeStatusResponse(
                    node_id=n.node_id,
                    status=NodeStatusEnum(n.status.value),
                    retry_count=n.retry_count,
                    error_msg=n.error_msg,
                    started_at=n.started_at,
                    completed_at=n.completed_at,
                )
                for n in nodes
            ],
            created_at=run.created_at,
        )


class RunListResponse(BaseModel):
    """Paginated list of runs."""
    runs: List[RunResponse]
    total: int
    limit: int


class BranchResponse(BaseModel):
    """Branch summary."""
    branch_name: str
    run_count: int
    latest_run: Optional[datetime] = None


class DiffNodeResponse(BaseModel):
    """Node-level diff between two runs."""
    node_id: str
    base_status: Optional[str] = None
    target_status: Optional[str] = None
    change_type: str  # "added", "deleted", "changed", "same"


class DiffResponse(BaseModel):
    """Diff between two runs."""
    base_run_id: str
    target_run_id: str
    base_commit: Optional[str] = None
    target_commit: Optional[str] = None
    nodes: List[DiffNodeResponse]
    summary: Dict[str, int]  # {"added": N, "deleted": N, ...}


# --- WebSocket Schemas ---

class WsProgressMessage(BaseModel):
    """WebSocket progress update message."""
    type: str = "progress"  # "progress", "node_update", "complete", "error"
    run_id: str
    node_id: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
