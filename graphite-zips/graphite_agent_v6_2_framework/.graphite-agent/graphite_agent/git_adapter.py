import os
import subprocess
from functools import lru_cache


class GitAdapter:
    def __init__(self, primary_remote="origin"):
        self.primary_remote = primary_remote

    def run(self, args, check=True, input_text=None):
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GRAPHITE_NO_INTERACTIVE"] = "1"
        result = subprocess.run(
            args, input=input_text, capture_output=True, text=True, env=env
        )
        if check and result.returncode != 0:
            raise RuntimeError(
                {
                    "command": args,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            )
        return result.stdout.strip() if result.stdout else ""

    def get_primary_remote(self):
        upstream = self.run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            check=False,
        )
        if upstream and "/" in upstream:
            return upstream.split("/")[0]
        remotes = self.run(["git", "remote"], check=False)
        return remotes.splitlines()[0].strip() if remotes else self.primary_remote

    def ref_exists(self, ref):
        return bool(
            ref
            and self.run(
                ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], check=False
            )
        )

    def resolve_ref(self, branch):
        if not branch:
            return branch
        if self.ref_exists(branch):
            return branch
        remote_ref = f"{self.primary_remote}/{branch}"
        return remote_ref if self.ref_exists(remote_ref) else branch

    @lru_cache(maxsize=None)
    def is_ancestor(self, ancestor, child):
        if not ancestor or not child:
            return False
        result = subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                str(self.resolve_ref(ancestor)),
                str(self.resolve_ref(child)),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0

    def merge_base(self, left, right):
        out = self.run(
            [
                "git",
                "merge-base",
                str(self.resolve_ref(left)),
                str(self.resolve_ref(right)),
            ],
            check=False,
        )
        return out or None

    def commit_distance(self, start, end):
        out = self.run(
            [
                "git",
                "rev-list",
                "--count",
                f"{self.resolve_ref(start)}..{self.resolve_ref(end)}",
            ],
            check=False,
        )
        return int(out) if out and out.isdigit() else None

    def merge_commits_between(self, root, branch):
        out = self.run(
            [
                "git",
                "log",
                "--merges",
                "--format=%H%x1f%P%x1f%s",
                f"{self.resolve_ref(root)}..{self.resolve_ref(branch)}",
            ],
            check=False,
        )
        return out.splitlines() if out else []

    @lru_cache(maxsize=None)
    def patch_ids_between(self, root, branch):
        log = self.run(
            [
                "git",
                "log",
                "-p",
                f"{self.resolve_ref(root)}..{self.resolve_ref(branch)}",
            ],
            check=False,
        )
        if not log:
            return frozenset()
        res = subprocess.run(
            ["git", "patch-id"], input=log, capture_output=True, text=True
        )
        if res.returncode != 0:
            return frozenset()
        return frozenset(
            line.split()[0] for line in res.stdout.splitlines() if line.strip()
        )

    def checkout_branch(self, branch):
        if (
            subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"]
            ).returncode
            == 0
        ):
            self.run(["git", "checkout", "-f", branch])
            return
        remote = self.get_primary_remote()
        remote_ref = f"refs/remotes/{remote}/{branch}"
        if (
            subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", remote_ref]
            ).returncode
            == 0
        ):
            self.run(
                ["git", "checkout", "-f", "-b", branch, "--track", f"{remote}/{branch}"]
            )
            return
        raise RuntimeError(f"Branch not found locally or on remote: {branch}")
