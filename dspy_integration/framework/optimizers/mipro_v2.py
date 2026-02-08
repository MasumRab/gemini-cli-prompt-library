import dspy

"""
MIPROv2 Optimizer Implementation.
"""

from .base import BaseOptimizer, OptimizerRegistry


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
        import dspy

        if not dspy.settings.lm:
            raise RuntimeError("No LM configured. Call dspy.configure(lm=...) first.")

        teleprompter = self._create_teleprompter()
        return teleprompter.compile(program, trainset=trainset, valset=valset)
