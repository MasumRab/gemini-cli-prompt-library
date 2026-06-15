#!/usr/bin/env python3
import argparse, json
from agent_core import revoke_decision
p=argparse.ArgumentParser(); p.add_argument('--decision', required=True); p.add_argument('--branch', required=True); p.add_argument('--reason', required=True); a=p.parse_args()
print(json.dumps(revoke_decision(a.decision, a.branch, a.reason), indent=2))
