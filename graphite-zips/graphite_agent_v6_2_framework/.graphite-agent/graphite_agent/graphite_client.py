class GraphiteClient:
    def __init__(self, git):
        self.git = git

    def checkout_branch(self, branch):
        self.git.checkout_branch(branch)

    def track(self, branch, parent):
        self.git.run(
            ["gt", "track", branch, "--parent", parent, "--force", "--no-interactive"]
        )

    def restack(self):
        self.git.run(["gt", "restack", "--no-interactive"])

    def verify_parent(self, branch, expected_parent):
        output = self.git.run(["gt", "branch", "info", branch, "--no-interactive"])
        actual = None
        for line in output.splitlines():
            if line.strip().startswith("Parent:"):
                actual = line.split(":", 1)[1].strip()
                break
        if actual != expected_parent:
            raise RuntimeError(
                f"Graphite parent mismatch for {branch}: expected {expected_parent!r}, got {actual!r}"
            )
