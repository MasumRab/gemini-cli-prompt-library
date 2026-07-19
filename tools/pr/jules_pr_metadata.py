#!/usr/bin/env python3
"""Fetch PR metadata from GitHub for sessions that have pr_url.

Reads the local Jules store, resolves pr_url → owner/repo/number,
calls ``gh pr view`` per PR (1 API call per PR), and outputs
a categorized table sorted by oldest session first.

Usage:
    uv run python -m tools.pr.jules_pr_metadata --limit 10
    uv run python -m tools.pr.jules_pr_metadata --state OPEN --sort additions
    uv run python -m tools.pr.jules_pr_metadata --sessions 2362388763594963052 1618067056155335146
"""

import argparse
import json
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

from tools.store.jules_store import JulesSessionStore


PR_URL_RE = re.compile(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)")


def parse_pr_url(url: str) -> Optional[Tuple[str, str, int]]:
    m = PR_URL_RE.search(url)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    return None


def fetch_pr_metadata(owner: str, repo: str, number: int) -> Optional[Dict[str, Any]]:
    fields = [
        "state", "title", "body", "additions", "deletions",
        "changedFiles", "mergeable", "labels", "createdAt",
        "updatedAt", "mergedAt", "headRefName", "baseRefName",
        "reviews",
    ]
    cmd = [
        "gh", "pr", "view", str(number),
        "--repo", f"{owner}/{repo}",
        "--json", ",".join(fields),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            print(f"  [warn] gh failed for {owner}/{repo}#{number}: {r.stderr.strip()}", file=sys.stderr)
            return None
        return json.loads(r.stdout)
    except subprocess.TimeoutExpired:
        print(f"  [warn] gh timed out for {owner}/{repo}#{number}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"  [warn] bad JSON for {owner}/{repo}#{number}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Fetch PR metadata for Jules sessions")
    parser.add_argument("--limit", type=int, default=20, help="Max sessions to process (0 = all)")
    parser.add_argument("--state", choices=["OPEN", "CLOSED", "MERGED", "all"], default=None,
                        help="Filter by PR state")
    parser.add_argument("--sort", choices=["oldest", "additions", "deletions", "changedFiles", "updated"],
                        default="oldest", help="Sort order")
    parser.add_argument("--min-changes", type=int, default=0,
                        help="Minimum additions+deletions to show")
    parser.add_argument("--min-files", type=int, default=0,
                        help="Minimum changedFiles to show")
    parser.add_argument("--label", type=str, default=None,
                        help="Only PRs matching this label (substring match)")
    parser.add_argument("--json", action="store_true", help="Output as JSON lines")
    parser.add_argument("--sessions", nargs="*", default=None,
                        help="Specific session IDs (space-separated). If omitted, reads from store.")
    args = parser.parse_args()

    store = JulesSessionStore()

    if args.sessions:
        rows = []
        for sid in args.sessions:
            s = store.get_session(sid)
            if s:
                rows.append(s)
            else:
                print(f"[warn] session {sid} not in store", file=sys.stderr)
    else:
        rows = store.list_sessions(limit=10000)

    # Filter to sessions with pr_url
    candidates = [r for r in rows if r.get("pr_url")]
    if not candidates:
        print("No sessions with pr_url found.")
        return

    # Sort by create_time (oldest first)
    sort_key = "create_time" if args.sort == "oldest" else args.sort
    reverse = args.sort != "oldest"
    candidates.sort(key=lambda r: r.get(sort_key, "") or "", reverse=reverse)
    candidates = candidates[:args.limit] if args.limit else candidates

    results: List[Dict[str, Any]] = []
    for row in candidates:
        parsed = parse_pr_url(row["pr_url"])
        if not parsed:
            continue
        owner, repo, number = parsed
        pr = fetch_pr_metadata(owner, repo, number)
        if pr is None:
            continue

        total_changes = pr.get("additions", 0) + pr.get("deletions", 0)
        if total_changes < args.min_changes:
            continue
        if pr.get("changedFiles", 0) < args.min_files:
            continue
        if args.label and not any(args.label.lower() in (l.get("name", "") or "").lower() for l in pr.get("labels", [])):
            continue
        if args.state and args.state != "all" and (pr.get("state") or "").upper() != args.state:
            continue

        results.append({
            "session_id": row["session_id"],
            "session_title": (row.get("title") or "")[:80],
            "session_state": row.get("state", "?"),
            "session_created": row.get("create_time", ""),
            "pr_number": number,
            "pr_repo": f"{owner}/{repo}",
            "pr_url": row["pr_url"],
            "pr_state": pr.get("state", "?"),
            "pr_title": (pr.get("title") or "")[:80],
            "pr_additions": pr.get("additions", 0),
            "pr_deletions": pr.get("deletions", 0),
            "pr_changedFiles": pr.get("changedFiles", 0),
            "pr_mergeable": pr.get("mergeable", "?"),
            "pr_labels": [l.get("name", "") for l in pr.get("labels", [])],
            "pr_created": pr.get("createdAt", ""),
            "pr_updated": pr.get("updatedAt", ""),
            "pr_reviews": len(pr.get("reviews", [])),
        })

    if args.json:
        for r in results:
            print(json.dumps(r))
    else:
        if not results:
            print("No matching PRs found.")
            return
        header = f"{'Session ID':<25} {'PR #':<8} {'State':<10} {'Changes':<10} {'Files':<6} {'Mergeable':<10} {'Labels':<20} {'Session Created':<25} Title"
        print(header)
        print("-" * len(header))
        for r in results:
            labels = ",".join(r["pr_labels"][:3])[:18]
            changes = f"+{r['pr_additions']}/-{r['pr_deletions']}"
            created = (r["session_created"] or "")[:19]
            print(
                f'{r["session_id"]:<25} '
                f'#{r["pr_number"]:<6} '
                f'{r["pr_state"]:<10} '
                f'{changes:<10} '
                f'{r["pr_changedFiles"]:<6} '
                f'{str(r["pr_mergeable"]):<10} '
                f'{labels:<20} '
                f'{created:<25} '
                f'{r["session_title"][:50]}'
            )
        print(f"\n{len(results)} PRs shown (out of {len(candidates)} scanned)")


if __name__ == "__main__":
    main()
