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

        assert hasattr(CodeReviewSignature, "code")
        assert hasattr(CodeReviewSignature, "review")

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
        mock_chain = MagicMock()
        mock_result = MagicMock()
        mock_result.review = "Test review"
        mock_chain.return_value = mock_result
        mock_dspy.ChainOfThought = MagicMock(return_value=mock_chain)

        from dspy_integration.modules.code_review import CodeReview

        module = CodeReview()
        result = module.forward("test code")

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
        mock_chain = MagicMock()
        mock_result = MagicMock()
        mock_result.review = "Security issues found"
        mock_chain.return_value = mock_result
        mock_dspy.ChainOfThought = MagicMock(return_value=mock_chain)

        from dspy_integration.modules.security_review import SecurityReview

        module = SecurityReview()
        result = module.forward("vulnerable code")

        assert result.review == "Security issues found"


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

        assert "Unknown scenario" in str(exc_info.value)

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
        assert hasattr(CodeReviewSignature, "code")
        assert hasattr(CodeReviewSignature, "review")

    def test_security_review_signature_structure(self):
        """Test SecurityReviewSignature has proper input/output fields."""
        from dspy_integration.modules.security_review import SecurityReviewSignature

        assert hasattr(SecurityReviewSignature, "code")
        assert hasattr(SecurityReviewSignature, "review")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
