"""
Unit tests for EventBus

Tests cover:
- publish() - publishing events
- subscribe() - subscribing to event types
- start_listening() - event loop
- Event types - NodeCompletedEvent, NodeFailedEvent, JobSubmittedEvent
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from cine_mate.infra.event_bus import (
    EventBus,
    CineMateEvent,
    NodeCompletedEvent,
    NodeFailedEvent,
    JobSubmittedEvent,
)


class TestEventBusInit:
    """Test EventBus initialization"""
    
    def test_init_default(self):
        """Test default initialization"""
        event_bus = EventBus()
        assert event_bus.redis_url == "redis://localhost:6379"
        assert event_bus.redis is None
        assert event_bus.pubsub is None
        assert len(event_bus._handlers) == 0
        assert event_bus._listening is False
    
    def test_init_custom_redis_url(self):
        """Test initialization with custom Redis URL"""
        event_bus = EventBus(redis_url="redis://custom:6379/1")
        assert event_bus.redis_url == "redis://custom:6379/1"


class TestEventBusConnect:
    """Test EventBus connection management"""
    
    @pytest.mark.asyncio
    async def test_connect(self):
        """Test successful connection"""
        event_bus = EventBus()
        await event_bus.connect()
        
        assert event_bus.redis is not None
        
        await event_bus.disconnect()
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection"""
        event_bus = EventBus()
        await event_bus.connect()
        assert event_bus.redis is not None
        
        await event_bus.disconnect()
        # Redis should be closed


class TestEventBusPublish:
    """Test EventBus.publish()"""
    
    @pytest.mark.asyncio
    async def test_publish_success(self):
        """Test successful event publishing"""
        event_bus = EventBus()
        
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock(return_value=1)
        event_bus.redis = mock_redis
        
        event = NodeCompletedEvent(
            run_id="test_run",
            node_id="test_node",
            payload={
                "artifact_hash": "test_hash",
                "output_url": "https://example.com/output.mp4",
                "cost": 0.5
            }
        )
        
        await event_bus.publish(event)
        
        mock_redis.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_publish_not_connected(self):
        """Test publishing when not connected"""
        event_bus = EventBus()
        event_bus.redis = None
        
        event = NodeCompletedEvent(
            run_id="test",
            node_id="test",
            payload={}
        )
        
        with pytest.raises(RuntimeError, match="Not connected"):
            await event_bus.publish(event)
    
    @pytest.mark.asyncio
    async def test_publish_serializes_event(self):
        """Test that publish serializes event to JSON"""
        event_bus = EventBus()
        
        mock_redis = AsyncMock()
        event_bus.redis = mock_redis
        
        event = NodeCompletedEvent(
            run_id="test_run",
            node_id="test_node",
            payload={"key": "value"}
        )
        
        await event_bus.publish(event)
        
        # Verify JSON was sent
        call_args = mock_redis.publish.call_args
        channel = call_args[0][0]
        message = call_args[0][1]
        
        assert channel == "cinemate:node_completed"
        assert isinstance(message, str)
        
        # Verify can deserialize
        data = json.loads(message)
        assert data["event_type"] == "node_completed"
        assert data["run_id"] == "test_run"
    
    @pytest.mark.asyncio
    async def test_publish_different_event_types(self):
        """Test publishing different event types to different channels"""
        event_bus = EventBus()
        mock_redis = AsyncMock()
        event_bus.redis = mock_redis
        
        # NodeCompletedEvent
        event1 = NodeCompletedEvent(run_id="test", node_id="test", payload={})
        await event_bus.publish(event1)
        channel1 = mock_redis.publish.call_args[0][0]
        assert channel1 == "cinemate:node_completed"
        
        # NodeFailedEvent
        event2 = NodeFailedEvent(run_id="test", node_id="test", payload={"error_code": "TEST"})
        await event_bus.publish(event2)
        channel2 = mock_redis.publish.call_args[0][0]
        assert channel2 == "cinemate:node_failed"
        
        # JobSubmittedEvent
        event3 = JobSubmittedEvent(run_id="test", node_id="test", payload={"job_id": "123"})
        await event_bus.publish(event3)
        channel3 = mock_redis.publish.call_args[0][0]
        assert channel3 == "cinemate:job_submitted"


class TestEventBusSubscribe:
    """Test EventBus.subscribe()"""
    
    def test_subscribe_success(self):
        """Test successful subscription"""
        event_bus = EventBus()
        
        handler = AsyncMock()
        event_bus.subscribe("node_completed", handler)
        
        assert "node_completed" in event_bus._handlers
        assert handler in event_bus._handlers["node_completed"]
    
    def test_subscribe_multiple_handlers(self):
        """Test subscribing multiple handlers to same event"""
        event_bus = EventBus()
        
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        event_bus.subscribe("node_completed", handler1)
        event_bus.subscribe("node_completed", handler2)
        
        # Should have list of handlers
        handlers = event_bus._handlers["node_completed"]
        assert isinstance(handlers, list)
        assert handler1 in handlers
        assert handler2 in handlers
    
    def test_unsubscribe(self):
        """Test unsubscribing a handler"""
        event_bus = EventBus()
        
        handler = AsyncMock()
        event_bus.subscribe("node_completed", handler)
        event_bus.unsubscribe("node_completed", handler)
        
        assert handler not in event_bus._handlers.get("node_completed", [])
    
    def test_unsubscribe_all(self):
        """Test unsubscribing all handlers for an event type"""
        event_bus = EventBus()
        
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        event_bus.subscribe("node_completed", handler1)
        event_bus.subscribe("node_completed", handler2)
        event_bus.unsubscribe("node_completed")
        
        assert "node_completed" not in event_bus._handlers


class TestEventBusStartListening:
    """Test EventBus.start_listening()"""
    
    @pytest.mark.asyncio
    async def test_start_listening_creates_task(self):
        """Test that start_listening creates a background task"""
        event_bus = EventBus()
        
        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)
        mock_pubsub.subscribe = AsyncMock()
        
        event_bus.redis = mock_redis
        
        handler = AsyncMock()
        event_bus.subscribe("node_completed", handler)
        
        await event_bus.start_listening()
        
        assert event_bus._listening is True
        assert event_bus._listen_task is not None
        
        # Cleanup
        await event_bus.stop_listening()
    
    @pytest.mark.asyncio
    async def test_stop_listening(self):
        """Test stopping the listener"""
        event_bus = EventBus()
        
        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        
        event_bus.redis = mock_redis
        
        await event_bus.start_listening()
        assert event_bus._listening is True
        
        await event_bus.stop_listening()
        assert event_bus._listening is False


class TestEventTypes:
    """Test Event Schema classes"""
    
    def test_node_completed_event(self):
        """Test NodeCompletedEvent creation"""
        event = NodeCompletedEvent(
            run_id="run_001",
            node_id="img_gen_01",
            payload={
                "artifact_hash": "abc123",
                "output_url": "https://example.com/image.png",
                "cost": 0.5
            }
        )
        
        assert event.event_type == "node_completed"
        assert event.run_id == "run_001"
        assert event.node_id == "img_gen_01"
        assert event.payload["artifact_hash"] == "abc123"
    
    def test_node_failed_event(self):
        """Test NodeFailedEvent creation"""
        event = NodeFailedEvent(
            run_id="run_001",
            node_id="img_gen_01",
            payload={
                "error_code": "UPSTREAM_ERROR",
                "error_msg": "API timeout",
                "retry_count": 2
            }
        )
        
        assert event.event_type == "node_failed"
        assert event.payload["error_code"] == "UPSTREAM_ERROR"
    
    def test_job_submitted_event(self):
        """Test JobSubmittedEvent creation"""
        event = JobSubmittedEvent(
            run_id="run_001",
            node_id="img_gen_01",
            payload={
                "job_id": "job_123",
                "upstream_provider": "kling",
                "estimated_duration": 60
            }
        )
        
        assert event.event_type == "job_submitted"
        assert event.payload["job_id"] == "job_123"
    
    def test_event_timestamp_auto_generated(self):
        """Test that timestamp is auto-generated"""
        event = NodeCompletedEvent(
            run_id="test",
            node_id="test",
            payload={}
        )
        
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)
    
    def test_event_to_dict(self):
        """Test event serialization"""
        event = NodeCompletedEvent(
            run_id="test",
            node_id="test",
            payload={"key": "value"}
        )
        
        data = event.model_dump()
        
        assert "event_type" in data
        assert "run_id" in data
        assert "timestamp" in data
        assert "payload" in data


class TestHelperFunctions:
    """Test helper functions"""
    
    @pytest.mark.asyncio
    async def test_publish_node_completed(self):
        """Test publish_node_completed helper"""
        from cine_mate.infra.event_bus import publish_node_completed
        
        mock_event_bus = AsyncMock()
        mock_event_bus.publish = AsyncMock()
        
        await publish_node_completed(
            event_bus=mock_event_bus,
            run_id="test_run",
            node_id="test_node",
            artifact_hash="test_hash",
            output_url="https://example.com/output.mp4",
            cost=0.5
        )
        
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(event, NodeCompletedEvent)
    
    @pytest.mark.asyncio
    async def test_publish_node_failed(self):
        """Test publish_node_failed helper"""
        from cine_mate.infra.event_bus import publish_node_failed
        
        mock_event_bus = AsyncMock()
        mock_event_bus.publish = AsyncMock()
        
        await publish_node_failed(
            event_bus=mock_event_bus,
            run_id="test_run",
            node_id="test_node",
            error_code="TEST_ERROR",
            error_msg="Test error message"
        )
        
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(event, NodeFailedEvent)
