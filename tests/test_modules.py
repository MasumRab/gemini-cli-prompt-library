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

        assert "code" in CodeReviewSignature.model_fields
        assert "review" in CodeReviewSignature.model_fields

    def test_module_init(self):
        """Test module initialization."""
        from dspy_integration.modules.code_review import CodeReview

        module = CodeReview()

        assert hasattr(module, "review_code")

    def test_forward(self):
        """Test forward pass."""
        from dspy_integration.modules.code_review import CodeReview

        with patch.object(CodeReview, "__init__", lambda self, model=None: None):
            module = CodeReview()
            mock_chain = MagicMock()
            mock_result = MagicMock()
            mock_result.review = "Test review"
            mock_chain.return_value = mock_result
            module.review_code = mock_chain

            result = module.forward("test code")

            assert result.review == "Test review"


class TestArchitectureModule:
    """Test Architecture module."""

    def test_module_init(self):
        """Test module initialization."""
        from dspy_integration.modules.architecture import Architecture

        module = Architecture()

        assert hasattr(module, "design_system")


class TestFeatureDevModule:
    """Test FeatureDev module."""

    def test_module_init(self):
        """Test module initialization."""
        from dspy_integration.modules.feature_dev import FeatureDev

        module = FeatureDev()

        assert hasattr(module, "generate_feature")


class TestUnitTestModule:
    """Test UnitTest module."""

    def test_module_init(self):
        """Test module initialization."""
        from dspy_integration.modules.unit_test import UnitTest

        module = UnitTest()

        assert hasattr(module, "generate")


class TestDocumentationModule:
    """Test Documentation module."""

    def test_module_init(self):
        """Test module initialization."""
        from dspy_integration.modules.documentation import Documentation

        module = Documentation()

        assert hasattr(module, "generate")


class TestSecurityReviewModule:
    """Test SecurityReview module."""

    def test_module_init(self):
        """Test module initialization."""
        from dspy_integration.modules.security_review import SecurityReview

        module = SecurityReview()

        assert hasattr(module, "review_code")

    def test_forward(self):
        """Test forward pass."""
        from dspy_integration.modules.security_review import SecurityReview

        with patch.object(SecurityReview, "__init__", lambda self, model=None: None):
            module = SecurityReview()
            mock_chain = MagicMock()
            mock_result = MagicMock()
            mock_result.review = "Security issues found"
            mock_chain.return_value = mock_result
            module.review_code = mock_chain

            result = module.forward("vulnerable code")

            assert result == "Security issues found"


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

    def test_get_module_for_scenario_architecture(self):
        """Test getting architecture module."""
        from dspy_integration.modules import get_module_for_scenario

        module = get_module_for_scenario("architecture")
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
        assert "code" in CodeReviewSignature.model_fields
        assert "review" in CodeReviewSignature.model_fields

    def test_security_review_signature_structure(self):
        """Test SecurityReviewSignature has proper input/output fields."""
        from dspy_integration.modules.security_review import SecurityReviewSignature

        assert "code" in SecurityReviewSignature.model_fields
        assert "review" in SecurityReviewSignature.model_fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
