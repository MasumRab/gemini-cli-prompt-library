#!/bin/bash
set -euo pipefail

REPOS=(
    "/home/engine/project"
    # Add other repo paths if applicable
)

echo "Checking multiple repositories..."
uv run python -m tools.multi_repo.jules_multi_repo "${REPOS[@]}"
