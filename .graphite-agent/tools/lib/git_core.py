"""
Git Core Utilities for Graphite Agent V8

Consolidated git utilities that provide a unified interface for:
- Patch ID calculations
- Remote ref resolution
- PR metadata fetching
- Merge base operations
- Ancestry checking
- Commit proximity calculations

This replaces the scattered git utilities in lib/git_utils.py and provides
a more comprehensive interface for V8 requirements.
"""

import json
import os
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional


class GitCore:
    """Core Git operations for Graphite Agent V8."""

    def __init__(
        self, repo_path: Optional[str] = None, remote: str = "origin", retries: int = 2
    ):
        """
        Initialize GitCore.

        Args:
            repo_path: Path to git repository. If None, uses current directory.
            remote: Default remote name.
            retries: Number of retries for git operations.
        """
        self.repo_path = Path(repo_path or ".").resolve()
        self.remote = remote
        self.retries = retries

        # Ensure we're in a git repo
        if not self._is_git_repo():
            raise RuntimeError(f"Not a git repository: {self.repo_path}")

    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        git_dir = self.repo_path / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def _run(
        self, args: List[str], check: bool = True, input_text: Optional[str] = None
    ) -> str:
        """
        Run a git command.

        Args:
            args: Git command arguments.
            check: Raise exception on non-zero exit code.
            input_text: Optional stdin input.

        Returns:
            stdout as string.
        """
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GRAPHITE_NO_INTERACTIVE"] = "1"

        last = None
        for i in range(max(1, self.retries + 1)):
            cmd = ["git"] + args
            last = subprocess.run(
                cmd,
                input=input_text,
                capture_output=True,
                text=True,
                env=env,
                cwd=self.repo_path,
            )
            if last.returncode == 0 or i == self.retries:
                break
            import time

            time.sleep(0.2 * (i + 1))

        if check and last.returncode != 0:
            raise RuntimeError(
                {
                    "command": " ".join(cmd),
                    "exit_code": last.returncode,
                    "stdout": last.stdout,
                    "stderr": last.stderr,
                }
            )
        return last.stdout.strip() if last.stdout else ""

    # ========================================================================
    # V8 Required Functions (from Phase 8.1/9.4 spec)
    # ========================================================================

    def get_patch_id(self, commit_hash: str) -> str:
        """
        Get the patch ID for a commit.

        The patch ID is a hash that identifies the patch (change) introduced by a commit.
        Commits with the same change (even if applied to different branches) will have
        the same patch ID, allowing detection of duplicate work or cherry-picks.

        Args:
            commit_hash: Git commit hash.

        Returns:
            Patch ID string.
        """
        out = self._run(["git", "patch-id", commit_hash], check=False)
        if out:
            return out.split()[0]  # First field is the patch ID
        return f"patch_{commit_hash[:12]}"

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        """
        Check if one commit is an ancestor of another.

        Args:
            ancestor: Potential ancestor commit.
            descendant: Potential descendant commit.

        Returns:
            True if ancestor is an ancestor of descendant.
        """
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", str(ancestor), str(descendant)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=self.repo_path,
        )
        return result.returncode == 0

    def get_merge_base(self, a: str, b: str) -> Optional[str]:
        """
        Find the merge base of two commits.

        Args:
            a: First commit.
            b: Second commit.

        Returns:
            Merge base commit hash, or None if no common ancestor.
        """
        try:
            out = self._run(["git", "merge-base", a, b], check=False)
            return out if out else None
        except:
            return None

    def get_remote_refs(self) -> List[str]:
        """
        Get all remote refs (branches and tags).

        Returns:
            List of remote ref names.
        """
        try:
            out = self._run(
                ["git", "ls-remote", "--heads", "--tags", self.remote], check=False
            )
            if out:
                return [
                    line.split("\t")[-1] for line in out.splitlines() if line.strip()
                ]
            return []
        except:
            return []

    def get_pr_metadata(self, branch_name: str) -> Optional[Dict]:
        """
        Get PR metadata for a branch using gh CLI.

        Args:
            branch_name: Name of the branch.

        Returns:
            Dictionary with PR metadata (title, number, base, etc.) or None.
        """
        try:
            # Check if gh CLI is available
            if (
                subprocess.run(["which", "gh"], stdout=subprocess.DEVNULL).returncode
                != 0
            ):
                return None

            # Try to find PR for this branch
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "view",
                    branch_name,
                    "--json",
                    "title,number,state,baseRefName,headRefName",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout.strip())

            # Alternative: search for PRs with this branch
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "list",
                    "--head",
                    branch_name,
                    "--json",
                    "title,number,state,baseRefName",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if result.returncode == 0 and result.stdout.strip():
                prs = json.loads(result.stdout.strip())
                if prs:
                    return prs[0]  # Return first matching PR

            return None
        except:
            return None

    def calculate_proximity(self, target: str, branch: str) -> int:
        """
        Calculate proximity score between target and branch.

        Proximity is based on the number of commits between the merge base
        and the branch head. Lower values mean closer proximity.

        Args:
            target: Target branch/ref.
            branch: Branch to compare.

        Returns:
            Proximity score (lower = closer).
        """
        merge_base = self.get_merge_base(target, branch)
        if not merge_base:
            return 999  # Very far if no common ancestor

        try:
            # Count commits between merge base and branch
            out = self._run(
                ["git", "rev-list", "--count", f"{merge_base}..{branch}"], check=False
            )
            distance = int(out) if out and out.isdigit() else 0
            return distance
        except:
            return 999

    def get_merge_parents(self, commit_hash: str) -> List[str]:
        """
        Get the parent commits of a merge commit.

        Args:
            commit_hash: Git commit hash.

        Returns:
            List of parent commit hashes.
        """
        try:
            out = self._run(["git", "cat-file", "-p", commit_hash], check=False)
            parents = []
            for line in out.splitlines():
                if line.startswith("parent "):
                    parents.append(line.split()[1])
            return parents
        except:
            return []

    # ========================================================================
    # Additional Utility Functions (compatibility with git_utils.py)
    # ========================================================================

    def ref_exists(self, ref: str) -> bool:
        """Check if a ref exists."""
        if not ref:
            return False
        try:
            return bool(
                self._run(
                    ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], check=False
                )
            )
        except:
            return False

    def resolve(self, ref: str) -> str:
        """Resolve a ref to a full commit hash."""
        if not ref:
            return ref
        if self.ref_exists(ref):
            return ref
        rr = f"{self.remote}/{ref}"
        return rr if self.ref_exists(rr) else ref

    @lru_cache(maxsize=None)
    def commit_distance(self, a: str, b: str) -> Optional[int]:
        """Get the number of commits between two refs."""
        out = self._run(
            ["git", "rev-list", "--count", f"{self.resolve(a)}..{self.resolve(b)}"],
            check=False,
        )
        return int(out) if out and out.isdigit() else None

    def merge_commits_between(self, root: str, branch: str) -> List[str]:
        """Get merge commits between root and branch."""
        out = self._run(
            [
                "git",
                "log",
                "--merges",
                "--format=%H",
                f"{self.resolve(root)}..{self.resolve(branch)}",
            ],
            check=False,
        )
        return out.splitlines() if out else []

    @lru_cache(maxsize=None)
    def patch_ids_between(self, root: str, branch: str) -> set:
        """Get patch IDs between root and branch."""
        log = self._run(
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


# Create a default instance for convenience
def get_git_core(repo_path: Optional[str] = None) -> GitCore:
    """Get a GitCore instance for the current repository."""
    return GitCore(repo_path)


if __name__ == "__main__":
    # Quick test
    git = get_git_core()
    print(f"Git repository: {git.repo_path}")
    print(f"Remote refs: {git.get_remote_refs()[:5]}...")  # First 5 refs
