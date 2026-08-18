#!/usr/bin/env python3
"""Query branch status and triage information.

This script allows querying by branch name or status filter.
"""

import argparse, json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import snap, nodes, analyse_outputs, rj, OUTPUTS_DIR
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

p = argparse.ArgumentParser(description="Query branch status")
p.add_argument("--branch", help="Branch name")
p.add_argument("--status", help="Status filter")
a = p.parse_args()

try:
    s = snap()
    d = analyse_outputs()
    if a.branch:
        print(
            json.dumps(
                {
                    "branch": a.branch,
                    "node": nodes(s).get(a.branch),
                    "triage_packet": rj(OUTPUTS_DIR / "triage_packets.json", {}).get(
                        a.branch
                    ),
                },
                indent=2,
            )
        )
    elif a.status:
        print(
            json.dumps(
                [b for b, n in nodes(s).items() if n.get("status") == a.status],
                indent=2,
            )
        )
    else:
        p.error("provide --branch or --status")
except Exception as e:
    print(f"Query failed: {e}", file=sys.stderr)
    sys.exit(1)
