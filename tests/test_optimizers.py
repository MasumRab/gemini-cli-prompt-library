"""
Tests for DSPy-HELM optimizers.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestBaseOptimizer:
    """Test base optimizer functionality."""

    def _get_dummy_optimizer(self):
        from dspy_integration.framework.optimizers.base import BaseOptimizer

        class DummyOptimizer(BaseOptimizer):
            def _create_teleprompter(self):
                pass

        return DummyOptimizer

    def test_base_optimizer_init(self):
        """Test base optimizer initialization."""
        DummyOptimizer = self._get_dummy_optimizer()

        mock_metric = MagicMock()
        optimizer = DummyOptimizer(metric=mock_metric)

        assert optimizer.metric is mock_metric
        assert optimizer.max_bootstrapped_demos == 3
        assert optimizer.max_labeled_demos == 3
        assert optimizer.num_threads == 16

    def test_base_optimizer_custom_values(self):
        """Test base optimizer with custom values."""
        DummyOptimizer = self._get_dummy_optimizer()

        mock_metric = MagicMock()
        optimizer = DummyOptimizer(
            metric=mock_metric,
            max_bootstrapped_demos=5,
            max_labeled_demos=4,
            num_threads=8,
        )

        assert optimizer.max_bootstrapped_demos == 5
        assert optimizer.max_labeled_demos == 4
        assert optimizer.num_threads == 8

    def test_base_optimizer_repr(self):
        """Test base optimizer string representation."""
        DummyOptimizer = self._get_dummy_optimizer()

        mock_metric = MagicMock()
        optimizer = DummyOptimizer(metric=mock_metric)

        repr_str = repr(optimizer)
        assert "DummyOptimizer" in repr_str
        assert "max_bootstrapped=3" in repr_str
        assert "max_labeled=3" in repr_str

    def test_base_optimizer_abstract_create_teleprompter(self):
        """Test that _create_teleprompter is abstract."""
        from dspy_integration.framework.optimizers.base import BaseOptimizer

        mock_metric = MagicMock()
        with pytest.raises(TypeError):
            BaseOptimizer(metric=mock_metric)


class TestMIPROv2Optimizer:
    """Test MIPROv2 optimizer."""

    def test_init(self):
        """Test MIPROv2 optimizer initialization."""
        from dspy_integration.framework.optimizers.mipro_v2 import MIPROv2Optimizer

        mock_metric = MagicMock()
        optimizer = MIPROv2Optimizer(metric=mock_metric)

        assert optimizer.metric is mock_metric
        assert optimizer.auto == "light"

    def test_init_custom_values(self):
        """Test MIPROv2 with custom values."""
        from dspy_integration.framework.optimizers.mipro_v2 import MIPROv2Optimizer

        mock_metric = MagicMock()
        optimizer = MIPROv2Optimizer(
            metric=mock_metric,
            max_bootstrapped_demos=5,
            max_labeled_demos=4,
            auto="medium",
            prompt_model="gpt-4",
            task_model="gpt-3.5-turbo",
        )

        assert optimizer.max_bootstrapped_demos == 5
        assert optimizer.max_labeled_demos == 4
        assert optimizer.auto == "medium"
        assert optimizer.prompt_model == "gpt-4"
        assert optimizer.task_model == "gpt-3.5-turbo"


class TestBootstrapFewShotOptimizer:
    """Test BootstrapFewShot optimizer."""

    def test_init(self):
        """Test BootstrapFewShot optimizer initialization."""
        from dspy_integration.framework.optimizers.bootstrap import (
            BootstrapFewShotOptimizer,
        )

        mock_metric = MagicMock()
        optimizer = BootstrapFewShotOptimizer(metric=mock_metric)

        assert optimizer.metric is mock_metric

    @patch(
        "dspy_integration.framework.optimizers.bootstrap.dspy.teleprompt.BootstrapFewShot"
    )
    def test_create_teleprompter(self, mock_bootstrap):
        """Test creating BootstrapFewShot teleprompter."""
        from dspy_integration.framework.optimizers.bootstrap import (
            BootstrapFewShotOptimizer,
        )

        mock_bootstrap.return_value = MagicMock()

        mock_metric = MagicMock()
        optimizer = BootstrapFewShotOptimizer(metric=mock_metric)

        teleprompter = optimizer._create_teleprompter()
        assert teleprompter is not None


class TestBootstrapFewShotRandomSearchOptimizer:
    """Test BootstrapFewShot with Random Search optimizer."""

    def test_init(self):
        """Test initialization."""
        from dspy_integration.framework.optimizers.bootstrap import (
            BootstrapFewShotRandomSearchOptimizer,
        )

        mock_metric = MagicMock()
        optimizer = BootstrapFewShotRandomSearchOptimizer(
            metric=mock_metric,
            num_candidate_programs=15,
        )

        assert optimizer.metric is mock_metric
        assert optimizer.num_candidate_programs == 15


class TestOptimizerRegistry:
    """Test optimizer registry."""

    def test_list_optimizers(self):
        """Test listing available optimizers."""
        from dspy_integration.framework.optimizers import OptimizerRegistry

        optimizers = OptimizerRegistry.list()
        assert "MIPROv2" in optimizers
        assert "BootstrapFewShot" in optimizers
        assert "BootstrapFewShotWithRandomSearch" in optimizers

    def test_get_optimizer(self):
        """Test retrieving an optimizer class."""
        from dspy_integration.framework.optimizers import OptimizerRegistry

        mock_metric = MagicMock()
        optimizer_class = OptimizerRegistry.create("MIPROv2", metric=mock_metric)
        assert optimizer_class is not None

    def test_get_unknown_optimizer(self):
        """Test that unknown optimizer raises error."""
        from dspy_integration.framework.optimizers import OptimizerRegistry

        mock_metric = MagicMock()
        with pytest.raises(ValueError) as exc_info:
            OptimizerRegistry.create("UnknownOptimizer", metric=mock_metric)
        assert "Unknown optimizer" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
