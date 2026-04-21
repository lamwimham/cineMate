"""
CineMate Engine Module

Core orchestration and execution engine for video production workflows.
"""

from cine_mate.engine.queue_integration import (
    JobQueueAdapter,
    create_engine_queue_integration,
)

__all__ = [
    "JobQueueAdapter",
    "create_engine_queue_integration",
]
