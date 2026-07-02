#!/usr/bin/env python3
import json
from agent_core import rj, OUTPUTS_DIR

so = rj(OUTPUTS_DIR / "stack_order.json", {"targets": {}})
fail = [
    {"id": "blocked-target-has-stacks", "target_root": t}
    for t, s in so["targets"].items()
    if not s.get("execution_allowed") and s.get("stacks")
]
r = {"status": "blocked" if fail else "pass", "failed_checks": fail}
(OUTPUTS_DIR / "stack_order_validation.json").write_text(json.dumps(r, indent=2))
print(json.dumps(r, indent=2))
raise SystemExit(1 if fail else 0)
