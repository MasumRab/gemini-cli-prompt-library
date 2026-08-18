#!/usr/bin/env python3
"""Explain branch status and topology.

This script prints the status, root, parent, and reason for a branch.
"""

import argparse, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import snap, nodes, analyse_outputs
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

p = argparse.ArgumentParser(description="Explain branch status")
p.add_argument("--branch", required=True, help="Branch name to explain")
a = p.parse_args()

try:
    analyse_outputs()
    n = nodes(snap()).get(a.branch)
    if not n:
        print(f"Branch not found: {a.branch}", file=sys.stderr)
        sys.exit(1)
    print(
        f"Branch: {a.branch}\n"
        f"Status: {n.get('status')}\n"
        f"Root: {n.get('root_branch')}\n"
        f"Parent: {n.get('resolved_parent')}\n"
        f"Reason: {n.get('reason')}"
    )
except Exception as e:
    print(f"Explanation failed: {e}", file=sys.stderr)
    sys.exit(1)
