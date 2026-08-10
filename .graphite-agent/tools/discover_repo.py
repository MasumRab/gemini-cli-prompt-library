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
from lib.io import run_id, write_run_json

parser = argparse.ArgumentParser(
    description="Discover portable repo inventory for branch stacking analysis."
)
parser.add_argument(
    "--local-only",
    action="store_true",
    help="Do not require network, gh, or Graphite metadata.",
)
parser.add_argument("--run-id")
args = parser.parse_args()

rid = args.run_id or run_id()
config = load_config(
    overrides={"repo": {"mode": "local_only"}} if args.local_only else None
)
inventory = collect_inventory(config, rid)
write_run_json("repo_inventory.json", inventory, rid)
print(json.dumps(inventory, indent=2))
