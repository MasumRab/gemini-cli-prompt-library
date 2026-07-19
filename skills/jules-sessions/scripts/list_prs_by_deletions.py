#!/usr/bin/env python3
"""
List GitHub PRs with significant deletions (>-300 lines).

Usage:
    python list_prs_by_deletions.py [--limit N] [--threshold T]

Options:
    --limit N      Number of PRs to fetch (default: 100)
    --threshold T  Deletion threshold (default: 300)
"""

import argparse
import json
import subprocess
import sys
from typing import List, Dict, Any


def run_gh_command(args: List[str]) -> Dict[str, Any]:
    """Run a gh CLI command and return JSON output."""
    cmd = ["gh"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def get_prs(limit: int = 100, state: str = "open") -> List[Dict[str, Any]]:
    """Fetch PRs from GitHub API."""
    fields = [
        "number",
        "title",
        "headRefName",
        "state",
        "createdAt",
        "additions",
        "deletions",
        "changedFiles"
    ]

    result = run_gh_command([
        "pr", "list",
        "--limit", str(limit),
        "--state", state,
        "--json", ",".join(fields)
    ])

    return result


def filter_prs_by_deletions(prs: List[Dict[str, Any]], threshold: int) -> List[Dict[str, Any]]:
    """Filter PRs with deletions greater than threshold."""
    return [pr for pr in prs if pr.get("deletions", 0) > threshold]


def format_pr(pr: Dict[str, Any]) -> str:
    """Format PR information for display."""
    number = pr["number"]
    title = pr["title"][:60] + "..." if len(pr["title"]) > 60 else pr["title"]
    branch = pr["headRefName"]
    additions = pr.get("additions", 0)
    deletions = pr.get("deletions", 0)
    files = pr.get("changedFiles", 0)

    # Calculate net change
    net_change = additions - deletions

    return (
        f"PR #{number}: {title}\n"
        f"  Branch: {branch}\n"
        f"  Changes: +{additions}/-{deletions} (net: {net_change:+d}) in {files} files\n"
    )


def main():
    parser = argparse.ArgumentParser(
        description="List GitHub PRs with significant deletions"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of PRs to fetch (default: 100)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=300,
        help="Deletion threshold (default: 300)"
    )
    parser.add_argument(
        "--state",
        choices=["open", "closed", "merged", "all"],
        default="open",
        help="PR state to filter by (default: open)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    print(f"Fetching up to {args.limit} PRs with state='{args.state}'...")
    print(f"Filtering for deletions > {args.threshold}\n")

    try:
        prs = get_prs(limit=args.limit, state=args.state)
        filtered_prs = filter_prs_by_deletions(prs, args.threshold)

        # Sort by deletions descending
        filtered_prs.sort(key=lambda x: x.get("deletions", 0), reverse=True)

        if args.json:
            print(json.dumps(filtered_prs, indent=2))
        else:
            if not filtered_prs:
                print(f"No PRs found with deletions > {args.threshold}")
                return

            print(f"Found {len(filtered_prs)} PR(s) with deletions > {args.threshold}:\n")
            print("=" * 80)
            for pr in filtered_prs:
                print(format_pr(pr))
                print("-" * 80)

            # Summary statistics
            total_deletions = sum(pr.get("deletions", 0) for pr in filtered_prs)
            total_additions = sum(pr.get("additions", 0) for pr in filtered_prs)
            total_files = sum(pr.get("changedFiles", 0) for pr in filtered_prs)

            print(f"\nSummary:")
            print(f"  Total PRs: {len(filtered_prs)}")
            print(f"  Total additions: +{total_additions}")
            print(f"  Total deletions: -{total_deletions}")
            print(f"  Total files changed: {total_files}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
