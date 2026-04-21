"""
Tests for Video Provider Adapters (Sprint 2 Day 3)

Test Coverage:
- BaseVideoProvider abstract class
- VideoGenerationResult dataclass
- GenerationParams dataclass
- ProviderError exceptions
- ProviderFactory functions
"""

import pytest
import asyncio
from datetime import datetime
from typing import Optional
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import dataclass

from cine_mate.adapters.base import (
    BaseVideoProvider,
    VideoGenerationResult,
    GenerationParams,
    VideoGenerationMode,
    ProviderStatus,
    ProviderError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from cine_mate.adapters.factory import (
    register_provider,
    get_available_providers,
    get_provider,
    get_primary_provider,
    health_check_all_providers,
    PROVIDER_REGISTRY,
)


# =============================================================================
# Mock Provider for Testing
# =============================================================================

class MockVideoProvider(BaseVideoProvider):
    """Mock provider for testing purposes."""

    provider_name = "mock"
    supported_modes = [
        VideoGenerationMode.TEXT_TO_VIDEO,
        VideoGenerationMode.IMAGE_TO_VIDEO,
    ]
    max_duration_seconds = 60
    min_duration_seconds = 1
    base_url = "https://mock.provider.api"

    def __init__(self, api_key: str = "mock_key", **kwargs):
        """Initialize mock provider."""
        super().__init__(
            api_key=api_key,
            base_url=self.base_url,
            timeout_seconds=300,
            max_retries=3
        )

    async def generate_video(self, params: GenerationParams) -> VideoGenerationResult:
        """Mock video generation."""
        return VideoGenerationResult(
            job_id="mock_job_001",
            status="completed",
            video_url="https://mock.video.url/output.mp4",
            thumbnail_url="https://mock.video.url/thumb.jpg",
            cost=1.5,
            duration_seconds=params.duration_seconds,
            resolution=params.resolution,
            provider=self.provider_name,
        )

    async def get_job_status(self, job_id: str) -> str:
        """Mock job status."""
        return "completed"

    async def cancel_job(self, job_id: str) -> bool:
        """Mock job cancellation."""
        return True

    def estimate_cost(self, duration_seconds: int, resolution: str = "720p", mode: VideoGenerationMode = VideoGenerationMode.TEXT_TO_VIDEO) -> float:
        """Mock cost estimation."""
        base_rate = 0.15  # $0.15 per second
        resolution_factor = {"720p": 1.0, "1080p": 1.5, "4k": 2.5}
        return duration_seconds * base_rate * resolution_factor.get(resolution, 1.0)

    async def check_status(self, job_id: str) -> str:
        """Mock job status check."""
        return "completed"

    async def get_result(self, job_id: str) -> Optional[VideoGenerationResult]:
        """Mock get result."""
        return VideoGenerationResult(
            job_id=job_id,
            status="completed",
            video_url="https://mock.video.url/output.mp4",
        )


# =============================================================================
# VideoGenerationResult Tests
# =============================================================================

class TestVideoGenerationResult:
    """Test VideoGenerationResult dataclass."""

    def test_result_creation(self):
        """Create basic VideoGenerationResult."""
        result = VideoGenerationResult(
            job_id="job_001",
            status="completed",
        )

        assert result.job_id == "job_001"
        assert result.status == "completed"

    def test_result_with_all_fields(self):
        """VideoGenerationResult with all fields."""
        result = VideoGenerationResult(
            job_id="job_002",
            status="completed",
            video_url="https://example.com/video.mp4",
            thumbnail_url="https://example.com/thumb.jpg",
            cost=2.5,
            duration_seconds=10,
            resolution="1080p",
            provider="kling",
            metadata={"fps": 30},
        )

        assert result.video_url == "https://example.com/video.mp4"
        assert result.cost == 2.5
        assert result.duration_seconds == 10
        assert result.resolution == "1080p"

    def test_is_completed_true(self):
        """is_completed returns True for successful result."""
        result = VideoGenerationResult(
            job_id="job_003",
            status="completed",
            video_url="https://example.com/video.mp4",
        )

        assert result.is_completed is True

    def test_is_completed_false_no_url(self):
        """is_completed returns False without video_url."""
        result = VideoGenerationResult(
            job_id="job_004",
            status="completed",
        )

        assert result.is_completed is False

    def test_is_completed_false_processing(self):
        """is_completed returns False for processing status."""
        result = VideoGenerationResult(
            job_id="job_005",
            status="processing",
            video_url=None,
        )

        assert result.is_completed is False

    def test_is_failed_true(self):
        """is_failed returns True for failed status."""
        result = VideoGenerationResult(
            job_id="job_006",
            status="failed",
            error_message="API timeout",
        )

        assert result.is_failed is True

    def test_is_failed_true_with_error(self):
        """is_failed returns True with error_message."""
        result = VideoGenerationResult(
            job_id="job_007",
            status="completed",
            error_message="Corrupted output",
        )

        assert result.is_failed is True

    def test_is_failed_false(self):
        """is_failed returns False for successful result."""
        result = VideoGenerationResult(
            job_id="job_008",
            status="completed",
            video_url="https://example.com/video.mp4",
        )

        assert result.is_failed is False

    def test_created_at_default(self):
        """created_at has default value."""
        result = VideoGenerationResult(
            job_id="job_009",
            status="completed",
        )

        assert result.created_at is not None
        assert isinstance(result.created_at, datetime)

    def test_completed_at_optional(self):
        """completed_at is optional."""
        result = VideoGenerationResult(
            job_id="job_010",
            status="completed",
            completed_at=datetime.now(),
        )

        assert result.completed_at is not None


# =============================================================================
# GenerationParams Tests
# =============================================================================

class TestGenerationParams:
    """Test GenerationParams dataclass."""

    def test_params_creation_minimal(self):
        """Create GenerationParams with minimal fields."""
        params = GenerationParams(prompt="A cinematic shot")

        assert params.prompt == "A cinematic shot"
        assert params.duration_seconds == 10  # default
        assert params.resolution == "720p"  # default

    def test_params_with_all_fields(self):
        """GenerationParams with all fields."""
        params = GenerationParams(
            prompt="A beautiful sunset",
            negative_prompt="blurry, low quality",
            duration_seconds=15,
            resolution="1080p",
            fps=60,
            mode=VideoGenerationMode.IMAGE_TO_VIDEO,
            image_url="https://example.com/input.jpg",
            seed=42,
            guidance_scale=8.5,
            num_inference_steps=100,
            extra_params={"style": "cinematic"},
        )

        assert params.negative_prompt == "blurry, low quality"
        assert params.duration_seconds == 15
        assert params.mode == VideoGenerationMode.IMAGE_TO_VIDEO
        assert params.image_url == "https://example.com/input.jpg"

    def test_params_default_mode(self):
        """Default mode is TEXT_TO_VIDEO."""
        params = GenerationParams(prompt="test")

        assert params.mode == VideoGenerationMode.TEXT_TO_VIDEO

    def test_params_extra_params_default(self):
        """extra_params defaults to empty dict."""
        params = GenerationParams(prompt="test")

        assert params.extra_params == {}

    def test_params_modes(self):
        """VideoGenerationMode enum values."""
        assert VideoGenerationMode.TEXT_TO_VIDEO == "text_to_video"
        assert VideoGenerationMode.IMAGE_TO_VIDEO == "image_to_video"
        assert VideoGenerationMode.VIDEO_TO_VIDEO == "video_to_video"


# =============================================================================
# BaseVideoProvider Tests
# =============================================================================

class TestBaseVideoProvider:
    """Test BaseVideoProvider abstract class."""

    def test_provider_initialization(self):
        """Initialize provider with config."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
            timeout_seconds=120,
            max_retries=5,
        )

        assert provider.api_key == "test_key"
        assert provider.base_url == "https://test.api"
        assert provider.timeout_seconds == 120
        assert provider.max_retries == 5

    def test_provider_status_default(self):
        """Provider status defaults to UNKNOWN."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
        )

        assert provider.status == ProviderStatus.UNKNOWN

    def test_provider_status_enum_values(self):
        """ProviderStatus enum values."""
        assert ProviderStatus.HEALTHY == "healthy"
        assert ProviderStatus.DEGRADED == "degraded"
        assert ProviderStatus.UNHEALTHY == "unhealthy"
        assert ProviderStatus.UNKNOWN == "unknown"

    def test_provider_name_attribute(self):
        """Provider has class-level name."""
        assert MockVideoProvider.provider_name == "mock"

    def test_provider_supported_modes(self):
        """Provider has supported_modes list."""
        assert len(MockVideoProvider.supported_modes) == 2
        assert VideoGenerationMode.TEXT_TO_VIDEO in MockVideoProvider.supported_modes

    def test_get_auth_headers(self):
        """_get_auth_headers returns correct headers."""
        provider = MockVideoProvider(
            api_key="secret_key",
            base_url="https://test.api",
        )

        headers = provider._get_auth_headers()

        assert headers["Authorization"] == "Bearer secret_key"
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_health_check_sets_status(self):
        """health_check updates provider status."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
        )

        result = await provider.health_check()

        assert result is True
        assert provider.status == ProviderStatus.HEALTHY


class TestProviderValidation:
    """Test provider parameter validation."""

    def test_validate_duration_min(self):
        """validate_params checks minimum duration."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
        )

        params = GenerationParams(
            prompt="test",
            duration_seconds=0,  # Below minimum
        )

        with pytest.raises(ValueError, match="Duration must be at least"):
            provider.validate_params(params)

    def test_validate_duration_max(self):
        """validate_params checks maximum duration."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
        )

        params = GenerationParams(
            prompt="test",
            duration_seconds=100,  # Above maximum
        )

        with pytest.raises(ValueError, match="Duration must be at most"):
            provider.validate_params(params)

    def test_validate_mode_not_supported(self):
        """validate_params checks supported modes."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
        )

        params = GenerationParams(
            prompt="test",
            mode=VideoGenerationMode.VIDEO_TO_VIDEO,  # Not in supported_modes
        )

        with pytest.raises(ValueError, match="not supported"):
            provider.validate_params(params)

    def test_validate_image_to_video_requires_image_url(self):
        """IMAGE_TO_VIDEO mode requires image_url."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
        )

        params = GenerationParams(
            prompt="test",
            mode=VideoGenerationMode.IMAGE_TO_VIDEO,
            image_url=None,  # Missing
        )

        with pytest.raises(ValueError, match="image_url required"):
            provider.validate_params(params)

    def test_validate_video_to_video_requires_video_url(self):
        """VIDEO_TO_VIDEO mode requires video_url."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
        )

        params = GenerationParams(
            prompt="test",
            mode=VideoGenerationMode.VIDEO_TO_VIDEO,
            video_url=None,  # Missing
        )

        with pytest.raises(ValueError, match="video_url required"):
            provider.validate_params(params)

    def test_validate_params_passes(self):
        """validate_params passes for valid params."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
        )

        params = GenerationParams(
            prompt="test",
            duration_seconds=10,
            mode=VideoGenerationMode.TEXT_TO_VIDEO,
        )

        provider.validate_params(params)  # No exception


# =============================================================================
# Provider Retry Tests
# =============================================================================

class TestProviderRetry:
    """Test provider retry mechanism."""

    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self):
        """Retry succeeds on first attempt."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
            max_retries=3,
        )

        async def success_func():
            return "success"

        result = await provider._retry_request(success_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """Retry succeeds after initial failures."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
            max_retries=3,
        )

        call_count = 0

        async def failing_then_success():
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            return "success"

        result = await provider._retry_request(failing_then_success)

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted_raises(self):
        """Retry raises after max_retries exhausted."""
        provider = MockVideoProvider(
            api_key="test_key",
            base_url="https://test.api",
            max_retries=2,
        )

        async def always_fails():
            raise Exception("Permanent error")

        with pytest.raises(Exception, match="Permanent error"):
            await provider._retry_request(always_fails)


# =============================================================================
# Provider Exceptions Tests
# =============================================================================

class TestProviderExceptions:
    """Test provider exception classes."""

    def test_provider_error_base(self):
        """ProviderError is base exception."""
        error = ProviderError("Generic error")
        assert str(error) == "Generic error"
        assert isinstance(error, Exception)

    def test_authentication_error(self):
        """ProviderAuthenticationError inherits ProviderError."""
        error = ProviderAuthenticationError("Invalid API key")
        assert isinstance(error, ProviderError)

    def test_rate_limit_error(self):
        """ProviderRateLimitError inherits ProviderError."""
        error = ProviderRateLimitError("Rate limit exceeded")
        assert isinstance(error, ProviderError)

    def test_timeout_error(self):
        """ProviderTimeoutError inherits ProviderError."""
        error = ProviderTimeoutError("Request timed out")
        assert isinstance(error, ProviderError)


# =============================================================================
# Mock Provider Tests
# =============================================================================

class TestMockVideoProvider:
    """Test MockVideoProvider functionality."""

    @pytest.mark.asyncio
    async def test_generate_video_returns_result(self):
        """generate_video returns VideoGenerationResult."""
        provider = MockVideoProvider(
            api_key="mock_key",
            base_url="https://mock.api",
        )

        params = GenerationParams(prompt="Test prompt")
        result = await provider.generate_video(params)

        assert isinstance(result, VideoGenerationResult)
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_generate_video_with_params(self):
        """generate_video respects params."""
        provider = MockVideoProvider(
            api_key="mock_key",
            base_url="https://mock.api",
        )

        params = GenerationParams(
            prompt="Test",
            duration_seconds=20,
            resolution="1080p",
        )
        result = await provider.generate_video(params)

        assert result.duration_seconds == 20
        assert result.resolution == "1080p"

    @pytest.mark.asyncio
    async def test_get_job_status(self):
        """get_job_status returns status."""
        provider = MockVideoProvider(
            api_key="mock_key",
            base_url="https://mock.api",
        )

        status = await provider.get_job_status("mock_job_001")

        assert status == "completed"

    @pytest.mark.asyncio
    async def test_cancel_job(self):
        """cancel_job returns True."""
        provider = MockVideoProvider(
            api_key="mock_key",
            base_url="https://mock.api",
        )

        result = await provider.cancel_job("mock_job_001")

        assert result is True

    def test_estimate_cost(self):
        """estimate_cost calculates correctly."""
        provider = MockVideoProvider(
            api_key="mock_key",
            base_url="https://mock.api",
        )

        cost = provider.estimate_cost(10, "720p")

        # 10 seconds * $0.15/sec * 1.0 = $1.5
        assert cost == 1.5

    def test_estimate_cost_resolution_factor(self):
        """estimate_cost applies resolution factor."""
        provider = MockVideoProvider(
            api_key="mock_key",
            base_url="https://mock.api",
        )

        cost_720p = provider.estimate_cost(10, "720p")
        cost_1080p = provider.estimate_cost(10, "1080p")
        cost_4k = provider.estimate_cost(10, "4k")

        # 1080p = 1.5x, 4k = 2.5x
        assert cost_1080p == cost_720p * 1.5
        assert cost_4k == cost_720p * 2.5


# =============================================================================
# Provider Factory Tests
# =============================================================================

class TestProviderRegistry:
    """Test provider registry functions."""

    def test_register_provider(self):
        """register_provider adds to registry."""
        # Clear registry for test isolation
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()

        register_provider("mock", MockVideoProvider)

        assert "mock" in PROVIDER_REGISTRY
        assert PROVIDER_REGISTRY["mock"] == MockVideoProvider

        # Restore
        PROVIDER_REGISTRY.update(original_registry)

    def test_get_available_providers(self):
        """get_available_providers returns registered names."""
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("mock", MockVideoProvider)

        providers = get_available_providers()

        assert "mock" in providers

        PROVIDER_REGISTRY.update(original_registry)

    def test_get_provider_creates_instance(self):
        """get_provider creates provider instance."""
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("mock", MockVideoProvider)

        provider = get_provider("mock", "test_key")

        assert isinstance(provider, MockVideoProvider)
        assert provider.api_key == "test_key"

        PROVIDER_REGISTRY.update(original_registry)

    def test_get_provider_unknown_raises(self):
        """get_provider raises for unknown provider."""
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()

        with pytest.raises(ProviderError, match="Unknown provider"):
            get_provider("unknown", "test_key")

        PROVIDER_REGISTRY.update(original_registry)

    def test_get_provider_custom_url(self):
        """get_provider uses custom base_url."""
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("mock", MockVideoProvider)

        provider = get_provider("mock", "test_key", base_url="https://custom.url")

        assert provider.base_url == "https://custom.url"

        PROVIDER_REGISTRY.update(original_registry)

    def test_get_provider_timeout_config(self):
        """get_provider respects timeout config."""
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("mock", MockVideoProvider)

        provider = get_provider("mock", "test_key", timeout_seconds=600)

        assert provider.timeout_seconds == 600

        PROVIDER_REGISTRY.update(original_registry)


class TestPrimaryProvider:
    """Test get_primary_provider function."""

    def test_get_primary_provider_priority(self):
        """get_primary_provider returns first available."""
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("kling", MockVideoProvider)
        register_provider("runway", MockVideoProvider)

        api_keys = {"kling": "kling_key", "runway": "runway_key"}

        provider = get_primary_provider(api_keys)

        # Should return kling (first in priority)
        assert provider.api_key == "kling_key"

        PROVIDER_REGISTRY.update(original_registry)

    def test_get_primary_provider_fallback(self):
        """get_primary_provider falls back to next provider."""
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("runway", MockVideoProvider)

        api_keys = {"runway": "runway_key"}  # No kling key

        provider = get_primary_provider(api_keys)

        assert provider.api_key == "runway_key"

        PROVIDER_REGISTRY.update(original_registry)

    def test_get_primary_provider_no_keys_raises(self):
        """get_primary_provider raises if no keys."""
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()

        with pytest.raises(ProviderError, match="No available providers"):
            get_primary_provider({})

        PROVIDER_REGISTRY.update(original_registry)


class TestHealthCheckAllProviders:
    """Test health_check_all_providers function."""

    @pytest.mark.asyncio
    async def test_health_check_all(self):
        """health_check_all_providers checks all providers."""
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()
        register_provider("mock", MockVideoProvider)

        api_keys = {"mock": "test_key"}

        results = await health_check_all_providers(api_keys)

        assert "mock" in results
        assert results["mock"] == ProviderStatus.HEALTHY

        PROVIDER_REGISTRY.update(original_registry)

    @pytest.mark.asyncio
    async def test_health_check_invalid_provider(self):
        """health_check_all_providers handles invalid providers."""
        original_registry = PROVIDER_REGISTRY.copy()
        PROVIDER_REGISTRY.clear()

        # Provider not registered
        api_keys = {"unknown": "test_key"}

        results = await health_check_all_providers(api_keys)

        assert "unknown" in results
        assert results["unknown"] == ProviderStatus.UNHEALTHY

        PROVIDER_REGISTRY.update(original_registry)