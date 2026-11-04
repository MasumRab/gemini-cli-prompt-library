#!/usr/bin/env python3
"""Analyse root health and generate root refresh questions/recommendations.

This script evaluates configured roots for staleness and generates
bounded questions when a root refresh decision is required.
"""

import json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import root_health
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

try:
    result = root_health()
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Root health analysis failed: {e}", file=sys.stderr)
    sys.exit(1)
