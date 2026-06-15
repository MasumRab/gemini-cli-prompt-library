#!/usr/bin/env python3
"""Graphite Agent V7 diagnostic command layer.

This layer is intentionally additive: it preserves existing V6.4 analysis and
execution behaviour, then adds commandable diagnostics, checklist validation,
question queues, decision history, and plan rework support.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

AGENT_DIR = Path(".graphite-agent")
OUTPUTS_DIR = AGENT_DIR / "outputs"
DECISION_LOG = OUTPUTS_DIR / "decision_log.jsonl"
EXECUTABLE_STATUSES = {"safe", "needs_restack"}
BLOCKED_STATUSES = {
    "blocked_merge_commits",
    "manual_triage",
    "cross_root_conflict",
    "unrooted",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    (AGENT_DIR / "tools").mkdir(parents=True, exist_ok=True)
    (AGENT_DIR / "prompts").mkdir(parents=True, exist_ok=True)
    (AGENT_DIR / "contracts").mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def run(cmd: str, check: bool = True) -> Optional[str]:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        if check:
            raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
        return None
    return result.stdout.strip()


def load_snapshot() -> Dict[str, Any]:
    snapshot = read_json(OUTPUTS_DIR / "analysis_snapshot.json") or read_json(
        AGENT_DIR / "analysis_snapshot.json"
    )
    if not snapshot:
        raise RuntimeError(
            "No analysis snapshot found. Run the existing V6.4 analyser first, or run tools/analyse.py."
        )
    return snapshot


def load_plan() -> Dict[str, Any]:
    plan = read_json(OUTPUTS_DIR / "execution_plan.json") or read_json(
        AGENT_DIR / "plan.json"
    )
    if not plan:
        raise RuntimeError("No execution plan found. Run the analyser first.")
    return plan


def branch_nodes(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    return (
        snapshot.get("branch_graph", {}).get("nodes", {})
        or snapshot.get("branch_state", {})
        or {}
    )


def relationship_edges(snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    return snapshot.get("relationship_graph", {}).get("edges", []) or []


def next_id(prefix: str, path: Path) -> str:
    return f"{prefix}-{len(read_jsonl(path))+1:06d}"


def status_action(status: str) -> str:
    if status == "blocked_merge_commits":
        return "manual history inspection; linearise only with human approval"
    if status == "cross_root_conflict":
        return "manual review; do not auto-track across roots"
    if status == "unrooted":
        return "ask user to identify intended root or exclude from migration"
    if status == "manual_triage":
        return "inspect relationship evidence and request targeted user decision"
    return "no triage required"


def build_summary(
    snapshot: Dict[str, Any], plan: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    nodes = branch_nodes(snapshot)
    by_status: Dict[str, int] = {}
    by_root: Dict[str, int] = {}
    indexes = {
        "safe_branches": [],
        "needs_restack_branches": [],
        "cross_root_branches": [],
        "merge_blocked_branches": [],
        "unrooted_branches": [],
        "manual_triage_branches": [],
        "failed_ci_branches": [],
        "pending_ci_branches": [],
    }
    for branch, node in nodes.items():
        status = node.get("status", "unknown")
        root = node.get("root_branch") or "<none>"
        by_status[status] = by_status.get(status, 0) + 1
        by_root[root] = by_root.get(root, 0) + 1
        key = {
            "safe": "safe_branches",
            "needs_restack": "needs_restack_branches",
            "cross_root_conflict": "cross_root_branches",
            "blocked_merge_commits": "merge_blocked_branches",
            "unrooted": "unrooted_branches",
            "manual_triage": "manual_triage_branches",
        }.get(status)
        if key:
            indexes[key].append(branch)
        pr = snapshot.get("pr_catalog", {}).get(branch, {})
        ci = pr.get("ci", {})
        if ci.get("failed_contexts"):
            indexes["failed_ci_branches"].append(branch)
        if ci.get("pending_contexts"):
            indexes["pending_ci_branches"].append(branch)
    execution_count = len((plan or {}).get("execution_queue", []))
    triage_count = len((plan or {}).get("manual_triage_queue", []))
    return {
        "metadata": snapshot.get("metadata", {}),
        "counts": {
            "branches_total": len(nodes),
            "execution_queue": execution_count,
            "manual_triage_queue": triage_count,
            "open_questions": len(read_json(OUTPUTS_DIR / "question_queue.json", [])),
        },
        "by_status": dict(sorted(by_status.items())),
        "by_root": dict(sorted(by_root.items())),
        "indexes": {k: sorted(v) for k, v in indexes.items()},
    }


def build_relationship_graph(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    existing = relationship_edges(snapshot)
    if existing:
        return {"edges": existing}
    edges = []
    counter = 0
    nodes = branch_nodes(snapshot)
    for branch, node in nodes.items():
        parent = node.get("resolved_parent") or node.get("parent")
        status = node.get("status")
        if parent:
            counter += 1
            edges.append(
                {
                    "id": f"rel-{counter:06d}",
                    "from": parent,
                    "to": branch,
                    "edge_type": (
                        "existing_plan_parent"
                        if status in EXECUTABLE_STATUSES
                        else "non_executable_parent_signal"
                    ),
                    "classification": (
                        "executable" if status in EXECUTABLE_STATUSES else "triage_only"
                    ),
                    "confidence": "high" if status == "safe" else "medium",
                    "root_branch": node.get("root_branch"),
                    "evidence": [
                        node.get("reason") or "derived from existing analysis output"
                    ],
                    "metadata": {},
                }
            )
        if status in BLOCKED_STATUSES:
            counter += 1
            edges.append(
                {
                    "id": f"rel-{counter:06d}",
                    "from": node.get("root_branch"),
                    "to": branch,
                    "edge_type": status,
                    "classification": (
                        "blocked" if status != "manual_triage" else "triage_only"
                    ),
                    "confidence": (
                        "high"
                        if status in {"cross_root_conflict", "blocked_merge_commits"}
                        else "medium"
                    ),
                    "root_branch": node.get("root_branch"),
                    "evidence": [node.get("reason") or f"branch status is {status}"],
                    "metadata": {},
                }
            )
    return {"edges": edges}


def edge_ids_for_branch(rel_graph: Dict[str, Any], branch: str) -> List[str]:
    return [
        e["id"]
        for e in rel_graph.get("edges", [])
        if e.get("from") == branch or e.get("to") == branch
    ]


def build_triage_packets(
    snapshot: Dict[str, Any], rel_graph: Dict[str, Any]
) -> Dict[str, Any]:
    packets = {}
    counter = 0
    for branch, node in branch_nodes(snapshot).items():
        status = node.get("status")
        if status in EXECUTABLE_STATUSES:
            continue
        counter += 1
        packets[branch] = {
            "id": f"triage-{counter:06d}",
            "branch": branch,
            "status": status,
            "root_branch": node.get("root_branch"),
            "primary_reason": node.get("reason"),
            "candidate_parents": (
                [node.get("resolved_parent")] if node.get("resolved_parent") else []
            ),
            "relationship_edges": edge_ids_for_branch(rel_graph, branch),
            "recommended_action": status_action(status),
            "detail_refs": {
                "branch_node_ref": f"branch_graph.nodes.{branch}",
                "pr_ref": f"pr_catalog.{branch}",
                "commit_list_ref": f"branch_graph.nodes.{branch}.commits",
            },
        }
    return packets


def build_question_queue(
    snapshot: Dict[str, Any], triage_packets: Dict[str, Any]
) -> List[Dict[str, Any]]:
    questions = []
    counter = 0
    for branch, packet in triage_packets.items():
        status = packet.get("status")
        if status not in {"manual_triage", "unrooted"}:
            continue
        counter += 1
        options = ["leave_triage", "exclude_from_migration"]
        if packet.get("root_branch"):
            options.insert(0, f"parent={packet['root_branch']}")
        questions.append(
            {
                "id": f"q-{counter:06d}",
                "branch": branch,
                "priority": "high",
                "reason": packet.get("primary_reason"),
                "question": f"Choose the intended handling for {branch}.",
                "options": options,
                "recommended_option": "leave_triage",
                "confidence": "medium",
            }
        )
    return questions


def current_decisions() -> Dict[str, Dict[str, Any]]:
    events = read_jsonl(DECISION_LOG)
    active: Dict[str, Dict[str, Any]] = {}
    superseded = set()
    revoked = set()
    for ev in events:
        if ev.get("supersedes"):
            superseded.add(ev["supersedes"])
        if ev.get("event_type") in {"decision_recorded", "decision_revised"}:
            active[ev["branch"]] = ev
        if ev.get("event_type") == "decision_revoked":
            revoked.add(ev.get("target_decision_id"))
    result = {
        b: ev
        for b, ev in active.items()
        if ev.get("event_id") not in superseded and ev.get("event_id") not in revoked
    }
    write_json(OUTPUTS_DIR / "current_decisions.json", result)
    return result


def build_recommendations(
    snapshot: Dict[str, Any], triage_packets: Dict[str, Any]
) -> Dict[str, Any]:
    decisions = current_decisions()
    recs = {}
    for branch, node in branch_nodes(snapshot).items():
        decision = decisions.get(branch)
        if decision and decision.get("choice", "").startswith("parent="):
            parent = decision["choice"].split("=", 1)[1]
            recs[branch] = {
                "branch": branch,
                "recommended_action": (
                    "track_and_restack"
                    if parent != node.get("root_branch")
                    else "track_only"
                ),
                "recommended_parent": parent,
                "confidence": "human_decision",
                "requires_user_confirmation": False,
                "decision_id": decision.get("event_id"),
                "because": [decision.get("reason")],
            }
            continue
        status = node.get("status")
        if status == "safe":
            recs[branch] = {
                "branch": branch,
                "recommended_action": "track_only",
                "recommended_parent": node.get("resolved_parent"),
                "confidence": "high",
                "requires_user_confirmation": False,
            }
        elif status == "needs_restack":
            recs[branch] = {
                "branch": branch,
                "recommended_action": "track_and_restack",
                "recommended_parent": node.get("resolved_parent"),
                "confidence": "medium",
                "requires_user_confirmation": False,
            }
        elif branch in triage_packets:
            recs[branch] = {
                "branch": branch,
                "recommended_action": (
                    "ask_user" if status in {"manual_triage", "unrooted"} else "block"
                ),
                "confidence": "medium",
                "because": [node.get("reason")],
                "triage_packet": triage_packets[branch]["id"],
            }
    return recs


def rebuild_execution_plan(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    decisions = current_decisions()
    old_plan = load_plan()
    exec_q = []
    triage_q = []
    for item in old_plan.get("execution_queue", []):
        branch = item["branch"]
        decision = decisions.get(branch)
        if decision and decision.get("choice", "").startswith("parent="):
            parent = decision["choice"].split("=", 1)[1]
            item = dict(item)
            item["resolved_parent"] = parent
            item["decision_provenance"] = {
                "active_decision_id": decision.get("event_id"),
                "decision_required": True,
            }
        exec_q.append(item)
    for item in old_plan.get("manual_triage_queue", []):
        branch = item["branch"]
        decision = decisions.get(branch)
        if decision and decision.get("choice", "").startswith("parent="):
            parent = decision["choice"].split("=", 1)[1]
            exec_q.append(
                {
                    "branch": branch,
                    "root_branch": item.get("root_branch"),
                    "resolved_parent": parent,
                    "status": "needs_restack",
                    "action": "track_and_restack",
                    "reason": f"Promoted by decision {decision.get('event_id')}",
                    "decision_provenance": {
                        "active_decision_id": decision.get("event_id"),
                        "decision_required": True,
                    },
                }
            )
        else:
            triage_q.append(item)
    plan = {
        "metadata": dict(old_plan.get("metadata", {})),
        "execution_queue": exec_q,
        "manual_triage_queue": triage_q,
        "logs": old_plan.get("logs", []),
    }
    plan["metadata"]["rebuilt_at_utc"] = utc_now()
    plan["metadata"]["decision_log_path"] = str(DECISION_LOG)
    write_json(OUTPUTS_DIR / "execution_plan.json", plan)
    write_json(AGENT_DIR / "plan.json", plan)
    return plan


def run_diagnostics(write: bool = True) -> Dict[str, Any]:
    ensure_dirs()
    snapshot = load_snapshot()
    plan = load_plan()
    rel_graph = build_relationship_graph(snapshot)
    triage = build_triage_packets(snapshot, rel_graph)
    questions = build_question_queue(snapshot, triage)
    recs = build_recommendations(snapshot, triage)
    summary = build_summary(snapshot, plan)
    payload = {
        "summary": summary,
        "relationship_graph": rel_graph,
        "triage_packets": triage,
        "question_queue": questions,
        "recommendations": recs,
    }
    if write:
        write_json(OUTPUTS_DIR / "analysis_summary.json", summary)
        write_json(OUTPUTS_DIR / "relationship_graph.json", rel_graph)
        write_json(OUTPUTS_DIR / "triage_packets.json", triage)
        write_json(OUTPUTS_DIR / "question_queue.json", questions)
        write_json(OUTPUTS_DIR / "recommendations.json", recs)
        if not DECISION_LOG.exists():
            DECISION_LOG.write_text("", encoding="utf-8")
        current_decisions()
    return payload


def record_decision(
    question_id: str,
    branch: str,
    choice: str,
    reason: str,
    source: str = "human",
    supersedes: Optional[str] = None,
    event_type: str = "decision_recorded",
) -> Dict[str, Any]:
    ensure_dirs()
    event = {
        "event_id": next_id("dec", DECISION_LOG),
        "event_type": event_type,
        "question_id": question_id,
        "branch": branch,
        "choice": choice,
        "reason": reason,
        "source": source,
        "timestamp": utc_now(),
        "supersedes": supersedes,
    }
    append_jsonl(DECISION_LOG, event)
    current_decisions()
    rebuild_execution_plan(load_snapshot())
    return event


def revoke_decision(
    target_decision_id: str, branch: str, reason: str, source: str = "human"
) -> Dict[str, Any]:
    event = {
        "event_id": next_id("dec", DECISION_LOG),
        "event_type": "decision_revoked",
        "target_decision_id": target_decision_id,
        "branch": branch,
        "reason": reason,
        "source": source,
        "timestamp": utc_now(),
    }
    append_jsonl(DECISION_LOG, event)
    current_decisions()
    rebuild_execution_plan(load_snapshot())
    return event


def validation_report() -> Dict[str, Any]:
    snapshot = load_snapshot()
    plan = load_plan()
    diag = run_diagnostics(write=True)
    failed = []
    nodes = branch_nodes(snapshot)
    triage = diag["triage_packets"]
    for item in plan.get("execution_queue", []):
        branch = item.get("branch")
        status = item.get("status")
        if status not in EXECUTABLE_STATUSES:
            failed.append(
                {
                    "id": "unsafe-status-in-execution",
                    "severity": "critical",
                    "branch": branch,
                    "message": f"Execution branch has unsafe status {status}",
                }
            )
        if not item.get("resolved_parent"):
            failed.append(
                {
                    "id": "missing-parent",
                    "severity": "critical",
                    "branch": branch,
                    "message": "Execution branch missing resolved_parent",
                }
            )
        if branch in triage:
            failed.append(
                {
                    "id": "branch-in-triage-and-execution",
                    "severity": "critical",
                    "branch": branch,
                    "message": "Branch appears in both execution and triage diagnostics",
                }
            )
    for branch, node in nodes.items():
        if node.get("status") in BLOCKED_STATUSES and branch not in triage:
            failed.append(
                {
                    "id": "missing-triage-packet",
                    "severity": "high",
                    "branch": branch,
                    "message": "Blocked branch has no triage packet",
                }
            )
    report = {
        "status": "blocked" if failed else "pass",
        "failed_checks": failed,
        "next_actions": [],
    }
    if failed:
        report["next_actions"].append(
            "Run tools/query.py or tools/explain.py for affected branches."
        )
    write_json(OUTPUTS_DIR / "checklist_report.json", report)
    return report


def query_branch(branch: str) -> Dict[str, Any]:
    snapshot = load_snapshot()
    diag = run_diagnostics(write=True)
    nodes = branch_nodes(snapshot)
    if branch not in nodes:
        raise RuntimeError(f"Branch not found in snapshot: {branch}")
    questions = [q for q in diag["question_queue"] if q.get("branch") == branch]
    return {
        "branch": branch,
        "node": nodes[branch],
        "triage_packet": diag["triage_packets"].get(branch),
        "recommendation": diag["recommendations"].get(branch),
        "questions": questions,
        "relationships": [
            e
            for e in diag["relationship_graph"].get("edges", [])
            if e.get("from") == branch or e.get("to") == branch
        ],
    }


def explain_branch(branch: str) -> str:
    q = query_branch(branch)
    node = q["node"]
    lines = [
        f"Branch: {branch}",
        f"Status: {node.get('status')}",
        f"Root: {node.get('root_branch')}",
        f"Declared base: {node.get('declared_base')}",
        f"Resolved parent: {node.get('resolved_parent')}",
        "",
        "Why:",
        f"- {node.get('reason')}",
    ]
    if q.get("relationships"):
        lines.append("\nRelationship evidence:")
        for e in q["relationships"][:10]:
            lines.append(
                f"- {e['id']} {e.get('edge_type')} [{e.get('classification')}]: {'; '.join(e.get('evidence', []))}"
            )
    if q.get("triage_packet"):
        lines.append("\nRecommended action:")
        lines.append(f"- {q['triage_packet'].get('recommended_action')}")
    if q.get("questions"):
        lines.append("\nOpen questions:")
        for question in q["questions"]:
            lines.append(
                f"- {question['id']}: {question['question']} Options={question.get('options')}"
            )
    return "\n".join(lines)
