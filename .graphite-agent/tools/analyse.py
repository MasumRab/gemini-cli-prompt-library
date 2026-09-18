#!/usr/bin/env python3
"""Analyse the repository and generate outputs.

This script loads the analysis snapshot, runs the core analysis pipeline,
and writes derived outputs to the outputs directory.
"""

import argparse, json, sys, os
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import analyse_outputs
    from lib.snapshot import build_snapshot, load_config
except ImportError as e:
    print(f"Error loading modules: {e}", file=sys.stderr)
    sys.exit(1)

p = argparse.ArgumentParser(description="Run Graphite analysis pipeline")
p.add_argument("--legacy-analyser", action="store_true",
               help="Generate live git snapshot directly")
a = p.parse_args()

try:
    if a.legacy_analyser:
        # Generate live git snapshot directly instead of using a legacy wrapper
        cfg = load_config()
        build_snapshot(cfg)

    result = analyse_outputs()
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Analysis failed: {e}", file=sys.stderr)
    sys.exit(1)
