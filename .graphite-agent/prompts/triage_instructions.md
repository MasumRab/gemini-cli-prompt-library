# Triage Instructions

## Reading Order
1. `outputs/analysis_summary.json` — branch counts and status overview
2. `outputs/root_health.json` — root staleness and execution readiness
3. `outputs/target_matrix.json` — target intent and conflicts
4. `outputs/triage_packets.json` — non-executable branches and diagnostic categories
5. `outputs/relationship_graph.json` — edge evidence and classifications
6. Raw Git only if diagnostics are ambiguous or missing

## Decision Rules
- **safe** / **needs_restack**: Can proceed to execution after validation
- **manual_triage**: Requires human decision via question queue
- **blocked_merge_commits**: Requires linearisation or recreation
- **cross_root_conflict**: Requires rebase onto correct root
- **unrooted**: Requires root owner assignment

## Append-Only Decisions
All decisions are recorded in `outputs/decision_log.jsonl` and summarized in `outputs/current_decisions.json`. Never edit historical decisions — append new correction events instead.
