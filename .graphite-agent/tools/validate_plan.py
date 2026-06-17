#!/usr/bin/env python3
import json
from agent_core import validate_plan
r=validate_plan(); print(json.dumps(r,indent=2)); raise SystemExit(1 if r['status']!='pass' else 0)
