#!/usr/bin/env python3
"""Show decision history.

This script prints the decision log, optionally filtered by branch.
"""

import argparse, json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import decisions
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

p = argparse.ArgumentParser(description="Show decision history")
p.add_argument("--branch", help="Filter by branch or target root")
a = p.parse_args()

try:
    ev = decisions()
    if a.branch:
        ev = [x for x in ev if x.get("branch") == a.branch]
    print(json.dumps(ev, indent=2))
except Exception as e:
    print(f"Error reading decision history: {e}", file=sys.stderr)
    sys.exit(1)
