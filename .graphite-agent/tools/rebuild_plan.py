#!/usr/bin/env python3
import json
from agent_core import plan

print(json.dumps(plan(), indent=2))
