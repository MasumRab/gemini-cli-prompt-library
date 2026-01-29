import dspy
from typing import Optional


class ApiDesignSignature(dspy.Signature):
    """RESTful API Design. Design comprehensive APIs for given requirements."""

    requirements = dspy.InputField(desc="Requirements for the API to be designed")
    design = dspy.OutputField(
        desc="API design with endpoints, structure, and specifications"
    )


class ApiDesign(dspy.Module):
    """API design module for creating RESTful API designs."""

    def __init__(self, model: Optional[dspy.LM] = None):
        super().__init__()
        self.model = model or dspy.settings.lm
        self.design_api = dspy.ChainOfThought(APIDesignSignature)

    def forward(self, requirements: str):
        result = self.design_api(requirements=requirements)
        return result.design


class ApiDesignOptimizer(dspy.Module):
    """Optimized API design module."""

    def __init__(self):
        super().__init__()
        self.program = dspy.ChainOfThought(APIDesignSignature)

    def forward(self, requirements: str):
        result = self.program(requirements=requirements)
        return result.design