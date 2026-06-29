#!/usr/bin/env python3
import json
from agent_core import root_health

print(json.dumps(root_health(), indent=2))
