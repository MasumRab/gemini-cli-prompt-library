#!/usr/bin/env python3
import argparse, json
from agent_core import query_branch
p=argparse.ArgumentParser(); p.add_argument('--branch', required=True); p.add_argument('--choice', required=True); p.add_argument('--dry-run', action='store_true'); a=p.parse_args()
q=query_branch(a.branch); current=q['node'].get('resolved_parent'); proposed=a.choice.split('=',1)[1] if a.choice.startswith('parent=') else None
print(json.dumps({'mode':'dry_run' if a.dry_run else 'preview','branch':a.branch,'current_parent':current,'proposed_choice':a.choice,'would_change':{'resolved_parent':{'from':current,'to':proposed}},'relationships':[e['id'] for e in q['relationships']]}, indent=2))
