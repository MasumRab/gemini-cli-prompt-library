import json

with open("docs/forensics/session_priority_batch_plan_2026-08-14.json") as f:
    plan = json.load(f)

md = []
md.append("# Session Priority Batch Plan — 2026-08-14")
md.append("")
md.append(
    "**Analysis thread:** [T-019fd887-be34-7014-9cb1-e24012ad3aad](https://ampcode.com/threads/T-019fd887-be34-7014-9cb1-e24012ad3aad)"
)
md.append(f"**Generated:** {plan['generated_at']}")
md.append("")
md.append("## Purpose")
md.append("")
md.append(
    "Revised month-long follow-up plan where priority is not based mainly on age."
)
md.append(
    "Highest priority reflects whether a session is waiting for user action or had"
)
md.append(
    "an unresolved conversational handoff. Smart follow-up messages are reconstructed"
)
md.append(
    "from each session's full evolved intent, messages, and plans — not generic retries."
)
md.append("")
md.append("## Summary Statistics")
md.append("")
s = plan["summary"]
md.append(f"| Metric | Value |")
md.append(f"|--------|-------|")
md.append(f"| Total sessions in API | {s['total_sessions_in_api']} |")
md.append(
    f"| Failed sessions not yet messaged | {s['total_failed_not_yet_messaged']} |"
)
md.append(f"| Nonterminal sessions (all states) | {s['nonterminal_sessions']} |")
md.append(f"| Nonterminal actionable (need reply) | {s['nonterminal_actionable']} |")
md.append(f"| Nonterminal monitor-only | {s['nonterminal_monitor_only']} |")
md.append(
    f"| Confirmed responders from prior intervention | {s['confirmed_responders_from_prior_intervention']} |"
)
md.append(f"| Batch size | {s['batch_size']} |")
md.append(f"| Total batches | {s['total_batches']} |")
md.append(
    f"| Estimated days to complete (1 batch/day) | {s['estimated_days_to_complete']} |"
)
md.append("")
md.append(f"**Priority order:** {s['priority_order']}")
md.append("")
md.append("## Repository Distribution (Failed Sessions)")
md.append("")
md.append("| Repository | Count |")
md.append("|-----------|-------|")
for repo, count in sorted(
    plan["statistics"]["failed_by_repo"].items(), key=lambda x: -x[1]
):
    md.append(f"| {repo} | {count} |")
md.append("")
ps = plan["statistics"]["pr_state_sample_30"]
md.append(
    f"**PR state sample (first 30 by date):** open={ps['open']}, closed_not_merged={ps['closed_not_merged']}, merged={ps['merged']}, no_pr={ps['no_pr']}"
)
md.append("")
md.append(
    "> **Note:** PR state sample is from first 30 sorted by date. Full PR state check should be done per-batch before messaging."
)
md.append("")
md.append("## Tier 0: Nonterminal Session Classification (Immediate Action)")
md.append("")
md.append("### P0 — Explicit User Action Pending (AWAITING_USER_FEEDBACK)")
md.append("")
md.append(
    "These 7 sessions are actively waiting for user input. They are the highest priority"
)
md.append("and should be addressed first, before any failed-session batch.")
md.append("")
md.append(
    "| Session ID | Repo | Title | PR | PR State | Last Activity | Recommended Action |"
)
md.append(
    "|-----------|------|-------|-----|----------|---------------|-------------------|"
)

p0 = [
    v for v in plan["nonterminal_classification"].values() if v["priority_tier"] == "P0"
]
for s in sorted(p0, key=lambda x: x["updated"], reverse=True):
    pr = f"#{s['pr']}" if s["pr"] else "none"
    md.append(
        f"| {s['sid']} | {s['repo'].split('/')[-1]} | {s['title'][:40]} | {pr} | {s['pr_state']} | {s['updated'][:10]} | {s['recommended_action']} |"
    )

md.append("")
md.append("#### Detailed P0 Analysis")
md.append("")
for s in sorted(p0, key=lambda x: x["updated"], reverse=True):
    md.append(f"##### {s['sid']} — {s['title']}")
    md.append(f"- **Repo:** {s['repo']}")
    md.append(f"- **PR:** {'#' + s['pr'] if s['pr'] else 'none'} ({s['pr_state']})")
    md.append(f"- **Created:** {s['created']} | **Updated:** {s['updated']}")
    md.append(
        f"- **Plan approved:** {s['plan_approved']} | **Has artifacts:** {s['has_artifacts']}"
    )
    md.append(
        f"- **Last agent message:** {s['last_agent_msg'][:200] if s['last_agent_msg'] else 'N/A'}"
    )
    md.append(
        f"- **Last user message:** {s['last_user_msg'][:200] if s['last_user_msg'] else 'N/A'}"
    )
    md.append(f"- **Reason for priority:** {s['reason']}")
    md.append(f"- **Recommended action:** `{s['recommended_action']}`")
    md.append(f"- **Action detail:** {s['action_detail']}")
    md.append("")

md.append("### P1 — In Progress / Possibly Stalled")
md.append("")
md.append("These 2 sessions are IN_PROGRESS. They should be monitored for 24 hours.")
md.append("If no state change, send a targeted follow-up.")
md.append("")
md.append(
    "| Session ID | Repo | Title | PR | PR State | Last Updated | Recommended Action |"
)
md.append(
    "|-----------|------|-------|-----|----------|-------------|-------------------|"
)

p1 = [
    v for v in plan["nonterminal_classification"].values() if v["priority_tier"] == "P1"
]
for s in p1:
    pr = f"#{s['pr']}" if s["pr"] else "none"
    md.append(
        f"| {s['sid']} | {s['repo'].split('/')[-1]} | {s['title'][:40]} | {pr} | {s['pr_state']} | {s['updated'][:10]} | {s['recommended_action']} |"
    )

md.append("")
md.append("#### Detailed P1 Analysis")
md.append("")
for s in p1:
    md.append(f"##### {s['sid']} — {s['title']}")
    md.append(f"- **Repo:** {s['repo']}")
    md.append(f"- **PR:** {'#' + s['pr'] if s['pr'] else 'none'} ({s['pr_state']})")
    md.append(f"- **Created:** {s['created']} | **Updated:** {s['updated']}")
    md.append(f"- **Reason:** {s['reason']}")
    md.append(f"- **Recommended action:** `{s['recommended_action']}`")
    md.append(f"- **Action detail:** {s['action_detail']}")
    md.append("")

md.append("### P2 — Queued / Monitor Only")
md.append("")
md.append(
    "These 2 sessions are QUEUED. They should not be messaged. Monitor for state transitions."
)
md.append("")
md.append("| Session ID | Repo | Title | Last Updated | Recommended Action |")
md.append("|-----------|------|-------|-------------|-------------------|")

p2 = [
    v for v in plan["nonterminal_classification"].values() if v["priority_tier"] == "P2"
]
for s in p2:
    md.append(
        f"| {s['sid']} | {s['repo'].split('/')[-1]} | {s['title'][:40]} | {s['updated'][:10]} | {s['recommended_action']} |"
    )

md.append("")
md.append("## Tier 1: Failed Session Batch Plan (342 sessions in 23 batches)")
md.append("")
md.append("### Batch Ordering Priority")
md.append("")
md.append("Within the failed-session pool, sessions are sorted by:")
md.append("")
md.append("1. **Has PR** (PR-bearing sessions are more likely actionable)")
md.append(
    "2. **Newest first** (younger sessions are more likely to restart successfully)"
)
md.append("3. **Repo** (grouping by repo helps with repo-specific message templates)")
md.append("")
md.append("### Batch Schedule")
md.append("")
md.append("| Batch | Date (est.) | Sessions | Cumulative | Notes |")
md.append("|-------|------------|----------|------------|-------|")

for batch in plan["failed_session_batches"]:
    bn = batch["batch_number"]
    count = batch["session_count"]
    cumulative = bn * 15
    date = f"2026-08-{14 + bn:02d}" if bn <= 17 else f"2026-09-{bn - 17:02d}"
    with_pr = sum(1 for s in batch["sessions"] if s["pr_num"])
    note = f"{with_pr} with PR" if with_pr else "no PRs"
    md.append(f"| {bn} | {date} | {count} | {cumulative} | {note} |")

md.append("")
md.append("### Batch 1 Detail (First 15 — Highest Priority Failed)")
md.append("")
md.append("| # | Session ID | Repo | Created | PR | Title |")
md.append("|---|-----------|------|---------|-----|-------|")

for i, s in enumerate(plan["failed_session_batches"][0]["sessions"], 1):
    pr = f"#{s['pr_num']}" if s["pr_num"] else "none"
    repo = s["repo"].split("/")[-1]
    md.append(
        f"| {i} | {s['session_id']} | {repo} | {s['created']} | {pr} | {s['title'][:50]} |"
    )

md.append("")
md.append("### Per-Batch Pre-Message Protocol")
md.append("")
md.append("Before messaging each batch:")
md.append("")
md.append("1. **Check current session state** via `GET /v1alpha/sessions/{sid}`")
md.append(
    "   - Skip sessions that have transitioned to COMPLETED or AWAITING_USER_FEEDBACK"
)
md.append("   - Sessions that are now IN_PROGRESS should be monitored, not re-messaged")
md.append("2. **Check PR state** via GitHub API for sessions with PRs")
md.append("   - If PR is merged: session task is complete, skip message")
md.append(
    "   - If PR is closed (not merged): inform agent PR was closed, ask if fix still needed"
)
md.append("   - If PR is open: include PR number in follow-up message")
md.append("3. **Fetch last 10 activities** for context")
md.append("   - Identify what the agent was doing when it failed")
md.append("   - Reconstruct the evolved task intent from conversation")
md.append(
    "4. **Craft message** using the session-specific template (see follow-up drafts)"
)
md.append("5. **Send message** via `POST /v1alpha/sessions/{sid}:sendMessage`")
md.append("6. **Record result** in the intervention ledger")
md.append("")
md.append("## Policy Reminders")
md.append("")
for p in plan["policy_reminders"]:
    md.append(f"- {p}")
md.append("")
md.append("## Evidence Audit Corrections")
md.append("")
md.append(
    "The prior e2e report (`INTERVENTION_E2E_OUTCOME_ANALYSIS_2026-08-07.md`) contains. Note: This data is now available in the standardized format in `migrated_forensics_data.json`."
)
md.append("several unsupported claims that should be corrected:")
md.append("")
md.append(
    "1. **'Free' API use** — `sendMessage` does not consume a new-session slot, but its"
)
md.append(
    "   API/rate-limit cost is not proven to be zero. Do not describe it as 'free.'"
)
md.append(
    "2. **'~12 activity-only' / '~325 no response'** — these were extrapolated from a"
)
md.append(
    "   limited sample, not established across all 345 messaged sessions. The confirmed"
)
md.append("   count of genuine state-changing responses is **8 out of 345**.")
md.append(
    "3. **'Stale sandbox' as proven cause** — sandbox lifecycle is observational, not a"
)
md.append(
    "   proven rule. Age alone is not deterministic (some sessions restart at 51 days,"
)
md.append("   others at 63 days, some don't restart at 9 days).")
md.append(
    "4. **Exact age-band denominators** — the original 345 messaged session IDs should be"
)
md.append("   cross-referenced against current state before citing exact counts.")
md.append("")
md.append("## Files")
md.append("")
md.append(
    "- **Batch plan data:** `docs/forensics/session_priority_batch_plan_2026-08-14.json`"
)
md.append(
    "- **Follow-up message drafts:** `docs/forensics/SESSION_FOLLOWUP_MESSAGE_DRAFTS_2026-08-14.md`"
)
md.append(
    "- **Prior intervention ledger:** `docs/forensics/intervention_e2e_ledger_2026-08-07.json`"
)
md.append(
    "- **Prior e2e report:** `docs/forensics/INTERVENTION_E2E_OUTCOME_ANALYSIS_2026-08-07.md` (Note: This data is now available in the standardized format in `migrated_forensics_data.json`)"
)
md.append(
    "- **Session tracker:** `docs/forensics/SESSION_FOLLOWUP_TRACKER_2026-08-06.json` (Note: This data is now available in the standardized format in `migrated_forensics_data.json`)"
)
md.append("")

with open("docs/forensics/SESSION_PRIORITY_BATCH_PLAN_2026-08-14.md", "w") as f:
    f.write("\n".join(md))

print(f"Markdown report saved: {len(md)} lines")
