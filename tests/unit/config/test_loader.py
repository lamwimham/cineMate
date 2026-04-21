"""
Tests for Config Loader (Sprint 2 Day 2)

Test Coverage:
- load_config() from defaults.yaml
- get_model_for_task()
- get_model_by_cost()
- Environment variable override (TODO: Sprint 2)
- Custom config file support (TODO: Sprint 2)
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from cine_mate.config.loader import (
    load_config,
    get_model_for_task,
    get_model_by_cost,
)
from cine_mate.config.models import (
    CineMateConfig,
    ModelProfile,
    ModelTier,
    LLMProvider,
    ImageProvider,
    VideoProvider,
)


class TestLoadConfig:
    """Test config loading functionality."""

    def test_load_config_returns_valid_config(self):
        """Verify load_config returns a valid CineMateConfig."""
        config = load_config()

        assert config is not None
        assert isinstance(config, CineMateConfig)

    def test_load_config_has_models(self):
        """Verify config has all required model configurations."""
        config = load_config()

        assert hasattr(config, "models")
        assert config.models is not None

    def test_load_config_has_llm_config(self):
        """Verify LLM config is present."""
        config = load_config()

        assert hasattr(config.models, "llm")
        assert config.models.llm.primary is not None

    def test_load_config_has_all_task_configs(self):
        """Verify all task model configs are present."""
        config = load_config()

        required_tasks = ["llm", "text_to_image", "image_to_video", "text_to_video", "tts"]

        for task in required_tasks:
            assert hasattr(config.models, task)
            tier = getattr(config.models, task)
            assert tier.primary is not None

    def test_load_config_has_infra_defaults(self):
        """Verify infrastructure defaults are loaded."""
        config = load_config()

        assert hasattr(config, "infra")
        assert config.infra.redis_url == "redis://localhost:6379"
        assert config.infra.db_path == "./cinemate.db"
        assert config.infra.worker_timeout == 600

    def test_load_config_has_app_defaults(self):
        """Verify application defaults are loaded."""
        config = load_config()

        assert hasattr(config, "app")
        assert config.app.log_level == "INFO"
        assert config.app.enable_telemetry is False
        assert config.app.max_concurrent_runs == 5

    def test_load_config_default_path(self):
        """Verify default config path is correct."""
        defaults_path = Path(__file__).parent.parent.parent.parent / "cine_mate" / "config" / "defaults.yaml"

        # File should exist
        assert defaults_path.exists()


class TestGetModelForTask:
    """Test get_model_for_task functionality."""

    def test_get_llm_model(self):
        """Get LLM model configuration."""
        config = load_config()

        model = get_model_for_task(config, "llm")

        assert model is not None
        assert isinstance(model, ModelProfile)
        assert model.provider == "dashscope_qwen"
        assert model.model_name == "qwen-max"

    def test_get_text_to_image_model(self):
        """Get text_to_image model configuration."""
        config = load_config()

        model = get_model_for_task(config, "text_to_image")

        assert model is not None
        assert model.provider == "flux"
        assert model.model_name == "flux-pro-1.1"

    def test_get_image_to_video_model(self):
        """Get image_to_video model configuration."""
        config = load_config()

        model = get_model_for_task(config, "image_to_video")

        assert model is not None
        assert model.provider == "kling"
        assert model.model_name == "kling-v1.6-pro"

    def test_get_tts_model(self):
        """Get tts model configuration."""
        config = load_config()

        model = get_model_for_task(config, "tts")

        assert model is not None
        assert model.provider == "cosyvoice"
        assert model.model_name == "cosyvoice-v2"

    def test_get_vision_model(self):
        """Get vision model configuration (optional)."""
        config = load_config()

        if config.models.vision:
            model = get_model_for_task(config, "vision")
            assert model is not None


class TestGetModelByCost:
    """Test get_model_by_cost functionality."""

    def test_get_primary_model(self):
        """Get primary (default) cost tier model."""
        config = load_config()

        model = get_model_by_cost(config, "llm", "primary")

        assert model.model_name == "qwen-max"

    def test_get_fallback_model(self):
        """Get fallback cost tier model."""
        config = load_config()

        model = get_model_by_cost(config, "llm", "fallback")

        assert model.model_name == "qwen-plus"

    def test_get_budget_model(self):
        """Get budget (lowest cost) tier model."""
        config = load_config()

        model = get_model_by_cost(config, "llm", "budget")

        assert model.model_name == "qwen-turbo"

    def test_invalid_tier_returns_primary(self):
        """Invalid cost tier should return primary."""
        config = load_config()

        model = get_model_by_cost(config, "llm", "invalid_tier")

        assert model.model_name == "qwen-max"

    def test_no_fallback_returns_primary(self):
        """If fallback is None, return primary."""
        # Create a minimal config without fallback
        minimal_tier = ModelTier(
            primary=ModelProfile(provider="test", model_name="test-primary")
        )

        class MinimalModels:
            llm = minimal_tier

        class MinimalConfig:
            models = MinimalModels()

        config = MinimalConfig()
        model = get_model_by_cost(config, "llm", "fallback")

        assert model.model_name == "test-primary"


class TestModelProfile:
    """Test ModelProfile data model."""

    def test_model_profile_creation(self):
        """Create basic ModelProfile."""
        profile = ModelProfile(
            provider="test_provider",
            model_name="test_model",
        )

        assert profile.provider == "test_provider"
        assert profile.model_name == "test_model"
        assert profile.max_retries == 2  # default
        assert profile.timeout_seconds == 120  # default

    def test_model_profile_with_api_key_env(self):
        """ModelProfile with API key environment variable."""
        profile = ModelProfile(
            provider="dashscope_qwen",
            model_name="qwen-max",
            api_key_env="DASHSCOPE_API_KEY",
        )

        assert profile.api_key_env == "DASHSCOPE_API_KEY"

    def test_model_profile_with_extra_params(self):
        """ModelProfile with extra parameters."""
        profile = ModelProfile(
            provider="flux",
            model_name="flux-pro-1.1",
            extra={"width": 1024, "height": 1024},
        )

        assert profile.extra["width"] == 1024
        assert profile.extra["height"] == 1024


class TestModelTier:
    """Test ModelTier data model."""

    def test_model_tier_with_primary_only(self):
        """ModelTier with only primary model."""
        tier = ModelTier(
            primary=ModelProfile(provider="test", model_name="test-primary")
        )

        assert tier.primary is not None
        assert tier.fallback is None
        assert tier.budget is None

    def test_model_tier_with_all_tiers(self):
        """ModelTier with all cost tiers."""
        tier = ModelTier(
            primary=ModelProfile(provider="test", model_name="primary"),
            fallback=ModelProfile(provider="test", model_name="fallback"),
            budget=ModelProfile(provider="test", model_name="budget"),
        )

        assert tier.primary.model_name == "primary"
        assert tier.fallback.model_name == "fallback"
        assert tier.budget.model_name == "budget"


class TestConfigValidation:
    """Test configuration validation."""

    def test_valid_config_passes_validation(self):
        """Valid config should pass Pydantic validation."""
        config_data = {
            "models": {
                "llm": {
                    "primary": {"provider": "test", "model_name": "test-primary"}
                },
                "text_to_image": {
                    "primary": {"provider": "test", "model_name": "test-image"}
                },
                "image_to_video": {
                    "primary": {"provider": "test", "model_name": "test-video"}
                },
                "text_to_video": {
                    "primary": {"provider": "test", "model_name": "test-t2v"}
                },
                "tts": {
                    "primary": {"provider": "test", "model_name": "test-tts"}
                },
            }
        }

        config = CineMateConfig(**config_data)
        assert config is not None

    def test_missing_required_field_raises(self):
        """Missing required field should raise ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CineMateConfig(models={})  # Missing required fields


class TestProviderEnums:
    """Test provider enum values."""

    def test_llm_provider_enum(self):
        """LLM provider enum values."""
        assert LLMProvider.DASHSCOPE_QWEN == "dashscope_qwen"
        assert LLMProvider.OPENAI == "openai"
        assert LLMProvider.ANTHROPIC == "anthropic"

    def test_image_provider_enum(self):
        """Image provider enum values."""
        assert ImageProvider.FLUX == "flux"
        assert ImageProvider.MIDJOURNEY == "midjourney"
        assert ImageProvider.DASHSCOPE_WANX == "dashscope_wanx"

    def test_video_provider_enum(self):
        """Video provider enum values."""
        assert VideoProvider.KLING == "kling"
        assert VideoProvider.RUNWAY == "runway"
        assert VideoProvider.LUMA == "luma"


class TestInfraConfig:
    """Test infrastructure configuration."""

    def test_infra_config_defaults(self):
        """Infrastructure config default values."""
        from cine_mate.config.models import InfraConfig

        infra = InfraConfig()

        assert infra.redis_url == "redis://localhost:6379"
        assert infra.db_path == "./cinemate.db"
        assert infra.cas_root == "./cinemate_cas"
        assert infra.queue_name == "default"
        assert infra.worker_timeout == 600

    def test_infra_config_custom_values(self):
        """Infrastructure config with custom values."""
        from cine_mate.config.models import InfraConfig

        infra = InfraConfig(
            redis_url="redis://custom:6380",
            db_path="/custom/path/db.db",
            worker_timeout=1200,
        )

        assert infra.redis_url == "redis://custom:6380"
        assert infra.db_path == "/custom/path/db.db"
        assert infra.worker_timeout == 1200


class TestAppConfig:
    """Test application configuration."""

    def test_app_config_defaults(self):
        """Application config default values."""
        from cine_mate.config.models import AppConfig

        app = AppConfig()

        assert app.log_level == "INFO"
        assert app.enable_telemetry is False
        assert app.max_concurrent_runs == 5

    def test_app_config_custom_values(self):
        """Application config with custom values."""
        from cine_mate.config.models import AppConfig

        app = AppConfig(
            log_level="DEBUG",
            enable_telemetry=True,
            max_concurrent_runs=10,
        )

        assert app.log_level == "DEBUG"
        assert app.enable_telemetry is True
        assert app.max_concurrent_runs == 10