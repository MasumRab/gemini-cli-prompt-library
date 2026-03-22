import dspy
from typing import Optional


class SecurityReviewSignature(dspy.Signature):
    """Security Code Review. Analyzes code for security vulnerabilities."""

    code = dspy.InputField(desc="Code snippet to review for security issues")
    review = dspy.OutputField(
        desc="Security review with vulnerabilities, severity, and fixes"
    )


class SecurityReview(dspy.Module):
    """Security review module for detecting security vulnerabilities."""

    def __init__(self, model: Optional[dspy.LM] = None):
        super().__init__()
        self.model = model or dspy.settings.lm
        self.review_code = dspy.ChainOfThought(SecurityReviewSignature)

    def forward(self, code: str) -> str:
        result = self.review_code(code=code)
        return result.review


class SecurityReviewOptimizer(dspy.Module):
    # TODO [Low Priority]: Optimize this module using dspy.MIPROv2
    # or BootstrapFewShot for better prompt performance.
    """Optimized security review module."""

    def __init__(self):
        super().__init__()
        self.program = dspy.ChainOfThought(SecurityReviewSignature)

    def forward(self, code: str) -> str:
        result = self.program(code=code)
        return result.review
