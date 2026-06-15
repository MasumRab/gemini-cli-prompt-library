#!/usr/bin/env python3
import json
from agent_core import load_snapshot, rebuild_execution_plan

print(json.dumps(rebuild_execution_plan(load_snapshot()), indent=2))
