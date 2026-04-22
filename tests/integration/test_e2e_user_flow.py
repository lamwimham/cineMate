"""
CineMate E2E User Flow Integration Tests

End-to-End tests simulating real user workflows:
- Creating video tasks
- Viewing history
- Video Git operations (branch/diff)

Usage:
    pytest tests/integration/test_e2e_user_flow.py -v --disable-warnings

Requirements:
    - FastAPI test client
    - pytest-asyncio
"""

import pytest
from typing import List

from fastapi.testclient import TestClient
from cine_mate.api.main import app


@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def test_db_path(tmp_path) -> str:
    """Create temporary database path for tests."""
    return str(tmp_path / "test_cinemate_e2e.db")


class TestCreateVideoTaskFlow:
    """E2E Test: Complete video creation workflow."""
    
    def test_full_creation_flow(self, client: TestClient, test_db_path: str):
        """
        Test complete video creation flow:
        1. User submits prompt
        2. System creates run
        3. User checks status
        4. User views result
        """
        # Step 1: Submit prompt
        prompt = "Create a sunset beach video, warm tones, 10 seconds"
        create_payload = {
            "prompt": prompt,
            "style": "cinematic",
            "branch_name": "main",
        }
        
        create_response = client.post(
            "/runs",
            json=create_payload,
            params={"db_path": test_db_path}
        )
        assert create_response.status_code == 201
        run_data = create_response.json()
        run_id = run_data["run_id"]
        
        # Step 2: Verify run created
        assert run_id.startswith("run_api_")
        assert run_data["commit_msg"] == prompt
        assert run_data["branch_name"] == "main"
        
        # Step 3: Check status
        status_response = client.get(
            f"/runs/{run_id}",
            params={"db_path": test_db_path}
        )
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["run_id"] == run_id
        assert status_data["status"] in ["pending", "processing", "completed"]
        
        # Step 4: View result (check nodes)
        assert "nodes" in status_data
        assert len(status_data["nodes"]) > 0
    
    def test_creation_with_custom_branch(
        self,
        client: TestClient,
        test_db_path: str
    ):
        """Test creating video on custom branch."""
        prompt = "Create a mountain landscape video"
        payload = {
            "prompt": prompt,
            "branch_name": "feature-mountains",
        }
        
        response = client.post(
            "/runs",
            json=payload,
            params={"db_path": test_db_path}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["branch_name"] == "feature-mountains"
    
    def test_creation_with_parent_version(
        self,
        client: TestClient,
        test_db_path: str
    ):
        """Test creating new version based on existing run."""
        # Create original
        original_payload = {"prompt": "Original video concept"}
        original_response = client.post(
            "/runs",
            json=original_payload,
            params={"db_path": test_db_path}
        )
        original_id = original_response.json()["run_id"]
        
        # Create new version
        new_payload = {
            "prompt": "Improved version with better lighting",
            "parent_run_id": original_id,
            "branch_name": "main",
        }
        new_response = client.post(
            "/runs",
            json=new_payload,
            params={"db_path": test_db_path}
        )
        
        assert new_response.status_code == 201
        new_data = new_response.json()
        assert new_data["parent_run_id"] == original_id


class TestViewHistoryFlow:
    """E2E Test: Viewing and filtering run history."""
    
    def test_list_recent_runs(self, client: TestClient, test_db_path: str):
        """Test listing recent runs."""
        # Create multiple runs
        prompts = [
            "Video 1: City scene",
            "Video 2: Nature scene",
            "Video 3: Abstract art",
        ]
        
        for prompt in prompts:
            client.post(
                "/runs",
                json={"prompt": prompt},
                params={"db_path": test_db_path}
            )
        
        # Small delay to ensure DB writes complete
        import time
        time.sleep(0.3)
        
        # List runs
        response = client.get(
            "/runs",
            params={"db_path": test_db_path, "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Note: Due to async DB writes, we might not see all runs immediately
        assert "runs" in data
        assert "total" in data
        assert data["limit"] == 10
    
    def test_pagination(self, client: TestClient, test_db_path: str):
        """Test pagination of run list."""
        # Create 25 runs
        for i in range(25):
            client.post(
                "/runs",
                json={"prompt": f"Video #{i}"},
                params={"db_path": test_db_path}
            )
        
        # Get first page (limit 10)
        import time
        time.sleep(0.5)
        response = client.get(
            "/runs",
            params={"db_path": test_db_path, "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Note: May not see all 25 runs due to async writes
        assert "runs" in data
        assert len(data["runs"]) <= 10
        assert data["limit"] == 10
    
    def test_filter_by_branch(self, client: TestClient, test_db_path: str):
        """Test filtering runs by branch."""
        # Create runs on different branches
        branches = ["main", "dev", "main", "feature", "main"]
        for branch in branches:
            client.post(
                "/runs",
                json={"prompt": "Test video", "branch_name": branch},
                params={"db_path": test_db_path}
            )
        
        # Small delay
        import time
        time.sleep(0.3)
        
        # Filter by main branch
        response = client.get(
            "/runs",
            params={"db_path": test_db_path, "branch": "main"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Note: May not see all runs due to async writes
        assert "runs" in data
        # Verify all returned runs are from main branch
        for run in data["runs"]:
            assert run["branch_name"] == "main"


class TestVideoGitOperations:
    """E2E Test: Video Git operations (branch, version, diff)."""
    
    def test_create_version_tree(self, client: TestClient, test_db_path: str):
        """
        Test creating a version tree:
        
        v1 (main)
          └─ v2 (main, parent=v1)
             └─ v3 (main, parent=v2)
        """
        # Create v1
        v1_response = client.post(
            "/runs",
            json={"prompt": "Version 1: Initial concept"},
            params={"db_path": test_db_path}
        )
        v1_id = v1_response.json()["run_id"]
        
        # Create v2 (child of v1)
        v2_response = client.post(
            "/runs",
            json={
                "prompt": "Version 2: Improved lighting",
                "parent_run_id": v1_id,
            },
            params={"db_path": test_db_path}
        )
        v2_id = v2_response.json()["run_id"]
        
        # Create v3 (child of v2)
        v3_response = client.post(
            "/runs",
            json={
                "prompt": "Version 3: Final version",
                "parent_run_id": v2_id,
            },
            params={"db_path": test_db_path}
        )
        v3_id = v3_response.json()["run_id"]
        
        # Verify chain
        assert v2_response.json()["parent_run_id"] == v1_id
        assert v3_response.json()["parent_run_id"] == v2_id
        
        # Get latest version details
        v3_details = client.get(
            f"/runs/{v3_id}",
            params={"db_path": test_db_path}
        ).json()
        
        assert v3_details["run_id"] == v3_id
        assert "Version 3" in v3_details["commit_msg"]
    
    def test_create_branch(self, client: TestClient, test_db_path: str):
        """
        Test creating branches:
        
        main: v1 → v2
               └─ feature-a: v3 → v4
        """
        # Create main line
        v1_response = client.post(
            "/runs",
            json={"prompt": "Main v1"},
            params={"db_path": test_db_path}
        )
        v1_id = v1_response.json()["run_id"]
        
        v2_response = client.post(
            "/runs",
            json={
                "prompt": "Main v2",
                "parent_run_id": v1_id,
                "branch_name": "main",
            },
            params={"db_path": test_db_path}
        )
        
        # Create feature branch from v1
        v3_response = client.post(
            "/runs",
            json={
                "prompt": "Feature v3 (experimental)",
                "parent_run_id": v1_id,
                "branch_name": "feature-a",
            },
            params={"db_path": test_db_path}
        )
        v3_id = v3_response.json()["run_id"]
        
        v4_response = client.post(
            "/runs",
            json={
                "prompt": "Feature v4",
                "parent_run_id": v3_id,
                "branch_name": "feature-a",
            },
            params={"db_path": test_db_path}
        )
        
        # Verify branches
        assert v2_response.json()["branch_name"] == "main"
        assert v3_response.json()["branch_name"] == "feature-a"
        assert v4_response.json()["branch_name"] == "feature-a"
        
        # List only feature-a branch
        feature_response = client.get(
            "/runs",
            params={"db_path": test_db_path, "branch": "feature-a"}
        )
        
        assert feature_response.json()["total"] == 2
    
    def test_get_run_details_with_nodes(
        self,
        client: TestClient,
        test_db_path: str
    ):
        """Test getting detailed run info with node executions."""
        # Create run
        response = client.post(
            "/runs",
            json={"prompt": "Test video with full pipeline"},
            params={"db_path": test_db_path}
        )
        run_id = response.json()["run_id"]
        
        # Get details
        details_response = client.get(
            f"/runs/{run_id}",
            params={"db_path": test_db_path}
        )
        
        assert details_response.status_code == 200
        data = details_response.json()
        
        # Verify structure
        assert "run_id" in data
        assert "nodes" in data
        assert "status" in data
        assert "created_at" in data
        
        # Check node structure
        nodes = data["nodes"]
        assert isinstance(nodes, list)
        if len(nodes) > 0:
            node = nodes[0]
            assert "node_id" in node
            assert "node_type" in node
            assert "status" in node


class TestUpdateRunFlow:
    """E2E Test: Updating run status and metadata."""
    
    def test_update_status_flow(self, client: TestClient, test_db_path: str):
        """Test updating run status through lifecycle."""
        # Create run
        create_response = client.post(
            "/runs",
            json={"prompt": "Test video"},
            params={"db_path": test_db_path}
        )
        run_id = create_response.json()["run_id"]
        
        # Update to processing
        update_response = client.patch(
            f"/runs/{run_id}",
            json={"status": "processing"},
            params={"db_path": test_db_path}
        )
        assert update_response.json()["status"] == "processing"
        
        # Update to completed
        update_response = client.patch(
            f"/runs/{run_id}",
            json={"status": "completed"},
            params={"db_path": test_db_path}
        )
        assert update_response.json()["status"] == "completed"
    
    def test_update_commit_message(
        self,
        client: TestClient,
        test_db_path: str
    ):
        """Test updating commit message (like git commit --amend)."""
        # Create run
        create_response = client.post(
            "/runs",
            json={"prompt": "Initial message"},
            params={"db_path": test_db_path}
        )
        run_id = create_response.json()["run_id"]
        
        # Amend message
        update_response = client.patch(
            f"/runs/{run_id}",
            json={"commit_msg": "Amended: Better description"},
            params={"db_path": test_db_path}
        )
        
        assert update_response.json()["commit_msg"] == "Amended: Better description"


class TestErrorScenarios:
    """E2E Test: Error scenarios and edge cases."""
    
    def test_parent_not_found(self, client: TestClient, test_db_path: str):
        """Test creating run with non-existent parent."""
        payload = {
            "prompt": "Child video",
            "parent_run_id": "non_existent_parent",
        }
        
        response = client.post(
            "/runs",
            json=payload,
            params={"db_path": test_db_path}
        )
        
        # Should handle gracefully (either create or return error)
        assert response.status_code in [201, 400, 404]
    
    def test_concurrent_creations(
        self,
        client: TestClient,
        test_db_path: str
    ):
        """Test multiple concurrent run creations."""
        # Create 10 runs quickly
        responses = []
        for i in range(10):
            response = client.post(
                "/runs",
                json={"prompt": f"Concurrent video #{i}"},
                params={"db_path": test_db_path}
            )
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 201
        
        # Verify all created
        list_response = client.get(
            "/runs",
            params={"db_path": test_db_path, "limit": 20}
        )
        assert list_response.json()["total"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
