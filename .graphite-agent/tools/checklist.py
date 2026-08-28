#!/usr/bin/env python3
"""Run pre-execution safety checklist.

This script executes validate_plan and prints the results.
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
    result = validate_plan()
    print(json.dumps(result, indent=2))
    sys.exit(1 if result.get("status") != "pass" else 0)
except Exception as e:
    print(f"Checklist failed: {e}", file=sys.stderr)
    sys.exit(1)
