"""
Tests for CineMate SkillReviewer — auto-generation of skills from PipelineRun analysis.
Covers success, failure, and retry review scenarios.
"""

import pytest
import tempfile
from pathlib import Path

from cine_mate.skills.skill_store import SkillStore
from cine_mate.skills.skill_reviewer import SkillReviewer
from cine_mate.skills.models import SkillCategory


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
async def skills_dir():
    """Provide a temporary skills directory."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
async def store(skills_dir):
    """Provide a fresh SkillStore instance."""
    s = SkillStore(skills_dir)
    await s.init()
    yield s


@pytest.fixture
def reviewer(store):
    """Provide a SkillReviewer backed by the store."""
    return SkillReviewer(store)


# =============================================================================
# Success Review Tests
# =============================================================================

class TestReviewSuccess:
    """Test SkillReviewer on successful PipelineRun outcomes."""
    
    @pytest.mark.asyncio
    async def test_creates_workflow_skill_for_complex_run(self, reviewer):
        """Creates a workflow skill for runs with 3+ nodes."""
        run_data = {
            "run_id": "run_success_001",
            "status": "completed",
            "intent": "Create a cyberpunk product showcase video",
            "nodes": [
                {"id": "script", "type": "script_gen", "params": {"prompt": "test"}, "status": "succeeded"},
                {"id": "image", "type": "text_to_image", "params": {"prompt": "test"}, "status": "succeeded"},
                {"id": "video", "type": "image_to_video", "status": "succeeded"},
            ],
            "retry_count": 0,
        }
        
        result = await reviewer.review(run_data)
        
        assert result is not None
        assert result.auto_generated is True
        assert result.source_run_id == "run_success_001"
        assert result.category == SkillCategory.WORKFLOW
        assert "workflow-auto-run_success_001" in result.name
    
    @pytest.mark.asyncio
    async def test_skips_simple_runs(self, reviewer):
        """Skips runs with fewer than 3 nodes (too simple to patternize)."""
        run_data = {
            "run_id": "run_simple",
            "status": "completed",
            "intent": "Make a video",
            "nodes": [
                {"id": "vid", "type": "text_to_video", "status": "succeeded"},
            ],
            "retry_count": 0,
        }
        
        result = await reviewer.review(run_data)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_skips_already_reviewed_runs(self, reviewer):
        """Does not create duplicate skills for the same run_id."""
        run_data = {
            "run_id": "run_dup",
            "status": "completed",
            "intent": "Test video",
            "nodes": [
                {"id": "a", "type": "script_gen", "status": "succeeded"},
                {"id": "b", "type": "text_to_image", "status": "succeeded"},
                {"id": "c", "type": "image_to_video", "status": "succeeded"},
            ],
            "retry_count": 0,
        }
        
        # First review creates skill
        result1 = await reviewer.review(run_data)
        assert result1 is not None
        
        # Second review skips
        result2 = await reviewer.review(run_data)
        assert result2 is None
    
    @pytest.mark.asyncio
    async def test_skill_content_includes_workflow(self, reviewer):
        """Generated skill content includes node sequence and configuration."""
        run_data = {
            "run_id": "run_content_test",
            "status": "completed",
            "intent": "Product ad for headphones",
            "nodes": [
                {"id": "hook", "type": "text_to_video", "params": {"duration": 3}, "status": "succeeded"},
                {"id": "demo", "type": "image_to_video", "params": {"duration": 5}, "status": "succeeded"},
                {"id": "compose", "type": "video_compose", "status": "succeeded"},
            ],
            "retry_count": 0,
        }
        
        result = await reviewer.review(run_data)
        assert result is not None
        
        # Verify content was written to file
        skill = await reviewer.store.read(result.name)
        assert skill is not None
        assert "text_to_video" in skill.content
        assert "image_to_video" in skill.content
        assert "video_compose" in skill.content


# =============================================================================
# Failure Review Tests
# =============================================================================

class TestReviewFailure:
    """Test SkillReviewer on failed PipelineRun outcomes."""
    
    @pytest.mark.asyncio
    async def test_creates_error_skill_for_identifiable_error(self, reviewer):
        """Creates an error recovery skill for identifiable error patterns."""
        run_data = {
            "run_id": "run_fail_001",
            "status": "failed",
            "intent": "Generate a portrait video",
            "nodes": [
                {"id": "image", "type": "text_to_image", "status": "succeeded"},
                {"id": "video", "type": "image_to_video", "status": "failed",
                 "params": {"duration": 10, "resolution": "4k"}},
            ],
            "error": {
                "type": "face_distortion",
                "message": "Kling API returned distorted face rendering",
            },
            "retry_count": 0,
        }
        
        result = await reviewer.review(run_data)
        
        assert result is not None
        assert result.auto_generated is True
        assert result.source_run_id == "run_fail_001"
        assert result.source_error == "face_distortion"
        assert result.category == SkillCategory.ERROR_RECOVERY
    
    @pytest.mark.asyncio
    async def test_skips_generic_errors(self, reviewer):
        """Skips timeout/cancelled/user_interrupt errors (too generic)."""
        generic_errors = ["timeout", "cancelled", "user_interrupt"]
        
        for error_type in generic_errors:
            run_data = {
                "run_id": f"run_{error_type}",
                "status": "failed",
                "intent": "Test",
                "nodes": [
                    {"id": "vid", "type": "text_to_video", "status": "failed"},
                ],
                "error": {
                    "type": error_type,
                    "message": f"Operation {error_type}",
                },
                "retry_count": 0,
            }
            
            result = await reviewer.review(run_data)
            assert result is None, f"Should skip generic error: {error_type}"
    
    @pytest.mark.asyncio
    async def test_skips_failure_without_error_info(self, reviewer):
        """Skips failures with no error details."""
        run_data = {
            "run_id": "run_no_error",
            "status": "failed",
            "intent": "Test",
            "nodes": [],
            "retry_count": 0,
        }
        
        result = await reviewer.review(run_data)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_error_skill_content_includes_recovery_steps(self, reviewer):
        """Error skill content includes recovery recommendations."""
        run_data = {
            "run_id": "run_error_content",
            "status": "failed",
            "intent": "Generate video",
            "nodes": [
                {"id": "video", "type": "image_to_video", "status": "failed",
                 "params": {"duration": 10}},
            ],
            "error": {
                "type": "out_of_memory",
                "message": "GPU memory exceeded for 4k resolution",
            },
            "retry_count": 0,
        }
        
        result = await reviewer.review(run_data)
        assert result is not None
        
        skill = await reviewer.store.read(result.name)
        assert skill is not None
        assert "Recovery" in skill.content or "recovery" in skill.content.lower()
        assert "out_of_memory" in skill.content


# =============================================================================
# Retry Review Tests
# =============================================================================

class TestReviewRetry:
    """Test SkillReviewer on retried PipelineRun outcomes."""
    
    @pytest.mark.asyncio
    async def test_creates_recovery_skill_for_multiple_retries(self, reviewer):
        """Creates a retry recovery skill for 2+ retries."""
        run_data = {
            "run_id": "run_retry_001",
            "status": "retried",
            "intent": "Generate a long video",
            "nodes": [
                {"id": "video", "type": "image_to_video", "status": "succeeded",
                 "retry_count": 3, "params": {"duration": 30}},
            ],
            "retry_count": 3,
        }
        
        result = await reviewer.review(run_data)
        
        assert result is not None
        assert result.auto_generated is True
        assert result.source_run_id == "run_retry_001"
        assert result.source_error == "retry_3"
        assert result.category == SkillCategory.ERROR_RECOVERY
    
    @pytest.mark.asyncio
    async def test_skips_single_retry(self, reviewer):
        """Skips runs with only 1 retry (too common to patternize)."""
        run_data = {
            "run_id": "run_single_retry",
            "status": "retried",
            "intent": "Test",
            "nodes": [
                {"id": "video", "type": "image_to_video", "status": "succeeded",
                 "retry_count": 1},
            ],
            "retry_count": 1,
        }
        
        result = await reviewer.review(run_data)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_skips_retry_without_retried_nodes(self, reviewer):
        """Skips when no nodes actually had retries."""
        run_data = {
            "run_id": "run_no_retried_nodes",
            "status": "retried",
            "intent": "Test",
            "nodes": [
                {"id": "video", "type": "image_to_video", "status": "succeeded",
                 "retry_count": 0},
            ],
            "retry_count": 3,
        }
        
        result = await reviewer.review(run_data)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_recovery_skill_content_includes_retry_info(self, reviewer):
        """Recovery skill content includes retry count and configuration."""
        run_data = {
            "run_id": "run_retry_content",
            "status": "retried",
            "intent": "Generate video",
            "nodes": [
                {"id": "video", "type": "text_to_video", "status": "succeeded",
                 "retry_count": 4, "params": {"duration": 60, "resolution": "1080p"}},
            ],
            "retry_count": 4,
        }
        
        result = await reviewer.review(run_data)
        assert result is not None
        
        skill = await reviewer.store.read(result.name)
        assert skill is not None
        assert "4" in skill.content  # Retry count
        assert "text_to_video" in skill.content


# =============================================================================
# Edge Cases
# =============================================================================

class TestReviewerEdgeCases:
    """Test SkillReviewer edge cases."""
    
    @pytest.mark.asyncio
    async def test_unknown_status_returns_none(self, reviewer):
        """Unknown status returns None."""
        run_data = {
            "run_id": "run_unknown",
            "status": "unknown_status",
            "intent": "Test",
            "nodes": [],
            "retry_count": 0,
        }
        
        result = await reviewer.review(run_data)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_empty_nodes_handled_gracefully(self, reviewer):
        """Empty nodes list handled without errors."""
        run_data = {
            "run_id": "run_empty",
            "status": "completed",
            "intent": "Test",
            "nodes": [],
            "retry_count": 0,
        }
        
        result = await reviewer.review(run_data)
        assert result is None  # Too few nodes
    
    @pytest.mark.asyncio
    async def test_missing_run_id_handled_gracefully(self, reviewer):
        """Missing run_id handled without errors."""
        run_data = {
            "status": "completed",
            "intent": "Test",
            "nodes": [
                {"id": "a", "type": "script_gen", "status": "succeeded"},
                {"id": "b", "type": "text_to_image", "status": "succeeded"},
                {"id": "c", "type": "image_to_video", "status": "succeeded"},
            ],
            "retry_count": 0,
        }
        
        # Should not raise, creates skill with empty run_id
        result = await reviewer.review(run_data)
        assert result is not None
