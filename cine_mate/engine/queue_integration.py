"""
Engine-Queue Integration Layer

Decouples Engine/Orchestrator from JobQueue implementation.
Provides a clean interface for job submission and status tracking.

Architecture:
    Orchestrator → JobQueueAdapter → JobQueue → Worker
         ↓                              ↓
    FSM callbacks ← EventBus ← Event publishing
"""

from typing import Optional, Dict, Any, Callable
from datetime import datetime

from cine_mate.infra.queue import JobQueue
from cine_mate.infra.event_bus import EventBus
from cine_mate.infra.schemas import (
    JobType,
    JobStatus,
    CineMateEvent,
    NodeCompletedEvent,
    NodeFailedEvent,
)


class JobQueueAdapter:
    """
    Adapter layer between Engine and JobQueue.
    
    Responsibilities:
    1. Translate Engine job requests to JobQueue format
    2. Subscribe to job completion events
    3. Notify Engine callbacks on job status changes
    
    Usage:
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        # Submit job from Engine
        job_id = await adapter.submit_node_job(
            run_id="run_001",
            node_id="img_gen_01",
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "a cat"}
        )
        
        # Register completion callback
        adapter.on_job_complete(node_id, callback_fn)
    """
    
    def __init__(
        self,
        job_queue: JobQueue,
        event_bus: EventBus
    ):
        """
        Initialize adapter.
        
        Args:
            job_queue: JobQueue instance
            event_bus: EventBus instance for event subscription
        """
        self.job_queue = job_queue
        self.event_bus = event_bus
        self._callbacks: Dict[str, Callable] = {}
        
        # Subscribe to job events
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event handlers for job completion/failure"""
        self.event_bus.subscribe("node_completed", self._on_node_completed)
        self.event_bus.subscribe("node_failed", self._on_node_failed)
    
    async def _on_node_completed(self, event: CineMateEvent):
        """Handle node completed event"""
        if isinstance(event, NodeCompletedEvent):
            callback = self._callbacks.get(event.node_id)
            if callback:
                await callback(event)
    
    async def _on_node_failed(self, event: CineMateEvent):
        """Handle node failed event"""
        # Similar to completed, but for failures
        if isinstance(event, NodeFailedEvent):
            callback = self._callbacks.get(event.node_id)
            if callback:
                await callback(event)
    
    def on_job_complete(
        self,
        node_id: str,
        callback: Callable
    ):
        """
        Register callback for job completion.
        
        Args:
            node_id: Node identifier
            callback: Async callback function(event: CineMateEvent)
        """
        self._callbacks[node_id] = callback
    
    def on_job_fail(
        self,
        node_id: str,
        callback: Callable
    ):
        """
        Register callback for job failure.
        
        Args:
            node_id: Node identifier
            callback: Async callback function(event: CineMateEvent)
        """
        self._callbacks[node_id] = callback
    
    async def submit_node_job(
        self,
        run_id: str,
        node_id: str,
        job_type: JobType,
        params: Dict[str, Any]
    ) -> str:
        """
        Submit a job for a node.
        
        Args:
            run_id: Run identifier
            node_id: Node identifier
            job_type: Type of job (TEXT_TO_IMAGE, IMAGE_TO_VIDEO, etc.)
            params: Job parameters
        
        Returns:
            Job ID for tracking
        """
        job_id = await self.job_queue.submit_job(
            run_id=run_id,
            node_id=node_id,
            job_type=job_type,
            params=params
        )
        return job_id
    
    async def get_job_status(self, job_id: str) -> JobStatus:
        """
        Get job status.
        
        Args:
            job_id: Job identifier
        
        Returns:
            JobStatus enum value
        """
        return await self.job_queue.get_job_status(job_id)
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job.
        
        Args:
            job_id: Job identifier
        
        Returns:
            True if cancelled, False otherwise
        """
        return await self.job_queue.cancel_job(job_id)
    
    async def get_all_jobs_status(self, run_id: str) -> Dict[str, JobStatus]:
        """
        Get status of all jobs in a run.
        
        Args:
            run_id: Run identifier
        
        Returns:
            Dict of job_id -> JobStatus
        """
        return await self.job_queue.get_all_jobs_status(run_id)


async def create_engine_queue_integration(
    redis_url: str = "redis://localhost:6379"
) -> JobQueueAdapter:
    """
    Factory function to create Engine-Queue integration.
    
    Args:
        redis_url: Redis connection URL
    
    Returns:
        Configured JobQueueAdapter instance
    """
    job_queue = JobQueue(redis_url=redis_url)
    event_bus = EventBus(redis_url=redis_url)
    
    await job_queue.connect()
    await event_bus.connect()
    
    return JobQueueAdapter(job_queue, event_bus)
