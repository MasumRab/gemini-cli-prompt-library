#!/usr/bin/env python3
"""Show question queue.

This script prints questions, optionally filtered by branch.
"""

import argparse, json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import analyse_outputs, rj, OUTPUTS_DIR
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

p = argparse.ArgumentParser(description="Show question queue")
p.add_argument("--branch", help="Filter by branch name")
a = p.parse_args()

try:
    analyse_outputs()
    q = rj(OUTPUTS_DIR / "question_queue.json", [])
    if a.branch:
        q = [x for x in q if x.get("branch") == a.branch]
    print(json.dumps(q, indent=2))
except Exception as e:
    print(f"Error reading questions: {e}", file=sys.stderr)
    sys.exit(1)
