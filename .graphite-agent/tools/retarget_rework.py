#!/usr/bin/env python3
"""Preview retarget rework without mutating state.

This script generates a preview of proposed target changes.
"""

import argparse, json, sys

p = argparse.ArgumentParser(description="Preview retarget rework")
p.add_argument("--branch", required=True, help="Branch name")
p.add_argument("--target", required=True, help="Proposed target")
p.add_argument("--dry-run", action="store_true", help="Preview without mutating state")
a = p.parse_args()

try:
    result = {
        "mode": "dry_run" if a.dry_run else "preview",
        "branch": a.branch,
        "proposed_target": a.target,
        "mutates_state": False,
    }
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Retarget preview failed: {e}", file=sys.stderr)
    sys.exit(1)
