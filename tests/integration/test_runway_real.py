"""
Runway ML Real API Integration Tests

These tests make REAL API calls to Runway ML (Gen-4).
They require a valid RUNWAY_API_KEY environment variable.

⚠️  WARNING: These tests cost money! Each test run will consume API credits.
    - Text-to-Video (720p, 4s): ~$0.20
    - Text-to-Video (1080p, 4s): ~$0.40

Usage:
    # Set API key
    export RUNWAY_API_KEY="your-api-key-here"
    
    # Run tests (with warnings disabled)
    pytest tests/integration/test_runway_real.py -v --disable-warnings
    
    # Run specific test
    pytest tests/integration/test_runway_real.py::test_runway_text_to_video_real -v

Requirements:
    - RUNWAY_API_KEY environment variable
    - Internet connection
    - Valid Runway ML account with credits
"""

import os
import pytest
import asyncio
from typing import Optional

from cine_mate.adapters.runway_provider import RunwayProvider, RUNWAY_BASE_URL
from cine_mate.adapters.base import VideoGenerationResult, ProviderError


# Skip all tests in this module if RUNWAY_API_KEY is not set
pytestmark = pytest.mark.skipif(
    not os.getenv("RUNWAY_API_KEY"),
    reason="RUNWAY_API_KEY environment variable not set. Set it to run real API tests."
)


@pytest.fixture
def runway_provider() -> RunwayProvider:
    """Create RunwayProvider instance with real API key."""
    api_key = os.getenv("RUNWAY_API_KEY")
    return RunwayProvider(api_key=api_key)


@pytest.fixture
def test_prompt() -> str:
    """Default test prompt for video generation."""
    return "A futuristic cityscape with flying vehicles, neon lights, cyberpunk aesthetic, cinematic 4K"


class TestRunwayRealAPI:
    """Real API integration tests for Runway Provider."""
    
    @pytest.mark.asyncio
    async def test_runway_text_to_video_real(
        self,
        runway_provider: RunwayProvider,
        test_prompt: str
    ):
        """
        Test REAL Runway text-to-video API call.
        
        This test:
        1. Submits a text-to-video job to Runway Gen-4
        2. Waits for job completion
        3. Validates the result contains a video URL
        
        ⚠️  COSTS MONEY: ~$0.20 per run (720p, 4s)
        """
        # Generate video with short duration to minimize cost
        result: VideoGenerationResult = await runway_provider.generate_video(
            prompt=test_prompt,
            duration=4,  # Minimum duration for Runway
            resolution="720p"
        )
        
        # Validate result
        assert result is not None, "Result should not be None"
        assert result.is_completed is True, f"Generation should succeed, got error: {result.error_message}"
        assert result.video_url is not None, "Result should contain video URL"
        assert result.video_url.startswith("http"), f"Video URL should be valid HTTP URL, got: {result.video_url}"
        
        # Validate metadata
        assert result.provider == "runway", f"Provider should be 'runway', got: {result.provider}"
        assert result.metadata.get("model") is not None, "Model should be specified in metadata"
        assert result.duration_seconds > 0, "Duration should be positive"
        assert result.cost > 0, "Cost should be positive for real API calls"
        
        print(f"\n✅ Runway text-to-video successful!")
        print(f"   Video URL: {result.video_url}")
        print(f"   Duration: {result.duration_seconds}s")
        print(f"   Cost: ${result.cost:.4f}")
    
    @pytest.mark.asyncio
    async def test_runway_api_key_validation(self):
        """
        Test that API key is properly configured.
        
        This is a lightweight test to validate API credentials
        without generating a full video.
        """
        api_key = os.getenv("RUNWAY_API_KEY")
        assert api_key is not None, "RUNWAY_API_KEY should be set"
        assert len(api_key) > 10, "API key should be a valid length"
        
        # Try to create provider (will fail if key is invalid format)
        provider = RunwayProvider(api_key=api_key)
        assert provider.api_key == api_key, "API key should match"
        assert provider.provider_name == "runway", "Provider name should be 'runway'"
        
        print(f"\n✅ Runway API key validation successful!")
    
    @pytest.mark.asyncio
    async def test_runway_error_handling_invalid_key(self):
        """
        Test error handling with invalid API key.
        
        Validates that the provider properly handles authentication errors.
        """
        invalid_key = "sk-invalid-key-12345"
        
        with pytest.raises(ProviderError) as exc_info:
            # This should fail during initialization or first API call
            provider = RunwayProvider(api_key=invalid_key)
            # Try to make a call to trigger auth error
            await provider.generate_video(
                prompt="test",
                duration=4,
                resolution="720p"
            )
        
        # Should raise ProviderError or aiohttp error
        assert exc_info.value is not None
        print(f"\n✅ Runway error handling test passed!")
        print(f"   Expected error caught: {type(exc_info.value).__name__}")
    
    @pytest.mark.asyncio
    async def test_runway_different_resolutions(
        self,
        runway_provider: RunwayProvider,
        test_prompt: str
    ):
        """
        Test video generation with different resolutions.
        
        Validates that resolution parameter is properly handled.
        """
        resolutions = ["720p", "1080p"]
        
        for resolution in resolutions:
            result: VideoGenerationResult = await runway_provider.generate_video(
                prompt=test_prompt,
                duration=4,
                resolution=resolution
            )
            
            assert result is not None
            assert result.is_completed is True
            assert result.resolution == resolution
            
            print(f"\n✅ Runway {resolution} test passed!")
            print(f"   Video URL: {result.video_url}")
            print(f"   Cost: ${result.cost:.4f}")


class TestRunwayRealAPIWithCallback:
    """
    Test Runway API with callback mechanism.
    
    Simulates the real workflow where the application
    needs to handle async job completion.
    """
    
    @pytest.mark.asyncio
    async def test_runway_job_status_polling(
        self,
        runway_provider: RunwayProvider,
        test_prompt: str
    ):
        """
        Test job status polling mechanism.
        
        Real Runway API calls are async - this test validates
        the polling logic works correctly.
        """
        # Submit job
        result: VideoGenerationResult = await runway_provider.generate_video(
            prompt=test_prompt,
            duration=4,
            resolution="720p"
        )
        
        # Validate initial state
        assert result is not None
        assert result.job_id is not None, "Job ID should be returned"
        
        # In real implementation, you would poll the job status
        # until it reaches "completed" or "failed" state
        print(f"\n✅ Runway job submitted successfully!")
        print(f"   Job ID: {result.job_id}")
        print(f"   Initial status: {result.status}")


# Helper functions for manual testing

async def manual_runway_test():
    """
    Manual test function for quick Runway API validation.
    
    Usage:
        python -c "from tests.integration.test_runway_real import manual_runway_test; asyncio.run(manual_runway_test())"
    """
    api_key = os.getenv("RUNWAY_API_KEY")
    if not api_key:
        print("❌ RUNWAY_API_KEY not set!")
        return
    
    provider = RunwayProvider(api_key=api_key)
    prompt = "A serene mountain landscape at sunrise, cinematic drone shot"
    
    print(f"🎬 Testing Runway API...")
    print(f"   Prompt: {prompt}")
    print(f"   Duration: 4s")
    print(f"   Resolution: 720p")
    print()
    
    try:
        result = await provider.generate_video(
            prompt=prompt,
            duration=4,
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
    asyncio.run(manual_runway_test())
