#!/usr/bin/env python3
import json
from agent_core import validation_report

print(json.dumps(validation_report(), indent=2))
