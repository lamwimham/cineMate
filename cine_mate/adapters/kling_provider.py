"""
Kling AI Video Generation Provider

Adapts the Kling API (via WaveSpeed or direct) to CineMate's BaseVideoProvider interface.
Supports:
- text-to-video: Generate video from text prompt
- image-to-video: Animate a still image

API Reference: https://open.kuaishou.com/
"""

import os
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

import aiohttp

from cine_mate.adapters.base import (
    BaseVideoProvider,
    VideoGenerationResult,
    ProviderError,
    ProviderStatus,
)

# Kling API endpoints (WaveSpeed proxy)
KLING_BASE_URL = "https://api.wavespeed.ai/v1"
KLING_MODEL_T2V = "kling-v2"
KLING_MODEL_I2V = "kling-v2-i2v"

# Pricing: ~$0.075/s for Kling 2.x (720p)
KLING_COST_PER_SECOND = {
    "720p": 0.075,
    "1080p": 0.15,
}


class KlingProvider(BaseVideoProvider):
    """
    Kling AI Video Generation Provider.
    
    Usage:
        provider = KlingProvider(api_key=os.getenv("KLING_API_KEY"))
        result = await provider.generate_video(
            prompt="A cyberpunk city at night with neon lights",
            duration=10,
            resolution="720p"
        )
    """
    
    provider_name = "kling"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = KLING_BASE_URL,
        model: str = KLING_MODEL_T2V,
        **kwargs
    ):
        resolved_key = api_key or os.getenv("KLING_API_KEY")
        if not resolved_key:
            raise ProviderError(
                "KLING_API_KEY not set. "
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
        Submit a video generation job to Kling.
        
        Args:
            prompt: Text description of the video
            duration: Duration in seconds (5, 10)
            resolution: Output resolution ("720p", "1080p")
            image_url: Optional source image for image-to-video mode
            **kwargs: Additional parameters (negative_prompt, seed, etc.)
        """
        mode = "image_to_video" if image_url else "text_to_video"
        model = KLING_MODEL_I2V if image_url else KLING_MODEL_T2V
        
        payload = {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
            "mode": mode,
        }
        
        if image_url:
            payload["image_url"] = image_url
        
        # Add optional parameters
        if "negative_prompt" in kwargs:
            payload["negative_prompt"] = kwargs["negative_prompt"]
        if "seed" in kwargs:
            payload["seed"] = kwargs["seed"]
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/video/generation",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as response:
                    if response.status != 200:
                        error_body = await response.text()
                        raise ProviderError(
                            f"Kling API error {response.status}: {error_body}"
                        )
                    
                    data = await response.json()
                    
                    return VideoGenerationResult(
                        job_id=data.get("job_id", ""),
                        status=data.get("status", ProviderStatus.PENDING),
                        video_url=None,
                        thumbnail_url=None,
                        cost=self.estimate_cost(duration, resolution),
                        duration=duration,
                        resolution=resolution,
                        extra={"mode": mode, "model": model},
                    )
            except aiohttp.ClientError as e:
                raise ProviderError(f"Kling API connection error: {e}")
    
    def estimate_cost(self, duration: int, resolution: str = "720p") -> float:
        """Estimate Kling video generation cost."""
        rate = KLING_COST_PER_SECOND.get(resolution, KLING_COST_PER_SECOND["720p"])
        return duration * rate
    
    async def check_status(self, job_id: str) -> str:
        """Check the status of a Kling generation job."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/video/status/{job_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                ) as response:
                    if response.status != 200:
                        raise ProviderError(
                            f"Kling status check error {response.status}"
                        )
                    
                    data = await response.json()
                    return data.get("status", ProviderStatus.PENDING)
            except aiohttp.ClientError as e:
                raise ProviderError(f"Kling status check connection error: {e}")
    
    async def get_result(self, job_id: str) -> Optional[VideoGenerationResult]:
        """Retrieve the completed video result from Kling."""
        status = await self.check_status(job_id)
        
        if status != ProviderStatus.COMPLETED:
            return None
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/video/result/{job_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                ) as response:
                    if response.status != 200:
                        raise ProviderError(
                            f"Kling result fetch error {response.status}"
                        )
                    
                    data = await response.json()
                    
                    return VideoGenerationResult(
                        job_id=job_id,
                        status=ProviderStatus.COMPLETED,
                        video_url=data.get("video_url"),
                        thumbnail_url=data.get("thumbnail_url"),
                        cost=self.estimate_cost(data.get("duration", 10)),
                        duration=data.get("duration", 10),
                        resolution=data.get("resolution", "720p"),
                    )
            except aiohttp.ClientError as e:
                raise ProviderError(f"Kling result fetch connection error: {e}")
