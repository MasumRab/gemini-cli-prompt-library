"""
Tests for DSPy-HELM scenarios.
"""

import pytest
from dspy_helm.scenarios import ScenarioRegistry


class TestScenarioRegistry:
    """Test the scenario registry."""

    def test_list_scenarios(self):
        """Test that all scenarios are registered."""
        scenarios = ScenarioRegistry.list()
        assert "security_review" in scenarios
        assert "unit_test" in scenarios
        assert "documentation" in scenarios
        assert "api_design" in scenarios

    def test_get_scenario_class(self):
        """Test retrieving scenario classes."""
        for name in ScenarioRegistry.list():
            scenario_class = ScenarioRegistry.get(name)
            assert scenario_class is not None
            assert hasattr(scenario_class, "_load_raw_data")
            assert hasattr(scenario_class, "make_prompt")
            assert hasattr(scenario_class, "metric")

    def test_unknown_scenario_raises_error(self):
        """Test that unknown scenario raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ScenarioRegistry.get("unknown_scenario")
        assert "Unknown scenario" in str(exc_info.value)


class TestSecurityReviewScenario:
    """Test security review scenario."""

    def test_load_data(self):
        """Test loading security review data."""
        scenario = ScenarioRegistry.get("security_review")()
        trainset, valset = scenario.load_data()

        assert len(trainset) > 0
        assert len(valset) > 0
        assert len(trainset) > len(valset)

    def test_data_fields(self):
        """Test that data has expected fields."""
        scenario = ScenarioRegistry.get("security_review")()
        trainset, _ = scenario.load_data()

        assert len(trainset) > 0
        example = trainset[0]
        assert hasattr(example, "code")
        assert hasattr(example, "expected")

    def test_make_prompt(self):
        """Test prompt generation."""
        scenario = ScenarioRegistry.get("security_review")()
        row = {"code": "eval(userInput);", "expected": "Dangerous eval"}
        prompt = scenario.make_prompt(row)

        assert "eval(userInput)" in prompt
        assert "Security Code Review" in prompt

    def test_metric_detection(self):
        """Test metric function detects vulnerabilities."""
        scenario = ScenarioRegistry.get("security_review")()

        # Create mock example and prediction
        class MockExample:
            expected = "SQL injection"

        class MockPrediction:
            review = "This code has a SQL injection vulnerability in the query string construction."

        score = scenario.metric(MockExample(), MockPrediction())
        assert score > 0

    def test_metric_no_match(self):
        """Test metric returns low score when no match."""
        scenario = ScenarioRegistry.get("security_review")()

        class MockExample:
            expected = "SQL injection"

        class MockPrediction:
            review = "This code looks perfectly fine."

        score = scenario.metric(MockExample(), MockPrediction())
        assert score < 1.0


class TestUnitTestScenario:
    """Test unit test scenario."""

    def test_load_data(self):
        """Test loading unit test data."""
        scenario = ScenarioRegistry.get("unit_test")()
        trainset, valset = scenario.load_data()

        assert len(trainset) > 0
        assert len(valset) > 0

    def test_data_fields(self):
        """Test that data has expected fields."""
        scenario = ScenarioRegistry.get("unit_test")()
        trainset, _ = scenario.load_data()

        assert len(trainset) > 0
        example = trainset[0]
        assert hasattr(example, "function")
        assert hasattr(example, "tests")

    def test_make_prompt(self):
        """Test prompt generation."""
        scenario = ScenarioRegistry.get("unit_test")()
        row = {"function": "add(a, b) { return a + b; }", "tests": "Basic addition"}
        prompt = scenario.make_prompt(row)

        assert "add(a, b)" in prompt
        assert "Unit Test Generation" in prompt


class TestDocumentationScenario:
    """Test documentation scenario."""

    def test_load_data(self):
        """Test loading documentation data."""
        scenario = ScenarioRegistry.get("documentation")()
        trainset, valset = scenario.load_data()

        assert len(trainset) > 0
        assert len(valset) > 0

    def test_data_fields(self):
        """Test that data has expected fields."""
        scenario = ScenarioRegistry.get("documentation")()
        trainset, _ = scenario.load_data()

        assert len(trainset) > 0
        example = trainset[0]
        assert hasattr(example, "project")
        assert hasattr(example, "readme")

    def test_make_prompt(self):
        """Test prompt generation."""
        scenario = ScenarioRegistry.get("documentation")()
        row = {
            "project": "A CLI tool for file processing",
            "readme": "installation, usage",
        }
        prompt = scenario.make_prompt(row)

        assert "CLI tool for file processing" in prompt
        assert "README Generation" in prompt


class TestAPIDesignScenario:
    """Test API design scenario."""

    def test_load_data(self):
        """Test loading API design data."""
        scenario = ScenarioRegistry.get("api_design")()
        trainset, valset = scenario.load_data()

        assert len(trainset) > 0
        assert len(valset) > 0

    def test_data_fields(self):
        """Test that data has expected fields."""
        scenario = ScenarioRegistry.get("api_design")()
        trainset, _ = scenario.load_data()

        assert len(trainset) > 0
        example = trainset[0]
        assert hasattr(example, "requirements")
        assert hasattr(example, "design")

    def test_make_prompt(self):
        """Test prompt generation."""
        scenario = ScenarioRegistry.get("api_design")()
        row = {"requirements": "User management with auth", "design": "POST /users"}
        prompt = scenario.make_prompt(row)

        assert "User management with auth" in prompt
        assert "RESTful API Design" in prompt
