#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

from lib.io import rj, run_id, write_run_text, wt
from lib.reports import branch_stacking_report

parser = argparse.ArgumentParser(
    description="Write portable branch stacking markdown report."
)
parser.add_argument("--local-only", action="store_true")
parser.add_argument("--run-id")
args = parser.parse_args()

latest_risk = rj(".graphite-agent/outputs/latest/replay_risk.json", {}) or {}
rid = args.run_id or latest_risk.get("run_id") or run_id()
inventory = (
    rj(f".graphite-agent/outputs/runs/{rid}/repo_inventory.json")
    or rj(".graphite-agent/outputs/latest/repo_inventory.json")
    or {"run_id": rid, "repo": {}, "state": {}, "targets": {}}
)
risk = (
    rj(f".graphite-agent/outputs/runs/{rid}/replay_risk.json")
    or latest_risk
    or {"run_id": rid, "summary": {}}
)
validation = (
    rj(f".graphite-agent/outputs/runs/{rid}/validation/replay_validation.json")
    or rj(".graphite-agent/outputs/latest/validation/replay_validation.json")
    or {}
)
report = branch_stacking_report(inventory, risk, validation)
write_run_text("branch_stacking_report.md", report, rid)
wt(".graphite-agent/reports/branch_stacking_report.md", report)
print(report)
