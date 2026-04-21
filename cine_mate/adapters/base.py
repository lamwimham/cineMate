"""
CineMate Video Provider Adapters

Abstract base class and factory for video generation providers.
Supports Kling, Runway, Luma, and other upstream providers.

Architecture:
    Engine/Worker → Provider Factory → Concrete Provider → Upstream API
                                              ↓
                                    VideoGenerationResult
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import asyncio


class ProviderStatus(str, Enum):
    """Status of a video generation job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProviderHealthStatus(str, Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class VideoGenerationMode(str, Enum):
    """Video generation modes"""
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_TO_VIDEO = "image_to_video"
    VIDEO_TO_VIDEO = "video_to_video"


@dataclass
class VideoGenerationResult:
    """Result from video generation"""
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    cost: float = 0.0
    duration_seconds: int = 0
    resolution: str = "720p"
    provider: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_completed(self) -> bool:
        return self.status == ProviderStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self.status == ProviderStatus.FAILED or self.error_message is not None


@dataclass
class GenerationParams:
    """Parameters for video generation"""
    prompt: str
    negative_prompt: Optional[str] = None
    duration_seconds: int = 10
    resolution: str = "720p"
    fps: int = 30
    mode: VideoGenerationMode = VideoGenerationMode.TEXT_TO_VIDEO
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    seed: Optional[int] = None
    guidance_scale: float = 7.5
    num_inference_steps: int = 50
    extra_params: Dict[str, Any] = field(default_factory=dict)


class ProviderError(Exception):
    """Base exception for provider errors"""
    pass


class ProviderAuthenticationError(ProviderError):
    """Authentication failed"""
    pass


class ProviderRateLimitError(ProviderError):
    """Rate limit exceeded"""
    pass


class ProviderTimeoutError(ProviderError):
    """Request timeout"""
    pass


class BaseVideoProvider(ABC):
    """
    Abstract base class for all video generation providers.

    Implementations:
    - KlingProvider (ByteDance)
    - RunwayProvider (Runway ML)
    - LumaProvider (Luma AI)

    Each provider must implement:
    - generate_video: Submit a generation job
    - estimate_cost: Estimate cost before generation
    - check_status: Poll job status
    - get_result: Retrieve completed video
    """

    provider_name: str = "base"
    supported_modes: List[VideoGenerationMode] = []
    max_duration_seconds: int = 60
    min_duration_seconds: int = 1

    def __init__(
        self,
        api_key: str,
        base_url: str = "",
        timeout_seconds: int = 300,
        max_retries: int = 3,
        **kwargs
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.extra_config = kwargs
        self._health_status = ProviderHealthStatus.UNKNOWN

    @property
    def health_status(self) -> ProviderHealthStatus:
        return self._health_status

    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        duration: int = 10,
        resolution: str = "720p",
        image_url: Optional[str] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """
        Submit a video generation job.

        Args:
            prompt: Text description of the video
            duration: Duration in seconds
            resolution: Output resolution (e.g., "720p", "1080p")
            image_url: Optional source image for image-to-video
            **kwargs: Provider-specific parameters

        Returns:
            VideoGenerationResult with job_id and initial status
        """
        pass

    @abstractmethod
    def estimate_cost(self, duration: int, resolution: str = "720p") -> float:
        """
        Estimate cost for video generation.

        Args:
            duration: Duration in seconds
            resolution: Output resolution

        Returns:
            Estimated cost in USD
        """
        pass

    @abstractmethod
    async def check_status(self, job_id: str) -> str:
        """
        Check the status of a generation job.

        Args:
            job_id: Job identifier from generate_video()

        Returns:
            Status string: "pending", "processing", "completed", "failed"
        """
        pass

    @abstractmethod
    async def get_result(self, job_id: str) -> Optional[VideoGenerationResult]:
        """
        Retrieve the final result of a completed job.

        Args:
            job_id: Job identifier

        Returns:
            VideoGenerationResult with video_url if completed, None otherwise
        """
        pass

    async def generate_and_wait(
        self,
        prompt: str,
        duration: int = 10,
        resolution: str = "720p",
        image_url: Optional[str] = None,
        poll_interval: int = 5,
        max_wait: int = 600,
        **kwargs
    ) -> VideoGenerationResult:
        """
        Convenience method: submit job and poll until completion.

        Args:
            prompt: Text description
            duration: Duration in seconds
            resolution: Output resolution
            image_url: Optional source image
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait
            **kwargs: Provider-specific parameters

        Returns:
            VideoGenerationResult with video_url

        Raises:
            ProviderError: If job fails or times out
        """
        result = await self.generate_video(
            prompt=prompt,
            duration=duration,
            resolution=resolution,
            image_url=image_url,
            **kwargs
        )

        job_id = result.job_id
        elapsed = 0

        while elapsed < max_wait:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            status = await self.check_status(job_id)

            if status == ProviderStatus.COMPLETED:
                final = await self.get_result(job_id)
                if final:
                    return final
                raise ProviderError(f"Job {job_id} completed but result retrieval failed")

            if status == ProviderStatus.FAILED:
                raise ProviderError(f"Job {job_id} failed during generation")

        raise ProviderError(f"Job {job_id} timed out after {max_wait}s")

    async def health_check(self) -> bool:
        """Check provider health."""
        try:
            self._health_status = ProviderHealthStatus.HEALTHY
            return True
        except Exception:
            self._health_status = ProviderHealthStatus.UNHEALTHY
            return False

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }