import dspy

class SystemDesignSignature(dspy.Signature):
    """
    System Architecture Design.
    Designs a comprehensive system architecture including requirements, capacity, high-level design, components, and data flow.
    """
    requirements = dspy.InputField(desc="System requirements and constraints")
    architecture = dspy.OutputField(desc="Complete system architecture design including diagram, component specs, and scaling strategy.")

class SystemDesignModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.design_system = dspy.ChainOfThought(SystemDesignSignature)

    def forward(self, requirements):
        return self.design_system(requirements=requirements)
