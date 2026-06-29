#!/usr/bin/env python3
import json
from agent_core import OUTPUTS_DIR

req = [
    "analysis_summary.json",
    "relationship_graph.json",
    "triage_packets.json",
    "recommendations.json",
]
miss = [x for x in req if not (OUTPUTS_DIR / x).exists()]
r = {"status": "blocked" if miss else "pass", "missing": miss}
print(json.dumps(r, indent=2))
raise SystemExit(1 if miss else 0)
