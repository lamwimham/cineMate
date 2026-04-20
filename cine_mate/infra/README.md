# CineMate Infra - Async Infrastructure

> Job Queue + Event Bus for async video generation tasks

**会议决议**: 2026-04-22 Interface Alignment Meeting

## 📦 Components

```
cine_mate/infra/
├── __init__.py       # Package exports
├── schemas.py        # Event Schema v1.0 + Job models
├── queue.py          # JobQueue class (Redis + RQ)
├── event_bus.py      # Redis Pub/Sub for async notifications
└── worker.py         # RQ Worker (executes jobs)
```

## 🚀 Quick Start

### 1. Start Redis

```bash
# Using Docker Compose
docker-compose -f docker-compose.infra.yml up -d

# Verify Redis is running
redis-cli ping  # Should return: PONG
```

### 2. Start RQ Worker

```bash
# In a separate terminal
cd /Users/lianwenhua/indie/Agents/copaw
python -m cine_mate.infra.worker
```

### 3. Submit Jobs (Example)

```python
import asyncio
from cine_mate.infra import JobQueue, JobType, EventBus

async def main():
    # Initialize
    queue = JobQueue(redis_url="redis://localhost:6379")
    event_bus = EventBus(redis_url="redis://localhost:6379")
    await queue.connect()
    await event_bus.connect()
    queue.event_bus = event_bus
    
    # Submit a job (hermes 的 DirectorAgent 会这样调用)
    job_id = await queue.submit_job(
        run_id="run_001",
        node_id="img_gen_01",
        job_type=JobType.TEXT_TO_IMAGE,
        params={"prompt": "a cyberpunk city at night"}
    )
    print(f"Submitted job: {job_id}")
    
    # Check status
    status = await queue.get_job_status(job_id)
    print(f"Status: {status.status}")
    
    # Cleanup
    await queue.disconnect()
    await event_bus.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Subscribe to Events (Engine Integration)

```python
import asyncio
from cine_mate.infra import EventBus, NodeCompletedEvent

async def on_node_completed(event: NodeCompletedEvent):
    """Handle node completion (FSM state transition)"""
    print(f"Node {event.node_id} completed!")
    print(f"Artifact hash: {event.payload['artifact_hash']}")
    
    # Trigger FSM state transition
    # fsm.transition("complete")

async def main():
    event_bus = EventBus(redis_url="redis://localhost:6379")
    await event_bus.connect()
    
    # Subscribe to events (会议决议：Event-Driven 回调)
    event_bus.subscribe("node_completed", on_node_completed)
    event_bus.subscribe("node_failed", on_node_failed)
    
    # Start listening
    await event_bus.start_listening()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await event_bus.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Architecture (会议决议)

```
┌─────────────────────────────────────────────────────────────┐
│  Engine/DirectorAgent (hermes)                              │
│    ↓ submit_job()                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  JobQueue (copaw)                                   │   │
│  │    - Redis Hash (job metadata)                      │   │
│  │    - RQ Queue (execution)                           │   │
│  └─────────────────────────────────────────────────────┘   │
│    ↑                                                        │
│    ↓ node_completed event                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  EventBus (Redis Pub/Sub)                           │   │
│  └─────────────────────────────────────────────────────┘   │
│    ↓                                                        │
│  FSM.transition("complete")                                 │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  RQ Worker                                                  │
│    - Pulls jobs from queue                                  │
│    - Calls upstream API (Kling/Runway/etc.)                 │
│    - Updates job status                                     │
│    - Publishes node_completed event                         │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Event Schema v1.0

### Base Event

```python
class CineMateEvent(BaseModel):
    event_type: str      # "node_completed", "node_failed", "job_submitted"
    run_id: str
    node_id: str
    timestamp: datetime
    payload: Dict[str, Any]
```

### Node Completed Event

```python
class NodeCompletedEvent(CineMateEvent):
    event_type: str = "node_completed"
    payload: {
        "artifact_hash": str,      # CAS content hash
        "output_url": str,         # Output file URL/path
        "cost": float              # Actual cost in credits
    }
```

### Node Failed Event

```python
class NodeFailedEvent(CineMateEvent):
    event_type: str = "node_failed"
    payload: {
        "error_code": str,         # e.g., "UPSTREAM_ERROR", "TIMEOUT"
        "error_msg": str,          # Human-readable message
        "retry_count": int         # Number of retries attempted
    }
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `RQ_QUEUE_NAME` | `default` | RQ queue name |
| `JOB_TIMEOUT` | `600` | Job timeout in seconds (10 min) |

## 🧪 Testing

```bash
# 1. Start Redis
docker-compose -f docker-compose.infra.yml up -d

# 2. Start Worker
python -m cine_mate.infra.worker

# 3. Run test script
python examples/test_infra.py

# 4. View RQ Dashboard (optional)
open http://localhost:9181
```

## 🔗 Related Docs

- [ADR-001: Job Queue Selection](../../docs/adr/ADR-001_job_queue.md)
- [Async Interface Design](../../docs/architecture/async_interface.md)
- [Sprint 1 Brief](../../docs/PMO/copaw_sprint1_brief.md)

## 📝 Meeting Notes

**Interface Alignment Meeting - 2026-04-22**

Attendees: copaw, hermes, PM

Decisions:
1. Event Bus: Redis Pub/Sub (not Stream)
2. Event Schema: v1.0 (see above)
3. Callback mechanism: Event-Driven
4. Interface boundary: JobQueue + EventBus

See `docs/architecture/async_interface.md` for details.
