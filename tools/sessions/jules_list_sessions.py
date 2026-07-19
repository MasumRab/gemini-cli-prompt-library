#!/usr/bin/env python3
"""List Jules sessions with their current status and associated PRs."""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from tools.api.jules_api_client import JulesAPIClient

# Known non-action states — these are the only states we treat as definitively
# not needing user attention. All other states (including unknown/future states)
# are surfaced so edge cases are visible.
NO_ACTION_STATES = {"COMPLETED", "QUEUED", "PLANNING", "STATE_UNSPECIFIED"}


def likely_pending(state: str) -> bool:
    """Return True if a state likely needs user attention.

    Only known no-action states return False. Every other state
    (including unknown or future API states) returns True so the
    session is surfaced for review.
    """
    return state not in NO_ACTION_STATES


def get_session_pr(session: Dict[str, Any]) -> str:
    """Extract PR URL from session outputs if available."""
    outputs = session.get("outputs", [])
    for output in outputs:
        pr_data = output.get("pullRequest", {})
        if "url" in pr_data:
            return pr_data["url"]
    return "N/A"


def get_latest_activity_summary(session_id: str, client: JulesAPIClient) -> str:
    """Fetch the latest activity and return a short summary."""
    activities = list(client.list_activities(session_id, page_size=1))
    if not activities:
        return "No activities"

    latest = activities[0]
    originator = latest.get("originator", "unknown")

    if "planGenerated" in latest:
        return "Plan Generated (Awaiting Approval)"
    elif "progressUpdated" in latest:
        return f"Progress: {latest['progressUpdated'].get('title', '...')}"
    elif "sessionCompleted" in latest:
        return "Completed"
    elif "sessionFailed" in latest:
        return "Failed"
    elif "planApproved" in latest:
        return "Plan Approved"
    elif "agentMessaged" in latest:
        msg = latest["agentMessaged"].get("agentMessage", "")
        return f"Agent: {msg[:40]}"
    elif "userMessaged" in latest:
        msg = latest["userMessaged"].get("userMessage", "")
        return f"User: {msg[:40]}"

    return f"Activity by {originator}"


def list_sessions(
    active_only: bool = False,
    pending_only: bool = False,
    include_states: Optional[List[str]] = None,
    exclude_states: Optional[List[str]] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Fetch sessions from the API with flexible filtering.

    Args:
        active_only: Exclude COMPLETED sessions.
        pending_only: Exclude known no-action states (COMPLETED, QUEUED,
            PLANNING, STATE_UNSPECIFIED). Unknown/future states are kept.
        include_states: Only include sessions with these states.
        exclude_states: Exclude sessions with these states.
        limit: Max sessions to return.
    """
    client = JulesAPIClient()
    sessions = []
    page_size = min(max(limit, 1), 50)

    for session in client.list_sessions(page_size=page_size):
        state = session.get("state", "UNKNOWN")
        state_upper = state.upper()

        if active_only and state_upper == "COMPLETED":
            continue
        if pending_only and state_upper in NO_ACTION_STATES:
            continue
        if include_states and state_upper not in [s.upper() for s in include_states]:
            continue
        if exclude_states and state_upper in [s.upper() for s in exclude_states]:
            continue

        sessions.append(session)

        if len(sessions) >= limit:
            break

    return sessions


def main():
    parser = argparse.ArgumentParser(description="List Jules sessions")
    parser.add_argument(
        "--active-only", action="store_true",
        help="Exclude COMPLETED sessions"
    )
    parser.add_argument(
        "--pending", action="store_true",
        help="Show sessions likely needing attention (excludes COMPLETED, QUEUED, PLANNING, STATE_UNSPECIFIED; "
             "unknown/future states are surfaced)"
    )
    parser.add_argument(
        "--state", dest="include_states", nargs="+",
        help="Only include these states (case-insensitive, e.g. --state FAILED PAUSED)"
    )
    parser.add_argument(
        "--exclude-state", dest="exclude_states", nargs="+",
        help="Exclude these states (e.g. --exclude-state COMPLETED QUEUED)"
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--limit", type=int, default=20, help="Max sessions to list")
    parser.add_argument("--with-activity", action="store_true", help="Include latest activity summary (slower)")
    args = parser.parse_args()

    client = JulesAPIClient()
    sessions = list_sessions(
        active_only=args.active_only,
        pending_only=args.pending,
        include_states=args.include_states,
        exclude_states=args.exclude_states,
        limit=args.limit,
    )

    if args.json:
        try:
            print(json.dumps(sessions, indent=2))
        except BrokenPipeError:
            pass
        return

    col_widths = [22, 12, 50, 40]
    marker = " " if not args.pending else "!"
    header = f"{'':1s} | {'Session ID':<{col_widths[0]}} | {'State':<{col_widths[1]}} | {'PR URL':<{col_widths[2]}} | {'Title'}"
    if args.with_activity:
        header += f" | {'Latest Activity'}"

    print(header)
    print("-" * (sum(col_widths) + 26))

    for session in sessions:
        state = session.get("state", "UNKNOWN")
        session_name = session.get("name", "")
        session_id = session_name.replace("sessions/", "")
        title = session.get("title", "Untitled")[:50]
        pr_url = get_session_pr(session)
        marker = " " if not args.pending else ("!" if likely_pending(state) else " ")

        row = f"{marker:1s} | {session_id:<{col_widths[0]}} | {state:<{col_widths[1]}} | {pr_url:<{col_widths[2]}} | {title}"
        if args.with_activity:
            activity = get_latest_activity_summary(session_name, client)
            row += f" | {activity}"

        print(row)

    if args.pending:
        print(f"\n  !  = likely needs attention | {' ':4s} = no action expected (known states: COMPLETED, QUEUED, PLANNING, STATE_UNSPECIFIED)")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
