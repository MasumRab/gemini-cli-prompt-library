#!/usr/bin/env python3
import argparse,json,subprocess
from pathlib import Path
from agent_core import analyse_outputs
p=argparse.ArgumentParser(); p.add_argument('--legacy-analyser'); a=p.parse_args()
if a.legacy_analyser:
    legacy=Path(a.legacy_analyser)
    if not legacy.exists(): raise SystemExit('legacy analyser not found')
    subprocess.run(f'python {legacy}',shell=True,check=True)
print(json.dumps(analyse_outputs(),indent=2))
