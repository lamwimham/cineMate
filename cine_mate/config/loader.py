"""
CineMate Config Loader (Skeleton)

Sprint 2 TODO:
- Load from YAML file
- Override with environment variables
- Validate API keys at startup
- Support per-run model overrides

Current: Loads defaults programmatically for validation.
"""

import os
import yaml
from pathlib import Path
from typing import Optional

from cine_mate.config.models import CineMateConfig, ModelProfile


def load_config(config_path: Optional[str] = None) -> CineMateConfig:
    """
    Load CineMate configuration.
    
    Priority:
    1. User config file (cine_mate.yaml)
    2. Environment variable overrides (CINEMATE_*)
    3. Built-in defaults
    
    Args:
        config_path: Optional path to custom config YAML.
                     Falls back to project root cine_mate.yaml or defaults.
    """
    # Sprint 2: Implement full loader
    # For now, return validated defaults
    defaults_path = Path(__file__).parent / "defaults.yaml"
    
    with open(defaults_path, "r") as f:
        raw = yaml.safe_load(f)
    
    return CineMateConfig(**raw)


def get_model_for_task(config: CineMateConfig, task: str) -> ModelProfile:
    """
    Get the primary model for a given task.
    
    Args:
        config: Loaded CineMateConfig
        task: One of "llm", "text_to_image", "image_to_video", 
              "text_to_video", "tts", "vision"
    
    Returns:
        ModelProfile for the primary provider
    """
    tier = getattr(config.models, task)
    return tier.primary


def get_model_by_cost(config: CineMateConfig, task: str, cost_tier: str = "primary") -> ModelProfile:
    """
    Get model by cost tier.
    
    Args:
        cost_tier: "primary" (default), "fallback", or "budget"
    """
    tier = getattr(config.models, task)
    if cost_tier == "primary":
        return tier.primary
    elif cost_tier == "fallback" and tier.fallback:
        return tier.fallback
    elif cost_tier == "budget" and tier.budget:
        return tier.budget
    return tier.primary
