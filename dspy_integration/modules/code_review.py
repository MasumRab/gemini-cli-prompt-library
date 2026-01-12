import dspy

class CodeReviewSignature(dspy.Signature):
    """
    Best Practices Code Review.
    Analyzes code for style, organization, error handling, testing, maintainability, SOLID principles, and more.
    """
    code = dspy.InputField(desc="Code snippet to review")
    review = dspy.OutputField(desc="Comprehensive review covering style, organization, error handling, testing, maintainability, SOLID principles, etc.")

class CodeReviewModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.review_code = dspy.ChainOfThought(CodeReviewSignature)

    def forward(self, code):
        return self.review_code(code=code)
