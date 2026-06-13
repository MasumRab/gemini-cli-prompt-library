# Graphite Agent V6.4

V6.4 implements V5.3 strict Topology Audit Engine capabilities inside a V6-style architecture.

Capabilities included:
- distance-based root ownership with ambiguity detection
- canonical cycle detection normalised by rotation and orientation
- Kahn topological validation
- parent-exists, lineage-clear, patch-unique and topo-valid invariants
- sibling-scoped patch-ID ghost detection
- `status_audit.json` output
- strict post-action invariant verification

Run:
```bash
python .graphite-agent/1_analyze_and_plan.py
GRAPHITE_DRY_RUN=1 python .graphite-agent/2_strict_executor.py
```
