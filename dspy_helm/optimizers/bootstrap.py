"""
BootstrapFewShot Optimizers.
"""

from .base import BaseOptimizer, OptimizerRegistry


@OptimizerRegistry.register("BootstrapFewShot")
class BootstrapFewShotOptimizer(BaseOptimizer):
    """BootstrapFewShot optimizer."""

    def _create_teleprompter(self):
        from dspy.teleprompt import BootstrapFewShot

        return BootstrapFewShot(
            metric=self.metric,
            max_bootstrapped_demos=self.max_bootstrapped_demos,
            max_labeled_demos=self.max_labeled_demos,
            num_threads=self.num_threads,
        )


@OptimizerRegistry.register("BootstrapFewShotWithRandomSearch")
class BootstrapFewShotRandomSearchOptimizer(BaseOptimizer):
    """BootstrapFewShot with Random Search optimizer."""

    def __init__(
        self,
        metric,
        max_bootstrapped_demos: int = 3,
        max_labeled_demos: int = 3,
        num_threads: int = 16,
        num_candidate_programs: int = 10,
    ):
        super().__init__(
            metric=metric,
            max_bootstrapped_demos=max_bootstrapped_demos,
            max_labeled_demos=max_labeled_demos,
            num_threads=num_threads,
        )
        self.num_candidate_programs = num_candidate_programs

    def _create_teleprompter(self):
        from dspy.teleprompt import BootstrapFewShotWithRandomSearch

        return BootstrapFewShotWithRandomSearch(
            metric=self.metric,
            max_bootstrapped_demos=self.max_bootstrapped_demos,
            max_labeled_demos=self.max_labeled_demos,
            num_candidate_programs=self.num_candidate_programs,
            num_threads=self.num_threads,
        )
