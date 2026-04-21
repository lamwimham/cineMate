"""
Mock Video Provider for Testing

Returns preset results without calling any real API.
Useful for testing without API keys or spending credits.
"""

import asyncio
from typing import Optional
from datetime import datetime

from cine_mate.adapters.base import (
    BaseVideoProvider,
    VideoGenerationResult,
    ProviderStatus,
)


class MockVideoProvider(BaseVideoProvider):
    """
    Mock video provider for testing.
    
    Simulates video generation with instant or delayed preset results.
    """
    
    provider_name = "mock"
    
    MOCK_VIDEO_URL = "https://example.com/mock_video.mp4"
    MOCK_THUMBNAIL_URL = "https://example.com/mock_thumbnail.jpg"
    
    def __init__(self, simulate_delay: bool = False, delay_seconds: int = 2):
        """
        Args:
            simulate_delay: If True, simulate API processing time
            delay_seconds: Seconds to wait when simulating delay
        """
        super().__init__(api_key="mock_key")
        self.simulate_delay = simulate_delay
        self.delay_seconds = delay_seconds
        self._jobs = {}  # Simulated job storage
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 10,
        resolution: str = "720p",
        image_url: Optional[str] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """Simulate submitting a video generation job."""
        import uuid
        job_id = f"mock_{uuid.uuid4().hex[:8]}"
        
        mode = "image_to_video" if image_url else "text_to_video"
        
        result = VideoGenerationResult(
            job_id=job_id,
            status=ProviderStatus.PENDING,
            video_url=None,
            thumbnail_url=None,
            cost=0.0,  # Free
            duration=duration,
            resolution=resolution,
            extra={"mode": mode, "prompt": prompt, "provider": "mock"},
        )
        
        self._jobs[job_id] = {
            "result": result,
            "status": ProviderStatus.PROCESSING,
            "prompt": prompt,
        }
        
        if self.simulate_delay:
            await asyncio.sleep(self.delay_seconds)
        
        # Mark as completed instantly for mock
        self._jobs[job_id]["status"] = ProviderStatus.COMPLETED
        self._jobs[job_id]["result"] = VideoGenerationResult(
            job_id=job_id,
            status=ProviderStatus.COMPLETED,
            video_url=self.MOCK_VIDEO_URL,
            thumbnail_url=self.MOCK_THUMBNAIL_URL,
            cost=0.0,
            duration=duration,
            resolution=resolution,
            extra={"mode": mode, "prompt": prompt, "provider": "mock"},
        )
        
        return result
    
    def estimate_cost(self, duration: int, resolution: str = "720p") -> float:
        """Mock videos are always free."""
        return 0.0
    
    async def check_status(self, job_id: str) -> str:
        """Check mock job status."""
        job = self._jobs.get(job_id)
        if not job:
            return ProviderStatus.FAILED
        return job["status"]
    
    async def get_result(self, job_id: str) -> Optional[VideoGenerationResult]:
        """Retrieve mock video result."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        return job["result"]
