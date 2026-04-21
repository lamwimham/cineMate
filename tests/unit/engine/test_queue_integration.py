"""
Tests for Engine-Queue Integration Layer

Test Coverage:
- JobQueueAdapter creation and initialization
- Event handler setup
- Job submission
- Callback registration
- Status tracking
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from cine_mate.engine.queue_integration import (
    JobQueueAdapter,
    create_engine_queue_integration,
)
from cine_mate.infra.queue import JobQueue
from cine_mate.infra.event_bus import EventBus
from cine_mate.infra.schemas import (
    JobType,
    JobStatus,
    NodeCompletedEvent,
    NodeFailedEvent,
)


class TestJobQueueAdapter:
    """Test JobQueueAdapter class."""
    
    def test_adapter_creation(self):
        """Test adapter can be created."""
        job_queue = Mock(spec=JobQueue)
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        assert adapter.job_queue is job_queue
        assert adapter.event_bus is event_bus
        assert adapter._callbacks == {}
    
    def test_setup_event_handlers(self):
        """Test event handlers are setup on init."""
        job_queue = Mock(spec=JobQueue)
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        # Should subscribe to node_completed and node_failed
        assert event_bus.subscribe.call_count == 2
        event_bus.subscribe.assert_any_call("node_completed", adapter._on_node_completed)
        event_bus.subscribe.assert_any_call("node_failed", adapter._on_node_failed)
    
    @pytest.mark.asyncio
    async def test_on_node_completed_calls_callback(self):
        """Test callback is called on node completed."""
        job_queue = Mock(spec=JobQueue)
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        callback = AsyncMock()
        adapter._callbacks["node_001"] = callback
        
        event = NodeCompletedEvent(
            run_id="run_001",
            node_id="node_001",
            payload={
                "artifact_hash": "abc123",
                "output_url": "https://example.com/video.mp4",
                "cost": 0.75
            }
        )
        
        await adapter._on_node_completed(event)
        
        callback.assert_called_once_with(event)
    
    @pytest.mark.asyncio
    async def test_on_node_completed_no_callback(self):
        """Test no error when no callback registered."""
        job_queue = Mock(spec=JobQueue)
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        event = NodeCompletedEvent(
            run_id="run_001",
            node_id="node_001",
            payload={
                "artifact_hash": "abc123",
                "output_url": "https://example.com/video.mp4",
                "cost": 0.0
            }
        )
        
        # Should not raise
        await adapter._on_node_completed(event)
    
    @pytest.mark.asyncio
    async def test_on_node_failed_calls_callback(self):
        """Test callback is called on node failed."""
        job_queue = Mock(spec=JobQueue)
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        callback = AsyncMock()
        adapter._callbacks["node_001"] = callback
        
        event = NodeFailedEvent(
            run_id="run_001",
            node_id="node_001",
            payload={
                "error_code": "TEST_ERROR",
                "error_msg": "Test error",
                "retry_count": 0
            }
        )
        
        await adapter._on_node_failed(event)
        
        callback.assert_called_once_with(event)
    
    def test_on_job_complete_registers_callback(self):
        """Test callback registration for job completion."""
        job_queue = Mock(spec=JobQueue)
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        callback = AsyncMock()
        adapter.on_job_complete("node_001", callback)
        
        assert adapter._callbacks["node_001"] is callback
    
    def test_on_job_fail_registers_callback(self):
        """Test callback registration for job failure."""
        job_queue = Mock(spec=JobQueue)
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        callback = AsyncMock()
        adapter.on_job_fail("node_001", callback)
        
        assert adapter._callbacks["node_001"] is callback
    
    @pytest.mark.asyncio
    async def test_submit_node_job(self):
        """Test job submission."""
        job_queue = Mock(spec=JobQueue)
        job_queue.submit_job = AsyncMock(return_value="job_001")
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        job_id = await adapter.submit_node_job(
            run_id="run_001",
            node_id="node_001",
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "a cat"}
        )
        
        assert job_id == "job_001"
        job_queue.submit_job.assert_called_once_with(
            run_id="run_001",
            node_id="node_001",
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "a cat"}
        )
    
    @pytest.mark.asyncio
    async def test_get_job_status(self):
        """Test getting job status."""
        job_queue = Mock(spec=JobQueue)
        job_queue.get_job_status = AsyncMock(return_value=JobStatus.COMPLETED)
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        status = await adapter.get_job_status("job_001")
        
        assert status == JobStatus.COMPLETED
        job_queue.get_job_status.assert_called_once_with("job_001")
    
    @pytest.mark.asyncio
    async def test_cancel_job(self):
        """Test job cancellation."""
        job_queue = Mock(spec=JobQueue)
        job_queue.cancel_job = AsyncMock(return_value=True)
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        result = await adapter.cancel_job("job_001")
        
        assert result is True
        job_queue.cancel_job.assert_called_once_with("job_001")
    
    @pytest.mark.asyncio
    async def test_get_all_jobs_status(self):
        """Test getting all jobs status."""
        job_queue = Mock(spec=JobQueue)
        job_queue.get_all_jobs_status = AsyncMock(return_value={
            "job_001": JobStatus.COMPLETED,
            "job_002": JobStatus.PENDING
        })
        event_bus = Mock(spec=EventBus)
        
        adapter = JobQueueAdapter(job_queue, event_bus)
        
        statuses = await adapter.get_all_jobs_status("run_001")
        
        assert statuses == {
            "job_001": JobStatus.COMPLETED,
            "job_002": JobStatus.PENDING
        }
        job_queue.get_all_jobs_status.assert_called_once_with("run_001")


class TestCreateEngineQueueIntegration:
    """Test factory function."""
    
    @pytest.mark.asyncio
    async def test_create_integration(self):
        """Test factory function creates adapter."""
        with patch('cine_mate.engine.queue_integration.JobQueue') as mock_queue, \
             patch('cine_mate.engine.queue_integration.EventBus') as mock_bus:
            
            mock_queue_instance = AsyncMock()
            mock_queue.return_value = mock_queue_instance
            
            mock_bus_instance = AsyncMock()
            mock_bus.return_value = mock_bus_instance
            
            adapter = await create_engine_queue_integration("redis://localhost:6379")
            
            assert isinstance(adapter, JobQueueAdapter)
            mock_queue.assert_called_once_with(redis_url="redis://localhost:6379")
            mock_bus.assert_called_once_with(redis_url="redis://localhost:6379")
            mock_queue_instance.connect.assert_called_once()
            mock_bus_instance.connect.assert_called_once()
