#!/usr/bin/env python3
"""
Session Tracking Utility for Jules

Queries the local SQLite store for sessions awaiting user feedback,
fetches their latest activity context, and creates detailed tracking
files to understand what kind of response is needed for each session.

Usage:
    python session_tracker.py --sync    # Sync from API first (requires JULES_API_KEY)
    python session_tracker.py --track   # Create tracking files from local store
    python session_tracker.py --list    # List awaiting sessions
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from tools.store.jules_store import JulesSessionStore
from tools.api.jules_api_client import JulesAPIClient
from tools.sessions.config import NO_ACTION_STATES

# States that need user attention
AWAITING_STATES = {
    "AWAITING_USER_FEEDBACK",
    "AWAITING_PLAN_APPROVAL",
    "PAUSED",
    "FAILED",
}

TRACKING_DIR = Path.home() / ".jules" / "session_tracking"


def ensure_tracking_dir():
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)


def categorize_awaiting_session(
    session: Dict[str, Any], activities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Analyze an awaiting session and determine what context/response is needed."""

    state = session.get("state", "UNKNOWN")
    session_id = session.get("session_id", "")
    title = session.get("title", "")
    prompt_snippet = session.get("prompt_snippet", "")
    activity_count = session.get("activity_count", 0)

    result = {
        "session_id": session_id,
        "title": title,
        "state": state,
        "activity_count": activity_count,
        "prompt_snippet": prompt_snippet[:500],
        "category": "unknown",
        "action_needed": "investigate",
        "context_summary": "",
        "decision_points": [],
        "suggested_response": "",
        "latest_agent_message": None,
        "latest_user_message": None,
        "recent_activities": [],
    }

    if not activities:
        result["context_summary"] = (
            f"No activities in local store for session {session_id}"
        )
        result["action_needed"] = "fetch_activities"
        return result

    # Get recent activities (last 10)
    recent = activities[-10:] if len(activities) > 10 else activities
    result["recent_activities"] = [
        {
            "time": a.get("create_time", ""),
            "type": a.get("activity_type", ""),
            "originator": a.get("originator", ""),
            "summary": a.get("summary", "")[:300],
        }
        for a in reversed(recent)
    ]

    # Find latest agent/user messages
    for a in reversed(activities):
        if (
            a.get("activity_type") == "agentMessaged"
            and not result["latest_agent_message"]
        ):
            result["latest_agent_message"] = a.get("summary", "")[:500]
        if (
            a.get("activity_type") == "userMessaged"
            and not result["latest_user_message"]
        ):
            result["latest_user_message"] = a.get("summary", "")[:500]
        if result["latest_agent_message"] and result["latest_user_message"]:
            break

    # Categorize by state and activity pattern
    if state == "AWAITING_PLAN_APPROVAL":
        result["category"] = "plan_approval_needed"
        result["action_needed"] = "approve_plan_or_send_guidance"
        result["context_summary"] = (
            "Agent generated a plan and is waiting for approval to proceed"
        )
        plan_steps = []
        for a in activities:
            if a.get("activity_type") == "planGenerated":
                # Would need full activity data for plan steps
                result["context_summary"] += f" - Plan has steps (see activities)"
        result["decision_points"] = [
            "Approve the plan as-is?",
            "Request modifications to the plan?",
            "Reject and ask for new plan?",
        ]
        result["suggested_response"] = (
            "Review the plan in activities. Reply 'approve' to proceed or provide guidance on changes needed."
        )

    elif state == "AWAITING_USER_FEEDBACK":
        # Analyze what the agent is asking for
        agent_msg = result["latest_agent_message"] or ""
        agent_msg_lower = agent_msg.lower()

        if "select" in agent_msg_lower and (
            "pull request" in agent_msg_lower or "pr" in agent_msg_lower
        ):
            result["category"] = "pr_selection_needed"
            result["action_needed"] = "send_guidance"
            result["context_summary"] = "Agent needs guidance on which PR to work on"
            result["decision_points"] = [
                "Which PR should the agent select?",
                "Should agent use different selection criteria?",
            ]
            result["suggested_response"] = (
                "Specify the PR number or provide selection criteria (e.g., 'work on PR #123' or 'pick the oldest failing PR')"
            )

        elif agent_msg.strip().endswith("?"):
            result["category"] = "question_pending"
            result["action_needed"] = "send_guidance"
            result["context_summary"] = f"Agent asked a question: {agent_msg[:200]}"
            result["decision_points"] = [
                "Answer the agent's question directly",
                "Provide additional context?",
                "Redirect to different approach?",
            ]
            result["suggested_response"] = f"Answer the question: '{agent_msg[:200]}'"

        elif "plan" in agent_msg_lower and (
            "step" in agent_msg_lower or "generated" in agent_msg_lower
        ):
            result["category"] = "plan_provided_awaiting_feedback"
            result["action_needed"] = "send_guidance"
            result["context_summary"] = (
                "Agent provided a plan and is awaiting feedback/approval"
            )
            result["decision_points"] = [
                "Approve the plan?",
                "Request changes to specific steps?",
                "Ask for clarification?",
            ]
            result["suggested_response"] = (
                "Review the plan steps. Reply with approval or specific modifications needed."
            )

        elif "progress" in agent_msg_lower or "working on" in agent_msg_lower:
            result["category"] = "in_progress_paused"
            result["action_needed"] = "monitor"
            result["context_summary"] = f"Agent was working on: {agent_msg[:200]}"
            result["decision_points"] = [
                "Let agent continue?",
                "Send new guidance?",
                "Check status?",
            ]
            result["suggested_response"] = (
                "Agent is in progress. Send 'continue' to let it proceed or provide new guidance."
            )

        else:
            result["category"] = "feedback_needed"
            result["action_needed"] = "send_guidance"
            result["context_summary"] = (
                f"Agent sent message awaiting response: {agent_msg[:200]}"
            )
            result["decision_points"] = [
                "Provide the requested feedback/guidance",
                "Ask clarifying question?",
                "Approve implicit plan?",
            ]
            result["suggested_response"] = (
                "Provide specific guidance on what the agent should do next."
            )

    elif state == "PAUSED":
        result["category"] = "paused"
        result["action_needed"] = "investigate"
        result["context_summary"] = (
            "Session is paused - may need resume, guidance, or cancellation"
        )
        result["decision_points"] = [
            "Resume the session?",
            "Send guidance before resuming?",
            "Cancel/abandon?",
        ]
        result["suggested_response"] = (
            "Check why paused (see activities). Then decide: resume, guide, or cancel."
        )

    elif state == "FAILED":
        result["category"] = "failed"
        result["action_needed"] = "retry_or_investigate"
        failure_reason = ""
        for a in reversed(activities):
            if a.get("activity_type") == "sessionFailed":
                failure_reason = a.get("summary", "")
                break
        result["context_summary"] = (
            f"Session failed: {failure_reason or 'Unknown reason'}"
        )
        result["decision_points"] = [
            "Retry with same prompt?",
            "Modify prompt and restart?",
            "Investigate failure cause first?",
        ]
        result["suggested_response"] = (
            "Review failure reason. Decide: retry, modify approach, or abandon."
        )

    else:
        result["category"] = f"state_{state.lower()}"
        result["action_needed"] = "none"
        result["context_summary"] = (
            f"Session in {state} state - no action typically needed"
        )
        result["decision_points"] = ["Monitor for state change"]
        result["suggested_response"] = "No action needed for this state."

    return result


def sync_from_api(
    store: JulesSessionStore, client: JulesAPIClient, limit: int = 100
) -> Dict[str, Any]:
    """Sync latest sessions from API to local store."""
    print(f"Syncing latest {limit} sessions from Jules API...")

    # Use the client's built-in sync with store
    client_with_store = JulesAPIClient(store=store)

    sessions_synced = 0
    activities_synced = 0

    for session in client.list_sessions(page_size=min(limit, 50), max_results=limit):
        session_name = session.get("name", "").replace("sessions/", "")
        if not session_name:
            continue

        store.upsert_session(session)
        sessions_synced += 1

        # Fetch activities for awaiting sessions
        state = session.get("state", "")
        if state in AWAITING_STATES:
            try:
                activities = list(
                    client_with_store.list_activities(
                        session_name, page_size=100, max_results=200
                    )
                )
                if activities:
                    new_count = store.upsert_activities(session_name, activities)
                    activities_synced += new_count
            except Exception as e:
                print(f"  Warning: Failed to fetch activities for {session_name}: {e}")

    print(f"Synced {sessions_synced} sessions, {activities_synced} new activities")
    return {"sessions_synced": sessions_synced, "activities_synced": activities_synced}


def get_awaiting_sessions(store: JulesSessionStore) -> List[Dict[str, Any]]:
    """Get all sessions in awaiting states from local store."""
    awaiting = []
    for state in AWAITING_STATES:
        sessions = store.list_sessions(state=state, limit=100)
        awaiting.extend(sessions)

    # Sort by update_time descending
    awaiting.sort(key=lambda s: s.get("update_time", ""), reverse=True)
    return awaiting


def get_activities_for_session(
    store: JulesSessionStore, session_id: str
) -> List[Dict[str, Any]]:
    """Get all activities for a session from local store."""
    sid = session_id.replace("sessions/", "")
    with store._conn() as conn:
        rows = conn.execute(
            "SELECT * FROM activities WHERE session_id=? ORDER BY create_time ASC",
            (sid,),
        ).fetchall()
    return [dict(r) for r in rows]


def create_tracking_file(session: Dict[str, Any], analysis: Dict[str, Any]) -> Path:
    """Create a tracking JSON file for the session."""
    ensure_tracking_dir()

    session_id = session.get("session_id", "")
    safe_id = session_id[:50]

    tracking_data = {
        "metadata": {
            "session_id": session_id,
            "title": session.get("title", ""),
            "state": session.get("state", ""),
            "repo": session.get("repo", ""),
            "pr_url": session.get("pr_url", ""),
            "activity_count": session.get("activity_count", 0),
            "create_time": session.get("create_time", ""),
            "update_time": session.get("update_time", ""),
            "last_synced": datetime.utcnow().isoformat() + "Z",
            "prompt_snippet": session.get("prompt_snippet", "")[:500],
        },
        "analysis": analysis,
        "notes": session.get("notes"),
        "tags": session.get("tags", "[]"),
    }

    filename = f"{safe_id}_{analysis['category']}.json"
    filepath = TRACKING_DIR / filename

    with open(filepath, "w") as f:
        json.dump(tracking_data, f, indent=2)

    return filepath


def list_awaiting_sessions():
    """List all sessions awaiting feedback."""
    store = JulesSessionStore()
    awaiting = get_awaiting_sessions(store)

    if not awaiting:
        print("No sessions awaiting user feedback.")
        return

    print(f"\n{'Session ID':<22} {'State':<28} {'Activities':>10} {'Repo':<30} Title")
    print("-" * 120)

    for s in awaiting:
        session_id = s.get("session_id", "")[:21]
        state = s.get("state", "")[:27]
        activity_count = s.get("activity_count", 0)
        repo = s.get("repo", "")[:29]
        title = s.get("title", "")[:40]
        print(f"{session_id:<22} {state:<28} {activity_count:>10} {repo:<30} {title}")


def track_sessions(sync_first: bool = False, limit: int = 100):
    """Create tracking files for all awaiting sessions."""
    store = JulesSessionStore()

    if sync_first:
        api_key = os.environ.get("JULES_API_KEY")
        if not api_key:
            print("ERROR: JULES_API_KEY not set. Cannot sync from API.")
            print("Run with --no-sync to use local store only, or set JULES_API_KEY.")
            sys.exit(1)
        client = JulesAPIClient()
        sync_from_api(store, client, limit=limit)

    awaiting = get_awaiting_sessions(store)

    if not awaiting:
        print("No sessions awaiting user feedback in local store.")
        if not sync_first:
            print(
                "Try running with --sync to fetch latest from API (requires JULES_API_KEY)."
            )
        return

    print(f"\nFound {len(awaiting)} sessions awaiting feedback:")
    print("=" * 80)

    for session in awaiting:
        session_id = session.get("session_id", "")
        state = session.get("state", "")
        title = session.get("title", "")[:60]

        print(f"\n📋 {session_id} ({state})")
        print(f"   Title: {title}")
        print(f"   Repo: {session.get('repo', 'N/A')}")
        print(f"   Activities: {session.get('activity_count', 0)}")

        # Get activities from local store
        activities = get_activities_for_session(store, session_id)

        # Analyze
        analysis = categorize_awaiting_session(session, activities)

        # Create tracking file
        filepath = create_tracking_file(session, analysis)

        print(f"   Category: {analysis['category']}")
        print(f"   Action: {analysis['action_needed']}")
        print(f"   Context: {analysis['context_summary'][:100]}...")
        print(f"   📝 Tracking file: {filepath}")

        if analysis.get("decision_points"):
            print(f"   Decision points:")
            for dp in analysis["decision_points"]:
                print(f"      - {dp}")

        if analysis.get("suggested_response"):
            print(f"   Suggested: {analysis['suggested_response'][:100]}...")


def main():
    parser = argparse.ArgumentParser(description="Jules Session Tracker")
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sync from API before tracking (requires JULES_API_KEY)",
    )
    parser.add_argument(
        "--no-sync", action="store_true", help="Use only local store (default)"
    )
    parser.add_argument(
        "--list", action="store_true", help="Just list awaiting sessions"
    )
    parser.add_argument(
        "--limit", type=int, default=100, help="Max sessions to sync from API"
    )

    args = parser.parse_args()

    if args.list:
        list_awaiting_sessions()
        return

    sync_first = args.sync and not args.no_sync
    track_sessions(sync_first=sync_first, limit=args.limit)


if __name__ == "__main__":
    main()
