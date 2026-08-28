EXECUTABLE_STATUSES = {"safe", "needs_restack"}
TRIAGE_STATUSES = {
    "cross_root_conflict",
    "blocked_merge_commits",
    "cycle",
    "unrooted",
    "patch_equivalence_only",
    "declared_base_mismatch",
    "ambiguous_relationship",
    "complex_hub_node",
    "complex_dag_dependency",
    "ghost_commit_overlap",
}
EXECUTABLE_EDGE_TYPES = {
    "declared_pr_base",
    "declared_base_mismatch",
    "nearest_same_root_ancestor",
}
BLOCKED_EDGE_TYPES = {
    "cross_root_ancestry",
    "trunk_update_merge",
    "foreign_dag_merge",
    "cycle_edge",
}
RELATIONSHIP_CLASSIFICATIONS = {"executable", "triage_only", "blocked", "informational"}
GRAPHITE_ACTIONS = {"track_only", "track_and_restack"}
