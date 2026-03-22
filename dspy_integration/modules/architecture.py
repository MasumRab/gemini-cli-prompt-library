import dspy
from typing import Optional


class ArchitectureSignature(dspy.Signature):
    """
    System Architecture Design.
    Designs a comprehensive system architecture including requirements, capacity, high-level design, components, and data flow.
    """

    requirements = dspy.InputField(desc="System requirements and constraints")
    architecture = dspy.OutputField(
        desc="Complete system architecture design including diagram, component specs, and scaling strategy."
    )


class Architecture(dspy.Module):
    """Architecture design module for system design."""

    def __init__(self, model: Optional[dspy.LM] = None):
        super().__init__()
        self.model = model or dspy.settings.lm
        self.design_system = dspy.ChainOfThought(ArchitectureSignature)

    def forward(self, requirements: str):
        return self.design_system(requirements=requirements)


class ArchitectureOptimizer(dspy.Module):
    # TODO [Low Priority]: Optimize this module using dspy.MIPROv2
    # or BootstrapFewShot for better prompt performance.
    """Optimized architecture module."""

    def __init__(self):
        super().__init__()
        self.program = dspy.ChainOfThought(ArchitectureSignature)

    def forward(self, requirements: str):
        result = self.program(requirements=requirements)
        return result.architecture
