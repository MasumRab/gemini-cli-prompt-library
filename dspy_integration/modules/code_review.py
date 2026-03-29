import dspy
from typing import Optional


class CodeReviewSignature(dspy.Signature):
    """
    Best Practices Code Review.
    Analyzes code for style, organization, error handling, testing, maintainability, SOLID principles, and more.
    """

    code = dspy.InputField(desc="Code snippet to review")
    review = dspy.OutputField(
        desc="Comprehensive review covering style, organization, error handling, testing, maintainability, SOLID principles, etc."
    )


class CodeReview(dspy.Module):
    """Code review module for best practices analysis."""

    def __init__(self, model: Optional[dspy.LM] = None):
        super().__init__()
        self.model = model or dspy.settings.lm
        self.review_code = dspy.ChainOfThought(CodeReviewSignature)

    def forward(self, code: str):
        return self.review_code(code=code)


class CodeReviewOptimizer(dspy.Module):
    """Optimized code review module."""

    # TODO [Low Priority]: Optimize this module using dspy.MIPROv2 or BootstrapFewShot for better prompt performance.
    # The current implementation uses a basic ChainOfThought without compiled examples.

    def __init__(self):
        super().__init__()
        self.program = dspy.ChainOfThought(CodeReviewSignature)

    def forward(self, code: str):
        result = self.program(code=code)
        return result.review
