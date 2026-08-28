#!/usr/bin/env python3
import argparse, json

p = argparse.ArgumentParser()
p.add_argument("--branch", required=True)
p.add_argument("--choice", required=True)
p.add_argument("--dry-run", action="store_true")
a = p.parse_args()
print(
    json.dumps(
        {
            "mode": "dry_run" if a.dry_run else "preview",
            "branch": a.branch,
            "proposed_choice": a.choice,
            "mutates_state": False,
        },
        indent=2,
    )
)
