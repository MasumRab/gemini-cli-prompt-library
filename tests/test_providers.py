"""
Tests for DSPy-HELM providers.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestBaseProvider:
    """Test base provider functionality."""

    def test_provider_response_dataclass(self):
        """Test ProviderResponse dataclass."""
        from dspy_integration.providers.base import ProviderResponse, RateLimitConfig

        response = ProviderResponse(
            success=True,
            content="Test response",
            provider="TestProvider",
            model="test-model",
            tokens_used=100,
            latency_seconds=0.5,
        )

        assert response.success is True
        assert response.content == "Test response"
        assert response.tokens_used == 100
        assert response.rate_limited is False

    def test_rate_limit_config(self):
        """Test RateLimitConfig dataclass."""
        from dspy_integration.providers.base import RateLimitConfig

        config = RateLimitConfig(
            enabled=True,
            max_retries=3,
            backoff_factor=2.0,
            max_backoff=60.0,
        )

        assert config.enabled is True
        assert config.max_retries == 3
        assert config.backoff_factor == 2.0

    def test_provider_chain(self):
        """Test ProviderChain."""
        from dspy_integration.providers.base import (
            BaseProvider,
            ProviderChain,
            ProviderResponse,
        )

        class MockProvider(BaseProvider):
            def __init__(self, name, fail_count=0):
                super().__init__(
                    name=name, command="test", subcommand="test", model="test"
                )
                self.fail_count = fail_count
                self.call_count = 0

            def _execute_cli(self, prompt, **kwargs):
                self.call_count += 1
                if self.call_count <= self.fail_count:
                    return ProviderResponse(
                        success=False,
                        error="Rate limited",
                        rate_limited=True,
                    )
                return ProviderResponse(
                    success=True,
                    content="Response from " + self.name,
                    provider=self.name,
                    model=self.model,
                )

        provider1 = MockProvider("Provider1", fail_count=5)  # Fail all retries
        provider2 = MockProvider("Provider2", fail_count=0)

        chain = ProviderChain([provider1, provider2])
        response = chain.call("Test prompt")

        assert response.success is True
        assert response.provider == "Provider2"

    def test_provider_chain_all_fail(self):
        """Test ProviderChain when all providers fail."""
        from dspy_integration.providers.base import (
            BaseProvider,
            ProviderChain,
            ProviderResponse,
        )

        class FailingProvider(BaseProvider):
            def _execute_cli(self, prompt, **kwargs):
                return ProviderResponse(
                    success=False,
                    error="Service unavailable",
                    provider=self.name,
                    model=self.model,
                )

        provider1 = FailingProvider(
            name="P1", command="test", subcommand="test", model="test"
        )
        provider2 = FailingProvider(
            name="P2", command="test", subcommand="test", model="test"
        )

        chain = ProviderChain([provider1, provider2])
        response = chain.call("Test prompt")

        assert response.success is False
        assert response.error is not None
        assert "failed" in response.error.lower()


class TestProviderRegistry:
    """Test provider registry functions."""

    def test_create_provider_chain(self):
        """Test creating provider chain."""
        from dspy_integration.providers import create_provider_chain

        chain = create_provider_chain()
        assert len(chain.providers) > 0

    def test_get_default_provider(self):
        """Test getting default provider."""
        from dspy_integration.providers import get_default_provider

        provider = get_default_provider()
        assert provider is not None
        assert "Groq" in provider.name

    def test_get_provider_by_name(self):
        """Test getting specific provider."""
        from dspy_integration.providers import get_provider_by_name

        provider = get_provider_by_name("opencode_zen")
        assert provider is not None

    def test_get_unknown_provider(self):
        """Test getting unknown provider raises error."""
        from dspy_integration.providers import get_provider_by_name

        with pytest.raises(ValueError) as exc_info:
            get_provider_by_name("unknown_provider")
        assert "Unknown provider" in str(exc_info.value)


class TestOpenCodeZenProvider:
    """Test OpenCode Zen provider."""

    def test_init(self):
        """Test provider initialization."""
        from dspy_integration.providers.opencode_zen import OpenCodeZenProvider

        provider = OpenCodeZenProvider(model="grok-code")
        assert provider.name == "OpenCode Zen (Grok Code Fast)"
        assert provider.model == "grok-code"
        assert provider.base_url == "https://opencode.ai/zen/v1/chat/completions"

    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        from dspy_integration.providers.opencode_zen import OpenCodeZenProvider

        provider = OpenCodeZenProvider(model="minimax-m2.1-free")
        assert provider.model == "minimax-m2.1-free"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
