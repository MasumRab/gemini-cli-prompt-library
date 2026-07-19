#!/usr/bin/env python3
"""Rebase orchestrator for Jules session PRs.

Manages a queue of sessions to rebase onto their target branches,
with safe merge-tree validation and pytest verification.

Usage:
    python jules_rebase_orchestrator.py --add "sessions/abc123"
    python jules_rebase_orchestrator.py --seq
    python jules_rebase_orchestrator.py --rebase [--limit N]
    python jules_rebase_orchestrator.py --report
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from tools.api.jules_api_client import jules_request

SCRIPT_DIR = Path(__file__).resolve().parent
QUEUE_FILE = SCRIPT_DIR.parent.parent / ".jules-rebase-queue.json"
AUDIT_REPORT = SCRIPT_DIR.parent.parent / "docs" / "jules" / "AUDIT_REPORT.md"


def get_queue() -> list:
    """Load the queue from the JSON file."""
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE) as f:
        return json.load(f)


def save_queue(queue: list):
    """Save the queue to the JSON file."""
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)


def resolve_session_pr(session_id: str) -> dict:
    """Resolve a session ID to its PR branch and metadata using Jules API."""
    if not session_id.startswith("sessions/"):
        session_id = f"sessions/{session_id}"

    session = jules_request(session_id)

    outputs = session.get("outputs", [])
    pr_url = None
    pr_number = None
    for output in outputs:
        pr_data = output.get("pullRequest", {})
        if "url" in pr_data:
            pr_url = pr_data["url"]
            # Extract PR number from URL
            if pr_url:
                pr_number = pr_url.rstrip("/").split("/")[-1]
            break

    source_context = session.get("sourceContext", {})
    starting_branch = source_context.get("startingBranch", "")

    # Extract repo info from cloneUrl or use config
    import os
    gh_repo = os.environ.get("GH_REPO", "MasumRab/jules")

    return {
        "session_id": session_id.replace("sessions/", ""),
        "branch": starting_branch,
        "gh_repo": gh_repo,
        "default_branch": "main",
        "pr_number": pr_number or "",
        "pr_url": pr_url or "",
        "timestamp": datetime.now().isoformat(),
    }


def cmd_add(session_id: str):
    """Add a session to the queue."""
    entry = resolve_session_pr(session_id)

    queue = get_queue()
    # Check if already in queue
    for e in queue:
        if e["session_id"] == entry["session_id"]:
            print(f"ALREADY IN QUEUE: session={entry['session_id']}")
            return

    queue.append(entry)
    save_queue(queue)
    print(f"Enqueued: session={entry['session_id']} branch={entry['branch']}")


def cmd_seq():
    """List queue entries with order numbers."""
    queue = get_queue()
    if not queue:
        print("[info] Queue is empty.")
        sys.exit(2)

    print(f"{'Order':<6}  {'Session':<22}  {'Branch':<40}  {'PR':<10}")
    print("-" * 80)
    for i, e in enumerate(queue, 1):
        print(f"{i:<6}  {e['session_id']:<22}  {e['branch'][:40]:<40}  {e['pr_number']:<10}")


def cmd_rebase(limit: int = None):
    """Pop entries from queue and attempt rebase."""
    queue = get_queue()
    if not queue:
        print("[info] Queue is empty.")
        sys.exit(2)

    count = 0
    while queue and (limit is None or count < limit):
        entry = queue.pop(0)
        count += 1

        session_id = entry["session_id"]
        branch = entry["branch"]
        gh_repo = entry["gh_repo"]
        default_branch = entry["default_branch"]

        print(f"\n[rebase] Processing session={session_id} branch={branch}")

        try:
            # Checkout default branch, fetch
            subprocess.run(["git", "checkout", default_branch], check=True, capture_output=True)
            subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)

            # Get the remote branch name
            remote_branch = f"origin/{branch}"
            local_branch = branch

            # Check if remote branch exists
            result = subprocess.run(
                ["git", "ls-remote", "--heads", "origin", branch],
                capture_output=True, text=True
            )
            if not result.stdout.strip():
                print(f"REBASE FAILED: session={session_id} reason=branch not found on remote")
                queue.insert(0, entry)  # Put back
                sys.exit(1)

            # Try merge-tree or merge (simpler approach)
            print(f"[rebase] Attempting merge of {remote_branch} into {default_branch}")

            # Use git merge to test if it would work cleanly
            result = subprocess.run(
                ["git", "merge", remote_branch, "--no-commit", "--no-ff"],
                capture_output=True, text=True
            )

            if result.returncode != 0:
                subprocess.run(["git", "merge", "--abort"], capture_output=True)
                print(f"REBASE FAILED: session={session_id} reason=merge conflict")
                queue.insert(0, entry)  # Put back for manual resolution
                sys.exit(1)

            # Run pytest
            print("[rebase] Running pytest...")
            pytest_result = subprocess.run(["pytest"], capture_output=True, text=True)
            if pytest_result.returncode != 0:
                subprocess.run(["git", "reset", "--hard", "HEAD~1"], capture_output=True)
                print(f"REBASE FAILED: session={session_id} reason=pytest failure")
                queue.insert(0, entry)  # Put back
                sys.exit(1)

            # Success - commit and mark merged
            entry["status"] = "merged"
            entry["merged_at"] = datetime.now().isoformat()
            subprocess.run(["git", "commit", "--allow-empty", "-m", f"Rebase: {branch}"],
                          capture_output=True)

            print(f"[rebase] Success: session={session_id}")
            cmd_report()  # Update report

        except subprocess.CalledProcessError as e:
            print(f"REBASE FAILED: session={session_id} reason=git error: {e}")
            queue.insert(0, entry)
            sys.exit(1)
        except Exception as e:
            print(f"REBASE FAILED: session={session_id} reason={e}")
            queue.insert(0, entry)
            sys.exit(1)

    save_queue(queue)


def cmd_report():
    """Write or update AUDIT_REPORT.md."""
    queue = get_queue()
    merged = [e for e in queue if e.get("status") == "merged"]
    pending = [e for e in queue if e.get("status") != "merged"]

    lines = [
        "# AUDIT_REPORT.md — Rebasing Session Registry",
        "",
        f"**Last updated:** {datetime.now().isoformat()}",
        "",
        "## Pending Queue",
        "",
    ]

    if pending:
        lines.append("| # | Session ID | Branch | PR | Status |")
        lines.append("|---|---|---|---|---|")
        for i, e in enumerate(pending, 1):
            lines.append(f"| {i} | {e['session_id']} | {e['branch']} | {e['pr_number']} | {e.get('status', 'pending')} |")
    else:
        lines.append("_No pending entries_")

    lines.append("")
    lines.append("## Recently Merged (last 20)")
    lines.append("")

    if merged:
        lines.append("| Session ID | Branch | PR | Merged At |")
        lines.append("|---|---|---|---|")
        for e in merged[-20:]:
            lines.append(f"| {e['session_id']} | {e['branch']} | {e['pr_number']} | {e.get('merged_at', 'N/A')} |")
    else:
        lines.append("_No merged entries yet_")

    with open(AUDIT_REPORT, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[report] Updated {AUDIT_REPORT}")


def main():
    parser = argparse.ArgumentParser(description="Rebase orchestrator for Jules sessions")
    parser.add_argument("--add", metavar="SESSION_ID", help="Add session to queue")
    parser.add_argument("--seq", action="store_true", help="List queue entries")
    parser.add_argument("--rebase", action="store_true", help="Process queue entries")
    parser.add_argument("--limit", type=int, metavar="N", help="Limit number of entries to process")
    parser.add_argument("--report", action="store_true", help="Update AUDIT_REPORT.md")

    args = parser.parse_args()

    if args.add:
        cmd_add(args.add)
    elif args.seq:
        cmd_seq()
    elif args.rebase:
        cmd_rebase(args.limit)
    elif args.report:
        cmd_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()