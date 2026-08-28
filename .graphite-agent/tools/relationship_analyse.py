#!/usr/bin/env python3
import json
from agent_core import snap, relationship_graph, wj, OUTPUTS_DIR

rel = relationship_graph(snap())
wj(OUTPUTS_DIR / "relationship_graph.json", rel)
print(json.dumps(rel, indent=2))
