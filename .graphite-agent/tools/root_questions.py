#!/usr/bin/env python3
import argparse, json
from agent_core import rj, OUTPUTS_DIR

p = argparse.ArgumentParser()
p.add_argument("--target")
a = p.parse_args()
q = rj(OUTPUTS_DIR / "root_refresh_questions.json", [])
if a.target:
    q = [x for x in q if x.get("target_root") == a.target]
print(json.dumps(q, indent=2))
