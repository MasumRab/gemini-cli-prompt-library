#!/usr/bin/env python3
"""Validate target consistency and intent resolution.

This script checks the target matrix for unresolved target decisions
and writes a validation report.
"""

import json, sys
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

try:
    m = rj(OUTPUTS_DIR / "target_matrix.json", {"branches": {}})
    fail = [
        {"id": "unresolved-target-intent", "branch": b}
        for b, x in m.get("branches", {}).items()
        if x.get("requires_user_decision")
    ]
    r = {"status": "blocked" if fail else "pass", "failed_checks": fail}
    (OUTPUTS_DIR / "target_validation_report.json").write_text(json.dumps(r, indent=2))
    print(json.dumps(r, indent=2))
    raise SystemExit(1 if fail else 0)
except Exception as e:
    print(f"Target validation failed: {e}", file=sys.stderr)
    sys.exit(1)
