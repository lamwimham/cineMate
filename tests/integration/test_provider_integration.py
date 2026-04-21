"""
Integration Tests for Provider Adapters (Sprint 2 Day 3)

Test Coverage:
- Provider factory integration
- Provider generation flow
- Worker + Provider integration
- Multiple provider fallback
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from cine_mate.adapters.base import (
    VideoGenerationResult,
    GenerationParams,
    VideoGenerationMode,
    ProviderStatus,
    ProviderError,
)
from cine_mate.adapters.factory import (
    register_provider,
    get_provider,
    get_primary_provider,
    get_available_providers,
    health_check_all_providers,
    PROVIDER_REGISTRY,
)


# =============================================================================
# Mock Provider for Integration Testing
# =============================================================================

class MockKlingProvider:
    """Mock Kling provider."""

    provider_name = "kling"
    supported_modes = [
        VideoGenerationMode.TEXT_TO_VIDEO,
        VideoGenerationMode.IMAGE_TO_VIDEO,
    ]
    max_duration_seconds = 60
    min_duration_seconds = 2
    base_url = "https://api.klingai.com"

    def __init__(self, api_key, base_url=None, timeout_seconds=300, max_retries=3):
        self.api_key = api_key
        self.base_url = base_url or self.base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._health_status = ProviderStatus.UNKNOWN

    @property
    def health_status(self):
        return self._health_status

    async def generate_video(self, params):
        return VideoGenerationResult(
            job_id="kling_job_001",
            status="completed",
            video_url="https://kling.output/video.mp4",
            cost=params.duration_seconds * 0.20,
            duration_seconds=params.duration_seconds,
            provider="kling",
        )

    async def get_job_status(self, job_id):
        return "completed"

    async def cancel_job(self, job_id):
        return True

    def estimate_cost(self, duration_seconds, resolution="720p", mode=None):
        return duration_seconds * 0.20

    async def health_check(self):
        self._health_status = ProviderStatus.HEALTHY
        return True

    def validate_params(self, params):
        if params.duration_seconds < self.min_duration_seconds:
            raise ValueError(f"Duration must be at least {self.min_duration_seconds}s")


class MockRunwayProvider:
    """Mock Runway provider."""

    provider_name = "runway"
    supported_modes = [
        VideoGenerationMode.TEXT_TO_VIDEO,
        VideoGenerationMode.IMAGE_TO_VIDEO,
    ]
    max_duration_seconds = 30
    min_duration_seconds = 5
    base_url = "https://api.runwayml.com"

    def __init__(self, api_key, base_url=None, timeout_seconds=300, max_retries=3):
        self.api_key = api_key
        self.base_url = base_url or self.base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._health_status = ProviderStatus.UNKNOWN

    @property
    def health_status(self):
        return self._health_status

    async def generate_video(self, params):
        return VideoGenerationResult(
            job_id="runway_job_001",
            status="completed",
            video_url="https://runway.output/video.mp4",
            cost=params.duration_seconds * 0.25,
            duration_seconds=params.duration_seconds,
            provider="runway",
        )

    async def get_job_status(self, job_id):
        return "completed"

    async def cancel_job(self, job_id):
        return True

    def estimate_cost(self, duration_seconds, resolution="720p", mode=None):
        return duration_seconds * 0.25

    async def health_check(self):
        self._health_status = ProviderStatus.HEALTHY
        return True

    def validate_params(self, params):
        if params.duration_seconds < self.min_duration_seconds:
            raise ValueError(f"Duration must be at least {self.min_duration_seconds}s")


class MockLumaProvider:
    """Mock Luma provider."""

    provider_name = "luma"
    supported_modes = [
        VideoGenerationMode.TEXT_TO_VIDEO,
        VideoGenerationMode.IMAGE_TO_VIDEO,
    ]
    max_duration_seconds = 10
    min_duration_seconds = 1
    base_url = "https://api.luma.ai"

    def __init__(self, api_key, base_url=None, timeout_seconds=300, max_retries=3):
        self.api_key = api_key
        self.base_url = base_url or self.base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._health_status = ProviderStatus.UNKNOWN

    @property
    def health_status(self):
        return self._health_status

    async def generate_video(self, params):
        return VideoGenerationResult(
            job_id="luma_job_001",
            status="completed",
            video_url="https://luma.output/video.mp4",
            cost=params.duration_seconds * 0.30,
            duration_seconds=params.duration_seconds,
            provider="luma",
        )

    async def get_job_status(self, job_id):
        return "completed"

    async def cancel_job(self, job_id):
        return True

    def estimate_cost(self, duration_seconds, resolution="720p", mode=None):
        return duration_seconds * 0.30

    async def health_check(self):
        self._health_status = ProviderStatus.HEALTHY
        return True

    def validate_params(self, params):
        pass  # No validation


# =============================================================================
# Provider Factory Integration Tests
# =============================================================================

class TestProviderFactoryIntegration:
    """Test provider factory with multiple providers."""

    def setup_method(self):
        """Setup: Register mock providers."""
        self.original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("kling", MockKlingProvider)
        register_provider("runway", MockRunwayProvider)
        register_provider("luma", MockLumaProvider)

    def teardown_method(self):
        """Teardown: Restore original registry."""
        PROVIDER_REGISTRY.clear()
        PROVIDER_REGISTRY.update(self.original_registry)

    def test_factory_creates_correct_provider_type(self):
        """Factory creates the correct provider type."""
        kling = get_provider("kling", "kling_key")
        runway = get_provider("runway", "runway_key")
        luma = get_provider("luma", "luma_key")

        assert isinstance(kling, MockKlingProvider)
        assert isinstance(runway, MockRunwayProvider)
        assert isinstance(luma, MockLumaProvider)

    def test_factory_provider_has_correct_config(self):
        """Factory provider has correct configuration."""
        provider = get_provider(
            "kling",
            "test_key",
            base_url="https://custom.url",
            timeout_seconds=600,
            max_retries=5,
        )

        assert provider.api_key == "test_key"
        assert provider.base_url == "https://custom.url"
        assert provider.timeout_seconds == 600
        assert provider.max_retries == 5

    def test_available_providers_list(self):
        """get_available_providers returns all registered."""
        providers = get_available_providers()

        assert "kling" in providers
        assert "runway" in providers
        assert "luma" in providers

    @pytest.mark.asyncio
    async def test_health_check_all_returns_dict(self):
        """health_check_all_providers returns status dict."""
        api_keys = {
            "kling": "kling_key",
            "runway": "runway_key",
            "luma": "luma_key",
        }

        results = await health_check_all_providers(api_keys)

        assert isinstance(results, dict)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_health_check_sets_provider_status(self):
        """health_check updates provider status."""
        api_keys = {"kling": "kling_key"}

        results = await health_check_all_providers(api_keys)

        assert results["kling"] == ProviderStatus.HEALTHY


class TestProviderFallback:
    """Test provider fallback chain."""

    def setup_method(self):
        """Setup: Register mock providers."""
        self.original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("kling", MockKlingProvider)
        register_provider("runway", MockRunwayProvider)
        register_provider("luma", MockLumaProvider)

    def teardown_method(self):
        """Teardown."""
        PROVIDER_REGISTRY.clear()
        PROVIDER_REGISTRY.update(self.original_registry)

    def test_primary_provider_first_available(self):
        """get_primary_provider returns first in priority."""
        api_keys = {
            "kling": "kling_key",
            "runway": "runway_key",
        }

        provider = get_primary_provider(api_keys)

        # kling is first in priority list
        assert provider.api_key == "kling_key"

    def test_primary_provider_fallback(self):
        """get_primary_provider falls back if first unavailable."""
        api_keys = {
            "runway": "runway_key",
            "luma": "luma_key",
        }

        provider = get_primary_provider(api_keys)

        # kling skipped (no key), runway is next
        assert provider.api_key == "runway_key"

    def test_primary_provider_last_fallback(self):
        """get_primary_provider uses last available."""
        api_keys = {
            "luma": "luma_key",
        }

        provider = get_primary_provider(api_keys)

        assert provider.api_key == "luma_key"

    def test_primary_provider_no_keys_raises(self):
        """get_primary_provider raises when no keys."""
        with pytest.raises(ProviderError):
            get_primary_provider({})


class TestProviderGenerationFlow:
    """Test complete generation flow."""

    def setup_method(self):
        """Setup."""
        self.original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("kling", MockKlingProvider)

    def teardown_method(self):
        """Teardown."""
        PROVIDER_REGISTRY.clear()
        PROVIDER_REGISTRY.update(self.original_registry)

    @pytest.mark.asyncio
    async def test_text_to_video_flow(self):
        """Complete text-to-video generation flow."""
        provider = get_provider("kling", "test_key")

        params = GenerationParams(
            prompt="A cinematic sunset",
            duration_seconds=10,
            mode=VideoGenerationMode.TEXT_TO_VIDEO,
        )

        result = await provider.generate_video(params)

        assert result.is_completed
        assert result.provider == "kling"
        assert result.duration_seconds == 10

    @pytest.mark.asyncio
    async def test_image_to_video_flow(self):
        """Complete image-to-video generation flow."""
        provider = get_provider("kling", "test_key")

        params = GenerationParams(
            prompt="Animate this image",
            duration_seconds=5,
            mode=VideoGenerationMode.IMAGE_TO_VIDEO,
            image_url="https://example.com/input.jpg",
        )

        result = await provider.generate_video(params)

        assert result.is_completed

    @pytest.mark.asyncio
    async def test_cost_estimation_flow(self):
        """Cost estimation before generation."""
        provider = get_provider("kling", "test_key")

        estimated_cost = provider.estimate_cost(10, "720p")
        params = GenerationParams(prompt="test", duration_seconds=10)

        result = await provider.generate_video(params)

        # Estimated cost matches actual
        assert estimated_cost == result.cost

    @pytest.mark.asyncio
    async def test_job_status_check(self):
        """Job status check after generation."""
        provider = get_provider("kling", "test_key")

        params = GenerationParams(prompt="test")
        result = await provider.generate_video(params)

        status = await provider.get_job_status(result.job_id)

        assert status == "completed"


class TestProviderValidationIntegration:
    """Test parameter validation in integration context."""

    def setup_method(self):
        """Setup."""
        self.original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("kling", MockKlingProvider)
        register_provider("runway", MockRunwayProvider)

    def teardown_method(self):
        """Teardown."""
        PROVIDER_REGISTRY.clear()
        PROVIDER_REGISTRY.update(self.original_registry)

    def test_kling_min_duration_validation(self):
        """Kling validates minimum duration."""
        provider = get_provider("kling", "test_key")

        params = GenerationParams(
            prompt="test",
            duration_seconds=1,  # Below Kling's min (2)
        )

        with pytest.raises(ValueError):
            provider.validate_params(params)

    def test_runway_min_duration_validation(self):
        """Runway validates minimum duration."""
        provider = get_provider("runway", "test_key")

        params = GenerationParams(
            prompt="test",
            duration_seconds=3,  # Below Runway's min (5)
        )

        with pytest.raises(ValueError):
            provider.validate_params(params)

    def test_valid_params_pass(self):
        """Valid params pass validation."""
        provider = get_provider("kling", "test_key")

        params = GenerationParams(
            prompt="test",
            duration_seconds=10,  # Above min
        )

        provider.validate_params(params)  # No exception


class TestMultipleProviderComparison:
    """Test multiple providers for cost comparison."""

    def setup_method(self):
        """Setup."""
        self.original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("kling", MockKlingProvider)
        register_provider("runway", MockRunwayProvider)
        register_provider("luma", MockLumaProvider)

    def teardown_method(self):
        """Teardown."""
        PROVIDER_REGISTRY.clear()
        PROVIDER_REGISTRY.update(self.original_registry)

    def test_cost_comparison_between_providers(self):
        """Compare costs across providers."""
        kling = get_provider("kling", "key1")
        runway = get_provider("runway", "key2")
        luma = get_provider("luma", "key3")

        duration = 10

        cost_kling = kling.estimate_cost(duration)
        cost_runway = runway.estimate_cost(duration)
        cost_luma = luma.estimate_cost(duration)

        # Kling cheapest ($0.20/s), Luma most expensive ($0.30/s)
        assert cost_kling < cost_runway < cost_luma

    @pytest.mark.asyncio
    async def test_generation_result_comparison(self):
        """Compare generation results across providers."""
        providers = {
            "kling": get_provider("kling", "key1"),
            "runway": get_provider("runway", "key2"),
            "luma": get_provider("luma", "key3"),
        }

        params = GenerationParams(prompt="test", duration_seconds=10)

        results = {}
        for name, provider in providers.items():
            results[name] = await provider.generate_video(params)

        # All complete successfully
        for name, result in results.items():
            assert result.is_completed
            assert result.provider == name


class TestProviderErrorHandling:
    """Test provider error handling in integration."""

    def setup_method(self):
        """Setup."""
        self.original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()

    def teardown_method(self):
        """Teardown."""
        PROVIDER_REGISTRY.clear()
        PROVIDER_REGISTRY.update(self.original_registry)

    def test_unknown_provider_error(self):
        """Unknown provider raises ProviderError."""
        with pytest.raises(ProviderError, match="Unknown provider"):
            get_provider("unknown_provider", "test_key")

    def test_provider_error_message_includes_available(self):
        """Error message includes available providers."""
        register_provider("kling", MockKlingProvider)

        with pytest.raises(ProviderError) as exc_info:
            get_provider("unknown", "test_key")

        # Error message should mention available providers
        assert "Available providers" in str(exc_info.value)


class TestWorkerProviderIntegration:
    """Test Worker integration with providers."""

    def setup_method(self):
        """Setup."""
        self.original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("kling", MockKlingProvider)

    def teardown_method(self):
        """Teardown."""
        PROVIDER_REGISTRY.clear()
        PROVIDER_REGISTRY.update(self.original_registry)

    @pytest.mark.asyncio
    async def test_worker_can_use_provider(self):
        """Worker can get provider and generate video."""
        # Simulate Worker flow
        from cine_mate.adapters.factory import get_provider

        provider = get_provider("kling", "worker_key")

        params = GenerationParams(
            prompt="Worker task",
            duration_seconds=5,
        )

        result = await provider.generate_video(params)

        assert result.is_completed
        assert result.job_id is not None