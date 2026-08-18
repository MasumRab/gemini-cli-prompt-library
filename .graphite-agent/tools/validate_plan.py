#!/usr/bin/env python3
"""Validate execution plan safety.

This script checks the execution plan for unsafe statuses, missing parents,
or branches that appear in both triage and execution queues.
"""

import json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import validate_plan
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

try:
    r = validate_plan()
    print(json.dumps(r, indent=2))
    raise SystemExit(1 if r.get("status") != "pass" else 0)
except Exception as e:
    print(f"Plan validation failed: {e}", file=sys.stderr)
    sys.exit(1)
