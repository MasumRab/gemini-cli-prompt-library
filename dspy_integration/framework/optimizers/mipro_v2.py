import dspy

"""
MIPROv2 Optimizer Implementation.
"""

from dspy_helm.optimizers.mipro_v2 import MIPROv2Optimizer

<<<<<<< HEAD
__all__ = ["MIPROv2Optimizer"]
=======

@OptimizerRegistry.register("MIPROv2")
class MIPROv2Optimizer(BaseOptimizer):
    """MIPROv2 optimizer for prompt optimization."""

    def __init__(
        self,
        metric,
        max_bootstrapped_demos: int = 3,
        max_labeled_demos: int = 3,
        num_threads: int = 16,
        auto: str = "light",
        prompt_model=None,
        task_model=None,
    ):
        if metric is None:
            raise ValueError("metric is required")

        super().__init__(
            metric=metric,
            max_bootstrapped_demos=max_bootstrapped_demos,
            max_labeled_demos=max_labeled_demos,
            num_threads=num_threads,
        )
        self.auto = auto
        self.prompt_model = prompt_model
        self.task_model = task_model

    def _create_teleprompter(self):
        from dspy.teleprompt import MIPROv2

        return MIPROv2(
            metric=self.metric,
            max_bootstrapped_demos=self.max_bootstrapped_demos,
            max_labeled_demos=self.max_labeled_demos,
            auto=self.auto,
            prompt_model=self.prompt_model,
            task_model=self.task_model,
            num_threads=self.num_threads,
        )

    def compile(self, program, trainset, valset):

        if not dspy.settings.lm:
            raise RuntimeError("No LM configured. Call dspy.configure(lm=...) first.")
<<<<<<< HEAD
<<<<<<< HEAD

        teleprompter = self._create_teleprompter()
        return teleprompter.compile(program, trainset=trainset, valset=valset)
>>>>>>> e2b28dc (Fix CI ruff linting failures across the codebase)
=======
__all__ = [MIPROv2Optimizer]
>>>>>>> 83b2453 (Fix leftover conflict marker in mipro_v2.py)
=======

        teleprompter = self._create_teleprompter()
        return teleprompter.compile(program, trainset=trainset, valset=valset)
>>>>>>> 29c7a5a (Apply Ruff formatting and Flake8 fixes)
