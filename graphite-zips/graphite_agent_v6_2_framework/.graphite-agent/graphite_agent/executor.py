class StrictExecutor:
    def __init__(self, plan_reader, graphite_client, post_action_verifier=None):
        self.plan_reader = plan_reader
        self.graphite = graphite_client
        self.post_action_verifier = post_action_verifier

    def execute(self):
        plan = self.plan_reader.read()
        for step in plan.get("execution_queue", []):
            self._validate_step(step)
            branch = step["branch"]
            parent = step["resolved_parent"]
            self.graphite.checkout_branch(branch)
            self.graphite.track(branch, parent)
            if step["action"] == "track_and_restack":
                self.graphite.restack()
            self.graphite.verify_parent(branch, parent)
            if self.post_action_verifier:
                self.post_action_verifier.verify(branch, parent)
        return True

    def _validate_step(self, step):
        if step["status"] not in {"safe", "needs_restack"}:
            raise RuntimeError(f"Non-executable status in queue: {step}")
        if step["action"] not in {"track_only", "track_and_restack"}:
            raise RuntimeError(f"Unsupported action in queue: {step}")
        if not step.get("resolved_parent"):
            raise RuntimeError(f"Missing resolved parent in queue: {step}")
