"""
CineMate Configuration System

Data Model First: Defines the configuration schema for all CineMate components.
- Model profiles per use case (LLM, Image, Video, TTS, Vision)
- Provider fallback chains for reliability
- Cost-tier model selection (turbo/plus/max)

Sprint 2 TODO:
- Implement config loader (YAML + env override)
- Integrate with DirectorAgent model selection
- Add provider adapter pattern for upstream APIs
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


# =============================================================================
# Model Provider Enum
# =============================================================================

class LLMProvider(str, Enum):
    DASHSCOPE_QWEN = "dashscope_qwen"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    ZHIPU_GLM = "zhipu_glm"


class ImageProvider(str, Enum):
    FLUX = "flux"
    MIDJOURNEY = "midjourney"
    STABLE_DIFFUSION = "stable_diffusion"
    DASHSCOPE_WANX = "dashscope_wanx"


class VideoProvider(str, Enum):
    KLING = "kling"
    RUNWAY = "runway"
    LUMA = "luma"
    MINIMAX = "minimax"


class TTSProvider(str, Enum):
    COSYVOICE = "cosyvoice"
    ELEVENLABS = "elevenlabs"
    DASHSCOPE_SAMBERT = "dashscope_sambert"


# =============================================================================
# Model Profile Schema
# =============================================================================

class ModelProfile(BaseModel):
    """Defines a model configuration for a specific task."""
    provider: str
    model_name: str
    api_key_env: Optional[str] = None  # env var name (e.g., DASHSCOPE_API_KEY)
    api_key: Optional[str] = None  # Direct API key (override env var)
    base_url: Optional[str] = None
    max_retries: int = 2
    timeout_seconds: int = 120
    extra: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"


class ModelTier(BaseModel):
    """Multi-provider tier for fallback and cost optimization."""
    primary: ModelProfile
    fallback: Optional[ModelProfile] = None
    budget: Optional[ModelProfile] = None  # Lower cost option


# =============================================================================
# CineMate Config Schema
# =============================================================================

class ModelsConfig(BaseModel):
    """All model configurations for CineMate pipeline."""
    llm: ModelTier  # Director Agent, script generation, intent parsing
    text_to_image: ModelTier  # Text -> Image generation
    image_to_video: ModelTier  # Image -> Video generation
    text_to_video: ModelTier  # Direct Text -> Video
    tts: ModelTier  # Text-to-Speech
    vision: Optional[ModelTier] = None  # Quality gate, visual analysis


class InfraConfig(BaseModel):
    """Infrastructure configuration."""
    redis_url: str = "redis://localhost:6379"
    db_path: str = "./cinemate.db"
    cas_root: str = "./cinemate_cas"
    queue_name: str = "default"
    worker_timeout: int = 600


class AppConfig(BaseModel):
    """Application-level settings."""
    log_level: str = "INFO"
    enable_telemetry: bool = False
    max_concurrent_runs: int = 5


class CineMateConfig(BaseModel):
    """Root configuration for CineMate."""
    models: ModelsConfig
    infra: InfraConfig = Field(default_factory=InfraConfig)
    app: AppConfig = Field(default_factory=AppConfig)
