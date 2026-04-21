"""
Unit tests for JobQueue

Tests cover:
- submit_job() - normal and error cases
- get_job_status() - status queries
- cancel_job() - job cancellation
- Error handling - Redis connection, Job not found
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from cine_mate.infra.queue import (
    JobQueue,
    JobQueueError,
    JobNotFoundError,
)
from cine_mate.infra.schemas import JobType, JobStatus


class TestJobQueueInit:
    """Test JobQueue initialization"""
    
    def test_init_default(self):
        """Test default initialization"""
        queue = JobQueue()
        assert queue.redis_url == "redis://localhost:6379"
        assert queue.redis is None
        assert queue.rq_queue is None
        assert queue._connected is False
    
    def test_init_custom_redis_url(self):
        """Test initialization with custom Redis URL"""
        queue = JobQueue(redis_url="redis://custom:6379/1")
        assert queue.redis_url == "redis://custom:6379/1"
    
    def test_init_with_event_bus(self):
        """Test initialization with EventBus"""
        mock_event_bus = MagicMock()
        queue = JobQueue(event_bus=mock_event_bus)
        assert queue.event_bus is mock_event_bus


class TestJobQueueConnect:
    """Test JobQueue connection management"""
    
    @pytest.mark.asyncio
    async def test_connect(self):
        """Test successful connection"""
        queue = JobQueue()
        await queue.connect()
        
        assert queue._connected is True
        assert queue.redis is not None
        assert queue.rq_queue is not None
        
        await queue.disconnect()
    
    @pytest.mark.asyncio
    async def test_connect_idempotent(self):
        """Test connecting twice doesn't create new connections"""
        queue = JobQueue()
        await queue.connect()
        first_redis = queue.redis
        
        await queue.connect()  # Should be no-op
        assert queue.redis is first_redis
        
        await queue.disconnect()
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection"""
        queue = JobQueue()
        await queue.connect()
        assert queue._connected is True
        
        await queue.disconnect()
        assert queue._connected is False


class TestJobQueueSubmitJob:
    """Test JobQueue.submit_job()"""
    
    @pytest.mark.asyncio
    async def test_submit_job_success(self):
        """Test successful job submission"""
        queue = JobQueue()
        
        # Mock Redis and RQ
        mock_redis = AsyncMock()
        mock_redis.expire = AsyncMock()
        queue.redis = mock_redis
        
        mock_rq_queue = MagicMock()
        mock_rq_job = MagicMock()
        mock_rq_job.id = "test_job_id"
        mock_rq_queue.enqueue = MagicMock(return_value=mock_rq_job)
        queue.rq_queue = mock_rq_queue
        
        queue._connected = True
        
        # Submit job
        job_id = await queue.submit_job(
            run_id="test_run",
            node_id="test_node",
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "test"},
            max_retries=2,
            priority=0
        )
        
        assert job_id is not None
        assert mock_redis.hset.called
        assert mock_rq_queue.enqueue.called
    
    @pytest.mark.asyncio
    async def test_submit_job_with_event_bus(self):
        """Test job submission with EventBus publishes event"""
        queue = JobQueue()
        
        mock_redis = AsyncMock()
        mock_redis.expire = AsyncMock()
        queue.redis = mock_redis
        
        mock_rq_queue = MagicMock()
        mock_rq_job = MagicMock()
        mock_rq_job.id = "test_job_id"
        mock_rq_queue.enqueue = MagicMock(return_value=mock_rq_job)
        queue.rq_queue = mock_rq_queue
        
        mock_event_bus = AsyncMock()
        mock_event_bus.publish = AsyncMock()
        queue.event_bus = mock_event_bus
        
        queue._connected = True
        
        await queue.submit_job(
            run_id="test_run",
            node_id="test_node",
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "test"}
        )
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_submit_job_not_connected(self):
        """Test submit_job raises error when not connected"""
        queue = JobQueue()
        queue._connected = False
        
        with pytest.raises(JobQueueError, match="Not connected"):
            await queue.submit_job(
                run_id="test",
                node_id="test",
                job_type=JobType.TEXT_TO_IMAGE,
                params={}
            )


class TestJobQueueGetStatus:
    """Test JobQueue.get_job_status()"""
    
    @pytest.mark.asyncio
    async def test_get_job_status_success(self):
        """Test successful status query"""
        queue = JobQueue()
        
        mock_redis = AsyncMock()
        mock_redis.hgetall = AsyncMock(return_value={
            "job_id": "test_job",
            "run_id": "test_run",
            "node_id": "test_node",
            "status": "queued",
            "progress": "50",
            "retry_count": "0",
            "created_at": "2026-04-21T08:00:00",
            "queued_at": "2026-04-21T08:00:01"
        })
        queue.redis = mock_redis
        queue._connected = True
        
        status = await queue.get_job_status("test_job")
        
        assert status.job_id == "test_job"
        assert status.run_id == "test_run"
        assert status.node_id == "test_node"
        assert status.status == JobStatus.QUEUED
        assert status.progress == 50
    
    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self):
        """Test status query for non-existent job"""
        queue = JobQueue()
        
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=False)
        queue.redis = mock_redis
        queue._connected = True
        
        with pytest.raises(JobNotFoundError):
            await queue.get_job_status("nonexistent_job")


class TestJobQueueCancelJob:
    """Test JobQueue.cancel_job()"""
    
    @pytest.mark.asyncio
    async def test_cancel_job_success(self):
        """Test successful job cancellation"""
        queue = JobQueue()
        
        mock_redis = AsyncMock()
        mock_redis.hgetall = AsyncMock(return_value={
            "job_id": "test_job",
            "status": "queued"
        })
        mock_redis.hset = AsyncMock()
        queue.redis = mock_redis
        
        mock_rq_queue = MagicMock()
        mock_rq_job = MagicMock()
        mock_rq_queue.fetch_job = MagicMock(return_value=mock_rq_job)
        queue.rq_queue = mock_rq_queue
        
        queue._connected = True
        
        result = await queue.cancel_job("test_job")
        
        assert result is True
        mock_redis.hset.assert_called()
    
    @pytest.mark.asyncio
    async def test_cancel_job_not_found(self):
        """Test cancellation of non-existent job"""
        queue = JobQueue()
        
        mock_redis = AsyncMock()
        mock_redis.hget = AsyncMock(return_value=None)
        queue.redis = mock_redis
        queue._connected = True
        
        result = await queue.cancel_job("nonexistent_job")
        
        # Should return False for non-existent job
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cancel_job_already_completed(self):
        """Test cancellation of completed job"""
        queue = JobQueue()
        
        mock_redis = AsyncMock()
        mock_redis.hget = AsyncMock(return_value="completed")
        queue.redis = mock_redis
        queue._connected = True
        
        result = await queue.cancel_job("test_job")
        
        # Can't cancel completed job
        assert result is False


class TestJobQueueEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_submit_job_with_special_chars(self):
        """Test job submission with special characters in params"""
        queue = JobQueue()
        
        mock_redis = AsyncMock()
        mock_redis.expire = AsyncMock()
        queue.redis = mock_redis
        
        mock_rq_queue = MagicMock()
        mock_rq_job = MagicMock()
        mock_rq_job.id = "test_job"
        mock_rq_queue.enqueue = MagicMock(return_value=mock_rq_job)
        queue.rq_queue = mock_rq_queue
        
        queue._connected = True
        
        # Special characters in prompt
        job_id = await queue.submit_job(
            run_id="test_run",
            node_id="test_node",
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "Test with \"quotes\" and 'apostrophes' & <tags>"}
        )
        
        assert job_id is not None
    
    @pytest.mark.asyncio
    async def test_submit_job_large_params(self):
        """Test job submission with large parameters"""
        queue = JobQueue()
        
        mock_redis = AsyncMock()
        mock_redis.expire = AsyncMock()
        queue.redis = mock_redis
        
        mock_rq_queue = MagicMock()
        mock_rq_job = MagicMock()
        mock_rq_job.id = "test_job"
        mock_rq_queue.enqueue = MagicMock(return_value=mock_rq_job)
        queue.rq_queue = mock_rq_queue
        
        queue._connected = True
        
        # Large prompt
        large_prompt = "x" * 10000
        job_id = await queue.submit_job(
            run_id="test_run",
            node_id="test_node",
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": large_prompt}
        )
        
        assert job_id is not None
    
    @pytest.mark.asyncio
    async def test_get_status_with_bytes_response(self):
        """Test status query with bytes response from Redis"""
        queue = JobQueue()
        
        mock_redis = AsyncMock()
        mock_redis.hgetall = AsyncMock(return_value={
            b"job_id": b"test_job",
            b"run_id": b"test_run",
            b"node_id": b"test_node",
            b"status": b"completed",
            b"progress": b"100",
            b"retry_count": b"0",
            b"created_at": b"2026-04-21T08:00:00",
            b"queued_at": b"2026-04-21T08:00:01"
        })
        queue.redis = mock_redis
        queue._connected = True
        
        status = await queue.get_job_status("test_job")
        
        assert status.job_id == "test_job"
        assert status.run_id == "test_run"
        assert status.node_id == "test_node"
        assert status.status == JobStatus.COMPLETED
