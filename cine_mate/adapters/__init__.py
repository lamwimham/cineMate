"""
CineMate Provider Adapters

Video generation provider abstraction layer.
Supports Kling, Runway, Luma, and other providers.
"""

from cine_mate.adapters.base import (
    BaseVideoProvider,
    VideoGenerationResult,
    GenerationParams,
    ProviderStatus,
    VideoGenerationMode,
    ProviderError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)

from cine_mate.adapters.factory import (
    get_provider,
    get_available_providers,
    get_primary_provider,
    register_provider,
    health_check_all_providers,
)

__all__ = [
    # Base classes
    "BaseVideoProvider",
    "VideoGenerationResult",
    "GenerationParams",
    "ProviderStatus",
    "VideoGenerationMode",
    
    # Exceptions
    "ProviderError",
    "ProviderAuthenticationError",
    "ProviderRateLimitError",
    "ProviderTimeoutError",
    
    # Factory
    "get_provider",
    "get_available_providers",
    "get_primary_provider",
    "register_provider",
    "health_check_all_providers",
]
