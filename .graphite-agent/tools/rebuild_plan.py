#!/usr/bin/env python3
"""Rebuild and display the execution plan.

This script prints the current execution plan.
"""

import json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import plan
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

try:
    result = plan()
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error reading plan: {e}", file=sys.stderr)
    sys.exit(1)
