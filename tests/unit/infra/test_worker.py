"""
Tests for Worker (Issue #7 Fix)

Verify that Worker can publish events via sync Redis Pub/Sub.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from cine_mate.infra.worker import (
    _publish_event_sync,
    CHANNEL_NODE_COMPLETED,
    CHANNEL_NODE_FAILED,
    execute_job,
    _execute_by_type,
)


class TestPublishEventSync:
    """Test the sync event publishing function (Issue #7 Fix)."""

    def test_publish_node_completed(self):
        """Test publishing node_completed event via sync Redis."""
        mock_redis = Mock()
        mock_redis.publish = Mock()

        _publish_event_sync(
            redis_conn=mock_redis,
            channel=CHANNEL_NODE_COMPLETED,
            event_type="node_completed",
            run_id="run_001",
            node_id="node_A",
            payload={
                "artifact_hash": "sha256_abc123",
                "output_url": "https://example.com/output.mp4",
                "cost": 1.5
            }
        )

        # Verify publish was called
        assert mock_redis.publish.called
        call_args = mock_redis.publish.call_args
        assert call_args[0][0] == CHANNEL_NODE_COMPLETED

        # Verify message structure
        message = json.loads(call_args[0][1])
        assert message["event_type"] == "node_completed"
        assert message["run_id"] == "run_001"
        assert message["node_id"] == "node_A"
        assert "timestamp" in message
        assert message["payload"]["artifact_hash"] == "sha256_abc123"

    def test_publish_node_failed(self):
        """Test publishing node_failed event via sync Redis."""
        mock_redis = Mock()
        mock_redis.publish = Mock()

        _publish_event_sync(
            redis_conn=mock_redis,
            channel=CHANNEL_NODE_FAILED,
            event_type="node_failed",
            run_id="run_002",
            node_id="node_B",
            payload={
                "error_code": "UPSTREAM_TIMEOUT",
                "error_msg": "API call timed out after 60s",
                "retry_count": 3
            }
        )

        # Verify publish was called
        assert mock_redis.publish.called
        call_args = mock_redis.publish.call_args
        assert call_args[0][0] == CHANNEL_NODE_FAILED

        # Verify message structure
        message = json.loads(call_args[0][1])
        assert message["event_type"] == "node_failed"
        assert message["payload"]["error_code"] == "UPSTREAM_TIMEOUT"


class TestExecuteByType:
    """Test job execution by type."""

    def test_text_to_image(self):
        """Test text_to_image job execution."""
        result = _execute_by_type("text_to_image", {"prompt": "a cat"})
        assert "artifact_hash" in result
        assert "output_url" in result
        assert "cost" in result
        assert result["cost"] == 0.1

    def test_image_to_video(self):
        """Test image_to_video job execution."""
        result = _execute_by_type("image_to_video", {"image_url": "http://example.com/img.png"})
        assert "artifact_hash" in result
        assert "duration" in result
        assert result["cost"] == 1.5

    def test_unknown_job_type_raises(self):
        """Test unknown job type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown job type"):
            _execute_by_type("unknown_type", {})


class TestExecuteJobIntegration:
    """Test execute_job with mocked RQ context (Issue #7 integration test)."""

    @patch('cine_mate.infra.worker.get_current_job')
    def test_execute_job_success_publishes_event(self, mock_get_current_job):
        """Test successful job execution publishes node_completed event."""
        # Mock RQ job and Redis connection
        mock_job = Mock()
        mock_redis = Mock()
        mock_redis.hgetall = Mock(return_value={
            "job_id": "test_job_001",
            "run_id": "run_001",
            "node_id": "node_A",
            "job_type": "text_to_image",
            "params": json.dumps({"prompt": "test"}),
            "status": "queued"
        })
        mock_redis.hset = Mock()
        mock_redis.publish = Mock()

        mock_job.connection = mock_redis
        mock_get_current_job.return_value = mock_job

        # Execute job
        execute_job("test_job_001")

        # Verify status was updated to completed
        hset_calls = mock_redis.hset.call_args_list
        assert any("completed" in str(call) for call in hset_calls)

        # Verify event was published
        assert mock_redis.publish.called
        publish_call = mock_redis.publish.call_args
        assert publish_call[0][0] == CHANNEL_NODE_COMPLETED

        message = json.loads(publish_call[0][1])
        assert message["event_type"] == "node_completed"
        assert message["run_id"] == "run_001"
        assert message["node_id"] == "node_A"

    @patch('cine_mate.infra.worker.get_current_job')
    def test_execute_job_failure_publishes_event(self, mock_get_current_job):
        """Test failed job execution publishes node_failed event."""
        # Mock RQ job with invalid job type to trigger failure
        mock_job = Mock()
        mock_redis = Mock()
        mock_redis.hgetall = Mock(return_value={
            "job_id": "test_job_002",
            "run_id": "run_002",
            "node_id": "node_B",
            "job_type": "invalid_type",  # Will trigger ValueError
            "params": json.dumps({}),
            "status": "queued"
        })
        mock_redis.hset = Mock()
        mock_redis.publish = Mock()

        mock_job.connection = mock_redis
        mock_get_current_job.return_value = mock_job

        # Execute job (should fail)
        with pytest.raises(ValueError):
            execute_job("test_job_002")

        # Verify status was updated to failed
        hset_calls = mock_redis.hset.call_args_list
        assert any("failed" in str(call) for call in hset_calls)

        # Verify error event was published
        assert mock_redis.publish.called
        publish_call = mock_redis.publish.call_args
        assert publish_call[0][0] == CHANNEL_NODE_FAILED

        message = json.loads(publish_call[0][1])
        assert message["event_type"] == "node_failed"
        assert message["payload"]["error_code"] == "EXECUTION_ERROR"


class TestChannelNames:
    """Test channel naming matches EventBus pattern."""

    def test_channel_names_match_eventbus(self):
        """Verify channel names follow cinemate:event_type pattern."""
        assert CHANNEL_NODE_COMPLETED == "cinemate:node_completed"
        assert CHANNEL_NODE_FAILED == "cinemate:node_failed"