"""
CineMate Infra - Schema Definitions (Event Schema v1.0)

会议决议：2026-04-22 Interface Alignment Meeting
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import uuid


# =============================================================================
# Event Schema v1.0 (会议决议)
# =============================================================================

class CineMateEvent(BaseModel):
    """
    Base event schema for all CineMate events.
    
    会议决议 v1.0 - 所有事件继承此基类
    """
    event_type: str  # "node_completed", "node_failed", "job_submitted"
    run_id: str
    node_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: Dict[str, Any]


class NodeCompletedEvent(CineMateEvent):
    """
    Published when a node execution completes successfully.
    
    Payload structure:
    {
        "artifact_hash": str,      # CAS content hash
        "output_url": str,         # Output file URL/path
        "cost": float              # Actual cost in credits
    }
    """
    event_type: str = "node_completed"
    payload: Dict[str, Any]  # {artifact_hash, output_url, cost}


class NodeFailedEvent(CineMateEvent):
    """
    Published when a node execution fails.
    
    Payload structure:
    {
        "error_code": str,         # e.g., "UPSTREAM_ERROR", "TIMEOUT"
        "error_msg": str,          # Human-readable message
        "retry_count": int         # Number of retries attempted
    }
    """
    event_type: str = "node_failed"
    payload: Dict[str, Any]  # {error_code, error_msg, retry_count}


class JobSubmittedEvent(CineMateEvent):
    """
    Published when a job is submitted to the queue.
    
    Payload structure:
    {
        "job_id": str,             # Queue job ID
        "upstream_provider": str,  # e.g., "kling", "runway"
        "estimated_duration": int  # Estimated seconds
    }
    """
    event_type: str = "job_submitted"
    payload: Dict[str, Any]  # {job_id, upstream_provider, estimated_duration}


# =============================================================================
# Job Queue Schema
# =============================================================================

class JobStatus(str, Enum):
    """Job lifecycle states"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    """Supported job types for video generation"""
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_VIDEO = "image_to_video"
    TEXT_TO_VIDEO = "text_to_video"
    TTS = "tts"
    VIDEO_EDIT = "video_edit"


class Job(BaseModel):
    """
    Represents an async job in the queue.
    
    Lifecycle:
    1. Created (PENDING) → submitted by Engine
    2. Queued → waiting in Redis queue
    3. Running → being executed by Worker
    4. Completed/Failed → terminal state
    """
    # Identity
    job_id: str = Field(default_factory=lambda: f"job_{uuid.uuid4().hex[:12]}")
    run_id: str
    node_id: str
    job_type: JobType
    
    # Parameters (from Engine/DirectorAgent)
    params: Dict[str, Any]
    
    # Status tracking
    status: JobStatus = JobStatus.PENDING
    progress: int = Field(default=0, ge=0, le=100)
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.now)
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Retry policy
    retry_count: int = 0
    max_retries: int = 2
    
    # Result / Error
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # External API tracking
    external_provider: Optional[str] = None
    external_job_id: Optional[str] = None
    
    def mark_queued(self):
        self.status = JobStatus.QUEUED
        self.queued_at = datetime.now()
    
    def mark_running(self):
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now()
    
    def mark_completed(self, result: Dict[str, Any]):
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        self.progress = 100
    
    def mark_failed(self, error: str):
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
    
    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries


class JobStatusResponse(BaseModel):
    """Response for JobQueue.get_job_status()"""
    job_id: str
    run_id: str
    node_id: str
    status: JobStatus
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
