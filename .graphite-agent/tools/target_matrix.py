#!/usr/bin/env python3
"""Display target matrix.

This script prints the target matrix, optionally filtered by branch.
"""

import argparse, json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import rj, OUTPUTS_DIR
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

p = argparse.ArgumentParser(description="Display target matrix")
p.add_argument("--branch", help="Filter by branch name")
a = p.parse_args()

try:
    m = rj(OUTPUTS_DIR / "target_matrix.json", {"branches": {}})
    branches = m.get("branches", {})
    if a.branch:
        branches = {a.branch: branches.get(a.branch, {})}
    print(json.dumps(branches, indent=2))
except Exception as e:
    print(f"Error reading target matrix: {e}", file=sys.stderr)
    sys.exit(1)
