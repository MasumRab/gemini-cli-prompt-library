#!/usr/bin/env python3
import json
from agent_core import run_diagnostics
print(json.dumps(run_diagnostics(write=True)['recommendations'], indent=2))
