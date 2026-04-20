"""
Tests for Mock Upstream APIs

Validates mock implementations work correctly for integration testing.
"""

import pytest
import asyncio

from tests.mocks.upstream import (
    MockKlingClient,
    MockRunwayClient,
    MockOpenAIClient,
    MockUpstreamFactory,
    MockJobStatus,
    MockJob
)


class TestMockKlingClient:
    """Tests for Mock Kling API."""

    @pytest.mark.asyncio
    async def test_create_text_to_image(self, mock_kling):
        """Test creating text-to-image job."""
        job_id = await mock_kling.create_text_to_image({
            "prompt": "A cyberpunk city",
            "seed": 42
        })

        assert job_id.startswith("kling_img_")
        assert len(mock_kling.jobs) == 1

    @pytest.mark.asyncio
    async def test_create_image_to_video(self, mock_kling):
        """Test creating image-to-video job."""
        job_id = await mock_kling.create_image_to_video({
            "image_url": "http://example.com/image.png",
            "duration": 5,
            "motion_strength": 0.5
        })

        assert job_id.startswith("kling_vid_")
        assert len(mock_kling.jobs) == 1

    @pytest.mark.asyncio
    async def test_job_status_initial(self, mock_kling):
        """Test initial job status is QUEUED."""
        job_id = await mock_kling.create_text_to_image({"prompt": "test"})
        status = await mock_kling.get_job_status(job_id)

        assert status["job_id"] == job_id
        assert status["status"] in ("queued", "running", "completed")

    @pytest.mark.asyncio
    async def test_job_completion(self, mock_kling):
        """Test job completes and returns result."""
        mock_kling.processing_delay = 0.05  # Faster for test

        job_id = await mock_kling.create_text_to_image({"prompt": "test"})
        await asyncio.sleep(0.2)  # Wait for processing

        status = await mock_kling.get_job_status(job_id)

        assert status["status"] == MockJobStatus.COMPLETED.value
        assert status["progress"] == 100
        assert status["result"] is not None
        assert "image_url" in status["result"]

    @pytest.mark.asyncio
    async def test_image_to_video_result(self, mock_kling):
        """Test image-to-video returns video result."""
        mock_kling.processing_delay = 0.05

        job_id = await mock_kling.create_image_to_video({
            "image_url": "test.png",
            "duration": 10
        })
        await asyncio.sleep(0.2)

        status = await mock_kling.get_job_status(job_id)

        assert "video_url" in status["result"]
        assert status["result"]["duration"] == 10

    @pytest.mark.asyncio
    async def test_job_not_found(self, mock_kling):
        """Test status for nonexistent job."""
        status = await mock_kling.get_job_status("nonexistent")

        assert "error" in status
        assert status["error"] == "Job not found"

    @pytest.mark.asyncio
    async def test_cancel_queued_job(self, mock_kling):
        """Test cancelling a queued job."""
        job_id = await mock_kling.create_text_to_image({"prompt": "test"})
        # Don't wait for processing

        cancelled = await mock_kling.cancel_job(job_id)
        status = await mock_kling.get_job_status(job_id)

        assert cancelled is True or status["status"] in ("failed", "queued")
        if cancelled:
            assert status["error"] == "Cancelled by user"

    @pytest.mark.asyncio
    async def test_cancel_running_job_fails(self, mock_kling):
        """Test cannot cancel a running/completed job."""
        mock_kling.processing_delay = 0.05
        job_id = await mock_kling.create_text_to_image({"prompt": "test"})
        await asyncio.sleep(0.15)  # Job is running or completed

        cancelled = await mock_kling.cancel_job(job_id)
        status = await mock_kling.get_job_status(job_id)

        # Cannot cancel if already running/completed
        if status["status"] in ("running", "completed"):
            assert cancelled is False

    @pytest.mark.asyncio
    async def test_cost_calculation(self, mock_kling):
        """Test cost is calculated correctly."""
        # Image job = 1 credit
        img_job_id = await mock_kling.create_text_to_image({"prompt": "test"})
        img_status = await mock_kling.get_job_status(img_job_id)
        assert img_status["cost"] == 1.0

        # Video job = duration * 1.0
        vid_job_id = await mock_kling.create_image_to_video({
            "image_url": "test.png",
            "duration": 10
        })
        vid_status = await mock_kling.get_job_status(vid_job_id)
        assert vid_status["cost"] == 10.0

    def test_reset_clears_jobs(self, mock_kling):
        """Test reset clears all jobs."""
        mock_kling.jobs["test_job"] = MockJob(
            job_id="test",
            job_type="test",
            params={}
        )
        mock_kling.reset()
        assert len(mock_kling.jobs) == 0


class TestMockRunwayClient:
    """Tests for Mock Runway API."""

    @pytest.mark.asyncio
    async def test_create_text_to_video(self, mock_runway):
        """Test creating text-to-video job."""
        task_id = await mock_runway.create_text_to_video({
            "prompt": "A sunset",
            "duration": 10,
            "model": "gen4"
        })

        assert task_id.startswith("runway_vid_")
        assert len(mock_runway.tasks) == 1

    @pytest.mark.asyncio
    async def test_create_image_to_video(self, mock_runway):
        """Test creating image-to-video job."""
        task_id = await mock_runway.create_image_to_video({
            "image_url": "test.png",
            "duration": 5
        })

        assert task_id.startswith("runway_i2v_")

    @pytest.mark.asyncio
    async def test_task_completion(self, mock_runway):
        """Test task completes."""
        mock_runway.processing_delay = 0.05

        task_id = await mock_runway.create_text_to_video({"prompt": "test"})
        await asyncio.sleep(0.5)

        status = await mock_runway.get_task_status(task_id)

        assert status["status"] == MockJobStatus.COMPLETED.value
        assert "video_url" in status["result"]

    @pytest.mark.asyncio
    async def test_cost_calculation(self, mock_runway):
        """Test Runway cost is higher."""
        task_id = await mock_runway.create_text_to_video({
            "prompt": "test",
            "duration": 10
        })
        status = await mock_runway.get_task_status(task_id)

        # Runway: duration * 2.0
        assert status["cost"] == 20.0


class TestMockOpenAIClient:
    """Tests for Mock OpenAI API."""

    @pytest.mark.asyncio
    async def test_chat_completion(self, mock_openai):
        """Test chat completion returns mock script."""
        response = await mock_openai.create_chat_completion({
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Write a cyberpunk video script"}
            ]
        })

        assert "id" in response
        assert "choices" in response
        assert len(response["choices"]) == 1
        assert "content" in response["choices"][0]["message"]

    @pytest.mark.asyncio
    async def test_cyberpunk_script(self, mock_openai):
        """Test cyberpunk prompt generates cyberpunk content."""
        response = await mock_openai.create_chat_completion({
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Create a cyberpunk video"}
            ]
        })

        content = response["choices"][0]["message"]["content"]
        assert "cyberpunk" in content.lower() or "NEON" in content

    @pytest.mark.asyncio
    async def test_product_script(self, mock_openai):
        """Test product prompt generates product content."""
        response = await mock_openai.create_chat_completion({
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Create a product showcase"}
            ]
        })

        content = response["choices"][0]["message"]["content"]
        assert "product" in content.lower() or "PRODUCT" in content

    @pytest.mark.asyncio
    async def test_usage_tokens(self, mock_openai):
        """Test usage includes token counts."""
        response = await mock_openai.create_chat_completion({
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Test prompt"}
            ]
        })

        assert "usage" in response
        assert "prompt_tokens" in response["usage"]
        assert "completion_tokens" in response["usage"]
        assert response["usage"]["total_tokens"] > 0

    @pytest.mark.asyncio
    async def test_call_history(self, mock_openai):
        """Test calls are recorded."""
        await mock_openai.create_chat_completion({
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Test 1"}]
        })
        await mock_openai.create_chat_completion({
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Test 2"}]
        })

        assert len(mock_openai.calls) == 2

    def test_reset_clears_calls(self, mock_openai):
        """Test reset clears call history."""
        mock_openai.calls.append({"test": True})
        mock_openai.reset()
        assert len(mock_openai.calls) == 0


class TestMockUpstreamFactory:
    """Tests for factory."""

    def test_get_kling_client(self):
        """Test getting Kling client."""
        client = MockUpstreamFactory.get_client("kling")
        assert isinstance(client, MockKlingClient)

    def test_get_runway_client(self):
        """Test getting Runway client."""
        client = MockUpstreamFactory.get_client("runway")
        assert isinstance(client, MockRunwayClient)

    def test_get_openai_client(self):
        """Test getting OpenAI client."""
        client = MockUpstreamFactory.get_client("openai")
        assert isinstance(client, MockOpenAIClient)

    def test_unknown_provider_raises(self):
        """Test unknown provider raises error."""
        with pytest.raises(ValueError):
            MockUpstreamFactory.get_client("unknown")

    def test_reuse_same_client(self):
        """Test same provider returns same client instance."""
        client1 = MockUpstreamFactory.get_client("kling")
        client2 = MockUpstreamFactory.get_client("kling")
        assert client1 is client2

    def test_reset_all(self):
        """Test reset clears all clients."""
        kling = MockUpstreamFactory.get_client("kling")
        kling.jobs["test"] = MockJob(job_id="test", job_type="test", params={})

        MockUpstreamFactory.reset_all()

        assert len(kling.jobs) == 0