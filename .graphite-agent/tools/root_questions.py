#!/usr/bin/env python3
"""Show root refresh questions.

This script prints root refresh questions, optionally filtered by target root.
"""

import argparse, json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import rj, OUTPUTS_DIR
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

p = argparse.ArgumentParser(description="Show root refresh questions")
p.add_argument("--target", help="Filter by target root")
a = p.parse_args()

try:
    q = rj(OUTPUTS_DIR / "root_refresh_questions.json", [])
    if a.target:
        q = [x for x in q if x.get("target_root") == a.target]
    print(json.dumps(q, indent=2))
except Exception as e:
    print(f"Error reading root questions: {e}", file=sys.stderr)
    sys.exit(1)
