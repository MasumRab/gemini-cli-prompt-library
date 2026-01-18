"""
Error handling and edge case tests for DSPy-HELM.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestScenarioEdgeCases:
    """Test edge cases for scenarios."""

    def test_empty_data_fallback(self):
        """Test scenario handles missing JSONL file."""
        from dspy_helm.scenarios.security_review import SecurityReviewScenario
        from pathlib import Path

        # Create scenario with non-existent data path
        scenario = SecurityReviewScenario()

        # Mock the data path to not exist
        with patch.object(Path, "exists", return_value=False):
            # Should still work because of fallback inline data
            data = scenario._load_raw_data()
            assert len(data) > 0

    def test_scenario_with_custom_split(self):
        """Test scenario with custom train/val split."""
        from dspy_helm.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("security_review")(test_size=0.3, seed=123)
        trainset, valset = scenario.load_data()

        expected_train_ratio = 0.7
        expected_val_ratio = 0.3

        assert len(trainset) >= len(valset) * expected_train_ratio / expected_val_ratio

    def test_scenario_repr(self):
        """Test scenario string representation."""
        from dspy_helm.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("security_review")(test_size=0.2, seed=42)
        repr_str = repr(scenario)

        assert "SecurityReviewScenario" in repr_str
        assert "test_size=0.2" in repr_str
        assert "seed=42" in repr_str


class TestProviderEdgeCases:
    """Test edge cases for providers."""

    def test_provider_response_with_no_tokens(self):
        """Test provider response when no token info available."""
        from dspy_helm.providers.base import ProviderResponse

        response = ProviderResponse(
            success=True,
            content="Test response",
            provider="Test",
            model="test-model",
            tokens_used=0,
        )

        assert response.success is True
        assert response.tokens_used == 0

    def test_rate_limit_config_defaults(self):
        """Test rate limit config default values."""
        from dspy_helm.providers.base import RateLimitConfig

        config = RateLimitConfig()
        assert config.enabled is True
        assert config.max_retries == 3
        assert config.backoff_factor == 1.0
        assert config.max_backoff == 60.0

    def test_provider_chain_with_single_provider(self):
        """Test provider chain with single provider."""
        from dspy_helm.providers.base import (
            BaseProvider,
            ProviderChain,
            ProviderResponse,
        )

        class TestProvider(BaseProvider):
            def _execute_cli(self, prompt, **kwargs):
                return ProviderResponse(
                    success=True,
                    content="Response",
                    provider=self.name,
                    model=self.model,
                )

        provider = TestProvider(
            name="Single", command="t", subcommand="t", model="test"
        )
        chain = ProviderChain([provider])

        response = chain.call("Test prompt")

        assert response.success is True
        assert response.provider == "Single"


class TestRegistryEdgeCases:
    """Test edge cases for registries."""

    def test_unknown_scenario_error_message(self):
        """Test that unknown scenario gives helpful error message."""
        from dspy_helm.scenarios import ScenarioRegistry

        with pytest.raises(ValueError) as exc_info:
            ScenarioRegistry.get("totally_unknown_scenario")

        error_msg = str(exc_info.value)
        assert "Unknown scenario" in error_msg
        # Should list available scenarios
        assert "Available scenarios" in error_msg

    def test_unknown_optimizer_error_message(self):
        """Test that unknown optimizer gives helpful error message."""
        from dspy_helm.optimizers import OptimizerRegistry

        with pytest.raises(ValueError) as exc_info:
            OptimizerRegistry.create("UnknownOptimizer123")

        error_msg = str(exc_info.value)
        assert "Unknown optimizer" in error_msg

    def test_unknown_provider_error_message(self):
        """Test that unknown provider gives helpful error message."""
        from dspy_helm.providers import get_provider_by_name

        with pytest.raises(ValueError) as exc_info:
            get_provider_by_name("nonexistent_provider")

        error_msg = str(exc_info.value)
        assert "Unknown provider" in error_msg
        assert "Available" in error_msg


class TestPromptEdgeCases:
    """Test edge cases for prompts."""

    def test_prompt_with_no_variables(self):
        """Test prompt with no variables."""
        from dspy_helm.prompts import TOMLPrompt
        from pathlib import Path

        prompt = TOMLPrompt(
            name="static",
            path=Path("/test.toml"),
            content={"prompt": "This is a static prompt with no variables"},
        )

        assert prompt.variables == []
        rendered = prompt.render()
        assert rendered == "This is a static prompt with no variables"

    def test_prompt_with_empty_content(self):
        """Test prompt with empty content."""
        from dspy_helm.prompts import TOMLPrompt
        from pathlib import Path

        prompt = TOMLPrompt(
            name="empty",
            path=Path("/test.toml"),
            content={},
        )

        assert prompt.prompt_template == ""
        assert prompt.variables == []

    def test_prompt_registry_clear(self):
        """Test clearing prompt registry."""
        from dspy_helm.prompts import PromptRegistry, TOMLPrompt
        from pathlib import Path

        # Add some prompts
        PromptRegistry._prompts["test/prompt"] = TOMLPrompt(
            "prompt", Path("/test.toml"), {"prompt": "{{x}}"}
        )

        # Clear
        PromptRegistry.clear()

        assert len(PromptRegistry._prompts) == 0

    def test_get_nonexistent_prompt(self):
        """Test getting nonexistent prompt returns None."""
        from dspy_helm.prompts import PromptRegistry

        result = PromptRegistry.get("nonexistent/prompt")
        assert result is None

    def test_get_dspy_module_for_unmapped_prompt(self):
        """Test getting DSPy module for unmapped prompt returns None."""
        from dspy_helm.prompts import PromptRegistry

        result = PromptRegistry.get_dspy_module("unmapped/prompt")
        assert result is None


class TestCLIEdgeCases:
    """Test CLI edge cases."""

    def test_cli_without_args_shows_help(self, capsys):
        """Test CLI without arguments shows help."""
        from dspy_helm.cli import main
        import sys

        with patch.object(sys, "argv", ["dspy_helm.cli"]):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        # Should show usage info
        assert "usage" in captured.out.lower() or "--help" in captured.out

    def test_cli_with_invalid_scenario(self):
        """Test CLI with invalid scenario name."""
        from dspy_helm.cli import main
        import sys

        with patch.object(
            sys, "argv", ["dspy_helm.cli", "--scenario", "invalid_scenario"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Should exit with error
            assert exc_info.value.code != 0

    def test_cli_with_invalid_optimizer(self):
        """Test CLI with invalid optimizer name."""
        from dspy_helm.cli import main
        import sys

        with patch.object(
            sys,
            "argv",
            [
                "dspy_helm.cli",
                "--scenario",
                "security_review",
                "--optimizer",
                "InvalidOptimizer",
            ],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Should exit with error
            assert exc_info.value.code != 0


class TestEvaluatorEdgeCases:
    """Test evaluator edge cases."""

    def test_evaluator_with_none_program(self):
        """Test evaluator handles None program gracefully."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        with pytest.raises(ValueError) as exc_info:
            evaluator.evaluate(None, [])

        assert "Program cannot be None" in str(exc_info.value)

    def test_evaluator_with_custom_threads(self):
        """Test evaluator with custom thread count."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric, num_threads=4)

        assert evaluator.num_threads == 4


class TestDataLoadingEdgeCases:
    """Test edge cases for data loading."""

    def test_scenario_with_insufficient_data(self):
        """Test scenario handles insufficient data gracefully."""
        from dspy_helm.scenarios.base import BaseScenario, ScenarioRegistry
        from typing import List, Dict, Any

        # Create a minimal scenario with few examples
        @ScenarioRegistry.register("minimal_test")
        class MinimalScenario(BaseScenario):
            INPUT_FIELDS = ["input"]
            OUTPUT_FIELDS = ["output"]

            def _load_raw_data(self) -> List[Dict[str, Any]]:
                return [{"input": "a", "output": "b"}]

            def make_prompt(self, row):
                return row["input"]

            def metric(self, example, pred, trace=None):
                return 1.0

        scenario = MinimalScenario()

        # Should raise ValueError for insufficient data
        with pytest.raises(ValueError) as exc_info:
            scenario.load_data()

        assert "Insufficient data" in str(exc_info.value)


class TestMetricEdgeCases:
    """Test edge cases for metrics."""

    def test_metric_with_none_trace(self):
        """Test metric handles None trace."""
        from dspy_helm.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("security_review")()

        class MockExample:
            expected = "SQL injection"

        class MockPred:
            review = "SQL injection detected"

        # Should work with trace=None (default)
        score = scenario.metric(MockExample(), MockPred(), trace=None)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_metric_with_empty_prediction(self):
        """Test metric handles empty prediction."""
        from dspy_helm.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("security_review")()

        class MockExample:
            expected = "SQL injection"

        class MockPred:
            review = ""

        score = scenario.metric(MockExample(), MockPred())
        assert isinstance(score, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
