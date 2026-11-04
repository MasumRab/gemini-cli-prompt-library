#!/usr/bin/env python3
"""Run target analysis and write outputs.

This script analyzes branches for target intent and writes
target_matrix.json, target_questions.json, and target_recommendations.json.
"""

import json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import target_analyse
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

try:
    result = target_analyse()
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Target analysis failed: {e}", file=sys.stderr)
    sys.exit(1)
