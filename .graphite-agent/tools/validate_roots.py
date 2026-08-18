#!/usr/bin/env python3
"""Validate root health and execution readiness.

This script checks root_health.json for stale roots that block execution
and exits with non-zero status if validation fails.
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
    rh = rj(OUTPUTS_DIR / "root_health.json", {"roots": {}})
    fail = [
        {"id": "stale-root-blocker", "target_root": t}
        for t, h in rh.get("roots", {}).items()
        if h.get("health") == "stale" and not h.get("execution_allowed")
    ]
    r = {"status": "blocked" if fail else "pass", "failed_checks": fail}
    print(json.dumps(r, indent=2))
    raise SystemExit(1 if fail else 0)
except Exception as e:
    print(f"Root validation failed: {e}", file=sys.stderr)
    sys.exit(1)
