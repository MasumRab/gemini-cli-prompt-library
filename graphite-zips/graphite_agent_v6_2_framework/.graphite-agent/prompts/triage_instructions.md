# Triage Instructions

1. Read `analysis_summary.json` first.
2. Open `triage_packets.json` second.
3. Hydrate only referenced relationship edges from `relationship_graph.json`.
4. Hydrate `analysis_snapshot.json` only by referenced detail path.
5. Never infer Graphite parentage from patch-id overlap alone.
6. Never auto-track a branch with cross-root or blocked merge evidence.
7. After manual Git topology changes, rerun `python .graphite-agent/1_analyze_and_plan.py`.
8. Halt on topology drift.
