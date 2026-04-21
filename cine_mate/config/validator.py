"""
CineMate Configuration Validator

Validates API keys and configuration at startup.
"""

import os
from typing import List, Tuple

from cine_mate.config.models import CineMateConfig


# Map provider names to their expected environment variables
PROVIDER_ENV_MAP = {
    "dashscope_qwen": "DASHSCOPE_API_KEY",
    "dashscope_wanx": "DASHSCOPE_API_KEY",
    "dashscope_sambert": "DASHSCOPE_API_KEY",
    "flux": "FLUX_API_KEY",
    "midjourney": "MIDJOURNEY_API_KEY",
    "stable_diffusion": "STABILITY_API_KEY",
    "kling": "KLING_API_KEY",
    "runway": "RUNWAY_API_KEY",
    "luma": "LUMA_API_KEY",
    "minimax": "MINIMAX_API_KEY",
    "cosyvoice": "DASHSCOPE_API_KEY",
    "elevenlabs": "ELEVENLABS_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "zhipu_glm": "ZHIPU_API_KEY",
}


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


def validate_api_keys(config: CineMateConfig) -> List[Tuple[str, bool, str]]:
    """
    Validate API keys at startup.
    
    Returns list of (provider, is_valid, env_var_name) tuples.
    
    Only validates providers that are actually configured in the loaded config
    (checks primary, fallback, and budget tiers).
    """
    results = []
    checked_env_vars = set()

    def check_tier(provider_name: str, env_var: str):
        if not provider_name or not env_var:
            return
        if env_var in checked_env_vars:
            return
        checked_env_vars.add(env_var)
        
        key_value = os.getenv(env_var)
        is_valid = bool(key_value)
        results.append((provider_name, is_valid, env_var))

    # Walk through all model tiers
    for tier_name in ["llm", "text_to_image", "image_to_video", "text_to_video", "tts", "vision"]:
        tier = getattr(config.models, tier_name, None)
        if tier is None:
            continue
        
        for role in ["primary", "fallback", "budget"]:
            profile = getattr(tier, role, None)
            if profile is None:
                continue
            
            env_var = PROVIDER_ENV_MAP.get(profile.provider)
            if env_var:
                check_tier(profile.provider, env_var)

    return results


def get_validation_summary(results: List[Tuple[str, bool, str]]) -> dict:
    """
    Generate a human-readable validation summary.
    
    Returns:
        dict with keys: valid_count, invalid_count, missing_keys
    """
    valid_count = sum(1 for _, v, _ in results if v)
    invalid_count = sum(1 for _, v, _ in results if not v)
    missing_keys = [env for _, v, env in results if not v]
    
    return {
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "missing_keys": list(set(missing_keys)),
    }


def print_validation_report(results: List[Tuple[str, bool, str]]) -> str:
    """Print a validation report and return the summary string."""
    summary = get_validation_summary(results)
    
    lines = ["\n" + "=" * 40]
    lines.append("[CONFIG] API Key Validation Report")
    lines.append("=" * 40)
    
    for provider, is_valid, env_var in results:
        status = "✅" if is_valid else "❌"
        lines.append(f"  {status} {provider}: {env_var} {'found' if is_valid else 'missing'}")
    
    lines.append(f"\n  Valid: {summary['valid_count']}, Missing: {summary['invalid_count']}")
    lines.append("=" * 40)
    
    report = "\n".join(lines)
    print(report)
    return report
