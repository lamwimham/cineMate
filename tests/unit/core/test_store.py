"""
Unit tests for Store (cine_mate/core/store.py)

Tests:
- Database initialization
- Run CRUD operations
- NodeExecution CRUD operations
- Blob operations
- Artifact operations
- Crash recovery helpers
"""

import pytest
import json
import aiosqlite
from datetime import datetime
from pathlib import Path

from cine_mate.core.store import Store
from cine_mate.core.models import (
    PipelineRun, RunStatus,
    NodeExecution, NodeStatus, NodeConfig,
    BlobMetadata, Artifact,
    ApiMode
)


class TestStoreInit:
    """Tests for Store initialization."""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self, store):
        """Test init_db creates all required tables."""
        async with aiosqlite.connect(store.db_path) as db:
            # Check runs table
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='pipeline_runs'"
            )
            assert await cursor.fetchone() is not None

            # Check blobs table
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='blobs'"
            )
            assert await cursor.fetchone() is not None

            # Check node_executions table
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='node_executions'"
            )
            assert await cursor.fetchone() is not None

            # Check artifacts table
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='artifacts'"
            )
            assert await cursor.fetchone() is not None

    @pytest.mark.asyncio
    async def test_init_db_enables_foreign_keys(self, store):
        """Test init_db enables foreign keys in Store connections."""
        # Store internally sets PRAGMA foreign_keys=ON on each connection
        # We verify by trying to violate foreign key constraint
        async with aiosqlite.connect(store.db_path) as db:
            await db.execute("PRAGMA foreign_keys=ON")
            # Try to insert node_execution with invalid run_id
            try:
                await db.execute(
                    "INSERT INTO node_executions (id, run_id, node_id, status) VALUES (?, ?, ?, ?)",
                    ("exec_invalid", "nonexistent_run", "node", "pending")
                )
                await db.commit()
                # If FK enabled, this should fail
                assert False, "Foreign key constraint not enforced"
            except aiosqlite.IntegrityError:
                # Expected - FK constraint violated
                pass

    @pytest.mark.asyncio
    async def test_init_db_uses_wal_mode(self, store):
        """Test init_db uses WAL journal mode."""
        async with aiosqlite.connect(store.db_path) as db:
            cursor = await db.execute("PRAGMA journal_mode")
            row = await cursor.fetchone()
            assert row[0] == "wal"


class TestRunOperations:
    """Tests for PipelineRun CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_run(self, store, sample_run):
        """Test creating a new run."""
        result = await store.create_run(sample_run)
        assert result.run_id == sample_run.run_id

        # Verify in database
        fetched = await store.get_run(sample_run.run_id)
        assert fetched is not None
        assert fetched.run_id == sample_run.run_id
        assert fetched.status == RunStatus.PENDING

    @pytest.mark.asyncio
    async def test_create_run_with_parent(self, store, sample_run, child_run):
        """Test creating a run with parent_run_id."""
        await store.create_run(sample_run)
        result = await store.create_run(child_run)

        assert result.parent_run_id == sample_run.run_id

        fetched = await store.get_run(child_run.run_id)
        assert fetched.parent_run_id == sample_run.run_id

    @pytest.mark.asyncio
    async def test_create_run_with_dag_snapshot(self, store):
        """Test creating a run with DAG snapshot."""
        dag_snapshot = {"nodes": ["A", "B", "C"], "edges": [["A", "B"]]}
        run = PipelineRun(
            run_id="run_with_dag",
            dag_snapshot=dag_snapshot
        )
        await store.create_run(run)

        fetched = await store.get_run("run_with_dag")
        assert fetched.dag_snapshot == dag_snapshot

    @pytest.mark.asyncio
    async def test_update_run_status(self, store, sample_run):
        """Test updating run status."""
        await store.create_run(sample_run)

        await store.update_run_status(sample_run.run_id, RunStatus.RUNNING)

        fetched = await store.get_run(sample_run.run_id)
        assert fetched.status == RunStatus.RUNNING

    @pytest.mark.asyncio
    async def test_update_run_status_to_completed(self, store, sample_run):
        """Test updating run status to completed."""
        await store.create_run(sample_run)

        await store.update_run_status(sample_run.run_id, RunStatus.COMPLETED)

        fetched = await store.get_run(sample_run.run_id)
        assert fetched.status == RunStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_update_run_status_to_failed(self, store, sample_run):
        """Test updating run status to failed."""
        await store.create_run(sample_run)

        await store.update_run_status(sample_run.run_id, RunStatus.FAILED)

        fetched = await store.get_run(sample_run.run_id)
        assert fetched.status == RunStatus.FAILED

    @pytest.mark.asyncio
    async def test_get_nonexistent_run(self, store):
        """Test getting a run that doesn't exist."""
        result = await store.get_run("nonexistent_run")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_run_with_all_fields(self, store):
        """Test creating run with all optional fields."""
        run = PipelineRun(
            run_id="full_run",
            parent_run_id="parent_001",
            branch_name="feature_branch",
            commit_msg="Full test run",
            status=RunStatus.RUNNING,
            dag_snapshot={"test": "data"},
            trace_id="trace_001",
            root_hash="abc123"
        )
        await store.create_run(run)

        fetched = await store.get_run("full_run")
        assert fetched.branch_name == "feature_branch"
        assert fetched.commit_msg == "Full test run"
        assert fetched.trace_id == "trace_001"
        assert fetched.root_hash == "abc123"


class TestNodeExecutionOperations:
    """Tests for NodeExecution CRUD operations."""

    @pytest.mark.asyncio
    async def test_upsert_node_execution(self, store, sample_run):
        """Test creating a node execution."""
        await store.create_run(sample_run)

        exec = NodeExecution(
            id="exec_001_node_A",
            run_id=sample_run.run_id,
            node_id="node_A",
            status=NodeStatus.PENDING
        )
        result = await store.upsert_node_execution(exec)

        assert result.id == exec.id
        assert result.node_id == "node_A"

    @pytest.mark.asyncio
    async def test_get_node_execution(self, store, sample_run):
        """Test getting a node execution."""
        await store.create_run(sample_run)

        exec = NodeExecution(
            id="exec_001_node_A",
            run_id=sample_run.run_id,
            node_id="node_A",
            status=NodeStatus.EXECUTING
        )
        await store.upsert_node_execution(exec)

        fetched = await store.get_node_execution(sample_run.run_id, "node_A")
        assert fetched is not None
        assert fetched.status == NodeStatus.EXECUTING

    @pytest.mark.asyncio
    async def test_update_node_execution_status(self, store, sample_run):
        """Test updating node execution status via upsert."""
        await store.create_run(sample_run)

        # Create initial
        exec = NodeExecution(
            id="exec_001_node_A",
            run_id=sample_run.run_id,
            node_id="node_A",
            status=NodeStatus.EXECUTING
        )
        await store.upsert_node_execution(exec)

        # Update status
        exec.status = NodeStatus.SUCCEEDED
        await store.upsert_node_execution(exec)

        fetched = await store.get_node_execution(sample_run.run_id, "node_A")
        assert fetched.status == NodeStatus.SUCCEEDED

    @pytest.mark.asyncio
    async def test_node_execution_with_config_snapshot(self, store, sample_run, sample_node_config):
        """Test node execution with config snapshot."""
        await store.create_run(sample_run)

        exec = NodeExecution(
            id="exec_with_config",
            run_id=sample_run.run_id,
            node_id="node_config",
            status=NodeStatus.EXECUTING,
            config_snapshot=sample_node_config
        )
        await store.upsert_node_execution(exec)

        fetched = await store.get_node_execution(sample_run.run_id, "node_config")
        assert fetched.config_snapshot is not None
        assert fetched.config_snapshot.prompt == "A beautiful sunset"
        assert fetched.config_snapshot.seed == 42

    @pytest.mark.asyncio
    async def test_node_execution_with_external_job_id(self, store, sample_run):
        """Test node execution with external job info for crash recovery."""
        await store.create_run(sample_run)

        exec = NodeExecution(
            id="exec_external",
            run_id=sample_run.run_id,
            node_id="node_ext",
            status=NodeStatus.EXECUTING,
            external_api_provider="kling",
            external_job_id="kling_job_12345"
        )
        await store.upsert_node_execution(exec)

        fetched = await store.get_node_execution(sample_run.run_id, "node_ext")
        assert fetched.external_api_provider == "kling"
        assert fetched.external_job_id == "kling_job_12345"

    @pytest.mark.asyncio
    async def test_node_execution_with_error(self, store, sample_run):
        """Test node execution with error info."""
        await store.create_run(sample_run)

        exec = NodeExecution(
            id="exec_error",
            run_id=sample_run.run_id,
            node_id="node_err",
            status=NodeStatus.FAILED,
            error_msg="API timeout",
            error_traceback="Traceback..."
        )
        await store.upsert_node_execution(exec)

        fetched = await store.get_node_execution(sample_run.run_id, "node_err")
        assert fetched.error_msg == "API timeout"
        assert fetched.error_traceback == "Traceback..."

    @pytest.mark.asyncio
    async def test_get_nonexistent_node_execution(self, store, sample_run):
        """Test getting a node execution that doesn't exist."""
        await store.create_run(sample_run)
        result = await store.get_node_execution(sample_run.run_id, "nonexistent")
        assert result is None


class TestBlobOperations:
    """Tests for BlobMetadata operations."""

    @pytest.mark.asyncio
    async def test_register_blob(self, store):
        """Test registering a blob."""
        blob = BlobMetadata(
            blob_id="sha256_test_hash",
            relative_path="objects/ab/cdef.mp4",
            file_size_bytes=1024,
            mime_type="video/mp4"
        )
        result = await store.register_blob(blob)
        assert result.blob_id == blob.blob_id

    @pytest.mark.asyncio
    async def test_get_blob(self, store):
        """Test getting a blob."""
        blob = BlobMetadata(
            blob_id="sha256_get_test",
            relative_path="objects/get/test.mp4",
            file_size_bytes=2048
        )
        await store.register_blob(blob)

        fetched = await store.get_blob(blob.blob_id)
        assert fetched is not None
        assert fetched.relative_path == "objects/get/test.mp4"
        assert fetched.file_size_bytes == 2048

    @pytest.mark.asyncio
    async def test_get_nonexistent_blob(self, store):
        """Test getting a blob that doesn't exist."""
        result = await store.get_blob("nonexistent_hash")
        assert result is None

    @pytest.mark.asyncio
    async def test_register_blob_upsert(self, store):
        """Test registering same blob twice updates it."""
        blob = BlobMetadata(
            blob_id="sha256_upsert",
            relative_path="objects/upsert/v1.mp4",
            file_size_bytes=1024
        )
        await store.register_blob(blob)

        # Update with same hash but different path/size
        blob2 = BlobMetadata(
            blob_id="sha256_upsert",
            relative_path="objects/upsert/v2.mp4",
            file_size_bytes=2048
        )
        await store.register_blob(blob2)

        fetched = await store.get_blob("sha256_upsert")
        assert fetched.relative_path == "objects/upsert/v2.mp4"
        assert fetched.file_size_bytes == 2048


class TestArtifactOperations:
    """Tests for Artifact operations."""

    @pytest.mark.asyncio
    async def test_link_artifact(self, store, sample_run):
        """Test linking an artifact."""
        await store.create_run(sample_run)

        # Register blob first
        blob = BlobMetadata(
            blob_id="sha256_art_test",
            relative_path="objects/art/test.mp4",
            file_size_bytes=1024
        )
        await store.register_blob(blob)

        artifact = Artifact(
            id="art_001",
            run_id=sample_run.run_id,
            node_id="node_A",
            blob_hash=blob.blob_id,
            metadata={"cost": 0.5},
            is_reused=False
        )
        result = await store.link_artifact(artifact)
        assert result.id == artifact.id

    @pytest.mark.asyncio
    async def test_get_artifact(self, store, sample_run):
        """Test getting an artifact."""
        await store.create_run(sample_run)

        blob = BlobMetadata(
            blob_id="sha256_get_art",
            relative_path="objects/get/art.mp4"
        )
        await store.register_blob(blob)

        artifact = Artifact(
            id="art_get",
            run_id=sample_run.run_id,
            node_id="node_get",
            blob_hash=blob.blob_id,
            metadata={"prompt": "test"}
        )
        await store.link_artifact(artifact)

        fetched = await store.get_artifact(sample_run.run_id, "node_get")
        assert fetched is not None
        assert fetched.blob_hash == blob.blob_id
        assert fetched.metadata["prompt"] == "test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_artifact(self, store, sample_run):
        """Test getting an artifact that doesn't exist."""
        await store.create_run(sample_run)
        result = await store.get_artifact(sample_run.run_id, "nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_artifact_is_reused_flag(self, store, sample_run):
        """Test artifact is_reused flag."""
        await store.create_run(sample_run)

        blob = BlobMetadata(
            blob_id="sha256_reused",
            relative_path="objects/reused.mp4"
        )
        await store.register_blob(blob)

        artifact = Artifact(
            id="art_reused",
            run_id=sample_run.run_id,
            node_id="node_reused",
            blob_hash=blob.blob_id,
            is_reused=True
        )
        await store.link_artifact(artifact)

        fetched = await store.get_artifact(sample_run.run_id, "node_reused")
        assert fetched.is_reused is True


class TestCrashRecovery:
    """Tests for crash recovery helpers."""

    @pytest.mark.asyncio
    async def test_find_stuck_executions(self, store, sample_run):
        """Test finding stuck executions (EXECUTING/QUEUED with external_job_id)."""
        await store.create_run(sample_run)

        # Create stuck execution
        stuck_exec = NodeExecution(
            id="exec_stuck",
            run_id=sample_run.run_id,
            node_id="node_stuck",
            status=NodeStatus.EXECUTING,
            external_api_provider="kling",
            external_job_id="kling_12345"
        )
        await store.upsert_node_execution(stuck_exec)

        # Create completed execution (should not be found)
        completed_exec = NodeExecution(
            id="exec_completed",
            run_id=sample_run.run_id,
            node_id="node_completed",
            status=NodeStatus.SUCCEEDED,
            external_job_id="kling_67890"
        )
        await store.upsert_node_execution(completed_exec)

        stuck = await store.find_stuck_executions()
        assert len(stuck) >= 1
        assert any(e.node_id == "node_stuck" for e in stuck)
        assert not any(e.node_id == "node_completed" for e in stuck)

    @pytest.mark.asyncio
    async def test_find_stuck_executions_by_provider(self, store, sample_run):
        """Test finding stuck executions filtered by provider."""
        await store.create_run(sample_run)

        # Kling stuck
        kling_exec = NodeExecution(
            id="exec_kling",
            run_id=sample_run.run_id,
            node_id="node_kling",
            status=NodeStatus.EXECUTING,
            external_api_provider="kling",
            external_job_id="kling_123"
        )
        await store.upsert_node_execution(kling_exec)

        # Runway stuck
        runway_exec = NodeExecution(
            id="exec_runway",
            run_id=sample_run.run_id,
            node_id="node_runway",
            status=NodeStatus.QUEUED,
            external_api_provider="runway",
            external_job_id="runway_456"
        )
        await store.upsert_node_execution(runway_exec)

        # Filter by provider
        kling_stuck = await store.find_stuck_executions(provider="kling")
        assert len(kling_stuck) == 1
        assert kling_stuck[0].node_id == "node_kling"

        runway_stuck = await store.find_stuck_executions(provider="runway")
        assert len(runway_stuck) == 1
        assert runway_stuck[0].node_id == "node_runway"

    @pytest.mark.asyncio
    async def test_find_no_stuck_executions(self, store, sample_run):
        """Test finding stuck executions when none exist."""
        await store.create_run(sample_run)

        stuck = await store.find_stuck_executions()
        assert stuck == []


class TestPopulatedStore:
    """Tests using populated_store fixture."""

    @pytest.mark.asyncio
    async def test_populated_store_has_run(self, populated_store):
        """Test populated_store has test run."""
        run = await populated_store.get_run("test_run_001")
        assert run is not None
        assert run.status == RunStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_populated_store_has_nodes(self, populated_store):
        """Test populated_store has node executions."""
        for node_id in ["node_A", "node_B", "node_C"]:
            exec = await populated_store.get_node_execution("test_run_001", node_id)
            assert exec is not None
            assert exec.status == NodeStatus.SUCCEEDED

    @pytest.mark.asyncio
    async def test_populated_store_has_artifact(self, populated_store):
        """Test populated_store has artifact."""
        artifact = await populated_store.get_artifact("test_run_001", "node_A")
        assert artifact is not None
        assert artifact.is_reused is False

    @pytest.mark.asyncio
    async def test_populated_store_blob(self, populated_store):
        """Test populated_store has blob."""
        blob = await populated_store.get_blob("sha256_test_abc123")
        assert blob is not None
        assert blob.mime_type == "video/mp4"


@pytest.mark.integration
class TestStoreIntegration:
    """Integration tests for Store."""

    @pytest.mark.asyncio
    async def test_run_deletes_cascade_artifacts(self, store, sample_run):
        """Test that deleting a run cascades to artifacts (FK enabled)."""
        await store.create_run(sample_run)

        blob = BlobMetadata(
            blob_id="sha256_cascade",
            relative_path="objects/cascade.mp4"
        )
        await store.register_blob(blob)

        artifact = Artifact(
            id="art_cascade",
            run_id=sample_run.run_id,
            node_id="node_cascade",
            blob_hash=blob.blob_id
        )
        await store.link_artifact(artifact)

        # Delete run with foreign keys enabled
        async with aiosqlite.connect(store.db_path) as db:
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("DELETE FROM pipeline_runs WHERE run_id = ?", (sample_run.run_id,))
            await db.commit()

        # Artifact should be gone due to cascade
        art = await store.get_artifact(sample_run.run_id, "node_cascade")
        assert art is None

    @pytest.mark.asyncio
    async def test_multiple_runs_same_node(self, store):
        """Test multiple runs with same node_id."""
        # Create two runs
        run1 = PipelineRun(run_id="run_multi_1")
        run2 = PipelineRun(run_id="run_multi_2")
        await store.create_run(run1)
        await store.create_run(run2)

        # Same node in both runs
        exec1 = NodeExecution(
            id="exec_multi_1_A",
            run_id="run_multi_1",
            node_id="node_A",
            status=NodeStatus.SUCCEEDED
        )
        exec2 = NodeExecution(
            id="exec_multi_2_A",
            run_id="run_multi_2",
            node_id="node_A",
            status=NodeStatus.EXECUTING
        )
        await store.upsert_node_execution(exec1)
        await store.upsert_node_execution(exec2)

        # Both should exist
        fetched1 = await store.get_node_execution("run_multi_1", "node_A")
        fetched2 = await store.get_node_execution("run_multi_2", "node_A")
        assert fetched1.status == NodeStatus.SUCCEEDED
        assert fetched2.status == NodeStatus.EXECUTING