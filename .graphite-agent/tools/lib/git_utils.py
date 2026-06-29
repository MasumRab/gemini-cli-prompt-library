import subprocess
import os
import time
from functools import lru_cache


class Git:
    def __init__(self, remote="origin", retries=2):
        self.remote = remote
        self.retries = retries

    def run(self, args, check=True, input_text=None):
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GRAPHITE_NO_INTERACTIVE"] = "1"
        last = None
        # ensure args is always a list to avoid command injection with shell=True
        if isinstance(args, str):
            import shlex

            safe_args = shlex.split(args)
        else:
            safe_args = args

        for i in range(max(1, self.retries + 1)):
            # sourcery skip: command-injection
            last = subprocess.run(
                safe_args, input=input_text, capture_output=True, text=True, env=env
            )
            if last.returncode == 0 or i == self.retries:
                break
            time.sleep(0.2 * (i + 1))
        if check and last.returncode != 0:
            raise RuntimeError(
                {
                    "command": args,
                    "exit_code": last.returncode,
                    "stdout": last.stdout,
                    "stderr": last.stderr,
                }
            )
        return last.stdout.strip() if last.stdout else ""

    def ref_exists(self, ref):
        return bool(
            ref
            and self.run(
                ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], check=False
            )
        )

    def resolve(self, ref):
        if not ref:
            return ref
        if self.ref_exists(ref):
            return ref
        rr = f"{self.remote}/{ref}"
        return rr if self.ref_exists(rr) else ref

    @lru_cache(maxsize=None)
    def is_ancestor(self, a, b):
        if not a or not b:
            return False
        return (
            subprocess.run(
                [
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    str(self.resolve(a)),
                    str(self.resolve(b)),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )

    def merge_base(self, a, b):
        out = self.run(
            ["git", "merge-base", str(self.resolve(a)), str(self.resolve(b))],
            check=False,
        )
        return out or None

    def commit_distance(self, a, b):
        out = self.run(
            ["git", "rev-list", "--count", f"{self.resolve(a)}..{self.resolve(b)}"],
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
                f"{self.resolve(root)}..{self.resolve(branch)}",
            ],
            check=False,
        )
        return out.splitlines() if out else []

    @lru_cache(maxsize=None)
    def patch_ids_between(self, root, branch):
        log = self.run(
            ["git", "log", "-p", f"{self.resolve(root)}..{self.resolve(branch)}"],
            check=False,
        )
        if not log:
            return frozenset()
        r = subprocess.run(
            ["git", "patch-id"], input=log, capture_output=True, text=True
        )
        return (
            frozenset(x.split()[0] for x in r.stdout.splitlines() if x.strip())
            if r.returncode == 0
            else frozenset()
        )

    def checkout(self, b):
        if (
            subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{b}"]
            ).returncode
            == 0
        ):
            self.run(["git", "checkout", "-f", b])
            return
        rb = f"{self.remote}/{b}"
        if (
            subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/remotes/{rb}"]
            ).returncode
            == 0
        ):
            self.run(["git", "checkout", "-f", "-b", b, "--track", rb])
            return
        raise RuntimeError(f"Branch not found: {b}")
