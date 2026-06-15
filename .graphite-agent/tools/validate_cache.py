#!/usr/bin/env python3
import json
from pathlib import Path
from agent_core import OUTPUTS_DIR, read_json

required = [
    "analysis_summary.json",
    "relationship_graph.json",
    "triage_packets.json",
    "recommendations.json",
]
missing = [f for f in required if not (OUTPUTS_DIR / f).exists()]
report = {"status": "blocked" if missing else "pass", "missing": missing}
print(json.dumps(report, indent=2))
raise SystemExit(1 if missing else 0)
