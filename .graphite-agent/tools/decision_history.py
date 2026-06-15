#!/usr/bin/env python3
import argparse, json
from agent_core import read_jsonl, DECISION_LOG

p = argparse.ArgumentParser()
p.add_argument("--branch")
a = p.parse_args()
events = read_jsonl(DECISION_LOG)
if a.branch:
    events = [e for e in events if e.get("branch") == a.branch]
print(json.dumps(events, indent=2))
