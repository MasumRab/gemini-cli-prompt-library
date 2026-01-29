"""
Tests for DSPy integration modules.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestCodeReviewModule:
    """Test CodeReview module."""

    def test_signature_fields(self):
        """Test that signature has correct fields."""
        from dspy_integration.modules.code_review import CodeReviewSignature

        # Check if the signature has the expected fields in model_fields
        assert "code" in CodeReviewSignature.model_fields
        assert "review" in CodeReviewSignature.model_fields

    @patch("dspy_integration.modules.code_review.dspy")
    def test_module_init(self, mock_dspy):
        """Test module initialization."""
        mock_dspy.ChainOfThought = MagicMock()

        from dspy_integration.modules.code_review import CodeReview

        module = CodeReview()

        assert hasattr(module, "review_code")
        mock_dspy.ChainOfThought.assert_called_once()

    @patch("dspy_integration.modules.code_review.dspy")
    def test_forward(self, mock_dspy):
        """Test forward pass."""
        # Create a mock result object that has a 'review' attribute
        mock_result_obj = MagicMock()
        mock_result_obj.review = "Test review"

        # Create a mock ChainOfThought instance that returns the result when called
        mock_cot_instance = MagicMock()
        mock_cot_instance.return_value = mock_result_obj  # When called with (code=code), returns mock_result_obj

        # Configure ChainOfThought to return our mock instance when called with the signature
        mock_dspy.ChainOfThought.return_value = mock_cot_instance
        # Mock settings.lm to avoid errors
        mock_dspy.settings.lm = MagicMock()

        from dspy_integration.modules.code_review import CodeReview

        module = CodeReview()
        result = module.forward("test code")

        # CodeReview.forward returns the result object directly, not result.review
        # So we should be able to access the review attribute
        assert result.review == "Test review"


class TestArchitectureModule:
    """Test Architecture module."""

    @patch("dspy_integration.modules.architecture.dspy")
    def test_module_init(self, mock_dspy):
        """Test module initialization."""
        mock_dspy.ChainOfThought = MagicMock()

        from dspy_integration.modules.architecture import Architecture

        module = Architecture()

        assert hasattr(module, "design_system")
        mock_dspy.ChainOfThought.assert_called_once()


class TestFeatureDevModule:
    """Test FeatureDev module."""

    @patch("dspy_integration.modules.feature_dev.dspy")
    def test_module_init(self, mock_dspy):
        """Test module initialization."""
        mock_dspy.ChainOfThought = MagicMock()

        from dspy_integration.modules.feature_dev import FeatureDev

        module = FeatureDev()

        assert hasattr(module, "generate_feature")
        mock_dspy.ChainOfThought.assert_called_once()


class TestUnitTestModule:
    """Test UnitTest module."""

    @patch("dspy_integration.modules.unit_test.dspy")
    def test_module_init(self, mock_dspy):
        """Test module initialization."""
        mock_dspy.ChainOfThought = MagicMock()

        from dspy_integration.modules.unit_test import UnitTest

        module = UnitTest()

        assert hasattr(module, "generate")
        mock_dspy.ChainOfThought.assert_called_once()


class TestDocumentationModule:
    """Test Documentation module."""

    @patch("dspy_integration.modules.documentation.dspy")
    def test_module_init(self, mock_dspy):
        """Test module initialization."""
        mock_dspy.ChainOfThought = MagicMock()

        from dspy_integration.modules.documentation import Documentation

        module = Documentation()

        assert hasattr(module, "generate")
        mock_dspy.ChainOfThought.assert_called_once()


class TestSecurityReviewModule:
    """Test SecurityReview module."""

    @patch("dspy_integration.modules.security_review.dspy")
    def test_module_init(self, mock_dspy):
        """Test module initialization."""
        mock_dspy.ChainOfThought = MagicMock()

        from dspy_integration.modules.security_review import SecurityReview

        module = SecurityReview()

        assert hasattr(module, "review_code")
        mock_dspy.ChainOfThought.assert_called_once()

    @patch("dspy_integration.modules.security_review.dspy")
    def test_forward(self, mock_dspy):
        """Test forward pass."""
        # Mock the ChainOfThought to return a callable that returns the result
        mock_chain_of_thought_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.review = "Security issues found"
        mock_chain_of_thought_instance.return_value = mock_result
        mock_dspy.ChainOfThought.return_value = mock_chain_of_thought_instance

        from dspy_integration.modules.security_review import SecurityReview

        module = SecurityReview()
        result = module.forward("vulnerable code")

        assert result == "Security issues found"  # The method returns result.review directly


class TestModuleRegistry:
    """Test module registry functions."""

    def test_get_module_for_scenario_security_review(self):
        """Test getting security_review module."""
        from dspy_integration.modules import get_module_for_scenario

        module = get_module_for_scenario("security_review")
        assert module is not None

    def test_get_module_for_scenario_unit_test(self):
        """Test getting unit_test module."""
        from dspy_integration.modules import get_module_for_scenario

        module = get_module_for_scenario("unit_test")
        assert module is not None

    def test_get_module_for_scenario_documentation(self):
        """Test getting documentation module."""
        from dspy_integration.modules import get_module_for_scenario

        module = get_module_for_scenario("documentation")
        assert module is not None

    def test_get_module_for_scenario_api_design(self):
        """Test getting api_design module."""
        from dspy_integration.modules import get_module_for_scenario

        module = get_module_for_scenario("api_design")
        assert module is not None

    def test_get_unknown_scenario(self):
        """Test getting unknown scenario raises error."""
        from dspy_integration.modules import get_module_for_scenario

        with pytest.raises(ValueError) as exc_info:
            get_module_for_scenario("unknown_scenario")

        # The error message changed when we updated the dynamic loader
        assert "not found" in str(exc_info.value) or "Unknown scenario" in str(exc_info.value)

    def test_get_optimizer_for_scenario(self):
        """Test getting optimizer for scenario."""
        from dspy_integration.modules import get_optimizer_for_scenario

        optimizer = get_optimizer_for_scenario("security_review")
        assert optimizer is not None


class TestModuleSignatureStructure:
    """Test that modules have proper DSPy signature structure."""

    def test_code_review_signature_structure(self):
        """Test CodeReviewSignature has proper input/output fields."""
        from dspy_integration.modules.code_review import CodeReviewSignature

        # Verify it's a proper signature class
        assert "code" in CodeReviewSignature.model_fields
        assert "review" in CodeReviewSignature.model_fields

    def test_security_review_signature_structure(self):
        """Test SecurityReviewSignature has proper input/output fields."""
        from dspy_integration.modules.security_review import SecurityReviewSignature

        assert "code" in SecurityReviewSignature.model_fields
        assert "review" in SecurityReviewSignature.model_fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
