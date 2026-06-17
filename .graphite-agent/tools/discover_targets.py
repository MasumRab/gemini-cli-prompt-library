#!/usr/bin/env python3
import json
from agent_core import discover_targets
print(json.dumps(discover_targets(),indent=2))
