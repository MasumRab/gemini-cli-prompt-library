#!/usr/bin/env python3
"""Validate cache consistency.

This script checks that required output files exist before proceeding.
"""

import json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import OUTPUTS_DIR
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

try:
    req = [
        "analysis_summary.json",
        "relationship_graph.json",
        "triage_packets.json",
        "question_queue.json",
        "recommendations.json",
    ]
    miss = [x for x in req if not (OUTPUTS_DIR / x).exists()]
    r = {"status": "blocked" if miss else "pass", "missing": miss}
    print(json.dumps(r, indent=2))
    raise SystemExit(1 if miss else 0)
except Exception as e:
    print(f"Cache validation failed: {e}", file=sys.stderr)
    sys.exit(1)
