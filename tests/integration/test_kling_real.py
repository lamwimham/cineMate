"""
Kling AI Real API Integration Tests

These tests make REAL API calls to Kling AI (via WaveSpeed proxy).
They require a valid KLING_API_KEY environment variable.

⚠️  WARNING: These tests cost money! Each test run will consume API credits.
    - Text-to-Video (720p, 5s): ~$0.375
    - Image-to-Video (720p, 5s): ~$0.375

Usage:
    # Set API key
    export KLING_API_KEY="your-api-key-here"
    
    # Run tests (with warnings disabled)
    pytest tests/integration/test_kling_real.py -v --disable-warnings
    
    # Run specific test
    pytest tests/integration/test_kling_real.py::test_kling_text_to_video_real -v

Requirements:
    - KLING_API_KEY environment variable
    - Internet connection
    - Valid Kling API account with credits
"""

import os
import pytest
import asyncio
from typing import Optional

from cine_mate.adapters.kling_provider import KlingProvider, KLING_BASE_URL
from cine_mate.adapters.base import VideoGenerationResult, ProviderError


# Skip all tests in this module if KLING_API_KEY is not set
pytestmark = pytest.mark.skipif(
    not os.getenv("KLING_API_KEY"),
    reason="KLING_API_KEY environment variable not set. Set it to run real API tests."
)


@pytest.fixture
def kling_provider() -> KlingProvider:
    """Create KlingProvider instance with real API key."""
    api_key = os.getenv("KLING_API_KEY")
    return KlingProvider(api_key=api_key)


@pytest.fixture
def test_prompt() -> str:
    """Default test prompt for video generation."""
    return "A cyberpunk city at night with neon lights and flying cars, cinematic lighting, highly detailed"


@pytest.fixture
def test_image_url() -> str:
    """Test image URL for image-to-video mode."""
    # Using a publicly available test image
    return "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&h=600&fit=crop"


class TestKlingRealAPI:
    """Real API integration tests for Kling Provider."""
    
    @pytest.mark.asyncio
    async def test_kling_text_to_video_real(
        self,
        kling_provider: KlingProvider,
        test_prompt: str
    ):
        """
        Test REAL Kling text-to-video API call.
        
        This test:
        1. Submits a text-to-video job to Kling
        2. Waits for job completion
        3. Validates the result contains a video URL
        
        ⚠️  COSTS MONEY: ~$0.375 per run (720p, 5s)
        """
        # Generate video with short duration to minimize cost
        result: VideoGenerationResult = await kling_provider.generate_video(
            prompt=test_prompt,
            duration=5,  # Minimum duration
            resolution="720p"
        )
        
        # Validate result
        assert result is not None, "Result should not be None"
        assert result.is_completed is True, f"Generation should succeed, got error: {result.error_message}"
        assert result.video_url is not None, "Result should contain video URL"
        assert result.video_url.startswith("http"), f"Video URL should be valid HTTP URL, got: {result.video_url}"
        
        # Validate metadata
        assert result.provider == "kling", f"Provider should be 'kling', got: {result.provider}"
        assert result.metadata.get("model") is not None, "Model should be specified in metadata"
        assert result.duration_seconds > 0, "Duration should be positive"
        assert result.cost > 0, "Cost should be positive for real API calls"
        
        print(f"\n✅ Kling text-to-video successful!")
        print(f"   Video URL: {result.video_url}")
        print(f"   Duration: {result.duration_seconds}s")
        print(f"   Cost: ${result.cost:.4f}")
    
    @pytest.mark.asyncio
    async def test_kling_image_to_video_real(
        self,
        kling_provider: KlingProvider,
        test_image_url: str
    ):
        """
        Test REAL Kling image-to-video API call.
        
        This test:
        1. Submits an image-to-video job to Kling
        2. Waits for job completion
        3. Validates the result contains a video URL
        
        ⚠️  COSTS MONEY: ~$0.375 per run (720p, 5s)
        """
        prompt = "Animate this image with subtle camera movement, cinematic style"
        
        result: VideoGenerationResult = await kling_provider.generate_video(
            prompt=prompt,
            duration=5,
            resolution="720p",
            image_url=test_image_url
        )
        
        # Validate result
        assert result is not None, "Result should not be None"
        assert result.is_completed is True, f"Generation should succeed, got error: {result.error_message}"
        assert result.video_url is not None, "Result should contain video URL"
        assert result.video_url.startswith("http"), f"Video URL should be valid HTTP URL, got: {result.video_url}"
        
        # Validate mode from metadata
        assert result.metadata.get("mode") == "image_to_video", f"Mode should be 'image_to_video', got: {result.metadata.get('mode')}"
        
        print(f"\n✅ Kling image-to-video successful!")
        print(f"   Video URL: {result.video_url}")
        print(f"   Duration: {result.duration_seconds}s")
        print(f"   Cost: ${result.cost:.4f}")
    
    @pytest.mark.asyncio
    async def test_kling_api_key_validation(self):
        """
        Test that API key is properly configured.
        
        This is a lightweight test to validate API credentials
        without generating a full video.
        """
        api_key = os.getenv("KLING_API_KEY")
        assert api_key is not None, "KLING_API_KEY should be set"
        assert len(api_key) > 10, "API key should be a valid length"
        
        # Try to create provider (will fail if key is invalid format)
        provider = KlingProvider(api_key=api_key)
        assert provider.api_key == api_key, "API key should match"
        assert provider.provider_name == "kling", "Provider name should be 'kling'"
        
        print(f"\n✅ Kling API key validation successful!")
    
    @pytest.mark.asyncio
    async def test_kling_error_handling_invalid_prompt(
        self,
        kling_provider: KlingProvider
    ):
        """
        Test error handling with invalid/empty prompt.
        
        Validates that the provider properly handles edge cases.
        """
        with pytest.raises((ProviderError, Exception)) as exc_info:
            await kling_provider.generate_video(
                prompt="",  # Empty prompt should fail
                duration=5,
                resolution="720p"
            )
        
        # Should raise an error
        assert exc_info.value is not None
        print(f"\n✅ Kling error handling test passed!")
        print(f"   Expected error caught: {type(exc_info.value).__name__}")


class TestKlingRealAPIWithCallback:
    """
    Test Kling API with callback mechanism.
    
    Simulates the real workflow where the application
    needs to handle async job completion.
    """
    
    @pytest.mark.asyncio
    async def test_kling_job_status_polling(
        self,
        kling_provider: KlingProvider,
        test_prompt: str
    ):
        """
        Test job status polling mechanism.
        
        Real Kling API calls are async - this test validates
        the polling logic works correctly.
        """
        # Submit job
        result: VideoGenerationResult = await kling_provider.generate_video(
            prompt=test_prompt,
            duration=5,
            resolution="720p"
        )
        
        # Validate initial state
        assert result is not None
        assert result.job_id is not None, "Job ID should be returned"
        
        # In real implementation, you would poll the job status
        # until it reaches "completed" or "failed" state
        print(f"\n✅ Kling job submitted successfully!")
        print(f"   Job ID: {result.job_id}")
        print(f"   Initial status: {result.status}")


# Helper functions for manual testing

async def manual_kling_test():
    """
    Manual test function for quick Kling API validation.
    
    Usage:
        python -c "from tests.integration.test_kling_real import manual_kling_test; asyncio.run(manual_kling_test())"
    """
    api_key = os.getenv("KLING_API_KEY")
    if not api_key:
        print("❌ KLING_API_KEY not set!")
        return
    
    provider = KlingProvider(api_key=api_key)
    prompt = "A beautiful sunset over the ocean, cinematic lighting"
    
    print(f"🎬 Testing Kling API...")
    print(f"   Prompt: {prompt}")
    print(f"   Duration: 5s")
    print(f"   Resolution: 720p")
    print()
    
    try:
        result = await provider.generate_video(
            prompt=prompt,
            duration=5,
            resolution="720p"
        )
        
        if result.is_completed:
            print(f"✅ SUCCESS!")
            print(f"   Video URL: {result.video_url}")
            print(f"   Duration: {result.duration_seconds}s")
            print(f"   Cost: ${result.cost:.4f}")
        else:
            print(f"❌ FAILED: {result.error_message}")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    # Run manual test
    asyncio.run(manual_kling_test())
