#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

from lib.io import rj, run_id, write_run_json


def validate(risk):
    failed = []
    state = risk.get("repository_state", {})
    conflicts = risk.get("conflicts", {})
    if state.get("active_rebase"):
        failed.append(
            {
                "id": "active-rebase",
                "severity": "critical",
                "message": "Repository is currently in an active rebase state.",
            }
        )
    if state.get("active_merge"):
        failed.append(
            {
                "id": "active-merge",
                "severity": "critical",
                "message": "Repository is currently in an active merge state.",
            }
        )
    if state.get("active_cherry_pick"):
        failed.append(
            {
                "id": "active-cherry-pick",
                "severity": "critical",
                "message": "Repository is currently in an active cherry-pick state.",
            }
        )
    if conflicts.get("conflicted_files"):
        failed.append(
            {
                "id": "conflicted-files",
                "severity": "critical",
                "message": "Conflicted files are present.",
            }
        )
    if conflicts.get("conflict_markers_detected"):
        failed.append(
            {
                "id": "conflict-markers",
                "severity": "critical",
                "message": "Conflict markers are present in files.",
            }
        )
    if any(
        x.get("conflict_type")
        in {"both_modified", "deleted_by_theirs", "deleted_by_us"}
        for x in conflicts.get("conflicted_files", [])
    ):
        failed.append(
            {
                "id": "blocking-conflict-types",
                "severity": "critical",
                "message": "Both-modified or delete/modify conflicts are present.",
            }
        )
    if risk.get("summary", {}).get("overall_risk") == "high" and not failed:
        failed.append(
            {
                "id": "high-replay-risk",
                "severity": "high",
                "message": "Replay risk is high.",
            }
        )
    return {
        "status": "blocked" if failed else "pass",
        "failed_checks": failed,
        "next_actions": (
            [
                "Resolve or abort the active replay.",
                "Rerun replay_risk.py after working tree is clean.",
            ]
            if failed
            else ["Replay validation passed."]
        ),
    }


parser = argparse.ArgumentParser(
    description="Validate replay risk before command plan generation."
)
parser.add_argument("--run-id")
args = parser.parse_args()

rid = (
    args.run_id
    or (rj(".graphite-agent/outputs/latest/replay_risk.json", {}) or {}).get("run_id")
    or run_id()
)
risk = (
    rj(f".graphite-agent/outputs/runs/{rid}/replay_risk.json")
    or rj(".graphite-agent/outputs/latest/replay_risk.json")
    or {"run_id": rid, "summary": {"overall_risk": "high"}}
)
result = validate(risk)
write_run_json("validation/replay_validation.json", result, rid)
print(json.dumps(result, indent=2))
