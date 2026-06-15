#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
from agent_core import validation_report, read_json, OUTPUTS_DIR
report=validation_report()
if report['status']!='pass':
    print(json.dumps(report, indent=2)); sys.exit(1)
plan=read_json(OUTPUTS_DIR/'execution_plan.json')
for step in plan.get('execution_queue', []):
    branch=step['branch']; parent=step['resolved_parent']; action=step['action']
    for cmd in [f'git checkout {branch}', f'gt track {branch} --parent {parent}']:
        print('[EXEC]', cmd); r=subprocess.run(cmd, shell=True);
        if r.returncode: sys.exit(r.returncode)
    if action=='track_and_restack':
        print('[EXEC] gt restack'); r=subprocess.run('gt restack', shell=True);
        if r.returncode: sys.exit(r.returncode)
print('[SUCCESS] Approved execution complete')
