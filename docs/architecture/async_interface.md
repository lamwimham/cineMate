# Async Interface Specification

> **Version**: 1.0  
> **Date**: 2026-04-22  
> **Status**: Approved (Interface Alignment Meeting)  
> **Owner**: copaw (Infra), hermes (Agent)

---

## 1. Overview

This document defines the interface between:
- **Engine (FSM/Orchestrator)** - hermes
- **Job Queue** - copaw
- **Event Bus** - copaw

**Communication Pattern**: Event-Driven Architecture using Redis Pub/Sub

---

## 2. Event Bus

### 2.1 Technology

**Selected**: Redis Pub/Sub (simplified for MVP)

**Rationale**:
- Lower latency than Redis Stream
- Sufficient for current use case
- Can upgrade to Stream later if needed

### 2.2 Event Schema v1.0

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class CineMateEvent(BaseModel):
    """Base event structure for all CineMate events"""
    event_type: str           # Event type identifier
    run_id: str               # Pipeline run ID
    node_id: str              # Node ID
    timestamp: datetime       # Event timestamp
    payload: Dict[str, Any]   # Event-specific data

class NodeCompletedEvent(CineMateEvent):
    """Emitted when a node execution completes successfully"""
    event_type: str = "node_completed"
    payload: Dict[str, Any] = {
        "artifact_hash": str,      # SHA256 hash of output blob
        "output_url": str,         # Pre-signed URL for result
        "cost": float,             # Actual cost in credits
        "duration_seconds": int    # Execution time
    }

class NodeFailedEvent(CineMateEvent):
    """Emitted when a node execution fails"""
    event_type: str = "node_failed"
    payload: Dict[str, Any] = {
        "error_code": str,         # Error classification
        "error_msg": str,          # Human-readable message
        "retry_count": int,        # Current retry attempt
        "max_retries": int         # Max allowed retries
    }

class JobSubmittedEvent(CineMateEvent):
    """Emitted when a job is submitted to upstream provider"""
    event_type: str = "job_submitted"
    payload: Dict[str, Any] = {
        "job_id": str,             # Upstream job ID
        "upstream_provider": str,  # "kling", "runway", etc.
        "estimated_duration": int, # Estimated seconds
        "params": Dict[str, Any]   # Job parameters
    }

class JobStatusUpdateEvent(CineMateEvent):
    """Periodic status update from upstream"""
    event_type: str = "job_status_update"
    payload: Dict[str, Any] = {
        "job_id": str,
        "status": str,             # "queued", "processing", "completed", "failed"
        "progress_percent": int,   # 0-100
        "message": str             # Status message
    }
```

### 2.3 EventBus Interface

```python
from typing import Callable, Awaitable
import redis.asyncio as redis

class EventBus:
    """
    Event Bus using Redis Pub/Sub
    
    Responsibilities:
    1. Publish events from Engine/Queue
    2. Subscribe handlers for event types
    3. Route events to appropriate handlers
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        self._handlers: Dict[str, List[Callable]] = {}
    
    async def connect(self):
        """Establish Redis connection"""
        self._redis = await redis.from_url(self._redis_url)
        self._pubsub = self._redis.pubsub()
    
    async def publish(self, channel: str, event: CineMateEvent) -> bool:
        """
        Publish event to channel
        
        Args:
            channel: Event channel (e.g., "cinemate.events.node")
            event: CineMateEvent instance
        
        Returns:
            True if published successfully
        """
        if not self._redis:
            raise RuntimeError("EventBus not connected")
        
        message = event.model_dump_json()
        await self._redis.publish(channel, message)
        return True
    
    async def subscribe(self, channel: str, handler: Callable[[CineMateEvent], Awaitable[None]]):
        """
        Subscribe handler to channel
        
        Args:
            channel: Channel pattern (e.g., "cinemate.events.*")
            handler: Async handler function
        """
        if not self._pubsub:
            raise RuntimeError("EventBus not connected")
        
        await self._pubsub.subscribe(channel)
        
        # Store handler
        if channel not in self._handlers:
            self._handlers[channel] = []
        self._handlers[channel].append(handler)
    
    async def listen(self):
        """Start listening for events (blocking)"""
        if not self._pubsub:
            raise RuntimeError("EventBus not connected")
        
        async for message in self._pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"].decode()
                data = json.loads(message["data"])
                
                # Reconstruct event
                event = CineMateEvent(**data)
                
                # Call handlers
                for handler in self._handlers.get(channel, []):
                    await handler(event)
    
    async def disconnect(self):
        """Close connections"""
        if self._pubsub:
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()
```

### 2.4 Event Channels

| Channel | Description | Publisher | Subscribers |
|---------|-------------|-----------|-------------|
| `cinemate.events.node` | Node execution events | Orchestrator | JobQueue |
| `cinemate.events.job` | Job lifecycle events | JobQueue | Orchestrator |
| `cinemate.events.status` | Status updates | JobQueue | Agent |

---

## 3. Job Queue

### 3.1 Job Schema

```python
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Job(BaseModel):
    """Job model for async task execution"""
    job_id: str               # Unique job ID
    run_id: str               # Associated pipeline run
    node_id: str              # Associated node
    job_type: str             # "text_to_image", "image_to_video", etc.
    params: Dict[str, Any]    # Job parameters
    
    status: JobStatus = JobStatus.PENDING
    priority: int = 0         # Higher = more priority
    
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    retry_count: int = 0
    max_retries: int = 2
    
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # External tracking
    external_job_id: Optional[str] = None  # Upstream provider ID
    upstream_provider: Optional[str] = None
```

### 3.2 JobQueue Interface

```python
class JobQueue:
    """
    Async Job Queue using Redis
    
    Responsibilities:
    1. Accept job submissions from Engine
    2. Manage job state (pending → queued → running → completed/failed)
    3. Distribute jobs to workers
    4. Handle upstream callbacks
    5. Publish events via EventBus
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", event_bus: Optional[EventBus] = None):
        self.redis_url = redis_url
        self.event_bus = event_bus
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Establish Redis connection"""
        self._redis = await redis.from_url(self.redis_url)
    
    async def submit_job(
        self,
        run_id: str,
        node_id: str,
        job_type: str,
        params: Dict[str, Any],
        priority: int = 0
    ) -> str:
        """
        Submit a job to the queue
        
        Args:
            run_id: Pipeline run ID
            node_id: Node ID
            job_type: Type of job (text_to_image, etc.)
            params: Job parameters
            priority: Job priority (higher = more urgent)
        
        Returns:
            job_id: Unique job identifier
        """
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        
        job = Job(
            job_id=job_id,
            run_id=run_id,
            node_id=node_id,
            job_type=job_type,
            params=params,
            priority=priority,
            created_at=datetime.now()
        )
        
        # Store job
        await self._store_job(job)
        
        # Add to priority queue
        await self._redis.zadd(
            "cinemate:job_queue",
            {job_id: priority}
        )
        
        # Publish event
        if self.event_bus:
            await self.event_bus.publish(
                "cinemate.events.job",
                JobSubmittedEvent(
                    run_id=run_id,
                    node_id=node_id,
                    payload={
                        "job_id": job_id,
                        "job_type": job_type,
                        "upstream_provider": self._select_provider(job_type)
                    }
                )
            )
        
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Job]:
        """
        Get job status and details
        
        Args:
            job_id: Job ID
        
        Returns:
            Job object or None if not found
        """
        job_data = await self._redis.get(f"cinemate:job:{job_id}")
        if job_data:
            return Job.model_validate_json(job_data)
        return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a pending or queued job
        
        Args:
            job_id: Job ID
        
        Returns:
            True if cancelled, False if already running/completed
        """
        job = await self.get_job_status(job_id)
        if not job or job.status in [JobStatus.RUNNING, JobStatus.COMPLETED, JobStatus.FAILED]:
            return False
        
        job.status = JobStatus.CANCELLED
        await self._store_job(job)
        await self._redis.zrem("cinemate:job_queue", job_id)
        
        return True
    
    async def on_node_completed(self, event: NodeCompletedEvent):
        """
        Event handler: Node completed in Engine
        
        Trigger: Orchestrator publishes node_completed
        Action: Find downstream nodes, submit new jobs
        """
        # Get DAG from Store
        dag = await self._get_dag(event.run_id)
        
        # Find downstream nodes
        downstream = dag.get_downstream(event.node_id)
        downstream.remove(event.node_id)  # Exclude self
        
        # Submit jobs for ready downstream nodes
        for node_id in downstream:
            if await self._is_node_ready(event.run_id, node_id):
                await self.submit_job(
                    run_id=event.run_id,
                    node_id=node_id,
                    job_type=dag.get_node_type(node_id),
                    params=dag.get_node_params(node_id)
                )
    
    async def _store_job(self, job: Job):
        """Persist job to Redis"""
        await self._redis.set(
            f"cinemate:job:{job.job_id}",
            job.model_dump_json(),
            ex=86400  # 24h TTL
        )
    
    def _select_provider(self, job_type: str) -> str:
        """Select upstream provider based on job type"""
        providers = {
            "text_to_image": "openai",
            "image_to_video": "kling",
            "video_enhance": "runway"
        }
        return providers.get(job_type, "kling")
    
    async def _get_dag(self, run_id: str) -> PipelineDAG:
        """Load DAG from Store"""
        # Implementation depends on Store interface
        pass
    
    async def _is_node_ready(self, run_id: str, node_id: str) -> bool:
        """Check if all dependencies are satisfied"""
        # Implementation depends on Store interface
        pass
```

---

## 4. FSM ↔ Queue Callback Flow

### 4.1 Sequence Diagram

```
Orchestrator          EventBus           JobQueue          Worker
    |                    |                   |                |
    |-- execute_node ----|                   |                |
    |                    |                   |                |
    |-- FSM: SUCCEEDED --|                   |                |
    |                    |                   |                |
    |-- publish(node_completed)              |                |
    |-------------------->|                   |                |
    |                    |-- on_node_completed|                |
    |                    |------------------>|                |
    |                    |                   |                |
    |                    |                   |-- submit_job -->|
    |                    |                   |                |
    |                    |<-- publish(job_submitted)          |
    |                    |-------------------|                |
    |<-- Event: job_submitted                 |                |
    |                    |                   |                |
    |                    |                   |                |-- execute()
    |                    |                   |                |
    |                    |                   |<-- complete ---|
    |                    |<-- publish(node_completed)         |
    |<-- Event: node_completed                |                |
    |                    |                   |                |
```

### 4.2 Key Points

1. **Event-Driven**: All communication via EventBus
2. **Decoupled**: Orchestrator doesn't know about JobQueue internals
3. **Async**: Non-blocking, supports concurrent execution
4. **Extensible**: Easy to add new event types

---

## 5. Integration with Engine

### 5.1 Orchestrator Modifications

```python
class Orchestrator:
    def __init__(self, store: Store, event_bus: EventBus):
        self.store = store
        self.event_bus = event_bus
    
    async def _execute_node(self, node_id: str):
        # ... existing execution logic ...
        
        # On success
        if success:
            await self.event_bus.publish(
                "cinemate.events.node",
                NodeCompletedEvent(
                    run_id=self.run.run_id,
                    node_id=node_id,
                    payload={
                        "artifact_hash": artifact.blob_hash,
                        "output_url": artifact.url,
                        "cost": cost
                    }
                )
            )
        else:
            await self.event_bus.publish(
                "cinemate.events.node",
                NodeFailedEvent(
                    run_id=self.run.run_id,
                    node_id=node_id,
                    payload={
                        "error_code": "EXECUTION_FAILED",
                        "error_msg": str(error),
                        "retry_count": retry_count
                    }
                )
            )
```

---

## 6. Changelog

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-04-22 | Initial version after Interface Alignment Meeting | PM |

---

**Approved by**: hermes, copaw  
**Meeting**: Interface Alignment Meeting (2026-04-22 11:00)
