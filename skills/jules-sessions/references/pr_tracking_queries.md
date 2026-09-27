# PR Tracking DB — skill query recipes

The per-repo **PR tracking databases** (`workspaces/<repo>/generated/pr_tracking.db`) hold each
repo's complete PR history in a governance-aware shape. For session work they close the gap that
previously required guesswork: **what PR state sits behind this session?**

Full operational detail: `docs/runbooks/pr_tracking_db.md`. Maintained by
`tools/store/repo_pr_db.py`. See also [[system/jules/overview]] for the session store itself.

## Bootstrap / refresh (per repo)

```bash
python3 tools/store/repo_pr_db.py sync          --repo <repo>   # or import-jsonl from the corpus
python3 tools/store/repo_pr_db.py link-sessions --repo <repo>
python3 tools/store/repo_pr_db.py refresh       --repo <repo>
python3 tools/store/repo_pr_db.py verify        --repo <repo>   # ALWAYS after sync
```

`verify` is not optional: it asserts stored rows == GitHub's declared totals per state. Without it
a truncated sync looks like a small repository.

## Session triage

**Sessions whose PR already merged** — the session's work is done regardless of its own state:

```sql
SELECT s.session_id, s.role, p.pr_number, p.merged_at
FROM pr_jules_session s JOIN pull_request p USING (pr_number)
WHERE p.merged = 1 AND s.role = 'author';
-- NOTE: merged/state live on pull_request; age_days and idle_days exist only on
-- v_pr. Always join v_pr (or use v_jules_linked) when selecting either.
```

**Sessions still open on idle PRs** — candidates for a nudge, ranked by PR inactivity:

```sql
SELECT session_id, role, pr_number, substr(title,1,50) AS title, idle_days, age_days
FROM v_jules_linked
WHERE state = 'open' AND idle_days > 30
ORDER BY idle_days DESC;
```

**A session with no PR row** — the PR was never ingested, or the session never produced one.
Treat as a data gap, not as evidence about the session:

```sql
SELECT session_id, pr_number FROM pr_jules_session s
WHERE NOT EXISTS (SELECT 1 FROM pull_request p WHERE p.pr_number = s.pr_number);
```

## Session steering

**What does this PR actually need?** (`v_actionable` has no closure action by construction):

```sql
SELECT * FROM v_actionable WHERE pr_number = ?;
```

**Is the PR blocked on review, CI, or conflict?** — the three things a steering message should name:

```sql
SELECT pr_number, has_conflicts, ci_failing_checks, approvals,
       changes_requested_count, actionable_comment_count, review_decision
FROM pull_request WHERE pr_number = ?;
```

## Historical work (the part the old model got wrong)

A closed-unmerged PR **is not a failure**. Before proposing anything about one, check whether its
work already landed elsewhere:

```sql
SELECT pr_number, title, closed_at, historical_outcome, queue_status,
       (SELECT count(*) FROM pr_lineage l WHERE l.ancestor_pr = h.pr_number) AS lineage_edges
FROM v_historical h WHERE h.pr_number = ?;
```

`historical_outcome = 'pending_analysis'` means: **not yet classified**. It does not mean abandoned,
unwanted, or closed-for-good. Never tell a user a PR is abandoned without lineage analysis having
failed *and* an auditable decision being recorded (`historical_validation`).

**Recovery candidates, ranked** (higher `priority_score` = more recoverable work):

```sql
SELECT q.pr_number, q.priority_score, q.status, p.title, p.churn
FROM restoration_queue q JOIN pull_request p USING (pr_number)
WHERE q.status = 'pending_analysis' ORDER BY q.priority_score DESC LIMIT 20;
```

## Guardrails for any session message about a PR

1. **Never propose closure because a PR is old, idle, or has stale reviews.** Age is informational
   (`is_historical` is a flag). The suggestion verbs that mean closure do not exist in the schema.
2. **A duplicate cluster is a lineage question, not a closure question** — `v_lineage_candidates`
   yields candidates for adjudication, and `pr_lineage` records the answer with confidence.
3. **Verify before asserting PR state.** `sync_meta.last_sync:<repo>` carries freshness; a stale DB
   makes confident claims wrong. Re-`sync` if in doubt.
4. **Never hand-edit `restoration_status` / `historical_outcome`** — run `refresh`. Only
   `intentionally_abandoned` is human-set, and it is deliberately sticky.
