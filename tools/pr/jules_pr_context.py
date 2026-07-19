#!/usr/bin/env python3
"""
Jules PR Context Aggregator
Extracts comprehensive PR context (comments, CI, conflicts, diff size) to inform Jules recovery prompts.
Requires `gh` CLI to be authenticated.
"""

import argparse
import json
import subprocess
import sys


# Priority levels for PR issues
PRIORITY_CRITICAL = 1  # Merge conflicts, CI failures, security issues
PRIORITY_HIGH = 2     # Failed tests, breaking changes
PRIORITY_MEDIUM = 3     # Warnings, style issues
PRIORITY_LOW = 4       # Documentation, cosmetic


def determine_priority(pr_info: dict, checks: str) -> tuple[int, str]:
    """
    Determine priority based on PR state and CI checks.
    Returns (priority_level, reason)
    """
    # Critical: Merge conflicts
    if pr_info.get("mergeable") == "CONFLICTING":
        return PRIORITY_CRITICAL, "Merge conflicts must be resolved"
    
    if pr_info.get("state") == "CLOSED":
        return PRIORITY_CRITICAL, "PR is closed"
    
    # High: CI failures
    if checks and "failure" in checks.lower():
        return PRIORITY_HIGH, "CI checks failing"
    
    # Medium: Warnings
    if checks and ("warning" in checks.lower() or "pending" in checks.lower()):
        return PRIORITY_MEDIUM, "CI checks have warnings or pending"
    
    # Low: Clean state
    return PRIORITY_LOW, "Ready for review"


def run_gh_api(endpoint):
    """Run gh api and return parsed JSON."""
    result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error calling GitHub API: {result.stderr}", file=sys.stderr)
        return None
    return json.loads(result.stdout)


def run_gh_cmd(args):
    """Run a gh command and return stdout."""
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Extract comprehensive PR context for Jules recovery."
    )
    parser.add_argument("pr_number", help="The PR number or branch name")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    pr_ref = args.pr_number

    if not args.json:
        print(f"Aggregating context for PR: {pr_ref}...\n")
        print("=" * 60)
        print("PR CONTEXT SUMMARY")
        print("=" * 60)

    # Fetch basic PR info & conflicts
    pr_info_str = run_gh_cmd(
        [
            "pr",
            "view",
            pr_ref,
            "--json",
            "number,title,state,mergeable,mergeStateStatus,additions,deletions,changedFiles",
        ]
    )
    if pr_info_str.startswith("Error:"):
        print(pr_info_str)
        sys.exit(1)

    pr_info = json.loads(pr_info_str)

    checks = run_gh_cmd(["pr", "checks", pr_ref])
    comments = run_gh_cmd(["pr", "view", pr_ref, "--comments"])

    # Determine priority
    priority, reason = determine_priority(pr_info, checks or "")
    
    priority_label = {
        1: "CRITICAL",
        2: "HIGH", 
        3: "MEDIUM",
        4: "LOW"
    }.get(priority, "UNKNOWN")

    if args.json:
        output_data = {
            "pr_info": pr_info, 
            "checks": checks, 
            "comments": comments,
            "priority": priority,
            "priority_label": priority_label,
            "priority_reason": reason
        }
        print(json.dumps(output_data, indent=2))
        return

    print("\n[PRIORITY]")
    print(f"Level: {priority_label} ({priority})")
    print(f"Reason: {reason}")

    print("\n[METRICS]")
    print(f"Title: {pr_info.get('title')}")
    print(f"State: {pr_info.get('state')}")
    print(f"Files Changed: {pr_info.get('changedFiles')}")
    print(f"Additions: +{pr_info.get('additions')} | Deletions: -{pr_info.get('deletions')}")

    print("\n[MERGE STATUS]")
    print(f"Mergeable: {pr_info.get('mergeable')}")
    print(f"Status: {pr_info.get('mergeStateStatus')}")
    if pr_info.get("mergeable") == "CONFLICTING":
        print(">> WARNING: Branch has merge conflicts. Jules must resolve these manually.")

    print("\n[CI CHECKS]")
    print(checks if checks else "No CI checks found or all passed.")

    print("\n[REVIEW COMMENTS & THREADS]")
    print(comments if comments else "No comments found.")

    print("\n" + "=" * 60)
    print("Instructions for Jules Prompting:")
    print(
        "Copy the relevant failing CI logs or review comments above and paste them into jules_send_message.py."
    )
    print(
        "If mergeable is CONFLICTING, explicitly instruct Jules to run 'git merge main' and resolve markers."
    )


if __name__ == "__main__":
    main()
