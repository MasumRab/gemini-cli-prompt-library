#!/usr/bin/env python3
"""Record a decision for a branch or target.

This script appends a decision event to the decision log.
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

p = argparse.ArgumentParser(description="Record a decision")
p.add_argument("--question", required=True, help="Question ID")
p.add_argument("--branch", required=True, help="Branch or target root")
p.add_argument("--choice", required=True, help="Chosen option")
p.add_argument("--reason", required=True, help="Reason for choice")
a = p.parse_args()

try:
    result = record_decision(a.question, a.branch, a.choice, a.reason)
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Decision recording failed: {e}", file=sys.stderr)
    sys.exit(1)
