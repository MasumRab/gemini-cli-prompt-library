#!/usr/bin/env python3
"""Build and persist the relationship graph.

This script generates the relationship graph from the analysis snapshot
and writes it to the outputs directory.
"""

import json, sys
from pathlib import Path

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    from agent_core import snap, relationship_graph, wj, OUTPUTS_DIR
except ImportError as e:
    print(f"Error loading agent_core: {e}", file=sys.stderr)
    sys.exit(1)

try:
    rel = relationship_graph(snap())
    wj(OUTPUTS_DIR / "relationship_graph.json", rel)
    print(json.dumps(rel, indent=2))
except Exception as e:
    print(f"Relationship analysis failed: {e}", file=sys.stderr)
    sys.exit(1)
