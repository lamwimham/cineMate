"""
Runway ML Video Generation Provider

Adapts the Runway Gen-4 API to CineMate's BaseVideoProvider interface.
Supports:
- text-to-video: Generate video from text prompt

API Reference: https://runwayml.com/
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime

import aiohttp

from cine_mate.adapters.base import (
    BaseVideoProvider,
    VideoGenerationResult,
    ProviderError,
    ProviderStatus,
)

# Runway API endpoints
RUNWAY_BASE_URL = "https://api.runwayml.com/v1"
RUNWAY_MODEL = "gen4"

# Pricing: ~$0.05/s for Runway Gen-4
RUNWAY_COST_PER_SECOND = {
    "720p": 0.05,
    "1080p": 0.10,
}


class RunwayProvider(BaseVideoProvider):
    """
    Runway ML Video Generation Provider.
    
    Usage:
        provider = RunwayProvider(api_key=os.getenv("RUNWAY_API_KEY"))
        result = await provider.generate_video(
            prompt="A cyberpunk city at night with neon lights",
            duration=10,
            resolution="720p"
        )
    """
    
    provider_name = "runway"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = RUNWAY_BASE_URL,
        model: str = RUNWAY_MODEL,
        **kwargs
    ):
        resolved_key = api_key or os.getenv("RUNWAY_API_KEY")
        if not resolved_key:
            raise ProviderError(
                "RUNWAY_API_KEY not set. "
                "Please set the environment variable or pass api_key parameter."
            )
        super().__init__(api_key=resolved_key, **kwargs)
        self.base_url = base_url
        self.model = model
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 10,
        resolution: str = "720p",
        image_url: Optional[str] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """
        Submit a text-to-video generation job to Runway.
        
        Note: Runway Gen-4 supports text-to-video primarily.
        Image-to-video may be supported in future API versions.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
        }
        
        if image_url:
            # Runway may support image-to-video in the future
            payload["image_url"] = image_url
        
        if "seed" in kwargs:
            payload["seed"] = kwargs["seed"]
        if "style" in kwargs:
            payload["style"] = kwargs["style"]
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/video/generation",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "X-Runway-Version": "2024-11-06",
                    },
                    json=payload,
                ) as response:
                    if response.status not in (200, 201, 202):
                        error_body = await response.text()
                        raise ProviderError(
                            f"Runway API error {response.status}: {error_body}"
                        )
                    
                    data = await response.json()
                    
                    return VideoGenerationResult(
                        job_id=data.get("id", data.get("job_id", "")),
                        status=data.get("status", ProviderStatus.PENDING),
                        video_url=None,
                        thumbnail_url=None,
                        cost=self.estimate_cost(duration, resolution),
                        duration=duration,
                        resolution=resolution,
                        extra={"model": self.model},
                    )
            except aiohttp.ClientError as e:
                raise ProviderError(f"Runway API connection error: {e}")
    
    def estimate_cost(self, duration: int, resolution: str = "720p") -> float:
        """Estimate Runway video generation cost."""
        rate = RUNWAY_COST_PER_SECOND.get(resolution, RUNWAY_COST_PER_SECOND["720p"])
        return duration * rate
    
    async def check_status(self, job_id: str) -> str:
        """Check the status of a Runway generation job."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/video/{job_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-Runway-Version": "2024-11-06",
                    },
                ) as response:
                    if response.status != 200:
                        raise ProviderError(
                            f"Runway status check error {response.status}"
                        )
                    
                    data = await response.json()
                    # Map Runway status to our enum
                    runway_status = data.get("status", "pending")
                    status_map = {
                        "PENDING": ProviderStatus.PENDING,
                        "RUNNING": ProviderStatus.PROCESSING,
                        "SUCCEEDED": ProviderStatus.COMPLETED,
                        "FAILED": ProviderStatus.FAILED,
                    }
                    return status_map.get(runway_status, runway_status.lower())
            except aiohttp.ClientError as e:
                raise ProviderError(f"Runway status check connection error: {e}")
    
    async def get_result(self, job_id: str) -> Optional[VideoGenerationResult]:
        """Retrieve the completed video result from Runway."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/video/{job_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-Runway-Version": "2024-11-06",
                    },
                ) as response:
                    if response.status != 200:
                        raise ProviderError(
                            f"Runway result fetch error {response.status}"
                        )
                    
                    data = await response.json()
                    status = data.get("status", "")
                    
                    if status not in ("SUCCEEDED", "completed"):
                        return None
                    
                    output = data.get("output", {})
                    if isinstance(output, dict):
                        video_url = output.get("video", output.get("url"))
                    elif isinstance(output, list):
                        video_url = output[0] if output else None
                    else:
                        video_url = output
                    
                    return VideoGenerationResult(
                        job_id=job_id,
                        status=ProviderStatus.COMPLETED,
                        video_url=video_url,
                        thumbnail_url=data.get("preview"),
                        cost=self.estimate_cost(data.get("duration", 10)),
                        duration=data.get("duration", 10),
                        resolution=data.get("resolution", "720p"),
                    )
            except aiohttp.ClientError as e:
                raise ProviderError(f"Runway result fetch connection error: {e}")
