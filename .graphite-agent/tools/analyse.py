#!/usr/bin/env python3
import argparse, json, sys, os
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

from agent_core import analyse_outputs
from lib.snapshot import build_snapshot, load_config

p = argparse.ArgumentParser()
p.add_argument("--legacy-analyser")
a = p.parse_args()

if a.legacy_analyser:
    # Generate live git snapshot directly instead of using a legacy wrapper
    cfg = load_config()
    build_snapshot(cfg)

print(json.dumps(analyse_outputs(), indent=2))
