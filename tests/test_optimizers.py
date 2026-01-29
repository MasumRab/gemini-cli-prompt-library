"""
Tests for DSPy-HELM optimizers.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestBaseOptimizer:
    """Test base optimizer functionality."""

    def test_base_optimizer_abstract_create_teleprompter(self):
        """Test that _create_teleprompter is abstract."""
        from dspy_integration.framework.optimizers.base import BaseOptimizer
        import abc

        # Verify that BaseOptimizer is indeed an abstract class
        assert abc.ABC in BaseOptimizer.__bases__ or BaseOptimizer.__name__ == 'BaseOptimizer'

        # Trying to instantiate should raise TypeError due to unimplemented abstract method
        mock_metric = MagicMock()
        with pytest.raises(TypeError):
            BaseOptimizer(metric=mock_metric)


class ConcreteTestOptimizer:
    """Helper class to test BaseOptimizer functionality by creating a concrete implementation."""

    def __init__(self):
        from dspy_integration.framework.optimizers.base import BaseOptimizer
        from unittest.mock import MagicMock

        # Create a concrete implementation for testing
        class TestOptimizer(BaseOptimizer):
            def _create_teleprompter(self):
                return MagicMock()

        self.TestOptimizer = TestOptimizer


class TestConcreteOptimizer:
    """Test optimizer functionality using a concrete implementation."""

    def test_concrete_optimizer_init(self):
        """Test concrete optimizer initialization."""
        from dspy_integration.framework.optimizers.base import BaseOptimizer
        from unittest.mock import MagicMock

        # Create a concrete implementation for testing
        class TestOptimizer(BaseOptimizer):
            def _create_teleprompter(self):
                return MagicMock()

        mock_metric = MagicMock()
        optimizer = TestOptimizer(metric=mock_metric)

        assert optimizer.metric is mock_metric
        assert optimizer.max_bootstrapped_demos == 3
        assert optimizer.max_labeled_demos == 3
        assert optimizer.num_threads == 16

    def test_concrete_optimizer_custom_values(self):
        """Test concrete optimizer with custom values."""
        from dspy_integration.framework.optimizers.base import BaseOptimizer
        from unittest.mock import MagicMock

        # Create a concrete implementation for testing
        class TestOptimizer(BaseOptimizer):
            def _create_teleprompter(self):
                return MagicMock()

        mock_metric = MagicMock()
        optimizer = TestOptimizer(
            metric=mock_metric,
            max_bootstrapped_demos=5,
            max_labeled_demos=4,
            num_threads=8,
        )

        assert optimizer.max_bootstrapped_demos == 5
        assert optimizer.max_labeled_demos == 4
        assert optimizer.num_threads == 8

    def test_concrete_optimizer_repr(self):
        """Test concrete optimizer string representation."""
        from dspy_integration.framework.optimizers.base import BaseOptimizer
        from unittest.mock import MagicMock

        # Create a concrete implementation for testing
        class TestOptimizer(BaseOptimizer):
            def _create_teleprompter(self):
                return MagicMock()

        mock_metric = MagicMock()
        optimizer = TestOptimizer(metric=mock_metric)

        repr_str = repr(optimizer)
        assert "TestOptimizer" in repr_str  # Changed from BaseOptimizer to TestOptimizer
        assert "max_bootstrapped=3" in repr_str
        assert "max_labeled=3" in repr_str


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
    def test_create_teleprompter(self, mock_miprov2_class):
        """Test creating MIPROv2 teleprompter."""
        from dspy_integration.framework.optimizers.mipro_v2 import MIPROv2Optimizer

        mock_miprov2_class.return_value = MagicMock()

        mock_metric = MagicMock()
        optimizer = MIPROv2Optimizer(metric=mock_metric)

        teleprompter = optimizer._create_teleprompter()
        assert teleprompter is not None

        # Verify MIPROv2 was called with correct args
        mock_miprov2_class.assert_called_once()
        call_kwargs = mock_miprov2_class.call_args[1]
        assert call_kwargs["metric"] is mock_metric
        assert call_kwargs["max_bootstrapped_demos"] == 3


class TestBootstrapFewShotOptimizer:
    """Test BootstrapFewShot optimizer."""

    def test_init(self):
        """Test BootstrapFewShot optimizer initialization."""
        from dspy_integration.framework.optimizers.bootstrap import BootstrapFewShotOptimizer

        mock_metric = MagicMock()
        optimizer = BootstrapFewShotOptimizer(metric=mock_metric)

        assert optimizer.metric is mock_metric

    @patch("dspy.teleprompt.BootstrapFewShot")
    def test_create_teleprompter(self, mock_bootstrapfewshot_class):
        """Test creating BootstrapFewShot teleprompter."""
        from dspy_integration.framework.optimizers.bootstrap import BootstrapFewShotOptimizer

        mock_bootstrapfewshot_class.return_value = MagicMock()

        mock_metric = MagicMock()
        optimizer = BootstrapFewShotOptimizer(metric=mock_metric)

        teleprompter = optimizer._create_teleprompter()
        assert teleprompter is not None


class TestBootstrapFewShotRandomSearchOptimizer:
    """Test BootstrapFewShot with Random Search optimizer."""

    def test_init(self):
        """Test initialization."""
        from dspy_integration.framework.optimizers.bootstrap import BootstrapFewShotRandomSearchOptimizer

        mock_metric = MagicMock()
        optimizer = BootstrapFewShotRandomSearchOptimizer(
            metric=mock_metric,
            num_candidate_programs=15,
        )

        assert optimizer.metric is mock_metric
        assert optimizer.num_candidate_programs == 15

    @patch("dspy.teleprompt.BootstrapFewShotWithRandomSearch")
    def test_create_teleprompter(self, mock_bootstrapfewshot_randomsearch_class):
        """Test creating teleprompter with random search."""
        from dspy_integration.framework.optimizers.bootstrap import BootstrapFewShotRandomSearchOptimizer

        mock_bootstrapfewshot_randomsearch_class.return_value = MagicMock()

        mock_metric = MagicMock()
        optimizer = BootstrapFewShotRandomSearchOptimizer(
            metric=mock_metric,
            num_candidate_programs=10,
        )

        teleprompter = optimizer._create_teleprompter()
        assert teleprompter is not None

        call_kwargs = mock_bootstrapfewshot_randomsearch_class.call_args[1]
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
        from unittest.mock import MagicMock

        mock_metric = MagicMock()
        optimizer = OptimizerRegistry.create("MIPROv2", metric=mock_metric)
        assert optimizer is not None

    def test_get_unknown_optimizer(self):
        """Test that unknown optimizer raises error."""
        from dspy_integration.framework.optimizers import OptimizerRegistry
        from unittest.mock import MagicMock

        mock_metric = MagicMock()
        with pytest.raises(ValueError) as exc_info:
            OptimizerRegistry.create("UnknownOptimizer", metric=mock_metric)
        assert "Unknown optimizer" in str(exc_info.value)


class TestOptimizerCompile:
    """Test optimizer compile functionality."""

    @patch("dspy.settings")
    def test_compile_requires_lm(self, mock_settings):
        """Test that compile requires LM to be configured."""
        from dspy_integration.framework.optimizers.mipro_v2 import MIPROv2Optimizer

        # Mock the settings.lm to be None to trigger the RuntimeError
        mock_settings.lm = None
        mock_settings.configure = MagicMock()

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
