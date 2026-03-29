"""
Tests for DSPy-HELM Evaluator.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestEvaluator:
    """Test Evaluator class."""

    def test_evaluator_init(self):
        """Test evaluator initialization."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        assert evaluator.metric is mock_metric
        assert evaluator.num_threads == 16
        assert evaluator.display_progress is True
        assert evaluator.display_table == 0

    def test_evaluator_custom_init(self):
        """Test evaluator with custom values."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(
            metric=mock_metric,
            num_threads=8,
            display_progress=False,
            display_table=3,
        )

        assert evaluator.num_threads == 8
        assert evaluator.display_progress is False
        assert evaluator.display_table == 3

    def test_evaluator_has_evaluator(self):
        """Test that evaluator has internal _evaluator."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        assert hasattr(evaluator, "_evaluator")
        assert evaluator._evaluator is not None


class TestEvaluatorEvaluate:
    """Test evaluator evaluate method."""

    def test_evaluate_basic(self):
        """Test basic evaluation using mocked dspy.Evaluate."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock(return_value=1.0)

        # Patch the Evaluate class used in the module
        with patch("dspy.Evaluate") as mock_evaluate_class:
            mock_evaluate_instance = MagicMock()
            mock_evaluate_instance.return_value = 0.85
            mock_evaluate_class.return_value = mock_evaluate_instance

            evaluator = Evaluator(metric=mock_metric)
            mock_program = MagicMock()
            mock_devset = [MagicMock(), MagicMock()]

            result = evaluator.evaluate(mock_program, mock_devset)

            assert "score" in result
            assert "count" in result

    def test_evaluate_with_return_outputs(self):
        """Test evaluation with return_outputs=True."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock(return_value=1.0)

        evaluator = Evaluator(metric=mock_metric, num_threads=4)

        # Create mock program that returns a prediction
        mock_program = MagicMock()
        mock_pred = MagicMock()
        mock_program.return_value = mock_pred

        # Create mock examples
        mock_example1 = MagicMock()
        mock_example1.inputs.return_value = {"input": "test1"}
        mock_example2 = MagicMock()
        mock_example2.inputs.return_value = {"input": "test2"}
        mock_devset = [mock_example1, mock_example2]

        # Patch where it's imported from (dspy.utils.parallelizer)
        with patch("dspy.utils.parallelizer.ParallelExecutor") as mock_executor:
            mock_executor_instance = MagicMock()
            mock_executor_instance.execute.side_effect = lambda fn, items: [fn(item) for item in items]
            mock_executor.return_value = mock_executor_instance

            result = evaluator.evaluate(mock_program, mock_devset, return_outputs=True)

            assert "score" in result
            assert "count" in result
            assert "outputs" in result
            assert len(result["outputs"]) == 2

    def test_evaluate_empty_devset(self):
        """Test evaluation with empty devset."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        mock_program = MagicMock()
        result = evaluator.evaluate(mock_program, [])

        assert result["count"] == 0

    def test_evaluate_none_program_raises_error(self):
        """Test that evaluate raises ValueError for None program."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        with pytest.raises(ValueError, match="Program cannot be None"):
            evaluator.evaluate(None, [MagicMock()])

    def test_evaluate_calls_metric_for_each_example(self):
        """Test that evaluate calls metric for each example."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock(return_value=0.5)
        evaluator = Evaluator(metric=mock_metric, num_threads=4)

        mock_program = MagicMock()
        mock_pred = MagicMock()
        mock_program.return_value = mock_pred

        # Create mock examples
        mock_example1 = MagicMock()
        mock_example1.inputs.return_value = {"input": "test1"}
        mock_example2 = MagicMock()
        mock_example2.inputs.return_value = {"input": "test2"}
        mock_devset = [mock_example1, mock_example2]

        # Patch where it's imported from (dspy.utils.parallelizer)
        with patch("dspy.utils.parallelizer.ParallelExecutor") as mock_executor:
            mock_executor_instance = MagicMock()
            mock_executor_instance.execute.side_effect = lambda fn, items: [fn(item) for item in items]
            mock_executor.return_value = mock_executor_instance

            evaluator.evaluate(mock_program, mock_devset, return_outputs=True)

            # Metric should be called twice (once for each example)
            assert mock_metric.call_count == 2


class TestEvaluatorExport:
    """Test evaluator export functionality."""

    def test_export_results(self, tmp_path):
        """Test exporting results to JSON."""
        from dspy_helm.eval import Evaluator
        import json

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        results = {
            "score": 0.85,
            "count": 10,
            "outputs": [{"example": "test", "score": 1.0}],
        }

        output_path = tmp_path / "results.json"
        evaluator.export_results(results, output_path)

        assert output_path.exists()

        with open(output_path, "r") as f:
            loaded = json.load(f)

        assert loaded["score"] == 0.85
        assert loaded["count"] == 10

    def test_export_creates_parent_dirs(self, tmp_path):
        """Test that export creates parent directories."""
        from dspy_helm.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        results = {"score": 0.5, "count": 5}

        output_path = tmp_path / "nested" / "dir" / "results.json"
        evaluator.export_results(results, output_path)

        assert output_path.exists()


class TestEvaluatorIntegration:
    """Integration tests for Evaluator."""

    def test_metric_function_called(self):
        """Test that metric function is called during evaluation."""
        from dspy_helm.eval import Evaluator

        call_count = 0

        def simple_metric(example, pred):
            nonlocal call_count
            call_count += 1
            return 1.0

        evaluator = Evaluator(metric=simple_metric, num_threads=1)

        # Create mock program that returns a prediction
        mock_program = MagicMock()
        mock_pred = MagicMock()
        mock_program.return_value = mock_pred

        # MockExample that supports dict() conversion
        class MockExample:
            def __init__(self, input_val):
                self.input = input_val
            
            def inputs(self):
                return {"input": self.input}
            
            def __iter__(self):
                return iter([("input", self.input)])

        mock_devset = [MockExample("test1"), MockExample("test2")]

        # Patch where it's imported from (dspy.utils.parallelizer)
        with patch("dspy.utils.parallelizer.ParallelExecutor") as mock_executor:
            mock_executor_instance = MagicMock()
            mock_executor_instance.execute.side_effect = lambda fn, items: [fn(item) for item in items]
            mock_executor.return_value = mock_executor_instance

            result = evaluator.evaluate(mock_program, mock_devset, return_outputs=True)

            # Metric should have been called for each example
            assert call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
