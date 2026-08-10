#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

from lib.io import rj, run_id, write_run_json

parser = argparse.ArgumentParser(
    description="Build a conservative dry-run command plan."
)
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--run-id")
args = parser.parse_args()

latest_risk = rj(".graphite-agent/outputs/latest/replay_risk.json", {}) or {}
rid = args.run_id or latest_risk.get("run_id") or run_id()
validation = (
    rj(f".graphite-agent/outputs/runs/{rid}/validation/replay_validation.json")
    or rj(".graphite-agent/outputs/latest/validation/replay_validation.json")
    or {"status": "blocked"}
)
blocked = validation.get("status") != "pass"
plan = {
    "run_id": rid,
    "mode": "dry_run",
    "execution_allowed": False,
    "blocked_by": ["validate_replay"] if blocked else [],
    "commands": [] if blocked else [],
}
write_run_json("command_plan.json", plan, rid)
print(json.dumps(plan, indent=2))
