#!/usr/bin/env python3
"""Analyse relationship evidence graph."""
import json
from pathlib import Path
from datetime import datetime, timezone
from agent_core import OUTPUTS_DIR, ensure_dirs, write_json, read_json, build_relationship_graph, branch_nodes

def main():
    ensure_dirs()
    snapshot = read_json(OUTPUTS_DIR / 'analysis_snapshot.json', {})
    rel_graph = build_relationship_graph(snapshot)
    rel_graph['generated_at_utc'] = datetime.now(timezone.utc).isoformat()
    write_json(OUTPUTS_DIR / 'relationship_graph.json', rel_graph)
    print(json.dumps(rel_graph, indent=2))

if __name__ == '__main__':
    main()