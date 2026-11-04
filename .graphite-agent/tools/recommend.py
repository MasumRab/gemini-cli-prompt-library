#!/usr/bin/env python3
"""Generate recommendations based on analysis.

This script runs the analysis pipeline and prints the summary section.
"""

import json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import analyse_outputs
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

try:
    result = analyse_outputs()
    print(json.dumps(result.get("summary", result), indent=2))
except Exception as e:
    print(f"Recommendation generation failed: {e}", file=sys.stderr)
    sys.exit(1)
