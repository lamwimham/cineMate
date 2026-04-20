"""
EventBus - Redis Pub/Sub for Async Notifications

会议决议：2026-04-22 Interface Alignment Meeting
- 选型：Redis Pub/Sub (简单、低延迟)
- 升级路径：Sprint 2 可升级到 Redis Stream

Architecture:
    Worker completes job
        ↓
    EventBus.publish(NodeCompletedEvent)
        ↓
    Redis Pub/Sub Channel
        ↓
    Engine FSM._on_event() → state transition
"""

import json
import asyncio
from typing import Callable, Dict, Any, Optional, List, Type
from datetime import datetime

import redis.asyncio as redis

from cine_mate.infra.schemas import (
    CineMateEvent,
    NodeCompletedEvent,
    NodeFailedEvent,
    JobSubmittedEvent,
)


# Event type mapping
EVENT_TYPES = {
    "node_completed": NodeCompletedEvent,
    "node_failed": NodeFailedEvent,
    "job_submitted": JobSubmittedEvent,
}


class EventBus:
    """
    Redis Pub/Sub Event Bus for async notifications.
    
    会议决议：Event-Driven 回调机制
    
    Usage:
        # Publisher (Worker/Engine)
        event_bus = EventBus(redis_url)
        await event_bus.publish(NodeCompletedEvent(...))
        
        # Subscriber (Engine FSM)
        event_bus = EventBus(redis_url)
        event_bus.subscribe("node_completed", handler_fn)
        await event_bus.start_listening()
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self._handlers: Dict[str, List[Callable]] = {}
        self._listening = False
        self._listen_task: Optional[asyncio.Task] = None
    
    async def connect(self):
        """Establish Redis connection"""
        self.redis = redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Close Redis connection"""
        await self.stop_listening()
        if self.redis:
            await self.redis.close()
    
    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Event name ("node_completed", "node_failed", etc.)
            handler: Async callback function(event: CineMateEvent)
        
        Example:
            async def on_node_completed(event: NodeCompletedEvent):
                print(f"Node {event.node_id} completed")
                fsm.transition("complete")
            
            event_bus.subscribe("node_completed", on_node_completed)
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Optional[Callable] = None):
        """Unsubscribe from an event type"""
        if handler and event_type in self._handlers:
            self._handlers[event_type].remove(handler)
        elif event_type in self._handlers:
            del self._handlers[event_type]
    
    async def publish(self, event: CineMateEvent):
        """
        Publish an event to all subscribers.
        
        Args:
            event: CineMateEvent instance (NodeCompletedEvent, etc.)
        
        Example:
            event = NodeCompletedEvent(
                run_id="run_001",
                node_id="img_gen_01",
                payload={"artifact_hash": "abc123", "output_url": "..."}
            )
            await event_bus.publish(event)
        """
        if not self.redis:
            raise RuntimeError("Not connected. Call connect() first.")
        
        # Serialize event to JSON
        message = {
            "event_type": event.event_type,
            "run_id": event.run_id,
            "node_id": event.node_id,
            "timestamp": event.timestamp.isoformat(),
            "payload": event.payload
        }
        
        # Publish to channel
        channel = f"cinemate:{event.event_type}"
        await self.redis.publish(channel, json.dumps(message))
    
    async def start_listening(self):
        """
        Start listening for events (non-blocking).
        
        Creates a background task that processes incoming events.
        Call this once when the application starts.
        """
        if not self.redis:
            raise RuntimeError("Not connected. Call connect() first.")
        
        if self._listening:
            return
        
        self._listening = True
        
        # Subscribe to all registered event types
        self.pubsub = self.redis.pubsub()
        if self._handlers:
            channels = [f"cinemate:{event_type}" for event_type in self._handlers.keys()]
            await self.pubsub.subscribe(*channels)
        
        # Start background listener
        self._listen_task = asyncio.create_task(self._listen_loop())
    
    async def stop_listening(self):
        """Stop listening for events"""
        self._listening = False
        
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None
        
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
            self.pubsub = None
    
    async def _listen_loop(self):
        """Background loop to process incoming events"""
        while self._listening:
            try:
                message = await self.pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0
                )
                
                if message and message["type"] == "message":
                    await self._process_message(message)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"EventBus error: {e}")
                await asyncio.sleep(1)
    
    async def _process_message(self, message: dict):
        """Process a single Pub/Sub message"""
        channel = message["channel"]
        event_type = channel.replace("cinemate:", "")
        payload = json.loads(message["data"])
        
        # Parse event with proper schema
        event_class = EVENT_TYPES.get(event_type, CineMateEvent)
        event = event_class(**payload)
        
        # Call registered handlers
        handlers = self._handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"Event handler error for {event_type}: {e}")


# =============================================================================
# Convenience functions (会议决议：简化使用)
# =============================================================================

async def publish_node_completed(
    event_bus: EventBus,
    run_id: str,
    node_id: str,
    artifact_hash: str,
    output_url: str,
    cost: float = 0.0
):
    """Publish a node_completed event"""
    event = NodeCompletedEvent(
        run_id=run_id,
        node_id=node_id,
        payload={
            "artifact_hash": artifact_hash,
            "output_url": output_url,
            "cost": cost
        }
    )
    await event_bus.publish(event)


async def publish_node_failed(
    event_bus: EventBus,
    run_id: str,
    node_id: str,
    error_code: str,
    error_msg: str,
    retry_count: int = 0
):
    """Publish a node_failed event"""
    event = NodeFailedEvent(
        run_id=run_id,
        node_id=node_id,
        payload={
            "error_code": error_code,
            "error_msg": error_msg,
            "retry_count": retry_count
        }
    )
    await event_bus.publish(event)


async def publish_job_submitted(
    event_bus: EventBus,
    run_id: str,
    node_id: str,
    job_id: str,
    upstream_provider: str,
    estimated_duration: int
):
    """Publish a job_submitted event"""
    event = JobSubmittedEvent(
        run_id=run_id,
        node_id=node_id,
        payload={
            "job_id": job_id,
            "upstream_provider": upstream_provider,
            "estimated_duration": estimated_duration
        }
    )
    await event_bus.publish(event)
