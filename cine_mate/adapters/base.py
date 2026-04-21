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
    status: str  # "processing", "completed", "failed"
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
    
    def is_completed(self) -> bool:
        return self.status == "completed" and self.video_url is not None
    
    def is_failed(self) -> bool:
        return self.status == "failed" or self.error_message is not None


@dataclass
class GenerationParams:
    """Parameters for video generation"""
    # Core
    prompt: str
    negative_prompt: Optional[str] = None
    
    # Video settings
    duration_seconds: int = 10
    resolution: str = "720p"
    fps: int = 30
    
    # Generation mode
    mode: VideoGenerationMode = VideoGenerationMode.TEXT_TO_VIDEO
    
    # Input for image/video to video
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    
    # Advanced
    seed: Optional[int] = None
    guidance_scale: float = 7.5
    num_inference_steps: int = 50
    
    # Provider-specific overrides
    extra_params: Dict[str, Any] = field(default_factory=dict)


class BaseVideoProvider(ABC):
    """
    Abstract base class for all video generation providers.
    
    Implementations:
    - KlingProvider (ByteDance)
    - RunwayProvider (Runway ML)
    - LumaProvider (Luma AI)
    
    Usage:
        provider = KlingProvider(api_key="xxx")
        result = await provider.generate_video(
            prompt="A cinematic shot of...",
            duration_seconds=10
        )
    """
    
    # Class-level configuration
    provider_name: str = "base"
    supported_modes: List[VideoGenerationMode] = []
    max_duration_seconds: int = 60
    min_duration_seconds: int = 1
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout_seconds: int = 300,
        max_retries: int = 3
    ):
        """
        Initialize provider.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for API endpoints
            timeout_seconds: Request timeout
            max_retries: Maximum retry attempts
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._status = ProviderStatus.UNKNOWN
    
    @property
    def status(self) -> ProviderStatus:
        """Get current provider health status"""
        return self._status
    
    @abstractmethod
    async def generate_video(
        self,
        params: GenerationParams
    ) -> VideoGenerationResult:
        """
        Generate video from prompt or image.
        
        Args:
            params: Generation parameters
        
        Returns:
            VideoGenerationResult with job_id and status
        
        Raises:
            ProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    async def get_job_status(self, job_id: str) -> str:
        """
        Get status of a generation job.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Status string: "processing", "completed", "failed"
        """
        pass
    
    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job.
        
        Args:
            job_id: Job identifier
        
        Returns:
            True if cancelled, False otherwise
        """
        pass
    
    @abstractmethod
    def estimate_cost(
        self,
        duration_seconds: int,
        resolution: str = "720p",
        mode: VideoGenerationMode = VideoGenerationMode.TEXT_TO_VIDEO
    ) -> float:
        """
        Estimate cost for video generation.
        
        Args:
            duration_seconds: Video duration
            resolution: Output resolution
            mode: Generation mode
        
        Returns:
            Estimated cost in USD
        """
        pass
    
    async def health_check(self) -> bool:
        """
        Check provider health.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Implement provider-specific health check
            self._status = ProviderStatus.HEALTHY
            return True
        except Exception:
            self._status = ProviderStatus.UNHEALTHY
            return False
    
    def validate_params(self, params: GenerationParams) -> None:
        """
        Validate generation parameters.
        
        Args:
            params: Parameters to validate
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Duration validation
        if params.duration_seconds < self.min_duration_seconds:
            raise ValueError(
                f"Duration must be at least {self.min_duration_seconds}s"
            )
        if params.duration_seconds > self.max_duration_seconds:
            raise ValueError(
                f"Duration must be at most {self.max_duration_seconds}s"
            )
        
        # Mode validation
        if params.mode not in self.supported_modes:
            raise ValueError(
                f"Mode {params.mode} not supported. "
                f"Supported: {self.supported_modes}"
            )
        
        # Input validation based on mode
        if params.mode == VideoGenerationMode.IMAGE_TO_VIDEO:
            if not params.image_url:
                raise ValueError("image_url required for image-to-video mode")
        
        if params.mode == VideoGenerationMode.VIDEO_TO_VIDEO:
            if not params.video_url:
                raise ValueError("video_url required for video-to-video mode")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def _retry_request(self, func, *args, **kwargs):
        """Retry a request with exponential backoff"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) * 1.0  # Exponential backoff
                    await asyncio.sleep(wait_time)
        
        raise last_error


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
