#!/usr/bin/env python3
"""
Session-PR Triage Skill.
Correlates Jules Sessions with GitHub PRs using bidirectional search.
"""
import argparse
import json
import os
import re
import sys

from tools.utils.auth_manager import get_github_token
from tools.sessions.jules_list_sessions import list_sessions
from tools.sessions.jules_list_activities import list_activities

try:
    from github import Github
except ImportError:
    print("❌ PyGithub required: pip install PyGithub")
    sys.exit(1)

def extract_session_from_branch(branch_name: str) -> str:
    """Extract Session ID from branch name patterns."""
    # Patterns: session-1234567890, jules-1234567890, task-1234567890
    match = re.search(r'(?:session|jules|task)[-_]?(\d{16,20})', branch_name, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def scan_activity_for_pr(activities: list) -> str:
    """Scan session activities for PR creation links."""
    for act in reversed(activities):
        text = ""
        if 'agentMessage' in act:
            text = act['agentMessage'].get('text', '')
        elif 'progressUpdated' in act:
            prog = act['progressUpdated']
            text = f"{prog.get('description', '')} {prog.get('title', '')}"

        # Explicit [a-zA-Z0-9_/-]+ avoids \w shorthand issues in Python 3.13
        pr_match = re.search(r'(github\.com/[\w\-]+/[\w\-]+/pull/\d+)', text)
        if pr_match:
            return pr_match.group(1)
    return None

def triage(repo_name: str):
    print(f"🔍 Starting Session-PR Triage for {repo_name}...")

    # Init GitHub
    gh = Github(get_github_token())
    repo = gh.get_repo(repo_name)

    # Get Active Jules Sessions (non-completed = IN_PROGRESS, AWAITING_USER_FEEDBACK, etc.)
    jules_sessions = list_sessions(active_only=True, limit=100)

    mappings = []

    print(f"📊 Analyzing {len(jules_sessions)} active sessions...")

    for session in jules_sessions:
        sid = session.get('id')
        title = session.get('title', 'Untitled')
        mapping = {
            "session_id": sid,
            "title": title,
            "state": session.get('state'),
            "pr_number": None,
            "branch_name": None,
            "confidence": "None",
            "method": ""
        }

        # Method 1: Branch Name Extraction
        # (Assuming title or internal metadata might contain branch info,
        # but primarily we check activities for git commands)
        activities = list_activities(sid, limit=20)

        # Check activities for git checkout/branch creation
        for act in activities:
            text = ""
            if 'agentMessage' in act:
                text = act['agentMessage'].get('text', '')

            # Look for "git checkout -b <branch>"
            branch_match = re.search(r'git checkout -b ([\w/-]+)', text)
            if branch_match:
                branch = branch_match.group(1)
                mapping["branch_name"] = branch
                mapping["confidence"] = "High"
                mapping["method"] = "Activity Log: Branch Creation"

                # Extract ID from branch if present
                extracted_id = extract_session_from_branch(branch)
                if extracted_id and extracted_id != sid:
                    print(f"⚠️  Mismatch: Session {sid} vs Branch ID {extracted_id}")
                break

        # Method 2: Scan for PR Links in Activity
        pr_url = scan_activity_for_pr(activities)
        if pr_url:
            pr_num = pr_url.split('/')[-1]
            mapping["pr_number"] = int(pr_num)
            mapping["confidence"] = "High"
            mapping["method"] = "Activity Log: PR Link Detected"

        # If no direct link, try to match by Session ID in Branch Name of Open PRs
        if not mapping["pr_number"]:
            # We iterate open PRs to find matching branch names
            for pr in repo.get_pulls(state='open'):
                if extract_session_from_branch(pr.head.ref) == sid:
                    mapping["pr_number"] = pr.number
                    mapping["branch_name"] = pr.head.ref
                    mapping["confidence"] = "Medium"
                    mapping["method"] = "PR Branch Name Match"
                    break

        if mapping["pr_number"] or mapping["branch_name"]:
            mappings.append(mapping)

    # Output Results
    print("\n" + "="*80)
    print(f"{'SESSION ID':<20} {'PR #':<10} {'CONFIDENCE':<12} {'METHOD'}")
    print("="*80)

    for m in mappings:
        pr_str = f"#{m['pr_number']}" if m['pr_number'] else "N/A"
        print(f"{m['session_id']:<20} {pr_str:<10} {m['confidence']:<12} {m['method']}")

    print("="*80)
    print(f"Total Mapped: {len(mappings)}")

    # Save to JSON
    with open('session_pr_map.json', 'w') as f:
        json.dump(mappings, f, indent=2)
    print("💾 Saved detailed map to session_pr_map.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Triage Sessions vs PRs")
    parser.add_argument("--repo", default="MasumRab/jules",
                    help="Repo name (e.g., owner/repo)")
    args = parser.parse_args()
    triage(args.repo)
