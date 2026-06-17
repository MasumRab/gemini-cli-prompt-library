#!/usr/bin/env python3
import argparse, json
from agent_core import run_diagnostics
p=argparse.ArgumentParser(); p.add_argument('--branch'); a=p.parse_args(); qs=run_diagnostics(write=True)['question_queue']
if a.branch: qs=[q for q in qs if q.get('branch')==a.branch]
print(json.dumps(qs, indent=2))
