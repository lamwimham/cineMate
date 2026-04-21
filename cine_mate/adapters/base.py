"""
CineMate Provider Adapter Base Classes

Defines the abstract interface for all video/image generation providers.
Each provider (Kling, Runway, Luma, etc.) implements this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProviderError(Exception):
    """Raised when a provider operation fails."""
    pass


class ProviderStatus(str, Enum):
    """Status of a video generation job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class VideoGenerationResult:
    """Result of a video generation request."""
    job_id: str
    status: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    cost: float = 0.0
    duration: int = 0
    resolution: str = "720p"
    created_at: datetime = field(default_factory=datetime.now)
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_completed(self) -> bool:
        return self.status == ProviderStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self.status == ProviderStatus.FAILED


class BaseVideoProvider(ABC):
    """
    Abstract base class for all video generation providers.
    
    Each provider (Kling, Runway, Luma, etc.) must implement:
    - generate_video: Submit a generation job
    - estimate_cost: Estimate cost before generation
    - check_status: Poll job status
    - get_result: Retrieve completed video
    """
    
    provider_name: str = "base"
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.extra_config = kwargs
    
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
            duration: Desired duration in seconds
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
            Estimated cost in the provider's currency (usually USD)
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
        import asyncio
        
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
        
        raise ProviderError(
            f"Job {job_id} timed out after {max_wait}s"
        )
