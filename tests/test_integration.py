"""
Integration tests for DSPy-HELM.
These tests verify end-to-end functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
import json


class TestScenarioDataLoading:
    """Integration tests for scenario data loading."""

    def test_security_review_data_format(self):
        """Test security review data has correct format."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("security_review")()
        trainset, valset = scenario.load_data()

        assert len(trainset) > 0
        assert len(valset) > 0

        # Check data structure
        for example in trainset:
            assert hasattr(example, "code")
            assert hasattr(example, "expected")
            assert isinstance(example.code, str)
            assert isinstance(example.expected, str)

    def test_unit_test_data_format(self):
        """Test unit test data has correct format."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("unit_test")()
        trainset, valset = scenario.load_data()

        assert len(trainset) > 0
        assert len(valset) > 0

        for example in trainset:
            assert hasattr(example, "function")
            assert hasattr(example, "tests")
            assert isinstance(example.function, str)
            assert isinstance(example.tests, str)

    def test_documentation_data_format(self):
        """Test documentation data has correct format."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("documentation")()
        trainset, valset = scenario.load_data()

        assert len(trainset) > 0
        assert len(valset) > 0

        for example in trainset:
            assert hasattr(example, "project")
            assert hasattr(example, "readme")
            assert isinstance(example.project, str)
            assert isinstance(example.readme, str)

    def test_api_design_data_format(self):
        """Test API design data has correct format."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("api_design")()
        trainset, valset = scenario.load_data()

        assert len(trainset) > 0
        assert len(valset) > 0

        for example in trainset:
            assert hasattr(example, "requirements")
            assert hasattr(example, "design")
            assert isinstance(example.requirements, str)
            assert isinstance(example.design, str)


class TestPromptToScenarioMapping:
    """Test mapping between TOML prompts and scenarios."""

    def test_default_mappings_exist(self):
        """Test that default mappings are defined."""
        from dspy_integration.prompts import DEFAULT_MAPPINGS

        assert len(DEFAULT_MAPPINGS) > 0

    def test_mapping_to_registered_scenarios(self):
        """Test that all mapped scenarios are registered."""
        from dspy_integration.prompts import DEFAULT_MAPPINGS
        from dspy_integration.scenarios import ScenarioRegistry

        for toml_name, scenario_name in DEFAULT_MAPPINGS.items():
            assert (
                scenario_name in ScenarioRegistry.list()
            ), f"Scenario '{scenario_name}' from mapping '{toml_name}' is not registered"

    def test_prompt_registry_has_mappings(self):
        """Test that prompt registry has the mappings."""
        from dspy_integration.prompts import (
            PromptRegistry,
            DEFAULT_MAPPINGS,
            initialize_prompt_registry,
        )

        # Initialize the registry with default mappings
        initialize_prompt_registry()

        for toml_name, scenario_name in DEFAULT_MAPPINGS.items():
            registered = PromptRegistry.get_dspy_module(toml_name)
            assert (
                registered == scenario_name
            ), f"Mapping for '{toml_name}' not found in registry"


class TestPromptRendering:
    """Test prompt rendering functionality."""

    def test_security_review_prompt_contains_code(self):
        """Test that security review prompt contains code placeholder."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("security_review")()
        prompt = scenario.make_prompt(
            {"code": "SELECT * FROM users", "expected": "SQL injection"}
        )

        assert "SELECT * FROM users" in prompt
        assert "Security Code Review" in prompt

    def test_unit_test_prompt_contains_function(self):
        """Test that unit test prompt contains function placeholder."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("unit_test")()
        prompt = scenario.make_prompt(
            {"function": "add(a, b)", "tests": "Basic addition"}
        )

        assert "add(a, b)" in prompt
        assert "Unit Test Generation" in prompt

    def test_documentation_prompt_contains_project(self):
        """Test that documentation prompt contains project placeholder."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("documentation")()
        prompt = scenario.make_prompt(
            {"project": "A CLI tool", "readme": "Installation guide"}
        )

        assert "A CLI tool" in prompt
        assert "README Generation" in prompt

    def test_api_design_prompt_contains_requirements(self):
        """Test that API design prompt contains requirements placeholder."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("api_design")()
        prompt = scenario.make_prompt(
            {"requirements": "User management", "design": "POST /users"}
        )

        assert "User management" in prompt
        assert "RESTful API Design" in prompt


class TestMetricEvaluation:
    """Test metric evaluation logic."""

    def test_security_review_metric_high_score(self):
        """Test security review metric with matching prediction."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("security_review")()

        class MockExample:
            expected = "SQL injection"

        class MockPred:
            review = "This code has SQL injection vulnerability in the query"

        score = scenario.metric(MockExample(), MockPred())
        assert score > 0.5

    def test_security_review_metric_low_score(self):
        """Test security review metric with non-matching prediction."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("security_review")()

        class MockExample:
            expected = "SQL injection"

        class MockPred:
            review = "This code looks fine and secure"

        score = scenario.metric(MockExample(), MockPred())
        assert score < 0.5

    def test_unit_test_metric(self):
        """Test unit test metric."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenario = ScenarioRegistry.get("unit_test")()

        class MockExample:
            tests = "basic, edge, negative cases"

        class MockPred:
            tests = "Testing basic, edge, and negative cases"

        score = scenario.metric(MockExample(), MockPred())
        assert score == 1.0


class TestProviderFailover:
    """Test provider failover chain."""

    def test_provider_chain_order(self):
        """Test that provider chain has correct order."""
        from dspy_integration.providers import create_provider_chain

        chain = create_provider_chain()
        providers = [p.name for p in chain.providers]

        # Groq should be first (primary free provider)
        assert "Groq" in providers[0]

    def test_provider_chain_add(self):
        """Test adding provider to chain."""
        from dspy_integration.providers.base import (
            ProviderChain,
            BaseProvider,
            ProviderResponse,
        )

        class TestProvider(BaseProvider):
            def _execute_cli(self, prompt, **kwargs):
                return ProviderResponse(
                    success=True, content="ok", provider=self.name, model="test"
                )

        provider1 = TestProvider(name="P1", command="t", subcommand="t", model="test")
        provider2 = TestProvider(name="P2", command="t", subcommand="t", model="test")

        chain = ProviderChain([provider1])
        chain.add_provider(provider2)

        assert len(chain.providers) == 2
        assert chain.providers[0].name == "P1"
        assert chain.providers[1].name == "P2"


class TestScenarioPromptVariability:
    """Test that prompts have variability."""

    def test_all_scenarios_have_different_prompts(self):
        """Test that each scenario generates different prompts."""
        from dspy_integration.scenarios import ScenarioRegistry

        scenarios = ["security_review", "unit_test", "documentation", "api_design"]
        prompts = {}

        for name in scenarios:
            scenario = ScenarioRegistry.get(name)()
            sample_data = scenario._load_raw_data()[0]
            prompt = scenario.make_prompt(sample_data)
            prompts[name] = prompt

        # All prompts should be different
        prompt_set = set(prompts.values())
        assert len(prompt_set) == len(
            prompts
        ), "Some scenarios generate identical prompts"


class TestJSONLDataConsistency:
    """Test that JSONL data is consistent across scenarios."""

    def test_security_review_jsonl_exists(self):
        """Test that security_review.jsonl exists and is valid JSON."""
        from pathlib import Path

        path = (
            Path(__file__).parent.parent
            / "dspy_helm"
            / "data"
            / "security_review.jsonl"
        )
        assert path.exists()

        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    assert "code" in data or "vars" in data

    def test_all_jsonl_files_have_similar_count(self):
        """Test that all JSONL files have similar number of entries."""
        from pathlib import Path

        data_dir = Path(__file__).parent.parent / "dspy_helm" / "data"
        counts = {}

        for jsonl_file in data_dir.glob("*.jsonl"):
            with open(jsonl_file, "r") as f:
                count = sum(1 for line in f if line.strip())
                counts[jsonl_file.stem] = count

        # All counts should be similar (within factor of 2)
        min_count = min(counts.values())
        max_count = max(counts.values())

        assert max_count <= min_count * 2, f"JSONL file counts vary too much: {counts}"


class TestCLIScenarioSelection:
    """Test CLI scenario selection."""

    def test_cli_with_valid_scenario(self):
        """Test CLI with valid scenario name."""
        from dspy_integration.cli import main
        import sys

        with patch.object(
            sys, "argv", ["dspy_helm.cli", "--scenario", "security_review"]
        ):
            with patch("dspy_helm.cli.run_evaluation") as mock_run:
                mock_run.return_value = {"score": 0.9}
                try:
                    main()
                except SystemExit:
                    pass

                mock_run.assert_called_once()
                assert mock_run.call_args[1]["scenario_name"] == "security_review"

    def test_cli_with_optimizer(self):
        """Test CLI with optimizer selection."""
        from dspy_integration.cli import main
        import sys

        with patch.object(
            sys,
            "argv",
            ["dspy_helm.cli", "--scenario", "unit_test", "--optimizer", "MIPROv2"],
        ):
            with patch("dspy_helm.cli.run_evaluation") as mock_run:
                mock_run.return_value = {"score": 0.8}
                try:
                    main()
                except SystemExit:
                    pass

                mock_run.assert_called_once()
                assert mock_run.call_args[1]["optimizer_name"] == "MIPROv2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
