#!/usr/bin/env python3
"""Revise a previous decision.

This script records a new decision event that supersedes an earlier one.
"""

import argparse, json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import record_decision
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

p = argparse.ArgumentParser(description="Revise a decision")
p.add_argument("--decision", required=True, help="Decision ID to supersede")
p.add_argument("--question", required=True, help="Question ID")
p.add_argument("--branch", required=True, help="Branch or target root")
p.add_argument("--choice", required=True, help="New choice")
p.add_argument("--reason", required=True, help="Reason for revision")
a = p.parse_args()

try:
    result = record_decision(
        a.question,
        a.branch,
        a.choice,
        a.reason,
        supersedes=a.decision,
        event_type="decision_revised",
    )
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Decision revision failed: {e}", file=sys.stderr)
    sys.exit(1)
