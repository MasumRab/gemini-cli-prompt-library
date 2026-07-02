#!/usr/bin/env python3
"""Execute approved Graphite commands from the queue."""
import json
import subprocess
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).parent.resolve()
OUTPUTS_DIR = AGENT_DIR / "outputs"
RECOMMENDATIONS_FILE = OUTPUTS_DIR / "recommendations.json"


def execute_approved():
    """Execute approved branch recommendations from recommendations.json."""
    if not RECOMMENDATIONS_FILE.exists():
        print("No recommendations found.")
        return

    with open(RECOMMENDATIONS_FILE) as f:
        recommendations = json.load(f)

    executed = []
    for branch, rec in recommendations.items():
        action = rec.get("recommended_action")
        # Only execute "safe" actions that have been approved
        if action in ("track_and_restack", "track_only"):
            try:
                # Use Graphite CLI to execute the recommended action
                result = subprocess.run(
                    ["gt", "branch", "track", branch],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    executed.append({"branch": branch, "action": action, "status": "success"})
                else:
                    executed.append({"branch": branch, "action": action, "status": "failed", "error": result.stderr})
            except FileNotFoundError:
                executed.append({"branch": branch, "action": action, "status": "failed", "error": "gt command not found"})

    # Write execution results
    with open(OUTPUTS_DIR / "execution_results.json", "w") as f:
        json.dump(executed, f, indent=2)

    print(f"Executed {len(executed)} approved commands.")


if __name__ == "__main__":
    execute_approved()
