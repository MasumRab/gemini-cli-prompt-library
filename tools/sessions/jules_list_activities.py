#!/usr/bin/env python3
"""List activities for a given Jules session."""

import argparse
import json
import sys

from tools.api.jules_api_client import JulesAPIClient


def list_activities(session_id: str, limit: int = None):
    """Fetch activities for a given session, optionally limiting the count."""
    client = JulesAPIClient()
    activities = client.list_activities(session_id)
    if limit is not None:
        import itertools
        activities = itertools.islice(activities, limit)
    return list(activities)


def format_activity(act: dict) -> str:
    """Format a single activity with rich details."""
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
        return f"[{time}] {orig}: Agent Messaged - {msg[:100]}..."

    elif "userMessaged" in act:
        msg = act["userMessaged"].get("userMessage", "")
        return f"[{time}] {orig}: User Messaged - {msg[:100]}..."

    elif "sessionFailed" in act:
        return f"[{time}] {orig}: Session Failed"

    else:
        # Activities don't have a "type" field; use description as fallback.
        return f"[{time}] {orig}: {act.get('description', 'UNKNOWN')}"


def main():
    parser = argparse.ArgumentParser(description="List activities for a Jules session")
    parser.add_argument("session_id", help="The Session ID")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    session_id = args.session_id.replace("sessions/", "")

    activities = list_activities(session_id)

    if args.raw:
        try:
            print(json.dumps(activities, indent=2))
        except BrokenPipeError:
            pass
        return

    print(f"Activities for session {session_id}:")
    print("-" * 80)

    for act in activities:
        print(format_activity(act))


if __name__ == "__main__":
    main()
