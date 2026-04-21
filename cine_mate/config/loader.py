"""
CineMate Config Loader

Load CineMate configuration with priority:
1. Environment variables (CINEMATE_*)
2. User config file (cine_mate.yaml)
3. Built-in defaults
"""

import os
import yaml
from pathlib import Path
from typing import Optional

from cine_mate.config.models import CineMateConfig, ModelProfile
from cine_mate.config.validator import validate_api_keys, print_validation_report

ENV_PREFIX = "CINEMATE_"


def load_config(
    config_path: Optional[str] = None,
    validate: bool = True,
    print_report: bool = True
) -> CineMateConfig:
    """
    Load CineMate configuration.
    
    Priority (highest to lowest):
    1. Environment variables (CINEMATE_*)
    2. User config file (cine_mate.yaml)
    3. Built-in defaults
    
    Args:
        config_path: Optional path to custom config YAML.
                     Falls back to project root cine_mate.yaml.
        validate: If True, validate API keys at load time.
        print_report: If True, print validation report to console.
    
    Returns:
        Loaded CineMateConfig instance.
    """
    # Step 1: Load built-in defaults
    defaults_path = Path(__file__).parent / "defaults.yaml"
    with open(defaults_path, "r") as f:
        raw = yaml.safe_load(f)

    # Step 2: Load user config file (overrides defaults)
    user_config_path = config_path or Path.cwd() / "cine_mate.yaml"
    if user_config_path.exists():
        with open(user_config_path, "r") as f:
            user_raw = yaml.safe_load(f)
            raw = _merge_dicts(raw, user_raw)

    # Step 3: Apply environment variable overrides (highest priority)
    raw = _apply_env_overrides(raw)

    # Step 4: Build and validate
    config = CineMateConfig(**raw)
    
    if validate:
        results = validate_api_keys(config)
        if print_report:
            print_validation_report(results)

    return config


def _merge_dicts(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.
    Values from override take precedence over base.
    """
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def _apply_env_overrides(raw: dict) -> dict:
    """
    Apply environment variable overrides to config dict.
    
    Supported environment variables:
    - CINEMATE_LLM_MODEL: Override LLM primary model name
    - CINEMATE_LLM_API_KEY: Override LLM primary API key env var
    - CINEMATE_REDIS_URL: Override Redis URL
    - CINEMATE_LOG_LEVEL: Override log level
    - CINEMATE_DB_PATH: Override database path
    """
    env_mappings = {
        "CINEMATE_LLM_MODEL": ("models", "llm", "primary", "model_name"),
        "CINEMATE_LLM_BASE_URL": ("models", "llm", "primary", "base_url"),
        "CINEMATE_REDIS_URL": ("infra", "redis_url"),
        "CINEMATE_DB_PATH": ("infra", "db_path"),
        "CINEMATE_LOG_LEVEL": ("app", "log_level"),
        "CINEMATE_CAS_ROOT": ("infra", "cas_root"),
        "CINEMATE_MAX_CONCURRENT_RUNS": ("app", "max_concurrent_runs"),
    }

    for env_key, path in env_mappings.items():
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Type conversion for numeric values
            if env_key in ("CINEMATE_MAX_CONCURRENT_RUNS",):
                env_value = int(env_value)
            _set_nested(raw, path, env_value)

    return raw


def _set_nested(d: dict, path: tuple, value):
    """Set a nested dict value, creating intermediate dicts as needed."""
    for key in path[:-1]:
        if key not in d:
            d[key] = {}
        d = d[key]
    d[path[-1]] = value


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
