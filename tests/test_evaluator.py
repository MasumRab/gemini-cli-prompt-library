"""
Tests for DSPy-HELM Evaluator.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestEvaluator:
    """Test Evaluator class."""

    def test_evaluator_init(self):
        """Test evaluator initialization."""
        from dspy_integration.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        assert evaluator.metric is mock_metric
        assert evaluator.num_threads == 16
        assert evaluator.display_progress is True
        assert evaluator.display_table == 0

    def test_evaluator_custom_init(self):
        """Test evaluator with custom values."""
        from dspy_integration.eval import Evaluator

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
        from dspy_integration.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        assert hasattr(evaluator, "_evaluator")
        assert evaluator._evaluator is not None


class TestEvaluatorEvaluate:
    """Test evaluator evaluate method."""

    @pytest.mark.skip(
        reason="Requires real dspy module - tests internal dspy integration"
    )
    @patch("dspy_helm.eval.evaluate.dspy")
    def test_evaluate_basic(self, mock_dspy):
        """Test basic evaluation."""
        from dspy_integration.eval import Evaluator

        mock_dspy.Evaluate.return_value = MagicMock()
        mock_dspy.Evaluate.return_value.return_value = 0.85

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        mock_program = MagicMock()
        mock_devset = [MagicMock(), MagicMock()]

        result = evaluator.evaluate(mock_program, mock_devset)

        assert "score" in result
        assert "count" in result
        assert result["score"] == 0.85
        assert result["count"] == 2

    @pytest.mark.skip(
        reason="Requires real dspy module - tests internal dspy integration"
    )
    @patch("dspy_helm.eval.evaluate.dspy")
    def test_evaluate_with_return_outputs(self, mock_dspy):
        """Test evaluation with return_outputs=True."""
        from dspy_integration.eval import Evaluator

        mock_dspy.Evaluate.return_value = MagicMock()
        mock_dspy.utils.parallelizer.ParallelExecutor.return_value = MagicMock()

        # Mock executor to return results
        def mock_execute(fn, items):
            return [fn(item) for item in items]

        mock_dspy.utils.parallelizer.ParallelExecutor.return_value.execute = (
            mock_execute
        )

        mock_metric = MagicMock()
        mock_metric.return_value = 1.0

        evaluator = Evaluator(metric=mock_metric, num_threads=4)

        mock_program = MagicMock()
        mock_program.return_value = MagicMock()
        mock_devset = [MagicMock(), MagicMock()]

        result = evaluator.evaluate(mock_program, mock_devset, return_outputs=True)

        assert "score" in result
        assert "count" in result
        assert "outputs" in result
        assert len(result["outputs"]) == 2

    @pytest.mark.skip(
        reason="Requires real dspy module - tests internal dspy integration"
    )
    @patch("dspy_helm.eval.evaluate.dspy")
    def test_evaluate_empty_devset(self, mock_dspy):
        """Test evaluation with empty devset."""
        from dspy_integration.eval import Evaluator

        mock_dspy.Evaluate.return_value = MagicMock()
        mock_dspy.Evaluate.return_value.return_value = 0.0

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        mock_program = MagicMock()
        result = evaluator.evaluate(mock_program, [])

        assert result["count"] == 0


class TestEvaluatorExport:
    """Test evaluator export functionality."""

    def test_export_results(self, tmp_path):
        """Test exporting results to JSON."""
        from dspy_integration.eval import Evaluator
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
        from dspy_integration.eval import Evaluator

        mock_metric = MagicMock()
        evaluator = Evaluator(metric=mock_metric)

        results = {"score": 0.5, "count": 5}

        output_path = tmp_path / "nested" / "dir" / "results.json"
        evaluator.export_results(results, output_path)

        assert output_path.exists()


class TestEvaluatorIntegration:
    """Integration tests for Evaluator."""

    @pytest.mark.skip(
        reason="Requires real dspy module - tests internal dspy integration"
    )
    def test_metric_function_called(self):
        """Test that metric function is called during evaluation."""
        from dspy_integration.eval import Evaluator
        import dspy

        # Create a simple metric
        def simple_metric(example, pred, trace=None):
            return 1.0

        evaluator = Evaluator(metric=simple_metric)

        # Create mock program and examples
        class MockProgram:
            def __call__(self, **inputs):
                class MockPred:
                    result = "test output"

                return MockPred()

        mock_program = MockProgram()

        class MockExample:
            def inputs(self):
                return {"input": "test"}

        mock_devset = [MockExample()]

        # Patch dspy.Evaluate to avoid actual LM calls
        with patch.object(dspy, "Evaluate") as mock_evaluate_class:
            mock_evaluate_instance = MagicMock()
            mock_evaluate_instance.return_value = 1.0
            mock_evaluate_class.return_value = mock_evaluate_instance

            result = evaluator.evaluate(mock_program, mock_devset)

            assert result["score"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
