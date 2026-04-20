"""
CineMate Core Data Models (Pydantic V2)
Mirrors the SQLite schema for the Local-First Video Git engine.
Includes Commercial/BYOK support.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# --- Enums ---

class ApiMode(str, Enum):
    MANAGED = "managed"   # Use CineMate Credits (Default)
    BYOK = "byok"         # Bring Your Own Key

class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NodeStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"  # Reused from parent
    CANCELLED = "cancelled"


# --- Core Git-like Models ---

class PipelineRun(BaseModel):
    """
    Represents a "Commit" in Video Git.
    Every generation or modification creates a new Run.
    """
    run_id: str  # e.g., "run_001"
    parent_run_id: Optional[str] = None  # Git Parent
    branch_name: Optional[str] = "main"  # Git Branch
    commit_msg: Optional[str] = None  # e.g., "Fix scene 2 lighting"
    
    status: RunStatus = RunStatus.PENDING
    dag_snapshot: Optional[Dict[str, Any]] = None  # Snapshot of the DAG structure
    
    trace_id: Optional[str] = None  # Link to Observability Trace
    created_at: datetime = Field(default_factory=datetime.now)

    # Metadata
    root_hash: Optional[str] = None  # Hash of the final DAG state


class NodeConfig(BaseModel):
    """Snapshot of configuration for a specific node execution"""
    model_name: Optional[str] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    style_params: Optional[Dict[str, Any]] = None
    
    # Commercial Context
    billing_mode: Optional[ApiMode] = ApiMode.MANAGED
    
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict)


class NodeExecution(BaseModel):
    """
    Represents the execution state of a single logical node in a Run.
    Tracks FSM state and external job IDs for crash recovery.
    """
    id: str  # e.g., "exec_001_img_gen_02"
    run_id: str
    node_id: str  # Logical ID, e.g., "img_gen_02"
    
    status: NodeStatus = NodeStatus.PENDING
    retry_count: int = 0
    
    # External API info for crash recovery (e.g., Kling Task ID)
    external_api_provider: Optional[str] = None
    external_job_id: Optional[str] = None
    
    # Error tracking
    error_msg: Optional[str] = None
    error_traceback: Optional[str] = None
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Configuration used for this specific execution
    config_snapshot: Optional[NodeConfig] = None


class BlobMetadata(BaseModel):
    """Physical storage info (Content-Addressable)"""
    blob_id: str  # SHA256 Hash
    relative_path: str  # e.g., "objects/ab/cdef...mp4"
    file_size_bytes: int = 0
    mime_type: Optional[str] = None


class Artifact(BaseModel):
    """
    Logical link: A specific Node in a Run points to a physical Blob.
    """
    id: str  # e.g., "art_001"
    run_id: str
    node_id: str
    blob_hash: Optional[str] = None  # FK to Blobs
    
    # Metadata specific to this artifact generation
    metadata: Optional[Dict[str, Any]] = None  # e.g., {"cost": 0.5, "prompt": "..."}
    is_reused: bool = False  # True if symlinked from a parent run
    
    created_at: datetime = Field(default_factory=datetime.now)


# --- Observability & Billing Models ---

class TraceLog(BaseModel):
    """
    Records the Agent's thought process, costs, and latency for a user request.
    Crucial for auditing user disputes and billing accuracy.
    """
    trace_id: str
    user_input: str
    agent_response_summary: Optional[str] = None
    
    # Billing breakdown
    cost_llm: float = 0.0
    cost_generation: float = 0.0
    total_cost: float = 0.0
    currency: str = "CNY"  # or USD/Credits
    
    # Routing info
    billing_mode: ApiMode = ApiMode.MANAGED
    route_provider: Optional[str] = None  # e.g., "Kling_Pro", "Runway_Gen3"
    
    latency_seconds: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.now)


class UserSettings(BaseModel):
    """
    Local client configuration.
    Defines how the client interacts with the Cloud Gateway.
    """
    user_id: str
    
    # Global Billing Mode Preference
    default_api_mode: ApiMode = ApiMode.MANAGED
    
    # BYOK Configuration (Keys themselves should be stored in OS Keychain,
    # this stores metadata/hashes)
    byok_config: Optional[Dict[str, Any]] = None
    # Example: {"openai_key_hash": "sha256...", "kling_key_hash": "sha256..."}
    
    # Credits Cache (Local cache of server balance)
    managed_credits_balance: float = 0.0
    last_sync_at: Optional[datetime] = None

