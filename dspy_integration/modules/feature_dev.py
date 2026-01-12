import dspy

class FeatureDevSignature(dspy.Signature):
    """
    Linear Feature Development Workflow.
    Executes context analysis, implementation, verification, and usage instructions in a single flow.
    """
    args = dspy.InputField(desc="Feature requirements and context")
    context_design = dspy.OutputField(desc="Phase 1: Context & Design. Key architectural decisions and API signatures.")
    implementation = dspy.OutputField(desc="Phase 2: Implementation. Complete, production-ready code.")
    verification = dspy.OutputField(desc="Phase 3: Verification Strategy. Unit and integration tests.")
    usage = dspy.OutputField(desc="Phase 4: Usage. concise README snippet.")

class FeatureDevModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_feature = dspy.ChainOfThought(FeatureDevSignature)

    def forward(self, args):
        return self.generate_feature(args=args)
