#!/usr/bin/env python3
import argparse,json
from agent_core import snap,nodes,analyse_outputs,rj,OUTPUTS_DIR
p=argparse.ArgumentParser(); p.add_argument('--branch'); p.add_argument('--status'); a=p.parse_args(); s=snap(); d=analyse_outputs()
if a.branch: print(json.dumps({'branch':a.branch,'node':nodes(s).get(a.branch),'triage_packet':rj(OUTPUTS_DIR/'triage_packets.json',{}).get(a.branch)},indent=2))
elif a.status: print(json.dumps([b for b,n in nodes(s).items() if n.get('status')==a.status],indent=2))
else: p.error('provide --branch or --status')
