"""
Tests for Core Models (Sprint 2 Day 2)

Test Coverage:
- PipelineRun model validation
- NodeExecution model validation
- NodeConfig model validation
- Artifact model validation
- BlobMetadata model validation
- Status enums validation
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from cine_mate.core.models import (
    PipelineRun,
    NodeExecution,
    NodeStatus,
    RunStatus,
    NodeConfig,
    Artifact,
    BlobMetadata,
    ApiMode,
)


class TestPipelineRun:
    """Test PipelineRun model."""

    def test_pipeline_run_creation(self):
        """Create basic PipelineRun."""
        run = PipelineRun(
            run_id="test_run_001",
            commit_msg="Test commit",
        )

        assert run.run_id == "test_run_001"
        assert run.commit_msg == "Test commit"
        assert run.status == RunStatus.PENDING
        assert run.parent_run_id is None

    def test_pipeline_run_with_parent(self):
        """PipelineRun with parent_run_id (fork)."""
        run = PipelineRun(
            run_id="test_run_002",
            parent_run_id="test_run_001",
            commit_msg="Modify scene 2",
        )

        assert run.parent_run_id == "test_run_001"

    def test_pipeline_run_status_values(self):
        """PipelineRun status enum values."""
        run = PipelineRun(run_id="test", commit_msg="test")

        assert RunStatus.PENDING == "pending"
        assert RunStatus.RUNNING == "running"
        assert RunStatus.COMPLETED == "completed"
        assert RunStatus.FAILED == "failed"

    def test_pipeline_run_dag_snapshot(self):
        """PipelineRun with DAG snapshot."""
        dag_snapshot = {
            "nodes": [{"id": "node_A", "type": "text_to_image"}],
            "edges": [],
        }

        run = PipelineRun(
            run_id="test_run_003",
            commit_msg="Test with DAG",
            dag_snapshot=dag_snapshot,
        )

        assert run.dag_snapshot == dag_snapshot

    def test_pipeline_run_missing_run_id_raises(self):
        """Missing run_id should raise ValidationError."""
        with pytest.raises(ValidationError):
            PipelineRun(commit_msg="test")


class TestNodeExecution:
    """Test NodeExecution model."""

    def test_node_execution_creation(self):
        """Create basic NodeExecution."""
        exec = NodeExecution(
            id="exec_test_run_001_node_A",
            run_id="test_run_001",
            node_id="node_A",
            status=NodeStatus.PENDING,
        )

        assert exec.id == "exec_test_run_001_node_A"
        assert exec.run_id == "test_run_001"
        assert exec.node_id == "node_A"
        assert exec.status == NodeStatus.PENDING

    def test_node_execution_with_config(self):
        """NodeExecution with config_snapshot."""
        config = NodeConfig(prompt="Test prompt", model_name="test-model")

        exec = NodeExecution(
            id="exec_test_config",
            run_id="test_run",
            node_id="node_1",
            status=NodeStatus.EXECUTING,
            config_snapshot=config,
        )

        assert exec.config_snapshot is not None
        assert exec.config_snapshot.prompt == "Test prompt"

    def test_node_execution_with_error(self):
        """NodeExecution with error info."""
        exec = NodeExecution(
            id="exec_test_error",
            run_id="test_run",
            node_id="node_1",
            status=NodeStatus.FAILED,
            error_msg="API timeout",
            error_traceback="Traceback...",
        )

        assert exec.error_msg == "API timeout"
        assert exec.error_traceback == "Traceback..."

    def test_node_execution_status_values(self):
        """NodeExecution status enum values."""
        statuses = [
            NodeStatus.PENDING,
            NodeStatus.QUEUED,
            NodeStatus.EXECUTING,
            NodeStatus.SUCCEEDED,
            NodeStatus.FAILED,
            NodeStatus.SKIPPED,
        ]

        for status in statuses:
            exec = NodeExecution(
                id=f"exec_{status.value}",
                run_id="test",
                node_id="node",
                status=status,
            )
            assert exec.status == status


class TestNodeConfig:
    """Test NodeConfig model."""

    def test_node_config_creation(self):
        """Create basic NodeConfig."""
        config = NodeConfig(prompt="Generate a sunset")

        assert config.prompt == "Generate a sunset"

    def test_node_config_with_all_fields(self):
        """NodeConfig with all optional fields."""
        config = NodeConfig(
            prompt="Test prompt",
            negative_prompt="blurry, low quality",
            model_name="kling-v2",
            seed=42,
            billing_mode=ApiMode.MANAGED,
            width=1024,
            height=1024,
            duration=5,
        )

        assert config.model_name == "kling-v2"
        assert config.seed == 42
        assert config.billing_mode == ApiMode.MANAGED
        assert config.width == 1024

    def test_node_config_billing_mode_values(self):
        """Billing mode enum values."""
        assert ApiMode.MANAGED == "managed"
        assert ApiMode.PREPAID == "prepaid"


class TestArtifact:
    """Test Artifact model."""

    def test_artifact_creation(self):
        """Create basic Artifact."""
        artifact = Artifact(
            id="art_test_run_node",
            run_id="test_run_001",
            node_id="node_A",
            blob_hash="sha256_abc123",
        )

        assert artifact.id == "art_test_run_node"
        assert artifact.run_id == "test_run_001"
        assert artifact.node_id == "node_A"
        assert artifact.blob_hash == "sha256_abc123"
        assert artifact.is_reused is False

    def test_artifact_with_metadata(self):
        """Artifact with metadata."""
        artifact = Artifact(
            id="art_test",
            run_id="test_run",
            node_id="node_1",
            blob_hash="sha256_test",
            metadata={"cost": 1.5, "duration": 5},
        )

        assert artifact.metadata["cost"] == 1.5
        assert artifact.metadata["duration"] == 5

    def test_artifact_reused_flag(self):
        """Artifact reused from parent run."""
        artifact = Artifact(
            id="art_test",
            run_id="test_run",
            node_id="node_1",
            blob_hash="sha256_test",
            is_reused=True,
        )

        assert artifact.is_reused is True


class TestBlobMetadata:
    """Test BlobMetadata model."""

    def test_blob_metadata_creation(self):
        """Create basic BlobMetadata."""
        blob = BlobMetadata(
            blob_id="sha256_test_hash",
            relative_path="objects/test/hash.mp4",
            file_size_bytes=1024,
            mime_type="video/mp4",
        )

        assert blob.blob_id == "sha256_test_hash"
        assert blob.relative_path == "objects/test/hash.mp4"
        assert blob.file_size_bytes == 1024
        assert blob.mime_type == "video/mp4"

    def test_blob_metadata_mime_types(self):
        """BlobMetadata with different mime types."""
        video_blob = BlobMetadata(
            blob_id="sha256_video",
            relative_path="video.mp4",
            file_size_bytes=1024,
            mime_type="video/mp4",
        )

        image_blob = BlobMetadata(
            blob_id="sha256_image",
            relative_path="image.png",
            file_size_bytes=512,
            mime_type="image/png",
        )

        audio_blob = BlobMetadata(
            blob_id="sha256_audio",
            relative_path="audio.mp3",
            file_size_bytes=256,
            mime_type="audio/mpeg",
        )

        assert video_blob.mime_type == "video/mp4"
        assert image_blob.mime_type == "image/png"
        assert audio_blob.mime_type == "audio/mpeg"


class TestStatusTransitions:
    """Test status transitions and validation."""

    def test_run_status_flow(self):
        """PipelineRun status flow: PENDING -> RUNNING -> COMPLETED."""
        run = PipelineRun(run_id="test", commit_msg="test")
        assert run.status == RunStatus.PENDING

        run.status = RunStatus.RUNNING
        assert run.status == RunStatus.RUNNING

        run.status = RunStatus.COMPLETED
        assert run.status == RunStatus.COMPLETED

    def test_node_status_flow(self):
        """NodeExecution status flow."""
        exec = NodeExecution(
            id="exec_test",
            run_id="test",
            node_id="node",
            status=NodeStatus.PENDING,
        )

        statuses = [
            NodeStatus.PENDING,
            NodeStatus.QUEUED,
            NodeStatus.EXECUTING,
            NodeStatus.SUCCEEDED,
        ]

        for status in statuses:
            exec.status = status
            assert exec.status == status

    def test_run_failure_status(self):
        """PipelineRun can be marked as FAILED."""
        run = PipelineRun(run_id="test", commit_msg="test")
        run.status = RunStatus.FAILED

        assert run.status == RunStatus.FAILED


class TestModelSerialization:
    """Test model serialization/deserialization."""

    def test_pipeline_run_to_dict(self):
        """PipelineRun can be converted to dict."""
        run = PipelineRun(run_id="test", commit_msg="test")

        # Pydantic v2 uses model_dump()
        data = run.model_dump()

        assert "run_id" in data
        assert "commit_msg" in data
        assert "status" in data

    def test_node_config_from_dict(self):
        """NodeConfig can be created from dict."""
        data = {
            "prompt": "Test prompt",
            "model_name": "test-model",
            "seed": 42,
        }

        config = NodeConfig(**data)

        assert config.prompt == "Test prompt"
        assert config.model_name == "test-model"
        assert config.seed == 42

    def test_artifact_json_serialization(self):
        """Artifact JSON serialization."""
        artifact = Artifact(
            id="art_test",
            run_id="test_run",
            node_id="node_1",
            blob_hash="sha256_test",
        )

        data = artifact.model_dump()

        assert data["id"] == "art_test"
        assert data["blob_hash"] == "sha256_test"