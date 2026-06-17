#!/usr/bin/env python3
import argparse,json
from agent_core import rj,OUTPUTS_DIR
p=argparse.ArgumentParser(); p.add_argument('--branch'); a=p.parse_args(); m=rj(OUTPUTS_DIR/'target_matrix.json',{'branches':{}}); print(json.dumps(m['branches'].get(a.branch) if a.branch else m,indent=2))
