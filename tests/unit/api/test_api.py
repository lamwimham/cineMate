"""
Tests for CineMate FastAPI Backend.
Covers REST API endpoints and WebSocket connection.
"""

import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from cine_mate.api.main import app
from cine_mate.core.store import Store
from cine_mate.core.models import PipelineRun, RunStatus, NodeExecution, NodeStatus


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_db():
    """Provide a temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
async def populated_db(temp_db):
    """Provide a database with sample runs."""
    store = Store(temp_db)
    await store.init_db()

    # Run 1
    run1 = PipelineRun(
        run_id="api_run_001",
        parent_run_id=None,
        branch_name="main",
        commit_msg="Cyberpunk city video",
        status=RunStatus.COMPLETED,
    )
    await store.create_run(run1)
    for node_id in ["script", "image", "video"]:
        await store.upsert_node_execution(NodeExecution(
            id=f"exec_api_001_{node_id}",
            run_id="api_run_001",
            node_id=node_id,
            status=NodeStatus.SUCCEEDED,
        ))

    # Run 2
    run2 = PipelineRun(
        run_id="api_run_002",
        parent_run_id="api_run_001",
        branch_name="experiment",
        commit_msg="Product ad",
        status=RunStatus.PENDING,
    )
    await store.create_run(run2)

    return str(temp_db)


@pytest.fixture
def client():
    """Provide a FastAPI test client."""
    return TestClient(app)


# =============================================================================
# Health & Root Tests
# =============================================================================

class TestHealthAndRoot:
    """Test basic API endpoints."""

    def test_health_check(self, client):
        """Health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "CineMate API"
        assert "docs" in data
        assert "runs" in data


# =============================================================================
# Runs CRUD Tests
# =============================================================================

class TestRunsAPI:
    """Test /runs REST API endpoints."""

    def test_list_runs_empty(self, client, temp_db):
        """List runs returns empty list for new database."""
        response = client.get("/runs", params={"db_path": str(temp_db)})
        assert response.status_code == 200
        data = response.json()
        assert data["runs"] == []
        assert data["total"] == 0

    def test_list_runs_with_data(self, client, populated_db):
        """List runs returns runs from database."""
        response = client.get("/runs", params={"db_path": populated_db})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        run_ids = {r["run_id"] for r in data["runs"]}
        assert "api_run_001" in run_ids
        assert "api_run_002" in run_ids

    def test_list_runs_filter_by_branch(self, client, populated_db):
        """List runs filters by branch."""
        response = client.get("/runs", params={
            "db_path": populated_db,
            "branch": "experiment",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["runs"][0]["run_id"] == "api_run_002"

    def test_list_runs_limit(self, client, populated_db):
        """List runs respects limit parameter."""
        response = client.get("/runs", params={
            "db_path": populated_db,
            "limit": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["runs"]) == 1

    def test_get_run_detail(self, client, populated_db):
        """Get run detail returns node-level info."""
        response = client.get(f"/runs/api_run_001", params={"db_path": populated_db})
        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == "api_run_001"
        assert len(data["nodes"]) == 3
        node_ids = {n["node_id"] for n in data["nodes"]}
        assert "script" in node_ids
        assert "image" in node_ids
        assert "video" in node_ids

    def test_get_run_not_found(self, client, populated_db):
        """Get non-existent run returns 404."""
        response = client.get(f"/runs/nonexistent", params={"db_path": populated_db})
        assert response.status_code == 404

    def test_create_run(self, client, temp_db):
        """Create run via API executes pipeline."""
        response = client.post("/runs", params={"db_path": str(temp_db)}, json={
            "prompt": "Test video creation",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["run_id"].startswith("run_api_")
        assert data["status"] == "completed"
        assert data["node_count"] > 0

    def test_create_run_with_parent(self, client, populated_db):
        """Create run with parent_run_id."""
        response = client.post("/runs", params={"db_path": populated_db}, json={
            "prompt": "Child run",
            "parent_run_id": "api_run_001",
            "branch_name": "main",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["parent_run_id"] == "api_run_001"

    def test_update_run_status(self, client, populated_db):
        """Update run status via PATCH."""
        response = client.patch(
            f"/runs/api_run_002",
            params={"db_path": populated_db},
            json={"status": "cancelled"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_update_run_not_found(self, client, populated_db):
        """Update non-existent run returns 404."""
        response = client.patch(
            f"/runs/nonexistent",
            params={"db_path": populated_db},
            json={"status": "cancelled"},
        )
        assert response.status_code == 404

    def test_delete_run(self, client, populated_db):
        """Delete run via DELETE."""
        response = client.delete(
            f"/runs/api_run_002",
            params={"db_path": populated_db},
        )
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/runs/api_run_002", params={"db_path": populated_db})
        assert response.status_code == 404

    def test_delete_run_not_found(self, client, populated_db):
        """Delete non-existent run returns 404."""
        response = client.delete(
            f"/runs/nonexistent",
            params={"db_path": populated_db},
        )
        assert response.status_code == 404


# =============================================================================
# OpenAPI Docs Tests
# =============================================================================

class TestOpenAPIDocs:
    """Test API documentation is generated correctly."""

    def test_openapi_schema_available(self, client):
        """OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "info" in schema
        assert schema["info"]["title"] == "CineMate API"

    def test_runs_endpoint_in_docs(self, client):
        """Runs endpoint documented in OpenAPI."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "/runs" in schema["paths"]
        assert "/runs/{run_id}" in schema["paths"]

    def test_health_endpoint_in_docs(self, client):
        """Health endpoint documented in OpenAPI."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "/health" in schema["paths"]
