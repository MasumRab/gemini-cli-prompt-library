#!/usr/bin/env python3
"""
Check Jules sessions needing response and generate suggested messages.

Usage:
    python skills/jules-sessions/scripts/check_needs_response.py [--api] [--stale-minutes N]

Options:
    --api           Pull latest state from Jules API first (hybrid)
    --stale-minutes N   Minutes before IN_PROGRESS session is "stuck" (default: 30)
    --json          Output as JSON
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


# Session states and their response categories
RESPONSE_CATEGORIES = {
    "AWAITING_PLAN_APPROVAL": {
        "action": "approve",
        "priority": 1,
        "description": "Plan ready, needs your approval"
    },
    "IN_PROGRESS_STUCK": {
        "action": "nudge",
        "priority": 2,
        "description": "Running too long, may need nudge"
    },
    "COMPLETED_NO_CHANGES": {
        "action": "follow_up_no_changes",
        "priority": 3,
        "description": "Completed without making changes"
    },
    "COMPLETED_NO_PR": {
        "action": "request_pr",
        "priority": 3,
        "description": "Completed but no PR created"
    },
    "COMPLETED_PR_STALE": {
        "action": "merge_reminder",
        "priority": 4,
        "description": "PR created but not merged"
    },
    "FAILED": {
        "action": "restart",
        "priority": 2,
        "description": "Session failed, may need restart"
    },
    "TIMEOUT": {
        "action": "restart_refined",
        "priority": 2,
        "description": "Timed out, needs refined prompt"
    }
}


def load_local_sessions(sessions_dir: str = "jules_sessions") -> List[Dict[str, Any]]:
    """Load all session JSON files from local directory."""
    sessions = []
    sessions_path = Path(sessions_dir)
    
    if not sessions_path.exists():
        return sessions
    
    for f in sessions_path.glob("*_session.json"):
        try:
            with open(f) as fp:
                session = json.load(fp)
                session["_local_file"] = str(f)
                sessions.append(session)
        except Exception as e:
            print(f"Warning: Could not load {f}: {e}", file=sys.stderr)
    
    return sessions


def fetch_session_from_api(session_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch latest session state from Jules API."""
    url = f"https://jules.googleapis.com/v1alpha/sessions/{session_id}"
    
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"x-goog-api-key: {api_key}", url],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Warning: API fetch failed for {session_id}: {e}", file=sys.stderr)
        return None


def categorize_session(
    session: Dict[str, Any],
    stale_minutes: int = 30
) -> Optional[Dict[str, Any]]:
    """Determine if session needs response and what kind."""
    state = session.get("state", "")
    update_time = session.get("updateTime", "")
    outputs = session.get("outputs", [])
    title = session.get("title", "Untitled")
    prompt = session.get("prompt", "")
    
    # Extract PR info
    pr_info = None
    changes = None
    for output in outputs:
        if output.get("pullRequest"):
            pr_info = output["pullRequest"]
        if output.get("changeSet"):
            changes = output["changeSet"]
    
    # Check for explicit timeout
    if "Jules was unable to complete" in prompt or state == "FAILED":
        # Check if it was a timeout
        if any("timeout" in str(o).lower() for o in outputs):
            category = "TIMEOUT"
        else:
            category = "FAILED"
    
    # AWAITING_PLAN_APPROVAL
    elif state == "AWAITING_PLAN_APPROVAL":
        category = "AWAITING_PLAN_APPROVAL"
    
    # IN_PROGRESS - check if stuck
    elif state == "IN_PROGRESS":
        if update_time:
            try:
                last_update = datetime.fromisoformat(update_time.replace("Z", "+00:00"))
                if datetime.now(last_update.tzinfo) - last_update > timedelta(minutes=stale_minutes):
                    category = "IN_PROGRESS_STUCK"
                else:
                    return None  # Not stuck yet
            except:
                category = "IN_PROGRESS_STUCK"  # Can't parse time, assume might be stuck
        else:
            category = "IN_PROGRESS_STUCK"
    
    # COMPLETED - check what happened
    elif state == "COMPLETED":
        # No PR created
        if not pr_info:
            category = "COMPLETED_NO_PR"
        # PR exists but no actual changes in diff
        elif changes and not changes.get("gitPatch"):
            category = "COMPLETED_NO_CHANGES"
        # PR exists with changes
        elif pr_info:
            # Could check PR status here via gh CLI
            category = "COMPLETED_PR_STALE"
        else:
            category = "COMPLETED_NO_PR"
    
    else:
        return None  # No action needed
    
    category_info = RESPONSE_CATEGORIES.get(category, {})
    
    return {
        "session_id": session.get("id", session.get("name", "unknown")),
        "title": title,
        "state": state,
        "category": category,
        "action": category_info.get("action", "unknown"),
        "priority": category_info.get("priority", 99),
        "description": category_info.get("description", ""),
        "pr_url": pr_info.get("url") if pr_info else None,
        "pr_title": pr_info.get("title") if pr_info else None,
        "prompt_summary": prompt[:200] + "..." if len(prompt) > 200 else prompt,
        "branch": session.get("sourceContext", {}).get("githubRepoContext", {}).get("startingBranch"),
        "update_time": update_time
    }


def generate_message(result: Dict[str, Any]) -> str:
    """Generate a suggested response message based on session context."""
    action = result.get("action", "")
    title = result.get("title", "")
    prompt_summary = result.get("prompt_summary", "")
    pr_url = result.get("pr_url", "")
    branch = result.get("branch", "")
    
    messages = {
        "approve": f"""Approve the plan for: {title}

Original intent: {prompt_summary}

Suggested response: "Proceed with the plan as outlined. Focus on the core requirements." """,
        
        "nudge": f"""Nudge stuck session: {title}

Session has been running for a while. Original task: {prompt_summary}

Suggested response: "Status update? If encountering blockers, describe them so I can help. Otherwise, continue with the current task." """,
        
        "follow_up_no_changes": f"""Follow up on session that made no changes: {title}

Original intent: {prompt_summary}

Suggested response: "I see the session completed but no changes were made. What happened? Were there issues with the codebase or requirements unclear?" """,
        
        "request_pr": f"""Request PR creation for: {title}

Session completed but no PR was created. Original task: {prompt_summary}

Suggested response: "Please push your changes to a branch and create a PR so I can review the implementation." """,
        
        "merge_reminder": f"""PR ready for review/merge: {title}

PR: {pr_url}

Suggested response: "The PR is ready. I'll review and merge when satisfied with the changes." """,
        
        "restart": f"""Session failed, consider restart: {title}

Original intent: {prompt_summary}

Suggested response: "The session encountered an error. I'll restart with a refined prompt addressing: [specific issue]" """,
        
        "restart_refined": f"""Session timed out, restart with refined prompt: {title}

Original intent: {prompt_summary}

Suggested response: "Session timed out. I'll create a new session with a more focused scope: [break down the original task]" """
    }
    
    return messages.get(action, f"Unknown action: {action}")


def main():
    parser = argparse.ArgumentParser(
        description="Check Jules sessions needing response"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Pull latest state from Jules API first (hybrid)"
    )
    parser.add_argument(
        "--stale-minutes",
        type=int,
        default=30,
        help="Minutes before IN_PROGRESS session is 'stuck' (default: 30)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--sessions-dir",
        default="jules_sessions",
        help="Path to sessions directory (default: jules_sessions)"
    )
    
    args = parser.parse_args()
    
    # Load local sessions
    sessions = load_local_sessions(args.sessions_dir)
    
    if not sessions:
        print("No sessions found in", args.sessions_dir, file=sys.stderr)
        sys.exit(1)
    
    # Optionally refresh from API
    api_key = os.environ.get("JULES_API_KEY", "")
    if args.api and api_key:
        print(f"Refreshing {len(sessions)} sessions from API...", file=sys.stderr)
        for session in sessions:
            session_id = session.get("id") or session.get("name", "").split("/")[-1]
            if session_id:
                updated = fetch_session_from_api(session_id, api_key)
                if updated:
                    session.update(updated)
    
    # Categorize and filter
    results = []
    for session in sessions:
        result = categorize_session(session, args.stale_minutes)
        if result:
            result["suggested_message"] = generate_message(result)
            results.append(result)
    
    # Sort by priority
    results.sort(key=lambda x: x.get("priority", 99))
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("No sessions needing response.")
            return
        
        print(f"Found {len(results)} session(s) needing response:\n")
        print("=" * 80)
        
        for r in results:
            print(f"\nSession: {r['session_id']}")
            print(f"Title: {r['title']}")
            print(f"State: {r['state']} → {r['description']}")
            if r.get("branch"):
                print(f"Branch: {r['branch']}")
            if r.get("pr_url"):
                print(f"PR: {r['pr_url']}")
            print(f"\nSuggested Response:\n{r['suggested_message']}")
            print("-" * 80)
        
        print("\n" + "=" * 80)
        print("📝 REMINDER: Log your sent prompts for tracking!")
        print("   Append to: references/sent_responses.md")
        print("   Format: session_id, prompt_type, prompt_sent, outcome")
        print("=" * 80)


if __name__ == "__main__":
    main()
