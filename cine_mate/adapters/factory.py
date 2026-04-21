"""
Provider Factory and Registry

Creates and manages video provider instances.
Supports configuration-based provider selection.
"""

from typing import Dict, Type, Optional, List
from cine_mate.adapters.base import (
    BaseVideoProvider,
    ProviderError,
    ProviderStatus,
)


# Provider registry - populated as providers are implemented
PROVIDER_REGISTRY: Dict[str, Type[BaseVideoProvider]] = {}


def register_provider(name: str, provider_class: Type[BaseVideoProvider]):
    """
    Register a provider class.
    
    Args:
        name: Provider name (e.g., "kling", "runway")
        provider_class: Provider class (not instance)
    """
    PROVIDER_REGISTRY[name] = provider_class


def get_available_providers() -> List[str]:
    """Get list of available provider names"""
    return list(PROVIDER_REGISTRY.keys())


def get_provider(
    provider_name: str,
    api_key: str,
    base_url: Optional[str] = None,
    timeout_seconds: int = 300,
    max_retries: int = 3
) -> BaseVideoProvider:
    """
    Factory function to create provider instance.
    
    Args:
        provider_name: Name of provider ("kling", "runway", "luma")
        api_key: API key for authentication
        base_url: Optional custom base URL (uses provider default if None)
        timeout_seconds: Request timeout
        max_retries: Maximum retry attempts
    
    Returns:
        Provider instance
    
    Raises:
        ProviderError: If provider not found or invalid
    """
    provider_class = PROVIDER_REGISTRY.get(provider_name)
    
    if not provider_class:
        available = get_available_providers()
        raise ProviderError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {available}"
        )
    
    # Use provider default base_url if not specified
    if base_url is None:
        base_url = provider_class.__dict__.get("base_url", "")
    
    return provider_class(
        api_key=api_key,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries
    )


def get_primary_provider(
    api_keys: Dict[str, str],
    mode: str = "text_to_video"
) -> BaseVideoProvider:
    """
    Get primary provider based on configuration.
    
    Args:
        api_keys: Dict of provider_name -> api_key
        mode: Generation mode
    
    Returns:
        Primary available provider
    
    Raises:
        ProviderError: If no provider available
    """
    # Priority order (configurable in production)
    priority = ["kling", "runway", "luma"]
    
    for provider_name in priority:
        api_key = api_keys.get(provider_name)
        if api_key:
            try:
                provider = get_provider(provider_name, api_key)
                # Quick health check
                # Note: In production, make this async
                return provider
            except Exception:
                continue
    
    raise ProviderError("No available providers with valid API keys")


async def health_check_all_providers(
    api_keys: Dict[str, str]
) -> Dict[str, ProviderStatus]:
    """
    Health check all configured providers.
    
    Args:
        api_keys: Dict of provider_name -> api_key
    
    Returns:
        Dict of provider_name -> status
    """
    results = {}
    
    for provider_name, api_key in api_keys.items():
        try:
            provider = get_provider(provider_name, api_key)
            is_healthy = await provider.health_check()
            results[provider_name] = provider.status
        except Exception:
            results[provider_name] = ProviderStatus.UNHEALTHY
    
    return results


# Auto-register providers as they are implemented
# This will be updated as providers are added
try:
    from cine_mate.adapters.kling_provider import KlingProvider
    register_provider("kling", KlingProvider)
except ImportError:
    pass  # Kling provider not yet implemented

try:
    from cine_mate.adapters.runway_provider import RunwayProvider
    register_provider("runway", RunwayProvider)
except ImportError:
    pass  # Runway provider not yet implemented

try:
    from cine_mate.adapters.luma_provider import LumaProvider
    register_provider("luma", LumaProvider)
except ImportError:
    pass  # Luma provider not yet implemented
