#!/usr/bin/env python3
"""Revoke a previous decision.

This script records a revocation event for a decision.
"""

import argparse, json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import revoke_decision
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

p = argparse.ArgumentParser(description="Revoke a decision")
p.add_argument("--decision", required=True, help="Decision ID to revoke")
p.add_argument("--branch", required=True, help="Branch or target root")
p.add_argument("--reason", required=True, help="Reason for revocation")
a = p.parse_args()

try:
    result = revoke_decision(a.decision, a.branch, a.reason)
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Decision revocation failed: {e}", file=sys.stderr)
    sys.exit(1)
