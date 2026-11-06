#!/usr/bin/env python3
import json
from agent_core import rj, OUTPUTS_DIR

m = rj(OUTPUTS_DIR / "target_matrix.json", {"branches": {}})
fail = [
    {"id": "unresolved-target-intent", "branch": b}
    for b, x in m["branches"].items()
    if x.get("requires_user_decision")
]
r = {"status": "blocked" if fail else "pass", "failed_checks": fail}
(OUTPUTS_DIR / "target_validation_report.json").write_text(json.dumps(r, indent=2))
print(json.dumps(r, indent=2))
raise SystemExit(1 if fail else 0)
