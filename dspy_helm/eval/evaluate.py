"""
Evaluation harness for DSPy programs.
"""

from typing import List, Callable, Dict, Any, TYPE_CHECKING
import json
from pathlib import Path

if TYPE_CHECKING:
    import dspy


class Evaluator:
    """Evaluation harness for DSPy programs."""

    def __init__(
        self,
        metric: Callable,
        num_threads: int = 16,
        display_progress: bool = True,
        display_table: int = 0,
    ):
        self.metric = metric
        self.num_threads = num_threads
        self.display_progress = display_progress
        self.display_table = display_table

        import dspy

        self._evaluator = dspy.Evaluate(
            devset=None,
            metric=metric,
            num_threads=num_threads,
            display_progress=display_progress,
            display_table=display_table,
        )

    def evaluate(
        self,
        program: "dspy.Module",
        devset: List["dspy.Example"],
        return_outputs: bool = False,
    ) -> Dict[str, Any]:
        """Evaluate a program on a dataset."""
        if program is None:
            raise ValueError("Program cannot be None")

        self._evaluator.devset = devset

        if return_outputs:
            from dspy.utils.parallelizer import ParallelExecutor

            results = []
            executor = ParallelExecutor(num_threads=self.num_threads)

            def process_item(example):
                try:
                    pred = program(**example.inputs())
                    score = self.metric(example, pred)
                    return (example, pred, score)
                except Exception as e:
                    return (example, None, 0.0)

            raw_results = executor.execute(process_item, devset)

            total_score = 0.0
            for example, pred, score in raw_results:
                if score is None:
                    score = 0.0
                total_score += score
                results.append(
                    {
                        "example": dict(example),
                        "prediction": dict(pred) if pred else None,
                        "score": score,
                    }
                )

            avg_score = total_score / len(devset) if devset else 0.0

            return {"score": avg_score, "count": len(devset), "outputs": results}
        else:
            avg_score = self._evaluator(program)
            return {"score": avg_score, "count": len(devset)}

    def export_results(self, results: Dict[str, Any], output_path: Path) -> None:
        """Export evaluation results to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Results exported to: {output_path}")
