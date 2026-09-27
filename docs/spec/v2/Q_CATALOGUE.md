# Q1–Q25 — Required Query Catalogue (reconstructed)

**Provenance warning.** The delivered spec contained only the header
`-- ========== A4. REQUIRED-QUERY VIEWS (Q1–Q25) ==========` followed by **unnumbered** view
bodies. The **views are delivered and authoritative**; the **numbering below is reconstructed**.
Treat `Q<n>` as an unstable identifier until the original list surfaces. If the numbers are
referenced elsewhere (runbooks, task specs, Linear issues) and disagree with this file, the
original wins — see brief §15 Q3.

Ordering principle used here: the sequence an operator actually works in — act → merge → resolve
→ deduplicate → clean up → report.

| # | Question | View / source | Notes |
|---|---|---|---|
| Q1 | What should I act on first, security first? | `v_triage_queue` | entry point; orders by `security_sla='BREACHED'`, then `risk_score` |
| Q2 | What can merge right now, in what order? | `v_merge_ready` ⋈ `mv_merge_order` | gated on `derived_state='READY'` |
| Q3 | Full merge train with waves and cycle flags | `mv_merge_order` | `in_cycle=1` ⇒ trapped in a prerequisite cycle |
| Q4 | What is blocked, and by which PR? | `v_pr_dossier.merge_after` / `.blocks_these` | drives `merge_prerequisite` review |
| Q5 | Which PRs conflict, and are they auto-fixable? | `v_conflicts` | `pr_conflict.resolved_at IS NULL` |
| Q6 | Which open PRs will conflict with each other? | `v_conflict_forecast` | path-overlap prediction, no checkout needed |
| Q7 | Duplicate clusters and the suggested survivor | `v_pr_fanout` | survivor = green CI → newest → most complete |
| Q8 | Which dependabot branches are superseded? | `v_dep_supersession` | `close_these` = all but the newest open bump |
| Q9 | Which PRs are tooling artifacts? | `v_tooling_artifacts` | `^trunk-merge/pr-\d+/[0-9a-f-]{36}$`, sub-minute lifetime |
| Q10 | Abandoned-in-place zombies | `v_zombies` | open, `age_days > 60`; `rebase_cost_index` ranks them |
| Q11 | Stale by inactivity | `v_stale` | open, `idle_days > 30` |
| Q12 | Awaiting author action, split review vs issue | `v_awaiting_changes` | the V3 defect fix: issue-level feedback is counted |
| Q13 | Who owes reviews, and how overdue? | `v_reviewer_workload` | `owed_reviews`, `oldest_request`, `avg_turnaround_h` |
| Q14 | Latest review state per reviewer | `v_reviewer_status` | `DISTINCT ON` latest submission |
| Q15 | Which approvals were invalidated by new commits? | `v_stale_approvals` | `review.commit_sha ≠ pull_request.head_sha` |
| Q16 | CI-blocked PRs and which checks block them | `v_ci_blocked` | `blocks_merge` uses `check_run.is_required` ← `core.required_check` |
| Q17 | Which checks fail most across the repo? | `v_failing_checks` | by `prs_blocked` |
| Q18 | Security findings past SLA | `v_security_sla` | sev1 > 7d, sev2 > 30d ⇒ `BREACHED` |
| Q19 | How much churn is CI-fixup rework? | `v_rework_ratio` | `fixup_pct`; needs `pr_commit` |
| Q20 | Wasted churn on abandoned PRs | `v_wasted_churn` | pairs with `core.v_portfolio_efficiency` |
| Q21 | Which PRs link to neither Linear nor a Jules session? | `v_unlinked_prs` | feeds P2 and P3 candidate sets |
| Q22 | Which Linear issues have more than one open PR? | `v_linear_duplicate_coverage` | |
| Q23 | Which Jules sessions need a human, or are stalled? | `v_jules_attention` | `blocked_on_human`, `stalled`, `orphan_session` |
| Q24 | Everything about one PR | `v_pr_dossier` | includes 2-hop Linear links and merge prerequisites |
| Q25 | Cross-repo portfolio and agent efficiency | `core.v_all_prs` → `core.v_portfolio_efficiency`, `core.v_agent_efficiency`, `core.v_template_drift` | |

## Two queries the delivered views do not cover

Neither is expressible against the delivered objects; both are worth adding explicitly:

**QX1 — ingest coverage vs the provider's own count.** The assertion that would have caught the
store truncating 348 of 827 PRs: compare stored rows per (repo, state) against the API's declared
total. Not a view over PR data — a reconciliation check.

```sql
-- expected: stored == declared, for every repo and state
SELECT r.name AS repo, w.resource, w.safe_water, w.high_water,
       (SELECT count(*) FROM pull_request p
         WHERE p.repo_id = r.repo_id AND p.state = 'open') AS stored_open
FROM core.repo r JOIN ingest.watermark w ON w.repo_id = r.repo_id
WHERE w.resource = 'pulls';
```

**QX2 — P1 classification coverage and threshold routing.** How much of the inbound comment
volume has actually been judged, and how much is waiting on a human because confidence fell
below the auto-apply threshold:

```sql
SELECT count(*) FILTER (WHERE j.judgment_id IS NULL)                      AS unjudged,
       count(*) FILTER (WHERE j.confidence >= 0.70)                       AS auto_applied,
       count(*) FILTER (WHERE j.confidence <  0.70)                       AS routed_to_human
FROM pr_comment c
LEFT JOIN core.llm_judgment j
       ON j.subject_key = 'comment:' || c.comment_id AND j.task_code = 'L-1';
```
