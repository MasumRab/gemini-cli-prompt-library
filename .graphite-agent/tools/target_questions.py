#!/usr/bin/env python3
import argparse
import json
from agent_core import rj, OUTPUTS_DIR

p = argparse.ArgumentParser()
p.add_argument("--branch")
a = p.parse_args()
q = rj(OUTPUTS_DIR / "target_questions.json", [])
if a.branch:
    q = [x for x in q if x.get("branch") == a.branch]
print(json.dumps(q, indent=2))
