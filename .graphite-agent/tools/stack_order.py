#!/usr/bin/env python3
import json
from agent_core import stack_order

print(json.dumps(stack_order(), indent=2))
