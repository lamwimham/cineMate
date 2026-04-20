"""
RQ Worker - Executes Async Jobs

Worker process that pulls jobs from the queue and executes them.
For video generation, this calls upstream APIs (Kling, Runway, etc.).

Usage:
    # Start worker process
    $ python -m cine_mate.infra.worker
    
    # Or with rq CLI
    $ rq worker cine_mate.infra.worker.execute_job
"""

import json
import traceback
from typing import Dict, Any

import redis
from rq import get_current_job

from cine_mate.infra.schemas import JobStatus
from cine_mate.infra.event_bus import EventBus, publish_node_completed, publish_node_failed


# Global event bus instance
_event_bus = None


def get_event_bus(redis_url: str = "redis://localhost:6379") -> EventBus:
    """Get or create global EventBus instance"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus(redis_url)
    return _event_bus


def execute_job(job_id: str):
    """
    Execute a single job.
    
    This is the entry point for RQ Worker.
    It fetches the job from Redis, executes the appropriate handler,
    and publishes completion/failure events.
    """
    print(f"[Worker] Starting job {job_id}")
    
    try:
        # Get Redis connection from RQ
        redis_conn = get_current_job().connection
        
        # Fetch job metadata
        job_key = f"job:{job_id}"
        job_data = redis_conn.hgetall(job_key)
        
        if not job_data:
            raise ValueError(f"Job {job_id} not found")
        
        # Parse job data
        job_type = job_data.get("job_type")
        params = json.loads(job_data.get("params", "{}"))
        run_id = job_data.get("run_id")
        node_id = job_data.get("node_id")
        
        print(f"[Worker] Executing {job_type} for run={run_id}, node={node_id}")
        
        # Execute based on job type
        result = _execute_by_type(job_type, params)
        
        # Update job status in Redis
        redis_conn.hset(
            job_key,
            mapping={
                "status": JobStatus.COMPLETED.value,
                "progress": "100",
                "result": json.dumps(result),
            }
        )
        
        # Publish node_completed event (会议决议：Event-Driven)
        event_bus = get_event_bus()
        import asyncio
        asyncio.run(publish_node_completed(
            event_bus=event_bus,
            run_id=run_id,
            node_id=node_id,
            artifact_hash=result.get("artifact_hash", ""),
            output_url=result.get("output_url", ""),
            cost=result.get("cost", 0.0)
        ))
        
        print(f"[Worker] Job {job_id} completed successfully")
        
    except Exception as e:
        print(f"[Worker] Job {job_id} failed: {e}")
        
        # Update job status in Redis
        tb = traceback.format_exc()
        redis_conn.hset(
            job_key,
            mapping={
                "status": JobStatus.FAILED.value,
                "error": str(e),
                "error_traceback": tb,
            }
        )
        
        # Publish node_failed event
        try:
            job_data = redis_conn.hgetall(job_key)
            event_bus = get_event_bus()
            asyncio.run(publish_node_failed(
                event_bus=event_bus,
                run_id=job_data.get("run_id"),
                node_id=job_data.get("node_id"),
                error_code="EXECUTION_ERROR",
                error_msg=str(e),
                retry_count=0
            ))
        except Exception as event_error:
            print(f"[Worker] Failed to publish error event: {event_error}")
        
        # Re-raise to let RQ handle retry logic
        raise


def _execute_by_type(job_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute job based on type.
    
    This is where you'd call the actual upstream APIs.
    For now, it's a placeholder that simulates execution.
    """
    import time
    time.sleep(2)  # Simulate API call delay
    
    if job_type == "text_to_image":
        return _text_to_image(params)
    elif job_type == "image_to_video":
        return _image_to_video(params)
    elif job_type == "text_to_video":
        return _text_to_video(params)
    elif job_type == "tts":
        return _tts(params)
    elif job_type == "video_edit":
        return _video_edit(params)
    else:
        raise ValueError(f"Unknown job type: {job_type}")


def _text_to_image(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate image from text prompt"""
    prompt = params.get("prompt", "")
    print(f"[Worker] Generating image for prompt: {prompt}")
    
    return {
        "artifact_hash": f"img_{hash(prompt)}",
        "output_url": "https://example.com/generated_image.png",
        "width": 1024,
        "height": 1024,
        "cost": 0.1,
    }


def _image_to_video(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate video from image"""
    image_url = params.get("image_url", "")
    print(f"[Worker] Generating video from image: {image_url}")
    
    return {
        "artifact_hash": f"vid_{hash(image_url)}",
        "output_url": "https://example.com/generated_video.mp4",
        "duration": params.get("duration", 5),
        "cost": 1.5,
    }


def _text_to_video(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate video from text prompt"""
    prompt = params.get("prompt", "")
    print(f"[Worker] Generating video for prompt: {prompt}")
    
    return {
        "artifact_hash": f"vid_{hash(prompt)}",
        "output_url": "https://example.com/generated_video.mp4",
        "duration": params.get("duration", 5),
        "cost": 2.0,
    }


def _tts(params: Dict[str, Any]) -> Dict[str, Any]:
    """Text-to-speech generation"""
    text = params.get("text", "")
    print(f"[Worker] Generating TTS for text: {text[:50]}...")
    
    return {
        "artifact_hash": f"audio_{hash(text)}",
        "output_url": "https://example.com/generated_audio.mp3",
        "duration": 10,
        "cost": 0.05,
    }


def _video_edit(params: Dict[str, Any]) -> Dict[str, Any]:
    """Video editing operation"""
    operation = params.get("operation", "concat")
    print(f"[Worker] Performing video edit: {operation}")
    
    return {
        "artifact_hash": f"edit_{hash(str(params))}",
        "output_url": "https://example.com/edited_video.mp4",
        "operation": operation,
        "cost": 0.5,
    }


if __name__ == "__main__":
    # Run worker directly (for development)
    import os
    from rq import Queue, Worker
    import redis
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    print(f"Starting worker with Redis: {redis_url}")
    
    # RQ 2.x: No need for Connection context manager
    redis_client = redis.from_url(redis_url)
    worker = Worker(["default"], connection=redis_client)
    worker.work()
