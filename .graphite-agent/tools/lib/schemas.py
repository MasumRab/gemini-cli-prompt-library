from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class PR:
    number: Optional[int]
    title: Optional[str]
    url: Optional[str]
    head_ref_name: str
    head_ref_oid: Optional[str]
    base_ref_name: Optional[str]
    is_draft: bool = False
    review_decision: Optional[str] = None
    merge_state_status: Optional[str] = None
    mergeable: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    id: str
    from_ref: str
    to_ref: str
    edge_type: str
    classification: str
    status: str
    confidence: str
    root_branch: Optional[str]
    evidence: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Audit:
    root_owner: Dict[str, Any] = field(default_factory=dict)
    invariants: Dict[str, Any] = field(default_factory=dict)
    failed_invariants: List[str] = field(default_factory=list)
    triage_reason: List[str] = field(default_factory=list)
    cycle_path: List[str] = field(default_factory=list)
    merge_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Node:
    branch: str
    root_branch: Optional[str]
    resolved_parent: Optional[str]
    status: str
    reason: str
    audit: Audit
    relationship_edges: List[str]
    sources: List[str] = field(default_factory=list)
    targets: List[str] = field(default_factory=list)
    risk_annotations: List[Dict[str, Any]] = field(default_factory=list)
