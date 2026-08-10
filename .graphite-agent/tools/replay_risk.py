#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

from lib.config import load_config
from lib.inventory import collect_inventory
from lib.io import rj, run_id, write_run_json
from lib.replay import assess_replay

parser = argparse.ArgumentParser(
    description="Assess read-only replay risk for branch stacking."
)
parser.add_argument("--local-only", action="store_true")
parser.add_argument("--run-id")
args = parser.parse_args()

if args.run_id:
    rid = args.run_id
else:
    rid = run_id()

config = load_config(
    overrides={"repo": {"mode": "local_only"}} if args.local_only else None
)

if args.run_id:
    inventory = rj(f".graphite-agent/outputs/runs/{rid}/repo_inventory.json")
    if inventory is None:
        print(f"Error: Inventory for run {rid} not found.", file=sys.stderr)
        sys.exit(1)
else:
    inventory = rj(f".graphite-agent/outputs/runs/{rid}/repo_inventory.json") or rj(
        ".graphite-agent/outputs/latest/repo_inventory.json"
    )
    if inventory is None:
        inventory = collect_inventory(config, rid)

risk = assess_replay(config, inventory, rid)
write_run_json("replay_risk.json", risk, rid)
print(json.dumps(risk, indent=2))
