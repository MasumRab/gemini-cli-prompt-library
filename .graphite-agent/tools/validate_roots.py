#!/usr/bin/env python3
import json
from agent_core import rj, OUTPUTS_DIR
rh=rj(OUTPUTS_DIR/'root_health.json',{'roots':{}}); fail=[{'id':'stale-root-blocker','target_root':t} for t,h in rh['roots'].items() if h.get('health')=='stale' and not h.get('execution_allowed')]
r={'status':'blocked' if fail else 'pass','failed_checks':fail}; print(json.dumps(r,indent=2)); raise SystemExit(1 if fail else 0)
