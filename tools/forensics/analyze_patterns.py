#!/usr/bin/env python3
"""
Analyze Jules session patterns: reuse, redundancy, and batch outcomes.

Groups sessions by PR + head SHA to detect duplicate runs, and
summarizes outcome distributions for forensics reports.

Usage:
    # As a library
    from tools.forensics.analyze_patterns import analyze_session_reuse
    result = analyze_session_reuse("EmailIntelligence")

    # As a CLI
    uv run python -m tools.forensics.analyze_patterns --repo EmailIntelligence
    uv run python -m tools.forensics.analyze_patterns --repo EmailIntelligence --json
"""

import argparse
import json
from collections import Counter
from typing import Any, Dict, List, Optional

from tools.api.jules_api_client import JulesAPIClient

# Session states considered "terminal" for outcome analysis
TERMINAL_STATES = {"COMPLETED", "FAILED"}


def _session_key(session: Dict[str, Any]) -> str:
    """Build a reuse-detection key from a session.

    Uses PR number + head SHA when available (strongest signal),
    falling back to title + branch (weaker, title-only runs).
    """
    pr = session.get("pullRequest") or {}
    pr_url = str(pr.get("url", "") or "")
    pr_num = pr_url.rstrip("/").split("/")[-1] if pr_url else "no-pr"

    # headSha appears under different keys across API versions
    sha = (
        session.get("headSha")
        or session.get("head_sha")
        or (session.get("sourceContext") or {}).get("headSha")
        or "no-sha"
    )
    if pr_num != "no-pr" and sha != "no-sha":
        return f"pr:{pr_num}::sha:{sha}"

    branch = session.get("headBranch") or session.get("head_branch") or "no-branch"
    title = session.get("title") or "untitled"
    return f"branch:{branch}::title:{title}"


def _session_id(session: Dict[str, Any]) -> str:
    return str(session.get("name", "")).replace("sessions/", "")


def _session_repo(session: Dict[str, Any]) -> str:
    """Extract the repo name from a session.

    The API returns repo identity in ``sourceContext.source`` as
    ``sources/github/<owner>/<repo>`` — there is no top-level
    ``repository`` field.
    """
    source = str((session.get("sourceContext") or {}).get("source", "") or "")
    # sources/github/<owner>/<repo> → <repo>
    parts = source.rstrip("/").split("/")
    return parts[-1] if len(parts) >= 2 else ""


def _session_in_repo(session: Dict[str, Any], repo: str) -> bool:
    """Case-insensitive repo match against sourceContext.source."""
    return repo.lower() in _session_repo(session).lower()


def analyze_session_reuse(
    repo: str,
    sessions: Optional[List[Dict[str, Any]]] = None,
    client: Optional[JulesAPIClient] = None,
    max_results: int = 100,
) -> Dict[str, Any]:
    """Detect session reuse and redundant runs for a repo.

    Args:
        repo: Repository name to filter by (substring match against
            the session's repository field).
        sessions: Pre-fetched session list. When omitted, fetched
            from the live API (capped at ``max_results``).
        client: Optional client for fetching.
        max_results: Session fetch cap when fetching from the API.
            Full enumeration can take minutes on large accounts.

    Returns:
        Dict with duplicate groups, outcome distribution, and totals.
    """
    if sessions is None:
        client = client or JulesAPIClient()
        all_sessions = list(
            client.list_sessions(page_size=50, max_results=max_results)
        )
        sessions = [s for s in all_sessions if _session_in_repo(s, repo)]

    # Group by reuse key
    by_key: Dict[str, List[Dict[str, Any]]] = {}
    for s in sessions:
        by_key.setdefault(_session_key(s), []).append(s)

    duplicates = {
        key: [
            {
                "session_id": _session_id(s),
                "state": s.get("state", "UNKNOWN"),
                "title": s.get("title", ""),
                "created": s.get("createTime", ""),
            }
            for s in group
        ]
        for key, group in by_key.items()
        if len(group) > 1
    }

    # Outcome distribution
    state_counts = Counter(s.get("state", "UNKNOWN") for s in sessions)

    return {
        "repo": repo,
        "total_sessions": len(sessions),
        "duplicate_groups": len(duplicates),
        "duplicates": duplicates,
        "state_distribution": dict(state_counts),
        # Redundancy signal: sessions that reran an already-terminal key
        "redundant_after_terminal": sum(
            1
            for group in by_key.values()
            if len(group) > 1
            and any(g.get("state") in TERMINAL_STATES for g in group)
        ),
    }


def analyze_batch_outcomes(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize outcomes for a batch of sessions.

    Useful for post-batch forensics: how many completed, failed,
    or are still open, and which failed.
    """
    state_counts = Counter(s.get("state", "UNKNOWN") for s in sessions)
    failed = [
        {"session_id": _session_id(s), "title": s.get("title", "")}
        for s in sessions
        if s.get("state") == "FAILED"
    ]
    return {
        "total": len(sessions),
        "state_distribution": dict(state_counts),
        "failed_sessions": failed,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze session patterns (reuse, redundancy, outcomes)"
    )
    parser.add_argument("--repo", help="Repository name to analyze")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--limit", type=int, default=200,
                        help="Max sessions to fetch (default 200)")
    args = parser.parse_args()

    if not args.repo:
        parser.error("--repo is required")

    client = JulesAPIClient()
    result = analyze_session_reuse(args.repo, client=client)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"Repo: {result['repo']}")
        print(f"Total sessions: {result['total_sessions']}")
        print(f"Duplicate groups: {result['duplicate_groups']}")
        print(f"Redundant-after-terminal: {result['redundant_after_terminal']}")
        print("State distribution:")
        for state, count in sorted(result["state_distribution"].items()):
            print(f"  {state}: {count}")
        if result["duplicates"]:
            print("\nDuplicate groups:")
            for key, sessions in result["duplicates"].items():
                print(f"  {key}")
                for s in sessions:
                    print(f"    - {s['session_id']} ({s['state']}) {s['title'][:60]}")


if __name__ == "__main__":
    main()
