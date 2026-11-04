class PostActionVerifier:
    def __init__(self, pipeline_factory):
        self.pipeline_factory = pipeline_factory

    def verify(self, branch, expected_parent):
        snap = self.pipeline_factory().run()
        node = snap.get("branch_graph", {}).get("nodes", {}).get(branch)
        if not node:
            raise RuntimeError(f"Post-analysis missing branch: {branch}")
        status = node.get("status") if isinstance(node, dict) else node.status
        parent = (
            node.get("resolved_parent")
            if isinstance(node, dict)
            else node.resolved_parent
        )
        if status not in {"safe", "needs_restack"}:
            raise RuntimeError(
                f"Topology drift for {branch}: post-analysis status={status}"
            )
        if parent != expected_parent:
            raise RuntimeError(
                f"Topology drift for {branch}: expected parent {expected_parent!r}, got {parent!r}"
            )
        return True
