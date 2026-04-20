"""
Mock Upstream API Clients for Integration Testing

Provides mock implementations of:
- Kling API (text-to-image, image-to-video)
- Runway API (text-to-video, image-to-video)
- OpenAI API (text generation)

Usage:
    from tests.mocks.upstream import MockKlingClient

    mock_kling = MockKlingClient()
    job_id = await mock_kling.create_image_job({"prompt": "test"})
    result = await mock_kling.get_job_status(job_id)
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# Mock Job Status
# =============================================================================

class MockJobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MockJob:
    """Mock job record"""
    job_id: str
    job_type: str
    params: Dict[str, Any]
    status: MockJobStatus = MockJobStatus.PENDING
    progress: int = 0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    cost: float = 0.0


# =============================================================================
# Mock Kling API
# =============================================================================

class MockKlingClient:
    """
    Mock Kling AI API Client.

    Simulates:
    - POST /v1/images/text2image (text-to-image)
    - POST /v1/videos/image2video (image-to-video)
    - GET /v1/jobs/{job_id}/status (job status)

    Usage:
        client = MockKlingClient()

        # Text to Image
        job_id = await client.create_text_to_image({
            "prompt": "A cyberpunk city",
            "negative_prompt": "blurry",
            "seed": 42
        })

        # Wait and get result
        await asyncio.sleep(0.5)  # Simulate processing
        result = await client.get_job_status(job_id)
        assert result["status"] == "completed"
    """

    def __init__(self, processing_delay: float = 0.1):
        """
        Args:
            processing_delay: Simulated API processing time (seconds)
        """
        self.jobs: Dict[str, MockJob] = {}
        self.processing_delay = processing_delay

    async def create_text_to_image(
        self,
        params: Dict[str, Any]
    ) -> str:
        """
        Create a text-to-image job.

        Args:
            params: {
                "prompt": str,
                "negative_prompt": Optional[str],
                "seed": Optional[int],
                "aspect_ratio": Optional[str],
                "model": Optional[str]  # "kling-v1" or "kling-v2"
            }

        Returns:
            job_id: Unique job identifier
        """
        job_id = f"kling_img_{uuid.uuid4().hex[:12]}"

        job = MockJob(
            job_id=job_id,
            job_type="text_to_image",
            params=params,
            status=MockJobStatus.QUEUED,
            cost=1.0  # 1 credit for image
        )
        self.jobs[job_id] = job

        # Simulate async processing
        asyncio.create_task(self._process_job(job_id))

        return job_id

    async def create_image_to_video(
        self,
        params: Dict[str, Any]
    ) -> str:
        """
        Create an image-to-video job.

        Args:
            params: {
                "image_url": str,  # Input image
                "prompt": Optional[str],
                "duration": int,  # 5 or 10 seconds
                "motion_strength": float,  # 0.0-1.0
                "camera_movement": Optional[str],
                "seed": Optional[int]
            }

        Returns:
            job_id: Unique job identifier
        """
        job_id = f"kling_vid_{uuid.uuid4().hex[:12]}"

        duration = params.get("duration", 5)
        cost = duration * 1.0  # 1 credit per second

        job = MockJob(
            job_id=job_id,
            job_type="image_to_video",
            params=params,
            status=MockJobStatus.QUEUED,
            cost=cost
        )
        self.jobs[job_id] = job

        asyncio.create_task(self._process_job(job_id))

        return job_id

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get job status and result.

        Returns:
            {
                "job_id": str,
                "status": str,
                "progress": int,
                "result": Optional[Dict],
                "error": Optional[str],
                "cost": float
            }
        """
        job = self.jobs.get(job_id)
        if not job:
            return {"error": "Job not found", "job_id": job_id}

        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "progress": job.progress,
            "result": job.result,
            "error": job.error,
            "cost": job.cost,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending/queued job."""
        job = self.jobs.get(job_id)
        if not job:
            return False

        if job.status in (MockJobStatus.PENDING, MockJobStatus.QUEUED):
            job.status = MockJobStatus.FAILED
            job.error = "Cancelled by user"
            return True

        return False

    async def _process_job(self, job_id: str):
        """Simulate job processing."""
        job = self.jobs[job_id]

        # Wait for processing delay
        await asyncio.sleep(self.processing_delay)

        # Update status
        job.status = MockJobStatus.RUNNING
        job.progress = 50

        await asyncio.sleep(self.processing_delay)

        # Complete job
        job.status = MockJobStatus.COMPLETED
        job.progress = 100
        job.completed_at = datetime.now()

        # Generate mock result
        if job.job_type == "text_to_image":
            job.result = {
                "image_url": f"mock://kling/images/{job_id}.png",
                "image_hash": f"sha256_{job_id}",
                "width": 1024,
                "height": 1024
            }
        elif job.job_type == "image_to_video":
            job.result = {
                "video_url": f"mock://kling/videos/{job_id}.mp4",
                "video_hash": f"sha256_{job_id}",
                "duration": job.params.get("duration", 5),
                "fps": 24
            }

    def reset(self):
        """Clear all jobs for fresh test."""
        self.jobs.clear()


# =============================================================================
# Mock Runway API
# =============================================================================

class MockRunwayClient:
    """
    Mock Runway Gen-4 API Client.

    Simulates:
    - POST /v1/generate (text-to-video)
    - POST /v1/image-to-video (image-to-video)
    - GET /v1/tasks/{task_id} (task status)
    """

    def __init__(self, processing_delay: float = 0.15):
        self.tasks: Dict[str, MockJob] = {}
        self.processing_delay = processing_delay

    async def create_text_to_video(
        self,
        params: Dict[str, Any]
    ) -> str:
        """
        Create text-to-video with Gen-4.

        Args:
            params: {
                "prompt": str,
                "duration": int,  # 5, 10, or 15 seconds
                "aspect_ratio": str,  # "16:9", "9:16", "1:1"
                "model": str,  # "gen4" or "gen4-turbo"
                "seed": Optional[int]
            }
        """
        task_id = f"runway_vid_{uuid.uuid4().hex[:12]}"

        duration = params.get("duration", 10)
        cost = duration * 2.0  # Runway is more expensive

        task = MockJob(
            job_id=task_id,
            job_type="text_to_video",
            params=params,
            status=MockJobStatus.QUEUED,
            cost=cost
        )
        self.tasks[task_id] = task

        asyncio.create_task(self._process_task(task_id))

        return task_id

    async def create_image_to_video(
        self,
        params: Dict[str, Any]
    ) -> str:
        """Image-to-video with motion control."""
        task_id = f"runway_i2v_{uuid.uuid4().hex[:12]}"

        duration = params.get("duration", 5)
        cost = duration * 1.5

        task = MockJob(
            job_id=task_id,
            job_type="image_to_video",
            params=params,
            status=MockJobStatus.QUEUED,
            cost=cost
        )
        self.tasks[task_id] = task

        asyncio.create_task(self._process_task(task_id))

        return task_id

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status."""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}

        return {
            "task_id": task.job_id,
            "status": task.status.value,
            "progress": task.progress,
            "result": task.result,
            "error": task.error,
            "cost": task.cost
        }

    async def _process_task(self, task_id: str):
        """Simulate processing."""
        task = self.tasks[task_id]

        await asyncio.sleep(self.processing_delay)
        task.status = MockJobStatus.RUNNING
        task.progress = 30

        await asyncio.sleep(self.processing_delay)
        task.progress = 60

        await asyncio.sleep(self.processing_delay)
        task.status = MockJobStatus.COMPLETED
        task.progress = 100
        task.completed_at = datetime.now()

        task.result = {
            "video_url": f"mock://runway/videos/{task_id}.mp4",
            "video_hash": f"sha256_{task_id}",
            "duration": task.params.get("duration", 10),
            "model": task.params.get("model", "gen4")
        }

    def reset(self):
        self.tasks.clear()


# =============================================================================
# Mock OpenAI API
# =============================================================================

class MockOpenAIClient:
    """
    Mock OpenAI API Client for script generation.

    Simulates:
    - POST /v1/chat/completions (GPT-4)
    """

    def __init__(self):
        self.calls: List[Dict[str, Any]] = []

    async def create_chat_completion(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mock chat completion.

        Args:
            params: {
                "model": str,
                "messages": List[Dict],
                "temperature": float,
                "max_tokens": int
            }

        Returns:
            {
                "id": str,
                "choices": List[Dict],
                "usage": Dict
            }
        """
        call_id = f"openai_chat_{uuid.uuid4().hex[:12]}"

        # Extract prompt from messages
        messages = params.get("messages", [])
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "")

        # Generate mock response
        mock_response = self._generate_mock_script(user_message)

        # Record call
        self.calls.append({
            "call_id": call_id,
            "params": params,
            "response": mock_response,
            "timestamp": datetime.now()
        })

        return {
            "id": call_id,
            "object": "chat.completion",
            "model": params.get("model", "gpt-4"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": mock_response
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(mock_response.split()),
                "total_tokens": len(user_message.split()) + len(mock_response.split())
            }
        }

    def _generate_mock_script(self, prompt: str) -> str:
        """Generate mock script based on prompt."""
        if "cyberpunk" in prompt.lower():
            return """
SCENE 1: NEON CITY

[Wide shot of a sprawling cyberpunk metropolis at night]
Neon lights flicker across rain-soaked streets.
A lone figure walks through the crowd, their face illuminated by passing holograms.

[Close-up: The protagonist's eyes]
They carry a secret that could change everything.

END SCENE 1
"""
        elif "product" in prompt.lower():
            return """
PRODUCT SHOWCASE

[Wide shot: Product on clean white background]
The camera slowly orbits around the premium watch.

[Close-up: Dial details]
Light refracts through the crystal face, highlighting craftsmanship.

[Zoom out: Product in lifestyle setting]
Elegant, sophisticated, timeless.

END
"""
        else:
            return f"""
VIDEO SCRIPT

Based on your request: "{prompt[:50]}..."

[Opening scene]
Establishing shot with cinematic lighting.

[Action]
Main content flows naturally.

[Conclusion]
Satisfying ending with clear message.

END
"""

    def reset(self):
        self.calls.clear()


# =============================================================================
# Mock Upstream Provider Factory
# =============================================================================

class MockUpstreamFactory:
    """
    Factory for creating mock upstream clients.

    Usage:
        factory = MockUpstreamFactory()

        kling = factory.get_client("kling")
        runway = factory.get_client("runway")
        openai = factory.get_client("openai")
    """

    _clients: Dict[str, Any] = {}

    @classmethod
    def get_client(cls, provider: str) -> Any:
        """
        Get or create mock client for provider.

        Args:
            provider: "kling", "runway", "openai"
        """
        if provider not in cls._clients:
            if provider == "kling":
                cls._clients[provider] = MockKlingClient()
            elif provider == "runway":
                cls._clients[provider] = MockRunwayClient()
            elif provider == "openai":
                cls._clients[provider] = MockOpenAIClient()
            else:
                raise ValueError(f"Unknown provider: {provider}")

        return cls._clients[provider]

    @classmethod
    def reset_all(cls):
        """Reset all mock clients."""
        for client in cls._clients.values():
            client.reset()


# =============================================================================
# pytest fixtures
# =============================================================================

def mock_kling():
    """pytest fixture for MockKlingClient."""
    return MockKlingClient()


def mock_runway():
    """pytest fixture for MockRunwayClient."""
    return MockRunwayClient()


def mock_openai():
    """pytest fixture for MockOpenAIClient."""
    return MockOpenAIClient()