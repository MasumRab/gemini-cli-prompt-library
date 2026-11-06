#!/usr/bin/env python3
import argparse
from agent_core import snap, nodes, analyse_outputs

p = argparse.ArgumentParser()
p.add_argument("--branch", required=True)
a = p.parse_args()
analyse_outputs()
n = nodes(snap()).get(a.branch)
if not n:
    raise SystemExit("branch not found")
print(
    f"Branch: {a.branch}\nStatus: {n.get('status')}\nRoot: {n.get('root_branch')}\nParent: {n.get('resolved_parent')}\nReason: {n.get('reason')}"
)
