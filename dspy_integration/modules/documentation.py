import dspy
from typing import Optional


class DocumentationSignature(dspy.Signature):
    """Write documentation for the specified code element."""

    input_code: str = dspy.InputField(
        desc="The function, class, or code snippet to document"
    )
    documented_code: str = dspy.OutputField(
        desc="Complete code with documentation (docstrings, comments)"
    )


class Documentation(dspy.Module):
    def __init__(self, model: Optional[dspy.LM] = None):
        super().__init__()
        self.model = model or dspy.settings.lm
        self.generate = dspy.ChainOfThought(DocumentationSignature)

    def forward(self, input_code: str) -> str:
        result = self.generate(input_code=input_code)
        return result.documented_code


class DocumentationOptimizer(dspy.Module):
    # TODO [Low Priority]: Optimize this module using dspy.MIPROv2
    # or BootstrapFewShot for better prompt performance.
    def __init__(self):
        super().__init__()
        self.untested_documentation = Documentation()
        self.program = dspy.ChainOfThought(DocumentationSignature)

    def forward(self, input_code: str) -> str:
        result = self.program(input_code=input_code)
        return result.documented_code
