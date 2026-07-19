#!/usr/bin/env python3
"""Jules PR Triage — Automated PR review pipeline for GitHub repositories.

Usage:
    python scripts/jules_pr_triage.py --repo OWNER/REPO
    python scripts/jules_pr_triage.py --repo OWNER/REPO --dry-run

This script automates the PR review checklist from JULES_PR_HANDOFF.md:
  1. Fetches open PRs via `gh` CLI
  2. Runs 3 instant-reject checks (checks #2, #3, #8 from the handoff doc)
  3. Builds a file-overlap conflict map between PRs
  4. Outputs a merge-order recommendation (security > bugs > tests > features > chores)

Requirements:
  - `gh` CLI authenticated (or GH_TOKEN env var set)
  - The repo must be cloned locally with `main` branch available
  - All PR branches must be fetchable (run `git fetch --all` first)

Reference: JULES_PR_HANDOFF.md "Quick Reference: What to Check on Every Jules PR"
  - Check #2: Build artefacts (.egg-info, /build/, /dist/, __pycache__)
  - Check #3: Shell variable paths in pyproject.toml (${...}, $PWD, $PROJECT_ROOT)
  - Check #8: analysis/ notebooks modified (Phase 0 is read-only)
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any


def run_cmd(cmd: list[str], capture: bool = True, check: bool = False) -> subprocess.CompletedProcess:
    """Run a subprocess command, returning CompletedProcess."""
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=check,
    )


def fetch_open_prs(repo: str) -> list[dict[str, Any]]:
    """Fetch open PRs from GitHub using `gh` CLI.

    Returns a list of dicts with keys: number, title, headRefName, author.
    Falls back to GH_TOKEN + urllib if `gh` is not available.
    """
    # Try gh CLI first
    result = run_cmd([
        "gh", "pr", "list",
        "--repo", repo,
        "--state", "open",
        "--json", "number,title,headRefName,author,labels",
        "--limit", "100",
    ])
    if result.returncode == 0 and result.stdout.strip():
        return json.loads(result.stdout)

    # Fallback: use urllib with GH_TOKEN
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: Neither `gh` CLI nor GH_TOKEN available.", file=sys.stderr)
        sys.exit(1)

    import urllib.request

    url = f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=100"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())

    return [
        {
            "number": pr["number"],
            "title": pr["title"],
            "headRefName": pr["head"]["ref"],
            "author": {"login": pr["user"]["login"]},
            "labels": [{"name": lb["name"]} for lb in pr.get("labels", [])],
        }
        for pr in data
    ]


def fetch_branches() -> None:
    """Ensure all remote branches are available locally."""
    run_cmd(["git", "fetch", "--all", "--quiet"])


def get_diff_files(branch: str) -> list[str]:
    """Get list of files changed in branch vs main."""
    result = run_cmd(["git", "diff", f"main...{branch}", "--name-only"])
    if result.returncode != 0:
        return []
    return [f for f in result.stdout.strip().splitlines() if f]


def check_build_artefacts(branch: str) -> list[str]:
    """Check #2 from JULES_PR_HANDOFF.md: Build artefacts in diff.

    Instant-reject if .egg-info, /build/, /dist/, or __pycache__ appear.
    """
    result = run_cmd(["git", "diff", f"main...{branch}", "--name-only"])
    if result.returncode != 0:
        return []
    violations = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if (".egg-info" in line or "/build/" in line or
                "/dist/" in line or "__pycache__" in line):
            violations.append(line)
    return violations


def check_shell_variable_paths(branch: str) -> list[str]:
    """Check #3 from JULES_PR_HANDOFF.md: Shell variable paths in pyproject.toml.

    Instant-reject if ${...}, $PWD, or $PROJECT_ROOT appear in pyproject.toml changes.
    """
    result = run_cmd([
        "git", "diff", f"main...{branch}", "--", "**/pyproject.toml"
    ])
    if result.returncode != 0:
        return []
    violations = []
    for line in result.stdout.splitlines():
        if not line.startswith("+"):
            continue
        if line.startswith("+++"):
            continue
        if "${" in line or "$PWD" in line or "$PROJECT_ROOT" in line:
            violations.append(line.strip())
    return violations


def check_analysis_notebooks(branch: str) -> list[str]:
    """Check #8 from JULES_PR_HANDOFF.md: analysis/ notebooks modified.

    Instant-reject if any .ipynb file under analysis/ is in the diff.
    Phase 0 is read-only for analysis notebooks.
    """
    result = run_cmd(["git", "diff", f"main...{branch}", "--name-only"])
    if result.returncode != 0:
        return []
    violations = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("analysis/") and line.endswith(".ipynb"):
            violations.append(line)
    return violations


def classify_pr(pr: dict[str, Any]) -> str:
    """Classify PR into priority tier based on title and labels.

    Priority order: security > bugs > tests > features > chores
    """
    title = pr.get("title", "").lower()
    labels = {lb.get("name", "").lower() for lb in pr.get("labels", [])}

    # Security tier
    if any(kw in title for kw in ("security", "vulnerability", "cve", "unsafe", "zip slip")):
        return "security"
    if "security" in labels:
        return "security"

    # Bug tier
    if any(kw in title for kw in ("fix", "bug", "patch", "hotfix", "regression")):
        return "bugs"
    if "bug" in labels or "bugfix" in labels:
        return "bugs"

    # Test tier
    if any(kw in title for kw in ("test", "spec", "coverage")):
        return "tests"
    if "test" in labels or "testing" in labels:
        return "tests"

    # Feature tier
    if any(kw in title for kw in ("feature", "add", "implement", "enhance", "new")):
        return "features"
    if "feature" in labels or "enhancement" in labels:
        return "features"

    # Default: chores
    return "chores"


TIER_PRIORITY = {"security": 0, "bugs": 1, "tests": 2, "features": 3, "chores": 4}


def build_conflict_map(pr_files: dict[int, list[str]]) -> dict[tuple[int, int], list[str]]:
    """Build a map of file overlaps between PRs.

    Returns {(pr_a, pr_b): [conflicting_files]} for all pairs with overlap.
    """
    conflicts: dict[tuple[int, int], list[str]] = {}
    pr_numbers = sorted(pr_files.keys())

    for i, pr_a in enumerate(pr_numbers):
        for pr_b in pr_numbers[i + 1:]:
            files_a = set(pr_files[pr_a])
            files_b = set(pr_files[pr_b])
            overlap = files_a & files_b
            if overlap:
                conflicts[(pr_a, pr_b)] = sorted(overlap)

    return conflicts


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Format a simple ASCII table."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))

    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_line = "|" + "|".join(f" {h:<{col_widths[i]}} " for i, h in enumerate(headers)) + "|"

    lines = [sep, header_line, sep]
    for row in rows:
        padded = []
        for i, cell in enumerate(row):
            w = col_widths[i] if i < len(col_widths) else len(cell)
            padded.append(f" {cell:<{w}} ")
        lines.append("|" + "|".join(padded) + "|")
    lines.append(sep)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Jules PR Triage — automated review pipeline per JULES_PR_HANDOFF.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--repo",
        default="MasumRab/jules",
        help="GitHub repo in owner/repo format",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be checked without running git commands against branches",
    )
    args = parser.parse_args()

    print(f"Jules PR Triage — {args.repo}")
    print("=" * 60)

    # Step 1: Fetch open PRs
    print("\n[1/4] Fetching open PRs...")
    prs = fetch_open_prs(args.repo)
    if not prs:
        print("  No open PRs found. Nothing to triage.")
        return

    print(f"  Found {len(prs)} open PR(s).")
    for pr in prs:
        author = pr.get("author", {}).get("login", "unknown")
        print(f"  - #{pr['number']}: {pr['title']} (by {author})")

    if args.dry_run:
        print("\n[dry-run] Would run instant-reject checks on branches:")
        for pr in prs:
            print(f"  - {pr['headRefName']}")
        print("\n[dry-run] Exiting without running checks.")
        return

    # Step 2: Fetch branches and run checks
    print("\n[2/4] Fetching branches and running instant-reject checks...")
    fetch_branches()

    results: list[dict[str, Any]] = []
    pr_files: dict[int, list[str]] = {}

    for pr in prs:
        branch = pr["headRefName"]
        pr_num = pr["number"]

        # Get changed files for conflict detection
        files = get_diff_files(branch)
        pr_files[pr_num] = files

        # Run 3 instant-reject checks
        artefacts = check_build_artefacts(branch)
        shell_vars = check_shell_variable_paths(branch)
        analysis_nbs = check_analysis_notebooks(branch)

        reject_reasons = []
        if artefacts:
            reject_reasons.append(f"Check #2: build artefacts ({len(artefacts)} files)")
        if shell_vars:
            reject_reasons.append(f"Check #3: shell variable paths ({len(shell_vars)} lines)")
        if analysis_nbs:
            reject_reasons.append(f"Check #8: analysis notebooks modified ({len(analysis_nbs)} files)")

        tier = classify_pr(pr)

        results.append({
            "number": pr_num,
            "title": pr["title"],
            "branch": branch,
            "tier": tier,
            "files_changed": len(files),
            "reject": bool(reject_reasons),
            "reject_reasons": reject_reasons,
            "artefacts": artefacts,
            "shell_vars": shell_vars,
            "analysis_nbs": analysis_nbs,
        })

    # Step 3: Build conflict map
    print("\n[3/4] Building file-overlap conflict map...")
    conflicts = build_conflict_map(pr_files)

    if conflicts:
        print(f"  Found {len(conflicts)} conflicting PR pair(s):")
        for (a, b), files in conflicts.items():
            print(f"  - PR #{a} <-> PR #{b}: {len(files)} shared file(s)")
            for f in files[:5]:
                print(f"      {f}")
            if len(files) > 5:
                print(f"      ... and {len(files) - 5} more")
    else:
        print("  No file overlaps detected.")

    # Determine which PRs have conflicts
    conflicting_prs: set[int] = set()
    for (a, b) in conflicts:
        conflicting_prs.add(a)
        conflicting_prs.add(b)

    # Step 4: Output results
    print("\n[4/4] Triage Results")
    print("=" * 60)

    # Instant-reject table
    rejects = [r for r in results if r["reject"]]
    if rejects:
        print("\n--- INSTANT REJECT (close without requesting changes) ---")
        print("Ref: JULES_PR_HANDOFF.md — 'If any of checks 2, 3, 8 are non-empty")
        print("     → close the PR immediately.'")
        print()
        rows = []
        for r in rejects:
            reasons = "; ".join(r["reject_reasons"])
            rows.append([f"#{r['number']}", r["title"][:40], reasons])
        print(format_table(["PR", "Title", "Reject Reason"], rows))
    else:
        print("\n  No instant-reject violations found.")

    # Merge-order recommendation
    print("\n--- MERGE ORDER RECOMMENDATION ---")
    print("Priority: security > bugs > tests > features > chores")
    print("Within tier: fewer file changes + no conflicts preferred\n")

    passable = [r for r in results if not r["reject"]]
    passable.sort(key=lambda r: (
        TIER_PRIORITY.get(r["tier"], 99),
        r["number"] in conflicting_prs,  # non-conflicting first
        r["files_changed"],
    ))

    if passable:
        rows = []
        for rank, r in enumerate(passable, 1):
            has_conflict = "YES" if r["number"] in conflicting_prs else "no"
            rows.append([
                str(rank),
                f"#{r['number']}",
                r["title"][:35],
                r["tier"],
                str(r["files_changed"]),
                has_conflict,
            ])
        print(format_table(
            ["Order", "PR", "Title", "Tier", "Files", "Conflicts"],
            rows,
        ))
    else:
        print("  All open PRs were instant-rejected. Nothing to merge.")

    # Conflict detail
    if conflicts and passable:
        print("\n--- CONFLICT DETAILS ---")
        print("These PRs modify the same files — merge one first, rebase the other:\n")
        for (a, b), files in conflicts.items():
            if any(r["number"] in (a, b) and not r["reject"] for r in results):
                print(f"  PR #{a} <-> PR #{b}:")
                for f in files:
                    print(f"    - {f}")
                print()

    # Summary
    print("--- SUMMARY ---")
    print(f"  Open PRs:        {len(prs)}")
    print(f"  Instant-reject:  {len(rejects)}")
    print(f"  Reviewable:      {len(passable)}")
    print(f"  Conflict pairs:  {len(conflicts)}")


if __name__ == "__main__":
    main()
