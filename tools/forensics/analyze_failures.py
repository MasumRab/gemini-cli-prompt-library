#!/usr/bin/env python3
"""
Analyze failed Jules sessions for forensics reports.

Extracts error-bearing activities and session-level failure state,
producing a structured dict suitable for report generation or direct
inspection.

Usage:
    # As a library
    from tools.forensics.analyze_failures import analyze_session_failure
    result = analyze_session_failure("596003508416904399")

    # As a CLI
    uv run python -m tools.forensics.analyze_failures 596003508416904399
    uv run python -m tools.forensics.analyze_failures --json 596003508416904399
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from tools.api.jules_api_client import JulesAPIClient

# Activity types that indicate errors, per REST API reference
ERROR_ACTIVITY_TYPES = {"commandExecutionFailed", "toolError"}
ERROR_TEXT_MARKERS = ("error", "failed", "exception", "traceback")


def _is_error_activity(activity: Dict[str, Any]) -> bool:
    """Heuristic error detection for an activity.

    An activity is error-bearing when:
      - its type is a known error type, OR
      - its text contains an error marker (case-insensitive).
    """
    act_type = str(activity.get("type", "") or "")
    if act_type in ERROR_ACTIVITY_TYPES:
        return True

    text = str(activity.get("text", "") or "").lower()
    return any(marker in text for marker in ERROR_TEXT_MARKERS)


def analyze_session_failure(
    session_id: str, client: Optional[JulesAPIClient] = None
) -> Dict[str, Any]:
    """Analyze a session for failure evidence.

    Args:
        session_id: The Jules session ID (with or without ``sessions/`` prefix).
        client: Optional pre-constructed client (reuses auth/store config).

    Returns:
        Dict with session state, error activities, and totals.
    """
    client = client or JulesAPIClient()
    session = client.get_session(session_id)
    activities = list(client.list_activities(session_id, page_size=100))

    errors = [a for a in activities if _is_error_activity(a)]

    return {
        "session_id": session_id,
        "state": session.get("state"),
        "title": session.get("title"),
        "errors": errors,
        "total_activities": len(activities),
        "error_count": len(errors),
        # Session-level error field, when the API provides one
        "session_error": session.get("error"),
    }


def analyze_failed_sessions(
    sessions: List[Dict[str, Any]],
    client: Optional[JulesAPIClient] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Analyze the most recent FAILED sessions.

    Args:
        sessions: Pre-fetched session list (filtered to FAILED upstream,
            or any list — FAILED entries are selected here).
        client: Optional client for activity fetching.
        limit: Max sessions to analyze.

    Returns:
        List of per-session failure analyses, most recent first.
    """
    client = client or JulesAPIClient()
    failed = [s for s in sessions if s.get("state") == "FAILED"]

    results = []
    for sess in failed[:limit]:
        sid = str(sess.get("name", "")).replace("sessions/", "")
        if not sid:
            continue
        try:
            results.append(analyze_session_failure(sid, client=client))
        except Exception as exc:  # one bad session should not kill the batch
            results.append({
                "session_id": sid,
                "state": "FAILED",
                "error": f"analysis failed: {exc}",
                "errors": [],
                "total_activities": 0,
                "error_count": 0,
            })
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Analyze failed sessions for forensics reporting"
    )
    parser.add_argument("session_id", nargs="?", help="Session ID to analyze")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--failed-batch", action="store_true",
                        help="Analyze all recent FAILED sessions instead of one")
    parser.add_argument("--limit", type=int, default=10,
                        help="Max FAILED sessions for --failed-batch (default 10)")
    args = parser.parse_args()

    if not args.session_id and not args.failed_batch:
        parser.error("provide a session_id or use --failed-batch")

    client = JulesAPIClient()

    if args.failed_batch:
        sessions = list(client.list_sessions(page_size=50))
        results = analyze_failed_sessions(sessions, client=client, limit=args.limit)
        payload: Any = results
    else:
        payload = analyze_session_failure(args.session_id, client=client)

    if args.json:
        print(json.dumps(payload, indent=2, default=str))
    else:
        if isinstance(payload, dict):
            print(f"Session: {payload.get('session_id')}")
            print(f"State:   {payload.get('state')}")
            print(f"Title:   {payload.get('title')}")
            print(f"Activities: {payload.get('total_activities')} "
                  f"({payload.get('error_count')} error-bearing)")
            if payload.get("session_error"):
                print(f"Session error: {payload['session_error']}")
            for i, err in enumerate(payload.get("errors", []), 1):
                text = str(err.get("text", ""))[:200]
                print(f"  [{i}] {err.get('type', '?')}: {text}")
        else:
            for r in payload:
                print(f"{r.get('session_id')}: {r.get('error_count', 0)} errors "
                      f"(state={r.get('state')})")


if __name__ == "__main__":
    main()
