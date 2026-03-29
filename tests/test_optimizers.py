"""
Tests for DSPy-HELM optimizers.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from unittest import skipUnless


class TestBaseOptimizer:
    """Test base optimizer functionality."""

    def test_base_optimizer_abstract_class(self):
        """Test that BaseOptimizer is abstract and cannot be instantiated directly."""
        from dspy_integration.framework.optimizers.base import BaseOptimizer
        from abc import ABC

        # BaseOptimizer should be an abstract class
        assert issubclass(BaseOptimizer, ABC), "BaseOptimizer should be abstract"
        
        # Attempting to instantiate should raise TypeError
        mock_metric = MagicMock()
        with pytest.raises(TypeError):
            BaseOptimizer(metric=mock_metric)

    def test_base_optimizer_methods_abstract(self):
        """Test that BaseOptimizer has abstract methods."""
        from dspy_integration.framework.optimizers.base import BaseOptimizer

        # The class should define abstract methods
        import inspect
        abstract_methods = [name for name, method in inspect.getmembers(BaseOptimizer) 
                           if getattr(method, '__isabstractmethod__', False)]
        assert len(abstract_methods) > 0, "BaseOptimizer should have abstract methods"
        assert "_create_teleprompter" in abstract_methods, "_create_teleprompter should be abstract"


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

    @patch("dspy.teleprompt.MIPROv2")
    def test_create_teleprompter(self, mock_mipro):
        """Test creating MIPROv2 teleprompter."""
        from dspy_integration.framework.optimizers.mipro_v2 import MIPROv2Optimizer

        mock_mipro.return_value = MagicMock()

        mock_metric = MagicMock()
        optimizer = MIPROv2Optimizer(metric=mock_metric)

        teleprompter = optimizer._create_teleprompter()
        assert teleprompter is not None
        mock_mipro.assert_called_once()


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

    @patch("dspy.teleprompt.BootstrapFewShotWithRandomSearch")
    def test_create_teleprompter(self, mock_bsrs):
        """Test creating teleprompter with random search."""
        from dspy_integration.framework.optimizers.bootstrap import (
            BootstrapFewShotRandomSearchOptimizer,
        )

        mock_bsrs.return_value = MagicMock()

        mock_metric = MagicMock()
        optimizer = BootstrapFewShotRandomSearchOptimizer(metric=mock_metric)

        teleprompter = optimizer._create_teleprompter()
        assert teleprompter is not None
        mock_bsrs.assert_called_once()


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

        # Use create() instead of get()
        optimizer = OptimizerRegistry.create("MIPROv2")
        assert optimizer is not None

    def test_get_unknown_optimizer(self):
        """Test that unknown optimizer raises error."""
        from dspy_integration.framework.optimizers import OptimizerRegistry

        with pytest.raises(ValueError) as exc_info:
            OptimizerRegistry.create("UnknownOptimizer")
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
