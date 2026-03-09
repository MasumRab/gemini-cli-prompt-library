"""
Real integration tests for DSPy-HELM.

These tests make actual API calls to LLM providers.
They require API keys to be available and will skip if keys aren't found.

API Keys are loaded from:
- ~/.config/terminal-jarvis/credentials.toml (Google Gemini)

OpenCode Zen: No API key needed (all models free)

Run with: pytest tests/test_real_integration.py -v
"""

import pytest
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key from config."""
    config_path = Path.home() / ".config" / "terminal-jarvis" / "credentials.toml"
    if config_path.exists():
        content = config_path.read_text()
        if "GEMINI_API_KEY" in content:
            for line in content.split("\n"):
                if "GEMINI_API_KEY" in line:
                    return line.split("=")[1].strip().strip('"')
    return None


def check_api_keys():
    """Check which API keys are available."""
    gemini = get_gemini_api_key()
    return {
        "gemini": gemini is not None,
        "opencode_zen": True,  # No API key needed
    }


# Global check for skip decorators
AVAILABLE_PROVIDERS = check_api_keys()

require_gemini = pytest.mark.skipif(
    not AVAILABLE_PROVIDERS["gemini"], reason="Gemini API key not available"
)

require_any_provider = pytest.mark.skipif(
    not any(AVAILABLE_PROVIDERS.values()), reason="No API providers available"
)


class TestOpenCodeZenProvider:
    """Real integration tests for OpenCode Zen provider (no API key needed, all models free)."""

    @require_any_provider
    def test_opencode_zen_basic_completion(self):
        """Test basic completion with OpenCode Zen grok-code (free)."""
        from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

        provider = OpenCodeZenProvider(model="grok-code")

        response = provider.call("Say 'Hello, World!' in exactly 5 words.")

        assert response.success is True
        assert len(response.content) > 0
        assert response.provider == "OpenCode Zen (Grok Code Fast)"
        assert response.model == "grok-code"
        assert response.latency_seconds > 0

    @require_any_provider
    def test_opencode_zen_security_review(self):
        """Test security review with OpenCode Zen (free model)."""
        from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

        provider = OpenCodeZenProvider(model="grok-code")

        code = "SELECT * FROM users WHERE name = 'user_input'"
        prompt = f"Identify the security vulnerability in this code: {code}"

        response = provider.call(prompt)

        assert response.success is True
        content_lower = response.content.lower()
        assert "sql" in content_lower or "injection" in content_lower

    @require_any_provider
    def test_opencode_zen_with_different_free_models(self):
        """Test OpenCode Zen with different free models."""
        from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

        free_models = ["grok-code", "minimax-m2.1-free", "glm-4.7-free"]

        for model in free_models:
            provider = OpenCodeZenProvider(model=model)
            response = provider.call("What is 2+2?")

            assert response.success is True, f"Model {model} failed"
            assert response.model == model

    @require_any_provider
    def test_opencode_zen_rate_limit_config(self):
        """Test provider with rate limiting config."""
        from dspy_helm.providers.opencode_zen import OpenCodeZenProvider
        from dspy_helm.providers.base import RateLimitConfig

        config = RateLimitConfig(enabled=True, max_retries=2, backoff_factor=0.5)
        provider = OpenCodeZenProvider(model="grok-code", rate_limit=config)

        response = provider.call("What is 2+2?")

        assert response.success is True
        assert response.rate_limited is False


@require_gemini
class TestGoogleGeminiProvider:
    """Real integration tests for Google Gemini provider."""

    def test_gemini_basic_completion(self):
        """Test basic completion with Gemini 1.5 Flash (free tier)."""
        from dspy_helm.providers.gemini import GeminiProvider

        api_key = get_gemini_api_key()
        # Gemini provider uses subprocess to call gemini CLI
        provider = GeminiProvider(model="gemini-1.5-flash")

        # Check if gemini CLI is available
        import subprocess

        result = subprocess.run(["which", "gemini"], capture_output=True, text=True)

        if result.returncode != 0:
            pytest.skip("Gemini CLI not installed")

        response = provider.call("Say 'Hello from Gemini!' in exactly 6 words.")

        assert response.success is True
        assert len(response.content) > 0


class TestProviderChainIntegration:
    """Integration tests for provider failover chain."""

    @require_any_provider
    def test_provider_chain_single_provider(self):
        """Test provider chain with OpenCode Zen (free)."""
        from dspy_helm.providers import create_provider_chain

        chain = create_provider_chain()

        response = chain.call("What is the capital of France?")

        assert response.success is True
        assert "Paris" in response.content or "paris" in response.content.lower()

    @require_any_provider
    def test_provider_chain_response_time(self):
        """Test that provider chain returns reasonable response times."""
        from dspy_helm.providers import create_provider_chain

        chain = create_provider_chain()

        import time

        start = time.time()
        response = chain.call("Calculate 15 + 27.")
        elapsed = time.time() - start

        assert response.success is True
        assert "42" in response.content
        assert elapsed < 120, f"Response took {elapsed}s, expected < 120s"


class TestScenarioIntegration:
    """Integration tests for scenarios with real API calls (free providers only)."""

    @require_any_provider
    def test_security_review_scenario_full(self):
        """Test security review scenario with real model call."""
        from dspy_helm.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("security_review")()
        trainset, valset = scenario.load_data()

        # Use first example from validation set
        if len(valset) > 0:
            example = valset[0]
            example_dict = {"code": example.code, "expected": example.expected}
            prompt = scenario.make_prompt(example_dict)

            # Get response from free provider
            from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

            provider = OpenCodeZenProvider(model="grok-code")

            response = provider.call(prompt)

            assert response.success is True
            assert len(response.content) > 50

    @require_any_provider
    def test_unit_test_scenario_full(self):
        """Test unit test scenario with real model call."""
        from dspy_helm.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("unit_test")()
        trainset, valset = scenario.load_data()

        if len(valset) > 0:
            example = valset[0]
            example_dict = {"function": example.function, "tests": example.tests}
            prompt = scenario.make_prompt(example_dict)

            from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

            provider = OpenCodeZenProvider(model="grok-code")

            response = provider.call(prompt)

            assert response.success is True
            assert (
                "test" in response.content.lower()
                or "assert" in response.content.lower()
            )

    @require_any_provider
    def test_documentation_scenario_full(self):
        """Test documentation scenario with real model call."""
        from dspy_helm.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("documentation")()
        trainset, valset = scenario.load_data()

        if len(valset) > 0:
            example = valset[0]
            example_dict = {"project": example.project, "readme": example.readme}
            prompt = scenario.make_prompt(example_dict)

            from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

            provider = OpenCodeZenProvider(model="grok-code")

            response = provider.call(prompt)

            assert response.success is True

    @require_any_provider
    def test_api_design_scenario_full(self):
        """Test API design scenario with real model call."""
        from dspy_helm.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("api_design")()
        trainset, valset = scenario.load_data()

        if len(valset) > 0:
            example = valset[0]
            example_dict = {
                "requirements": example.requirements,
                "design": example.design,
            }
            prompt = scenario.make_prompt(example_dict)

            from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

            provider = OpenCodeZenProvider(model="grok-code")

            response = provider.call(prompt)

            assert response.success is True


class TestMetricIntegration:
    """Integration tests for metrics with real predictions."""

    @require_any_provider
    def test_security_review_metric_real(self):
        """Test security review metric with real prediction."""
        from dspy_helm.scenarios import ScenarioRegistry
        from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

        scenario = ScenarioRegistry.get("security_review")()
        example_data = scenario._load_raw_data()[0]

        prompt = scenario.make_prompt(example_data)
        provider = OpenCodeZenProvider(model="grok-code")
        response = provider.call(prompt)

        # Create a prediction with the real response
        class MockPred:
            def __init__(self, review):
                self.review = review

        pred = MockPred(response.content)
        score = scenario.metric(example_data, pred)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestCLIFullIntegration:
    """Integration tests for CLI."""

    @require_any_provider
    def test_cli_list_scenarios(self):
        """Test CLI scenario listing."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "dspy_helm.cli", "--list-scenarios"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        assert "security_review" in result.stdout
        assert "unit_test" in result.stdout


class TestPerformanceIntegration:
    """Performance tests with free providers."""

    @require_any_provider
    def test_response_time_under_60s(self):
        """Test that responses complete within 60 seconds."""
        from dspy_helm.providers.opencode_zen import OpenCodeZenProvider
        import time

        provider = OpenCodeZenProvider(model="grok-code")

        start = time.time()
        response = provider.call("What is 1+1?")
        elapsed = time.time() - start

        assert response.success is True
        assert elapsed < 60, f"Response took {elapsed}s, expected < 60s"

    @require_any_provider
    def test_multiple_sequential_requests(self):
        """Test multiple sequential requests."""
        from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

        provider = OpenCodeZenProvider(model="grok-code")

        results = []
        for i in range(3):
            response = provider.call(f"What is {i} + {i}?")
            results.append(response)

        assert all(r.success for r in results)
        assert len(results) == 3


class TestFreeProviderVerification:
    """Verify all providers are actually free."""

    def test_opencode_zen_no_api_key_required(self):
        """Verify OpenCode Zen doesn't require API key."""
        from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

        provider = OpenCodeZenProvider(model="grok-code")
        assert provider.api_key == "not-required"  # Free models don't need key

    def test_opencode_zen_free_models_listed(self):
        """Verify OpenCode Zen free models are documented."""
        from dspy_helm.providers.opencode_zen import OpenCodeZenProvider

        provider = OpenCodeZenProvider()
        assert "grok-code" in provider.model  # Primary free model


# Run tests
if __name__ == "__main__":
    print("Available free providers for integration tests:")
    for name, available in AVAILABLE_PROVIDERS.items():
        status = "✓ Available" if available else "✗ Not available"
        print(f"  {name}: {status}")
    print("\nAll tests use FREE providers - no cost!")
    pytest.main([__file__, "-v", "--tb=short"])
