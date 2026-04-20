"""
CineMate Infra - Async Infrastructure

Job Queue + Event Bus for async video generation tasks.

会议决议：2026-04-22 Interface Alignment Meeting
"""

from cine_mate.infra.schemas import (
    Job,
    JobStatus,
    JobType,
    JobStatusResponse,
    CineMateEvent,
    NodeCompletedEvent,
    NodeFailedEvent,
    JobSubmittedEvent,
)
from cine_mate.infra.queue import JobQueue
from cine_mate.infra.event_bus import EventBus
from cine_mate.infra.event_bus import (
    publish_node_completed,
    publish_node_failed,
    publish_job_submitted,
)

__all__ = [
    # Schemas
    "Job",
    "JobStatus",
    "JobType",
    "JobStatusResponse",
    "CineMateEvent",
    "NodeCompletedEvent",
    "NodeFailedEvent",
    "JobSubmittedEvent",
    # Components
    "JobQueue",
    "EventBus",
    # Convenience functions
    "publish_node_completed",
    "publish_node_failed",
    "publish_job_submitted",
]
