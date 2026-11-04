#!/usr/bin/env python3
"""Preview rework actions without mutating state.

This script generates a preview of proposed rework actions.
"""

import argparse, json, sys

p = argparse.ArgumentParser(description="Preview rework actions")
p.add_argument("--branch", required=True, help="Branch name")
p.add_argument("--choice", required=True, help="Proposed choice")
p.add_argument("--dry-run", action="store_true", help="Preview without mutating state")
a = p.parse_args()

try:
    result = {
        "mode": "dry_run" if a.dry_run else "preview",
        "branch": a.branch,
        "proposed_choice": a.choice,
        "mutates_state": False,
    }
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Rework preview failed: {e}", file=sys.stderr)
    sys.exit(1)
