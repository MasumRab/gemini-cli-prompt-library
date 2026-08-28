from dataclasses import dataclass, field
from typing import Any, Literal

RelationshipClassification = Literal[
    "executable", "triage_only", "blocked", "informational"
]
BranchStatus = Literal[
    "safe",
    "needs_restack",
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
]


@dataclass
class PullRequestInfo:
    number: int | None
    title: str | None
    url: str | None
    head_ref_name: str
    head_ref_oid: str | None
    base_ref_name: str | None
    is_draft: bool = False
    review_decision: str | None = None
    merge_state_status: str | None = None
    mergeable: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class RelationshipEdge:
    id: str
    from_ref: str
    to_ref: str
    edge_type: str
    classification: RelationshipClassification
    status: str
    confidence: str
    root_branch: str | None
    evidence: list[str]


@dataclass
class BranchAudit:
    root_owner: dict[str, Any]
    invariants: dict[str, bool]
    failed_invariants: list[str]
    triage_reason: list[str]


@dataclass
class BranchNode:
    branch: str
    root_branch: str | None
    resolved_parent: str | None
    status: BranchStatus | str
    reason: str
    audit: BranchAudit
    relationship_edges: list[str]
    risk_annotations: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ExecutionStep:
    id: str
    branch: str
    resolved_parent: str
    root_branch: str
    status: Literal["safe", "needs_restack"]
    action: Literal["track_only", "track_and_restack"]
    relationship_edges: list[str]
    preconditions: dict[str, bool]


@dataclass
class TriagePacket:
    id: str
    branch: str
    status: str
    root_branch: str | None
    primary_reason: str
    relationship_edges: list[str]
    candidate_parents: list[str]
    recommended_action: str
    risk_annotations: list[dict[str, Any]]
    detail_refs: dict[str, Any]
