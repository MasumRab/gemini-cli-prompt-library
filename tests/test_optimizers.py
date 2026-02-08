"""
Tests for DSPy-HELM optimizers.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestBaseOptimizer:
    """Test base optimizer functionality."""

    def test_base_optimizer_init(self):
        """Test base optimizer initialization."""
        from dspy_integration.framework.optimizers.base import BaseOptimizer

        mock_metric = MagicMock()
        optimizer = BaseOptimizer(metric=mock_metric)

        assert optimizer.metric is mock_metric
        assert optimizer.max_bootstrapped_demos == 3
        assert optimizer.max_labeled_demos == 3
        assert optimizer.num_threads == 16

    def test_base_optimizer_custom_values(self):
        """Test base optimizer with custom values."""
        from dspy_integration.framework.optimizers.base import BaseOptimizer

        mock_metric = MagicMock()
        optimizer = BaseOptimizer(
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
        from dspy_integration.framework.optimizers.base import BaseOptimizer

        mock_metric = MagicMock()
        optimizer = BaseOptimizer(metric=mock_metric)

        repr_str = repr(optimizer)
        assert "BaseOptimizer" in repr_str
        assert "max_bootstrapped=3" in repr_str
        assert "max_labeled=3" in repr_str

    def test_base_optimizer_abstract_create_teleprompter(self):
        """Test that _create_teleprompter is abstract."""
        from dspy_integration.framework.optimizers.base import BaseOptimizer

        mock_metric = MagicMock()
        optimizer = BaseOptimizer(metric=mock_metric)

        with pytest.raises(NotImplementedError):
            optimizer._create_teleprompter()


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

    @patch("dspy_integration.framework.optimizers.mipro_v2.dspy")
    def test_create_teleprompter(self, mock_dspy):
        """Test creating MIPROv2 teleprompter."""
        from dspy_integration.framework.optimizers.mipro_v2 import MIPROv2Optimizer

        mock_dspy.teleprompt.MIPROv2.return_value = MagicMock()

        mock_metric = MagicMock()
        optimizer = MIPROv2Optimizer(metric=mock_metric)

        teleprompter = optimizer._create_teleprompter()
        assert teleprompter is not None

        # Verify MIPROv2 was called with correct args
        mock_dspy.teleprompt.MIPROv2.assert_called_once()
        call_kwargs = mock_dspy.teleprompt.MIPROv2.call_args[1]
        assert call_kwargs["metric"] is mock_metric
        assert call_kwargs["max_bootstrapped_demos"] == 3


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

    @patch("dspy_integration.framework.optimizers.bootstrap.dspy")
    def test_create_teleprompter(self, mock_dspy):
        """Test creating BootstrapFewShot teleprompter."""
        from dspy_integration.framework.optimizers.bootstrap import (
            BootstrapFewShotOptimizer,
        )

        mock_dspy.teleprompt.BootstrapFewShot.return_value = MagicMock()

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

    @patch("dspy_integration.framework.optimizers.bootstrap.dspy")
    def test_create_teleprompter(self, mock_dspy):
        """Test creating teleprompter with random search."""
        from dspy_integration.framework.optimizers.bootstrap import (
            BootstrapFewShotRandomSearchOptimizer,
        )

        mock_dspy.teleprompt.BootstrapFewShotWithRandomSearch.return_value = MagicMock()

        mock_metric = MagicMock()
        optimizer = BootstrapFewShotRandomSearchOptimizer(
            metric=mock_metric,
            num_candidate_programs=10,
        )

        teleprompter = optimizer._create_teleprompter()
        assert teleprompter is not None

        call_kwargs = mock_dspy.teleprompt.BootstrapFewShotWithRandomSearch.call_args[1]
        assert call_kwargs["num_candidate_programs"] == 10


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

        optimizer_class = OptimizerRegistry.get("MIPROv2")
        assert optimizer_class is not None

    def test_get_unknown_optimizer(self):
        """Test that unknown optimizer raises error."""
        from dspy_integration.framework.optimizers import OptimizerRegistry

        with pytest.raises(ValueError) as exc_info:
            OptimizerRegistry.get("UnknownOptimizer")
        assert "Unknown optimizer" in str(exc_info.value)


class TestOptimizerCompile:
    """Test optimizer compile functionality."""

    @patch("dspy_integration.framework.optimizers.mipro_v2.dspy")
    def test_compile_requires_lm(self, mock_dspy):
        """Test that compile requires LM to be configured."""
        from dspy_integration.framework.optimizers.mipro_v2 import MIPROv2Optimizer

        mock_dspy.settings.lm = None
        mock_dspy.settings.configure = MagicMock()

        mock_metric = MagicMock()
        optimizer = MIPROv2Optimizer(metric=mock_metric)

        mock_program = MagicMock()
        mock_trainset = []
        mock_valset = []

        with pytest.raises(RuntimeError) as exc_info:
            optimizer.compile(mock_program, mock_trainset, mock_valset)

        assert "No LM configured" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
