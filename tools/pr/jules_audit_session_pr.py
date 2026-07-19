#!/usr/bin/env python3
"""Refactored: Automated PR safety auditor for Jules sessions."""

import argparse
import subprocess
import sys
from typing import List

from tools.api.jules_api_client import JulesAPIClient

def run_cmd(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)

class PRSafetyAuditor:
    def __init__(self, branch_name: str, base_branch: str = None):
        self.branch_name = branch_name
        # Dynamically detect default branch instead of hardcoding "origin/main"
        if base_branch is None:
            result = run_cmd(["git", "rev-parse", "--abbrev-ref", "origin/HEAD"])
            if result.returncode == 0:
                self.base_branch = result.stdout.strip()
            else:
                # Fallback to common default branch names
                for candidate in ["origin/main", "origin/master", "origin/develop"]:
                    res = run_cmd(["git", "rev-parse", "--verify", candidate])
                    if res.returncode == 0:
                        self.base_branch = candidate
                        break
                else:
                    self.base_branch = "origin/main"
        else:
            self.base_branch = base_branch
        self.failures = []
        self.warnings = []

    def audit(self):
        print(f"\n[AUDIT] Starting safety audit for branch: {self.branch_name}")
        print("=" * 60)

        self.check_build_artefacts()
        self.check_shell_variables()
        self.check_readonly_files()
        self.check_stub_replacements()
        self.check_missing_tests()

        print("\nAudit Summary:")
        if not self.failures and not self.warnings:
            print("✅ All safety checks passed.")
        else:
            for f in self.failures:
                print(f"❌ FAILURE: {f}")
            for w in self.warnings:
                print(f"⚠️ WARNING: {w}")

        print("=" * 60)
        return len(self.failures) == 0

    def check_build_artefacts(self):
        res = run_cmd(["git", "diff", f"{self.base_branch}...HEAD", "--name-only"])
        if res.returncode != 0:
            self.warnings.append(f"Failed to run git diff for build artefacts check (exit {res.returncode})")
            return
        artefacts = [
            line for line in res.stdout.splitlines()
            if any(x in line for x in [".egg-info", "/build/", "/dist/", "__pycache__", ".pyc"])
        ]
        if artefacts:
            self.failures.append(f"Build artefacts found: {', '.join(artefacts[:3])}...")

    def check_shell_variables(self):
        res = run_cmd(["git", "diff", f"{self.base_branch}...HEAD", "--", "**pyproject.toml", "**/*.sh"])
        if res.returncode != 0:
            self.warnings.append(f"Failed to run git diff for shell variables check (exit {res.returncode})")
            return
        if any(x in res.stdout for x in ["$PWD", "$PROJECT_ROOT", "${"]):
            self.failures.append("Potentially unexpanded shell variables found in config or scripts.")

    def check_readonly_files(self):
        res = run_cmd(["git", "diff", f"{self.base_branch}...HEAD", "--name-only"])
        if res.returncode != 0:
            self.warnings.append(f"Failed to run git diff for readonly files check (exit {res.returncode})")
            return
        readonly = [line for line in res.stdout.splitlines() if line.startswith("analysis/") and line.endswith(".ipynb")]
        if readonly:
            self.failures.append(f"Modified read-only analysis notebooks: {', '.join(readonly)}")

    def check_stub_replacements(self):
        res = run_cmd(["git", "diff", f"{self.base_branch}...HEAD"])
        if res.returncode != 0:
            self.warnings.append(f"Failed to run git diff for stub check (exit {res.returncode})")
            return
        if "TODO: implement" in res.stdout.lower() or "pass  # stub" in res.stdout.lower():
            self.warnings.append("Possible stub implementation detected.")

    def check_missing_tests(self):
        res = run_cmd(["git", "diff", f"{self.base_branch}...HEAD", "--name-only"])
        if res.returncode != 0:
            self.warnings.append(f"Failed to run git diff for missing tests check (exit {res.returncode})")
            return
        files = res.stdout.splitlines()
        code_files = [f for f in files if f.endswith(".py") and not f.startswith("tests/") and "test" not in f]
        test_files = [f for f in files if "test" in f.lower()]

        if code_files and not test_files:
            self.warnings.append("Code changes detected without corresponding test changes.")

def main():
    parser = argparse.ArgumentParser(description="Automated PR safety auditor")
    parser.add_argument("--session", help="Session ID to audit")
    parser.add_argument("--branch", help="Specific branch to audit")
    args = parser.parse_args()

    if args.session:
        client = JulesAPIClient()
        session = client.get_session(args.session)
        # The Jules API PullRequest object only has url, title, description (no headRef).
        # To determine the branch to audit, use sourceContext.githubRepoContext.startingBranch.
        source_context = session.get("sourceContext", {})
        github_ctx = source_context.get("githubRepoContext", {})
        pr_branch = github_ctx.get("startingBranch")
        if not pr_branch:
            print(f"No branch found for session {args.session}")
            sys.exit(0)
        branch_to_audit = pr_branch
    elif args.branch:
        branch_to_audit = args.branch
    else:
        print("Error: Must provide --session or --branch")
        sys.exit(1)

    print(f"Fetching origin to audit {branch_to_audit}...")
    run_cmd(["git", "fetch", "origin"])

    auditor = PRSafetyAuditor(branch_to_audit)
    success = auditor.audit()

    if not success:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
