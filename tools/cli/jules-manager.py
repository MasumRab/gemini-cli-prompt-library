#!/usr/bin/env python3
"""Jules Session Manager - CLI tool to manage Jules sessions via REST API.
Compatible with .agents/commands/ structure for cross-agent use.

Usage:
    python .agents/commands/jules-manager.py list [pageSize]
    python .agents/commands/jules-manager.py session SESSION_ID
    python .agents/commands/jules-manager.py send SESSION_ID "Your message"
    python .agents/commands/jules-manager.py approve SESSION_ID
"""

import os
import sys
import json
import requests

API_BASE = "https://jules.googleapis.com/v1alpha"
API_KEY = os.environ.get("JULES_API_KEY")

if not API_KEY:
    print("Error: JULES_API_KEY not set. Generate at https://jules.google.com/settings#api")
    sys.exit(1)

HEADERS = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}


def api_call(path, method="GET", data=None):
    url = f"{API_BASE}/{path}"
    response = requests.request(method, url, headers=HEADERS, json=data)
    if not response.ok:
        error_text = response.text if hasattr(response, 'text') else str(response.status)
        print(f"API Error ({response.status}): {error_text}")
        sys.exit(1)
    return response.json()


def cmd_list(page_size=20):
    try:
        data = api_call(f"sessions?pageSize={page_size}")
        for session in data.get("sessions", []):
            pr_info = ""
            for output in session.get("outputs", []):
                if "pullRequest" in output:
                    pr = output["pullRequest"]
                    pr_info = f" -> PR #{pr.get('url', '').split('/')[-1]}"
            print(f"{session['name']}: {session['state']}{pr_info}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_session(session_id):
    if not session_id.startswith("sessions/"):
        session_id = f"sessions/{session_id}"
    try:
        data = api_call(session_id)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")


def cmd_send(session_id, message):
    if not session_id.startswith("sessions/"):
        session_id = f"sessions/{session_id}"
    try:
        api_call(f"{session_id}:sendMessage", method="POST", data={"prompt": message})
        print("Message sent successfully")
    except Exception as e:
        print(f"Error: {e}")


def cmd_approve(session_id):
    if not session_id.startswith("sessions/"):
        session_id = f"sessions/{session_id}"
    try:
        api_call(f"{session_id}:approvePlan", method="POST", data={})
        print("Plan approved successfully")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: jules-manager.py <list|session|send|approve> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        cmd_list(int(sys.argv[2])) if len(sys.argv) > 2 else cmd_list()
    elif cmd == "session" and len(sys.argv) > 2:
        cmd_session(sys.argv[2])
    elif cmd == "send" and len(sys.argv) > 3:
        cmd_send(sys.argv[2], sys.argv[3])
    elif cmd == "approve" and len(sys.argv) > 2:
        cmd_approve(sys.argv[2])
    else:
        print(f"Unknown command or missing args")
        print("Available: list [pageSize], session SESSION_ID, send SESSION_ID 'msg', approve SESSION_ID")
        sys.exit(1)