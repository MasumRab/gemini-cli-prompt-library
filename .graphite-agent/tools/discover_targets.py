#!/usr/bin/env python3
"""Discover target roots from analysis snapshot.

This script identifies configured roots and inferred roots from the branch graph.
"""

import json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import discover_targets
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

try:
    result = discover_targets()
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Target discovery failed: {e}", file=sys.stderr)
    sys.exit(1)
