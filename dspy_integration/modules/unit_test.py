import dspy
from typing import Optional


class UnitTestSignature(dspy.Signature):
    """Write a unit test for the specified function or class."""

    input_code: str = dspy.InputField(
        desc="The function, class, or code snippet to write tests for"
    )
    test_code: str = dspy.OutputField(desc="Complete, working unit test code")


class UnitTest(dspy.Module):
    def __init__(self, model: Optional[dspy.LM] = None):
        super().__init__()
        self.model = model or dspy.settings.lm
        self.generate = dspy.ChainOfThought(UnitTestSignature)

    def forward(self, input_code: str) -> str:
        result = self.generate(input_code=input_code)
        return result.test_code


class UnitTestOptimizer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.untested_unit_test = UnitTest()
        self.program = dspy.ChainOfThought(UnitTestSignature)

    def forward(self, input_code: str) -> str:
        result = self.program(input_code=input_code)
        return result.test_code
