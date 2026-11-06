#!/usr/bin/env python3
import argparse, json
from agent_core import analyse_outputs, rj, OUTPUTS_DIR

p = argparse.ArgumentParser()
p.add_argument("--branch")
a = p.parse_args()
analyse_outputs()
q = rj(OUTPUTS_DIR / "question_queue.json", [])
if a.branch:
    q = [x for x in q if x.get("branch") == a.branch]
print(json.dumps(q, indent=2))
