#!/usr/bin/env python3
"""Validate stack order consistency.

This script checks stack_order.json for blocked targets that still have
stacks defined, which indicates an invalid state.
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
    so = rj(OUTPUTS_DIR / "stack_order.json", {"targets": {}})
    fail = [
        {"id": "blocked-target-has-stacks", "target_root": t}
        for t, s in so.get("targets", {}).items()
        if not s.get("execution_allowed") and s.get("stacks")
    ]
    r = {"status": "blocked" if fail else "pass", "failed_checks": fail}
    (OUTPUTS_DIR / "stack_order_validation.json").write_text(json.dumps(r, indent=2))
    print(json.dumps(r, indent=2))
    raise SystemExit(1 if fail else 0)
except Exception as e:
    print(f"Stack order validation failed: {e}", file=sys.stderr)
    sys.exit(1)
