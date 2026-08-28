#!/usr/bin/env python3
import argparse, json
from agent_core import decisions

p = argparse.ArgumentParser()
p.add_argument("--branch")
a = p.parse_args()
ev = decisions()
if a.branch:
    ev = [x for x in ev if x.get("branch") == a.branch]
print(json.dumps(ev, indent=2))
