#!/usr/bin/env python3
import argparse, json
from agent_core import query_branch, load_snapshot, branch_nodes

p = argparse.ArgumentParser()
p.add_argument("--branch")
p.add_argument("--status")
a = p.parse_args()
if a.branch:
    print(json.dumps(query_branch(a.branch), indent=2))
elif a.status:
    snap = load_snapshot()
    print(
        json.dumps(
            [b for b, n in branch_nodes(snap).items() if n.get("status") == a.status],
            indent=2,
        )
    )
else:
    p.error("provide --branch or --status")
