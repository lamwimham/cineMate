"""
Unit tests for Event Schemas

Tests cover:
- CineMateEvent base class
- NodeCompletedEvent
- NodeFailedEvent
- JobSubmittedEvent
- Validation and edge cases
"""

import pytest
from datetime import datetime

from cine_mate.infra.schemas import (
    CineMateEvent,
    NodeCompletedEvent,
    NodeFailedEvent,
    JobSubmittedEvent,
    JobType,
    JobStatus,
)


class TestCineMateEvent:
    """Test base event class"""
    
    def test_create_base_event(self):
        """Test creating base CineMateEvent"""
        event = CineMateEvent(
            event_type="custom_event",
            run_id="run_001",
            node_id="node_01",
            payload={"key": "value"}
        )
        
        assert event.event_type == "custom_event"
        assert event.run_id == "run_001"
        assert event.node_id == "node_01"
        assert event.payload == {"key": "value"}
        assert isinstance(event.timestamp, datetime)
    
    def test_event_timestamp_auto(self):
        """Test timestamp is auto-generated"""
        event = CineMateEvent(
            event_type="test",
            run_id="test",
            node_id="test",
            payload={}
        )
        
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)
    
    def test_event_with_custom_timestamp(self):
        """Test creating event with custom timestamp"""
        custom_ts = datetime(2026, 4, 21, 10, 30, 0)
        event = CineMateEvent(
            event_type="test",
            run_id="test",
            node_id="test",
            payload={},
            timestamp=custom_ts
        )
        
        assert event.timestamp == custom_ts
    
    def test_event_serialization(self):
        """Test event can be serialized to dict"""
        event = NodeCompletedEvent(
            run_id="run_001",
            node_id="node_01",
            payload={"result": "success"}
        )
        
        data = event.model_dump()
        
        assert "event_type" in data
        assert "run_id" in data
        assert "node_id" in data
        assert "timestamp" in data
        assert "payload" in data
        assert data["event_type"] == "node_completed"
    
    def test_event_json_serialization(self):
        """Test event can be serialized to JSON"""
        import json
        
        event = NodeCompletedEvent(
            run_id="run_001",
            node_id="node_01",
            payload={"result": "success"}
        )
        
        json_str = event.model_dump_json()
        data = json.loads(json_str)
        
        assert data["event_type"] == "node_completed"
        assert data["run_id"] == "run_001"


class TestNodeCompletedEvent:
    """Test NodeCompletedEvent"""
    
    def test_create_node_completed(self):
        """Test creating NodeCompletedEvent"""
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
        assert event.payload["artifact_hash"] == "abc123"
        assert event.payload["output_url"] == "https://example.com/image.png"
        assert event.payload["cost"] == 0.5
    
    def test_node_completed_minimal_payload(self):
        """Test NodeCompletedEvent with minimal payload"""
        event = NodeCompletedEvent(
            run_id="run_001",
            node_id="img_gen_01",
            payload={}
        )
        
        assert event.event_type == "node_completed"
        assert event.payload == {}
    
    def test_node_completed_complex_payload(self):
        """Test NodeCompletedEvent with complex payload"""
        event = NodeCompletedEvent(
            run_id="run_001",
            node_id="video_gen_01",
            payload={
                "artifact_hash": "xyz789",
                "output_url": "https://example.com/video.mp4",
                "cost": 2.5,
                "metadata": {
                    "duration": 60,
                    "resolution": "1080p",
                    "fps": 30
                },
                "upstream_job_id": "job_12345"
            }
        )
        
        assert event.payload["metadata"]["duration"] == 60
        assert event.payload["metadata"]["resolution"] == "1080p"


class TestNodeFailedEvent:
    """Test NodeFailedEvent"""
    
    def test_create_node_failed(self):
        """Test creating NodeFailedEvent"""
        event = NodeFailedEvent(
            run_id="run_001",
            node_id="img_gen_01",
            payload={
                "error_code": "UPSTREAM_ERROR",
                "error_msg": "API timeout after 30s",
                "retry_count": 2
            }
        )
        
        assert event.event_type == "node_failed"
        assert event.payload["error_code"] == "UPSTREAM_ERROR"
        assert "API timeout" in event.payload["error_msg"]
    
    def test_node_failed_with_stack_trace(self):
        """Test NodeFailedEvent with stack trace"""
        event = NodeFailedEvent(
            run_id="run_001",
            node_id="img_gen_01",
            payload={
                "error_code": "INTERNAL_ERROR",
                "error_msg": "Unexpected error",
                "stack_trace": "Traceback (most recent call last):\n  ..."
            }
        )
        
        assert event.payload["error_code"] == "INTERNAL_ERROR"
        assert "stack_trace" in event.payload
    
    def test_node_failed_retry_info(self):
        """Test NodeFailedEvent with retry information"""
        event = NodeFailedEvent(
            run_id="run_001",
            node_id="img_gen_01",
            payload={
                "error_code": "RATE_LIMIT",
                "error_msg": "Rate limit exceeded",
                "retry_count": 3,
                "retry_after": 60
            }
        )
        
        assert event.payload["retry_count"] == 3
        assert event.payload["retry_after"] == 60


class TestJobSubmittedEvent:
    """Test JobSubmittedEvent"""
    
    def test_create_job_submitted(self):
        """Test creating JobSubmittedEvent"""
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
        assert event.payload["upstream_provider"] == "kling"
    
    def test_job_submitted_with_queue_info(self):
        """Test JobSubmittedEvent with queue information"""
        event = JobSubmittedEvent(
            run_id="run_001",
            node_id="video_gen_01",
            payload={
                "job_id": "job_456",
                "upstream_provider": "haiper",
                "estimated_duration": 120,
                "queue_position": 5,
                "estimated_wait": 30
            }
        )
        
        assert event.payload["queue_position"] == 5
        assert event.payload["estimated_wait"] == 30


class TestJobType:
    """Test JobType enum"""
    
    def test_job_type_values(self):
        """Test JobType enum values"""
        assert JobType.TEXT_TO_IMAGE.value == "text_to_image"
        assert JobType.IMAGE_TO_VIDEO.value == "image_to_video"
        assert JobType.TEXT_TO_VIDEO.value == "text_to_video"
        assert JobType.TTS.value == "tts"
        assert JobType.VIDEO_EDIT.value == "video_edit"
    
    def test_job_type_from_string(self):
        """Test creating JobType from string"""
        assert JobType("text_to_image") == JobType.TEXT_TO_IMAGE
        assert JobType("image_to_video") == JobType.IMAGE_TO_VIDEO


class TestJobStatus:
    """Test JobStatus enum"""
    
    def test_job_status_values(self):
        """Test JobStatus enum values"""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.QUEUED.value == "queued"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"
    
    def test_job_status_from_string(self):
        """Test creating JobStatus from string"""
        assert JobStatus("queued") == JobStatus.QUEUED
        assert JobStatus("completed") == JobStatus.COMPLETED


class TestEventValidation:
    """Test event validation and edge cases"""
    
    def test_event_required_fields(self):
        """Test that required fields are validated"""
        # Should work with all required fields
        event = CineMateEvent(
            event_type="test",
            run_id="test",
            node_id="test",
            payload={}
        )
        assert event is not None
    
    def test_event_payload_types(self):
        """Test payload accepts various types"""
        # Dict payload
        event1 = CineMateEvent(
            event_type="test",
            run_id="test",
            node_id="test",
            payload={"key": "value"}
        )
        assert event1.payload == {"key": "value"}
        
        # Empty dict payload
        event2 = CineMateEvent(
            event_type="test",
            run_id="test",
            node_id="test",
            payload={}
        )
        assert event2.payload == {}
    
    def test_event_nested_data(self):
        """Test event with deeply nested payload"""
        event = NodeCompletedEvent(
            run_id="run_001",
            node_id="complex_node",
            payload={
                "level1": {
                    "level2": {
                        "level3": {
                            "value": "deep"
                        }
                    }
                },
                "list": [1, 2, 3, {"nested": True}]
            }
        )
        
        assert event.payload["level1"]["level2"]["level3"]["value"] == "deep"
        assert len(event.payload["list"]) == 4
