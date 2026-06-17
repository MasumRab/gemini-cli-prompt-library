#!/usr/bin/env python3
import json
from agent_core import validation_report
report=validation_report()
print(json.dumps(report, indent=2))
raise SystemExit(1 if report['status'] != 'pass' else 0)
