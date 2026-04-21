"""
JobQueue - Async Task Queue for Video Generation

Uses Redis + RQ (Redis Queue) for simple, reliable async job processing.

Architecture (会议决议):
    Engine/DirectorAgent → JobQueue.submit_job() → Redis Queue → Worker
                                                    ↓
    Engine FSM ← EventBus (node_completed) ← Worker completes
"""

import json
import asyncio
from typing import Optional, Dict, Any, Callable
from datetime import datetime

import redis.asyncio as redis_async
import redis
from rq import Queue
from rq.job import Job as RQJob

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


class JobQueueError(Exception):
    """Base exception for JobQueue errors"""
    pass


class JobNotFoundError(JobQueueError):
    """Raised when job is not found"""
    pass


class JobQueue:
    """
    Async Job Queue using Redis + RQ.
    
    Responsibilities:
    1. Accept jobs from Engine (DirectorAgent via EngineTools)
    2. Manage job state in Redis
    3. Dispatch to RQ Worker for execution
    4. Publish events via EventBus
    
    Usage:
        queue = JobQueue(redis_url="redis://localhost:6379")
        await queue.connect()
        
        job_id = await queue.submit_job(
            run_id="run_001",
            node_id="img_gen_01",
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "a cat"}
        )
        
        status = await queue.get_job_status(job_id)
    """
    
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        event_bus: Optional[Any] = None  # EventBus instance
    ):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.rq_queue: Optional[Queue] = None
        self.event_bus = event_bus
        self._connected = False
    
    async def connect(self):
        """Establish connection to Redis"""
        if self._connected:
            return
        
        # Async redis for JobQueue operations
        self.redis = redis_async.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Sync redis for RQ Queue (RQ 2.x requires sync client)
        sync_redis = redis.from_url(self.redis_url, decode_responses=True)
        self.rq_queue = Queue(connection=sync_redis)
        
        self._connected = True
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
        self._connected = False
    
    async def submit_job(
        self,
        run_id: str,
        node_id: str,
        job_type: JobType,
        params: Dict[str, Any],
        max_retries: int = 2,
        priority: int = 0
    ) -> str:
        """
        Submit a job to the async queue.
        
        Args:
            run_id: PipelineRun ID (Video Git Commit)
            node_id: DAG Node ID
            job_type: Type of job (text_to_image, image_to_video, etc.)
            params: Job parameters (prompt, model, seed, etc.)
            max_retries: Maximum retry attempts on failure
            priority: Job priority (0 = normal, higher = more priority)
        
        Returns:
            job_id: Unique job identifier for status tracking
        """
        if not self._connected:
            raise JobQueueError("Not connected. Call connect() first.")
        
        # Create Job record
        job = Job(
            run_id=run_id,
            node_id=node_id,
            job_type=job_type,
            params=params,
            max_retries=max_retries
        )
        
        # Store job metadata in Redis Hash
        job_key = f"job:{job.job_id}"
        await self.redis.hset(
            job_key,
            mapping={
                "job_id": job.job_id,
                "run_id": job.run_id,
                "node_id": job.node_id,
                "job_type": job.job_type.value,
                "params": json.dumps(job.params),
                "status": job.status.value,
                "progress": str(job.progress),
                "retry_count": str(job.retry_count),
                "max_retries": str(job.max_retries),
                "created_at": job.created_at.isoformat(),
            }
        )
        
        # Set expiry (7 days)
        await self.redis.expire(job_key, 7 * 24 * 60 * 60)
        
        # Enqueue to RQ for async execution
        self.rq_queue.enqueue(
            "cine_mate.infra.worker.execute_job",
            job.job_id,
            job_timeout=600,  # 10 minute timeout
            retry_on_failure=True,
            max_retries=max_retries
        )
        
        # Update status to QUEUED
        job.mark_queued()
        await self.redis.hset(
            job_key,
            mapping={
                "status": job.status.value,
                "queued_at": job.queued_at.isoformat(),
            }
        )
        
        # Publish job_submitted event (会议决议：Event-Driven)
        if self.event_bus:
            event = JobSubmittedEvent(
                run_id=run_id,
                node_id=node_id,
                payload={
                    "job_id": job.job_id,
                    "upstream_provider": "pending",
                    "estimated_duration": 60
                }
            )
            await self.event_bus.publish(event)
        
        return job.job_id
    
    async def get_job_status(self, job_id: str) -> JobStatusResponse:
        """
        Get current status of a job.
        
        Args:
            job_id: Job identifier from submit_job()
        
        Returns:
            JobStatusResponse with current state
        
        Raises:
            JobNotFoundError: If job doesn't exist
        """
        if not self._connected:
            raise JobQueueError("Not connected. Call connect() first.")
        
        job_key = f"job:{job_id}"
        
        # Check if job exists
        exists = await self.redis.exists(job_key)
        if not exists:
            raise JobNotFoundError(f"Job {job_id} not found")
        
        # Fetch all fields
        data = await self.redis.hgetall(job_key)
        
        # Helper to get value (handle bytes/str)
        def get_val(key: str, default=None):
            val = data.get(key) or data.get(key.encode())
            if isinstance(val, bytes):
                val = val.decode()
            return val or default
        
        return JobStatusResponse(
            job_id=get_val("job_id"),
            run_id=get_val("run_id"),
            node_id=get_val("node_id"),
            status=JobStatus(get_val("status", "pending")),
            progress=int(get_val("progress", 0)),
            result=json.loads(get_val("result")) if get_val("result") else None,
            error=get_val("error"),
            created_at=datetime.fromisoformat(get_val("created_at")),
            started_at=datetime.fromisoformat(get_val("started_at")) if get_val("started_at") else None,
            completed_at=datetime.fromisoformat(get_val("completed_at")) if get_val("completed_at") else None,
        )
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job if it's still queued.
        
        Returns:
            True if cancelled, False if already running/completed
        """
        if not self._connected:
            raise JobQueueError("Not connected. Call connect() first.")
        
        job_key = f"job:{job_id}"
        current_status = await self.redis.hget(job_key, "status")
        
        # Handle bytes response
        if isinstance(current_status, bytes):
            current_status = current_status.decode()
        
        # Job not found
        if current_status is None:
            return False
        
        if current_status in (JobStatus.RUNNING.value, JobStatus.COMPLETED.value, JobStatus.FAILED.value):
            return False
        
        # Cancel RQ job
        try:
            rq_job = RQJob.fetch(job_id, connection=self.rq_queue.connection)
            rq_job.cancel()
        except Exception:
            pass
        
        # Update status
        await self.redis.hset(job_key, "status", JobStatus.CANCELLED.value)
        return True
    
    async def on_node_completed(self, event: NodeCompletedEvent):
        """
        Handle node_completed event from Engine.
        会议决议：Event-Driven 回调机制
        
        This method is called when Engine completes a node execution.
        It checks for downstream nodes and submits new jobs.
        """
        # This would integrate with the DAG engine
        # For now, just log the event
        print(f"JobQueue: Received node_completed for {event.node_id}")
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics for monitoring"""
        if not self._connected:
            raise JobQueueError("Not connected. Call connect() first.")
        
        stats = {}
        for status in JobStatus:
            count = 0
            async for key in self.redis.scan_iter("job:*"):
                job_status = await self.redis.hget(key, "status")
                if job_status == status.value:
                    count += 1
            stats[status.value] = count
        
        return stats
