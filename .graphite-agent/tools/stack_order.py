#!/usr/bin/env python3
"""Generate stack order for executable branches.

This script builds per-root execution stacks, respecting root health
execution_allowed flags and parent-before-child ordering.
"""

import json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import stack_order
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

try:
    result = stack_order()
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Stack order generation failed: {e}", file=sys.stderr)
    sys.exit(1)
