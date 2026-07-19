import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from tools.api.jules_api_client import JulesAPIClient

# Official SDK state names (REST API SCREAMING_SNAKE_CASE → meaning)
STATE_AWAITING_PLAN_APPROVAL = "AWAITING_PLAN_APPROVAL"
STATE_AWAITING_USER_FEEDBACK = "AWAITING_USER_FEEDBACK"
STATE_IN_PROGRESS = "IN_PROGRESS"
STATE_FAILED = "FAILED"
STATE_COMPLETED = "COMPLETED"
STATE_QUEUED = "QUEUED"
STATE_PLANNING = "PLANNING"
STATE_PAUSED = "PAUSED"
STATE_UNSPECIFIED = "STATE_UNSPECIFIED"

# Known no-action states. Any state NOT in this set (including unknown or
# future API states) is treated as potentially needing attention, ensuring
# edge cases are surfaced rather than silently excluded.
NO_ACTION_STATES = {STATE_COMPLETED, STATE_QUEUED, STATE_PLANNING, STATE_UNSPECIFIED}


def likely_pending(state: str) -> bool:
    """Return True if a state likely needs user attention."""
    return state not in NO_ACTION_STATES

# Activity type constants matching the REST API union fields
ACTIVITY_AGENT_MESSAGED = "agentMessaged"
ACTIVITY_USER_MESSAGED = "userMessaged"
ACTIVITY_PLAN_GENERATED = "planGenerated"
ACTIVITY_PROGRESS_UPDATED = "progressUpdated"
ACTIVITY_SESSION_COMPLETED = "sessionCompleted"
ACTIVITY_SESSION_FAILED = "sessionFailed"
ACTIVITY_PLAN_APPROVED = "planApproved"


def get_session_state(session_id: str, client: JulesAPIClient) -> str:
    """Fetch session and return its state string."""
    session = client.get_session(session_id)
    return session.get("state", "UNKNOWN")


def get_last_activities(session_id: str, client: JulesAPIClient, count: int = 20) -> List[Dict[str, Any]]:
    """Get the most recent activities for a session.

    Passes ``max_results`` to the API client so the generator stops
    early, preventing unnecessary page fetches.
    """
    return list(
        client.list_activities(session_id, page_size=min(max(count, 1), 100), max_results=count)
    )


def categorize_awaiting_state(
    session_id: str,
    client: JulesAPIClient,
) -> Dict[str, Any]:
    """
    Categorize why a session is in an awaiting state and recommend an action.

    Returns a dict with:
      - state: the session state string
      - category: description of what's needed
      - action: recommended action (approve_plan, send_guidance, investigate, none)
      - details: supporting context from recent activities
    """
    state = get_session_state(session_id, client)
    activities = get_last_activities(session_id, client)

    result: Dict[str, Any] = {
        "session_id": session_id,
        "state": state,
        "category": "unknown",
        "action": "investigate",
        "details": [],
    }

    if state == STATE_AWAITING_PLAN_APPROVAL:
        # Agent generated a plan and is waiting for approval
        plan_steps = []
        for act in activities:
            if ACTIVITY_PLAN_GENERATED in act:
                plan = act[ACTIVITY_PLAN_GENERATED].get("plan", {})
                steps = plan.get("steps", [])
                plan_steps = [s.get("title", "") for s in steps]
                break
        result["category"] = "plan_approval_needed"
        result["action"] = "approve_plan"
        result["details"] = plan_steps if plan_steps else ["Plan pending approval"]

    elif state == STATE_AWAITING_USER_FEEDBACK:
        # Agent is waiting for user input - scan activities to categorize
        for act in activities:
            if ACTIVITY_AGENT_MESSAGED in act:
                msg = act[ACTIVITY_AGENT_MESSAGED].get("agentMessage", "")
                lower = msg.lower()

                # Detect PR selection prompts (common pattern in CI fix sessions)
                if "select" in lower and ("pull request" in lower or "pr" in lower):
                    result["category"] = "pr_selection_needed"
                    result["action"] = "send_guidance"
                    result["details"].append(f"Agent needs PR selection guidance: {msg[:200]}")
                    break

                # Detect explicit questions
                if msg.strip().endswith("?"):
                    result["category"] = "question_pending"
                    result["action"] = "send_guidance"
                    result["details"].append(f"Agent asked: {msg[:200]}")
                    break

                # General awaiting - agent sent a non-question message
                result["category"] = "feedback_needed"
                result["action"] = "send_guidance"
                result["details"].append(f"Agent says: {msg[:200]}")
                break

            elif ACTIVITY_PLAN_GENERATED in act:
                plan = act[ACTIVITY_PLAN_GENERATED].get("plan", {})
                steps = plan.get("steps", [])
                result["category"] = "plan_provided"
                result["action"] = "send_guidance"
                result["details"].append("Plan generated — send approval or guidance")
                result["details"].extend(
                    s.get("title", "") for s in steps[:5]
                )
                break

            elif ACTIVITY_PROGRESS_UPDATED in act:
                title = act[ACTIVITY_PROGRESS_UPDATED].get("title", "")
                desc = act[ACTIVITY_PROGRESS_UPDATED].get("description", "")
                result["category"] = "in_progress_paused"
                result["action"] = "monitor"
                result["details"].append(f"Paused during: {title} — {desc[:200]}")
                break

        if not result["details"]:
            result["details"].append("Session awaiting feedback — no recent agent messages found")

    elif state == STATE_FAILED:
        result["category"] = "failed"
        result["action"] = "retry_or_investigate"
        for act in activities:
            if ACTIVITY_SESSION_FAILED in act:
                reason = act[ACTIVITY_SESSION_FAILED].get("reason", "Unknown reason")
                result["details"].append(f"Failure reason: {reason}")
                break
        if not result["details"]:
            result["details"].append("Session failed — no failure activity found")

    elif state == STATE_PAUSED:
        result["category"] = "paused"
        result["action"] = "investigate"
        for act in activities:
            if ACTIVITY_PROGRESS_UPDATED in act:
                title = act[ACTIVITY_PROGRESS_UPDATED].get("title", "")
                result["details"].append(f"Paused during: {title}")
                break
        if not result["details"]:
            result["details"].append("Session paused — review and decide: resume, send guidance, or cancel")

    elif state == STATE_IN_PROGRESS:
        result["category"] = "in_progress"
        result["action"] = "monitor"
        for act in activities:
            if ACTIVITY_PROGRESS_UPDATED in act:
                title = act[ACTIVITY_PROGRESS_UPDATED].get("title", "")
                result["details"].append(f"Working on: {title}")
                break
        if not result["details"]:
            result["details"].append("Session is running")

    elif state == STATE_QUEUED:
        result["category"] = "queued"
        result["action"] = "none"
        result["details"].append("Session queued — will start automatically")

    elif state == STATE_PLANNING:
        result["category"] = "planning"
        result["action"] = "none"
        result["details"].append("Agent is creating a plan — wait")

    elif state == STATE_COMPLETED:
        result["category"] = "completed"
        result["action"] = "audit"
        result["details"].append("Session completed — review outputs and PR")

    elif state == STATE_UNSPECIFIED:
        result["category"] = "unknown_state"
        result["action"] = "investigate"
        result["details"].append("Session has unspecified state — check API response")

    else:
        result["category"] = f"state_{state.lower()}"
        result["action"] = "none"
        result["details"].append(f"Session in {state} state — no action needed")

    return result


def find_awaiting_sessions(
    client: Optional[JulesAPIClient] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Scan all sessions and return those potentially needing attention.

    Uses a permissive heuristic: any session in a state not known to be
    no-action (COMPLETED, QUEUED, PLANNING, STATE_UNSPECIFIED) is included.
    Unknown or future API states are surfaced rather than silently excluded.

    Each result includes the session metadata plus categorization.
    """
    from tools.api.jules_api_client import JulesAPIClient as _JulesAPIClient
    client = client or _JulesAPIClient()
    pending = []
    # Scan up to 500 sessions max to handle accounts with many completed
    # sessions without server-side filtering.
    for session in client.list_sessions(
        page_size=min(max(limit, 1), 50), max_results=500
    ):
        state = session.get("state", "UNKNOWN")
        if likely_pending(state):
            cat = categorize_awaiting_state(
                session.get("name", "").replace("sessions/", ""),
                client,
            )
            pending.append({**session, "_analysis": cat})
            if len(pending) >= limit:
                break
    return pending


def analyze_unanswered(session_id: str, max_activities: int = 50) -> List[str]:
    """
    Legacy wrapper: detect unanswered agent questions.
    Replaced by categorize_awaiting_state() for production use.

    Args:
        session_id: Jules session ID.
        max_activities: Max recent activities to scan (prevents flooding).
    """
    client = JulesAPIClient()
    activities = list(
        client.list_activities(session_id, page_size=max_activities, max_results=max_activities)
    )
    unanswered = []
    for activity in reversed(activities):
        if ACTIVITY_AGENT_MESSAGED in activity:
            text = activity[ACTIVITY_AGENT_MESSAGED].get("agentMessage", "")
            if text.strip().endswith("?"):
                unanswered.append(text)
            else:
                break
        elif ACTIVITY_USER_MESSAGED in activity:
            break
    return unanswered


def main():
    parser = argparse.ArgumentParser(description="Analyze session awaiting state and recommend action")
    parser.add_argument("session_id", nargs="?", help="Session ID to analyze")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--pending", action="store_true", help="List sessions likely needing attention (excludes COMPLETED, QUEUED, PLANNING, STATE_UNSPECIFIED; unknown/future states surfaced)")
    args = parser.parse_args()

    client = JulesAPIClient()

    if args.pending:
        pending = find_awaiting_sessions(client)
        if args.json:
            print(json.dumps(pending, indent=2))
            return
        if not pending:
            print("No sessions currently need user action.")
            return
        for s in pending:
            sid = s.get("name", "?").replace("sessions/", "")
            state = s.get("state", "?")
            title = s.get("title", "Untitled")[:60]
            cat = s["_analysis"]["category"].replace("_", " ")
            act = s["_analysis"]["action"].replace("_", " ")
            print(f"{sid:<22} {state:<28} {cat:<20} {act:<20} {title}")
        return

    if not args.session_id:
        parser.print_help()
        return

    result = categorize_awaiting_state(args.session_id, client)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    state_labels = {
        STATE_AWAITING_PLAN_APPROVAL: "Awaiting Plan Approval",
        STATE_AWAITING_USER_FEEDBACK: "Awaiting User Feedback",
        STATE_IN_PROGRESS: "In Progress",
        STATE_FAILED: "Failed",
        STATE_COMPLETED: "Completed",
        STATE_PAUSED: "Paused",
        STATE_QUEUED: "Queued",
        STATE_PLANNING: "Planning",
    }
    label = state_labels.get(result["state"], result["state"])

    print(f"Session: {result['session_id']}")
    print(f"State:   {label}")
    print(f"Needs:   {result['category'].replace('_', ' ').title()}")
    print(f"Action:  {result['action'].replace('_', ' ').title()}")
    if result["details"]:
        print("Details:")
        for d in result["details"]:
            print(f"  - {d}")


if __name__ == "__main__":
    main()
