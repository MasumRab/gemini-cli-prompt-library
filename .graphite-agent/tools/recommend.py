#!/usr/bin/env python3
import json
from agent_core import analyse_outputs

print(json.dumps(analyse_outputs()["summary"], indent=2))
