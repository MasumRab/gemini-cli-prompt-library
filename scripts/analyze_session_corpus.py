#!/usr/bin/env python3
"""T2/T3: Session-corpus difficulty matrix + message-pattern audit.

Parses session_tracking/*.json (both schema generations) plus SUMMARY.json and
reports:
  1. Outcome matrix by agent_type (FAILED / awaiting-decision / stale / completed)
  2. PR-creation decision dead-end count (cross-check vs response_templates "NEVER create PRs")
  3. Corpus schema-generation drift
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKING = ROOT / "session_tracking"

PR_CREATE_ASK_RE = [
    "awaiting approval to create pr",
    "awaiting approval for pr",
    "awaiting pr creation approval",
    "proceed with creating a pr",
    "instruct the agent to create pr",
    "approval for pr creation",
    "guidance on pr creation",
    "decision on whether to proceed with pr",
]
NEVER_CREATE_RE = [
    "never create new pr",
    "we never create",
    "do not create a new pr",
    "never create pr",
    "don't create new pr",
]


def classify(text: str, patterns) -> bool:
    t = (text or "").lower()
    return any(p in t for p in patterns)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return {}


def normalize_session(data: dict, fname: str, overlay: dict | None = None) -> dict:
    """Handle both schema generations; overlay SUMMARY.json metadata when present."""
    sid = str(data.get("id") or data.get("session_id") or fname)
    o = (overlay or {}).get(sid, {})
    title = data.get("title") or o.get("title") or data.get("prompt", "").splitlines()[0][:60] or "?"
    state = data.get("state") or o.get("state") or "UNKNOWN"
    tags = data.get("tags") or []
    agent_type = o.get("agent_type") or next(
        (t for t in tags if any(k in t for k in
         ("ci", "sentinel", "bolt", "schedul", "data-pipeline", "general"))), "general")
    key_issue = data.get("key_issue") or o.get("key_issue") or data.get("summary", "")
    suggested = (data.get("context_analysis") or {}).get("suggested_response", "")
    rec_action = (data.get("recommended_action")
                  or o.get("recommended_action")
                  or (data.get("context_analysis") or {}).get("recommended_action", ""))
    has_analysis = bool(data.get("context_analysis"))
    activity_count = data.get("activity_count", 0)
    user_msgs = data.get("user_messages") or []
    created = data.get("createTime") or data.get("last_update") or ""
    try:
        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
    except ValueError:
        dt = None
    age_days = None
    if dt:
        age_days = max(0, (datetime.now(timezone.utc) - dt).days)
    return {
        "id": sid, "title": title, "state": state, "agent_type": agent_type,
        "key_issue": key_issue, "suggested": suggested, "rec_action": rec_action,
        "has_analysis": has_analysis, "activity_count": activity_count,
        "user_msg_count": len(user_msgs), "age_days": age_days,
    }


def main() -> int:
    meta = load_json(TRACKING / "SUMMARY.json")
    overlay = {}
    for s in meta.get("sessions", []) + meta.get("older_sessions_still_awaiting", []):
        if s.get("session_id"):
            overlay[s["session_id"]] = s

    rows = []
    schema_raw = schema_analyzed = 0
    for p in sorted(TRACKING.glob("*.json")):
        if p.name == "SUMMARY.json":
            continue
        data = load_json(p)
        if not data:
            continue
        rows.append(normalize_session(data, p.name, overlay))
        if data.get("context_analysis"):
            schema_analyzed += 1
        else:
            schema_raw += 1

    for s in meta.get("sessions", []) + meta.get("older_sessions_still_awaiting", []):
        if not any(r["id"] == s.get("session_id") for r in rows):
            rows.append(normalize_session(s, s.get("tracking_file", s.get("session_id", "?")), overlay))
            schema_raw += 1

    print("=" * 72)
    print("T2 - DIFFICULTY MATRIX: agent_type x outcome")
    print("=" * 72)
    outcomes = {}
    for r in rows:
        if r["state"] == "FAILED":
            outcome = "FAILED"
        elif r["state"] == "COMPLETED":
            outcome = "completed"
        elif r["state"] == "AWAITING_USER_FEEDBACK" and r["rec_action"] in ("investigate_or_close",):
            outcome = "stale-awaiting"
        elif r["state"] == "AWAITING_USER_FEEDBACK":
            outcome = "awaiting-decision"
        else:
            outcome = r["state"]
        outcomes.setdefault(r["agent_type"], {}).setdefault(outcome, 0)
        outcomes[r["agent_type"]][outcome] += 1

    print(f"{'agent_type':<18} {'FAILED':>6} {'awaiting':>10} {'stale':>6} {'done':>5} {'total':>6}")
    totals = {}
    for at, counts in sorted(outcomes.items()):
        f = counts.get("FAILED", 0); a = counts.get("awaiting-decision", 0)
        st = counts.get("stale-awaiting", 0); c = counts.get("completed", 0)
        t = sum(counts.values())
        for k, v in counts.items():
            totals[k] = totals.get(k, 0) + v
        print(f"{at:<18} {f:>6} {a:>10} {st:>6} {c:>5} {t:>6}")
    tf = totals.get("FAILED", 0)
    print(f"{'TOTAL':<18} {tf:>6} {totals.get('awaiting-decision',0):>10} "
          f"{totals.get('stale-awaiting',0):>6} {totals.get('completed',0):>5} {len(rows):>6}")

    print()
    print("=" * 72)
    print("T3 - PR-CREATION DECISION DEAD-END (vs response_templates NEVER-create policy)")
    print("=" * 72)
    ask_ct = never_ct = 0
    conflicting = []
    for r in rows:
        text = f"{r['key_issue']} {r['suggested']}".lower()
        asks = classify(text, PR_CREATE_ASK_RE)
        forbids = classify(text, NEVER_CREATE_RE)
        ask_ct += asks
        never_ct += forbids
        if asks and forbids:
            conflicting.append(r["id"][:22])
    print(f"sessions asking for PR-creation decision: {ask_ct}/{len(rows)}")
    print(f"sessions quoting NEVER-create policy:      {never_ct}/{len(rows)}")
    print(f"sessions with BOTH signals:                {len(conflicting)} -> {conflicting}")

    print()
    print("=" * 72)
    print("T2b - CORPUS SCHEMA DRIFT + STALL METRICS")
    print("=" * 72)
    print(f"analyzed schema (has context_analysis): {schema_analyzed}")
    print(f"raw schema (session payload only):      {schema_raw}")
    stalled = [r for r in rows if r["state"] == "AWAITING_USER_FEEDBACK" and r["user_msg_count"] == 0]
    print(f"awaiting sessions with ZERO user replies: {len(stalled)}")
    for r in sorted(stalled, key=lambda x: -(x["age_days"] or 0)):
        print(f"  {r['id'][:22]}  age={r['age_days']}d  acts={r['activity_count']}  {r['title'][:50]}")

    print()
    print("T2c - session-level detail (id, state, age, user_msgs, acts, agent_type)")
    for r in sorted(rows, key=lambda x: -(x["age_days"] or 0)):
        print(f"  {r['id'][:22]}  {r['state']:<24} age={str(r['age_days']):>4}  "
              f"u={r['user_msg_count']} acts={r['activity_count']:<4} {r['agent_type']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())