#!/usr/bin/env python3
"""List Jules sessions with their current status and associated PRs."""

import argparse
import json
import sys
from typing import Any, Dict, List

from tools.api.jules_api_client import JulesAPIClient


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


def list_sessions(active_only=False, limit=20) -> List[Dict[str, Any]]:
    """Fetch sessions from the API with efficient pagination."""
    client = JulesAPIClient()
    sessions = []
    page_size = min(max(limit, 1), 50)

    for session in client.list_sessions(page_size=page_size):
        state = session.get("state", "UNKNOWN")

        if active_only and state == "COMPLETED":
            continue

        sessions.append(session)

        if len(sessions) >= limit:
            break

    return sessions


def main():
    parser = argparse.ArgumentParser(description="List Jules sessions")
    parser.add_argument(
        "--active-only", action="store_true", help="Only show non-completed sessions"
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--limit", type=int, default=20, help="Max sessions to list")
    parser.add_argument("--with-activity", action="store_true", help="Include latest activity summary (slower)")
    args = parser.parse_args()

    client = JulesAPIClient()
    sessions = list_sessions(active_only=args.active_only, limit=args.limit)

    if args.json:
        try:
            print(json.dumps(sessions, indent=2))
        except BrokenPipeError:
            pass
        return

    col_widths = [22, 12, 50, 40]
    header = f"{'Session ID':<{col_widths[0]}} | {'State':<{col_widths[1]}} | {'PR URL':<{col_widths[2]}} | {'Title'}"
    if args.with_activity:
        header += f" | {'Latest Activity'}"
    
    print(header)
    print("-" * (sum(col_widths) + 20))

    for session in sessions:
        state = session.get("state", "UNKNOWN")
        session_name = session.get("name", "")
        session_id = session_name.replace("sessions/", "")
        title = session.get("title", "Untitled")[:50]
        pr_url = get_session_pr(session)

        row = f"{session_id:<{col_widths[0]}} | {state:<{col_widths[1]}} | {pr_url:<{col_widths[2]}} | {title}"
        if args.with_activity:
            activity = get_latest_activity_summary(session_name, client)
            row += f" | {activity}"
        
        print(row)


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
