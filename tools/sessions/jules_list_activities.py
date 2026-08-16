#!/usr/bin/env python3
"""List activities for a given Jules session.

By default agent/user messages are truncated to 100 characters. Use
``--full`` to print the complete untruncated message text.
"""

import argparse
import json
import sys

from tools.api.jules_api_client import JulesAPIClient


def list_activities(session_id: str, limit: int = None):
    """Fetch activities for a given session, optionally limiting the count.

    Passes ``max_results`` to the API client so the generator stops at
    ``limit`` items, preventing flood for long-running sessions.
    """
    client = JulesAPIClient()
    if limit is not None:
        return list(client.list_activities(session_id, max_results=limit))
    return list(client.list_activities(session_id))


def format_activity(act: dict, full: bool = False) -> str:
    """Format a single activity with rich details.

    Agent/user messages are truncated to 100 chars unless ``full`` is
    True, in which case the complete message text is emitted.
    """
    orig = act.get("originator", "?")
    time = act.get("createTime", "")

    if "planGenerated" in act:
        lines = [f"[{time}] {orig}: Plan Generated"]
        for step in act["planGenerated"]["plan"]["steps"]:
            lines.append(f"  - {step.get('title')}")
        return "\n".join(lines)

    elif "progressUpdated" in act:
        prog = act["progressUpdated"]
        desc = prog.get("description", "")
        if desc:
            desc = desc.replace("\n", "\n    ")
            return f"[{time}] {orig}: Progress - {prog.get('title', '')}\n    {desc}"
        return f"[{time}] {orig}: Progress - {prog.get('title', '')}"

    elif "sessionCompleted" in act:
        return f"[{time}] {orig}: Session Completed"

    elif "planApproved" in act:
        return f"[{time}] {orig}: Plan Approved"

    elif "agentMessaged" in act:
        msg = act["agentMessaged"].get("agentMessage", "")
        text = msg if full else f"{msg[:100]}..."
        return f"[{time}] {orig}: Agent Messaged - {text}"

    elif "userMessaged" in act:
        msg = act["userMessaged"].get("userMessage", "")
        text = msg if full else f"{msg[:100]}..."
        return f"[{time}] {orig}: User Messaged - {text}"

    elif "sessionFailed" in act:
        return f"[{time}] {orig}: Session Failed"

    else:
        # Activities don't have a "type" field; use description as fallback.
        return f"[{time}] {orig}: {act.get('description', 'UNKNOWN')}"


def main():
    parser = argparse.ArgumentParser(description="List activities for a Jules session (--full emits untruncated messages)")
    parser.add_argument("session_id", help="The Session ID")
    parser.add_argument("--limit", type=int, default=50, help="Max activities to fetch (default: 50; use -1 for all)")
    parser.add_argument("--all", action="store_true", help="Fetch all activities (overrides --limit)")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON")
    parser.add_argument("--full", action="store_true", help="Output full untruncated message text for agent/user messages")
    args = parser.parse_args()

    session_id = args.session_id.replace("sessions/", "")

    limit = None if args.all else args.limit if args.limit > 0 else None
    activities = list_activities(session_id, limit=limit)

    if args.raw:
        try:
            print(json.dumps(activities, indent=2))
        except BrokenPipeError:
            pass
        return

    print(f"Activities for session {session_id}:")
    print("-" * 80)

    for act in activities:
        print(format_activity(act, full=args.full))


if __name__ == "__main__":
    main()
