#!/usr/bin/env python3
import argparse, json
from agent_core import record_decision

p = argparse.ArgumentParser()
p.add_argument("--question", required=True)
p.add_argument("--target", required=True)
p.add_argument("--choice", required=True)
p.add_argument("--reason", required=True)
a = p.parse_args()
print(
    json.dumps(
        record_decision(
            a.question, a.target, a.choice, a.reason, "root_refresh_policy"
        ),
        indent=2,
    )
)
