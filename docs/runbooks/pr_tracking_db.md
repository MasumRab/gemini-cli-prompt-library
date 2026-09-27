# Runbook — Per-Repo PR Tracking DB

**What it is.** One SQLite database per target repository, holding that repo's complete PR history
in a **governance-aware** shape: historical work is preserved and classified, never closed because
it is old. Created and maintained by `tools/store/repo_pr_db.py`.

**Why it exists.** Before this, answering "what is the state of PR X and which Jules session drove
it?" meant ad-hoc `gh` calls per question, and the answer for a closed-unmerged PR was framed as a
failure. The DB makes those questions one query, and makes closure-by-staleness *unrepresentable*.

**Where it lives.**

```
workspaces/<repo>/generated/pr_tracking.db      # gitignored (rule 62) — never commit it
```

A DB at the workspace **root** would be tracked, because `.gitignore` only covers
`/workspaces/*/generated/**`. Placing it under `generated/` is deliberate. Verify with
`git check-ignore -v <path>` before moving it.

---

## 1. Daily use

```bash
cd /home/masum/github/remote/jules

# refresh every repo from GitHub (resumable; re-run after an interruption)
python3 tools/store/repo_pr_db.py sync        --repo <repo>     # rows
python3 tools/store/repo_pr_db.py fetch-files --repo <repo>     # per-PR file detail (slow)
python3 tools/store/repo_pr_db.py link-sessions --repo <repo>   # PR <-> Jules session
python3 tools/store/repo_pr_db.py refresh     --repo <repo>     # recompute projections + enqueue
python3 tools/store/repo_pr_db.py verify      --repo <repo>     # parity vs the API
python3 tools/store/repo_pr_db.py report      --repo <repo>     # one-screen summary
```

**Always `verify` after `sync`.** It compares stored rows against GitHub's declared totals per
state. This is the assertion that would have caught the original defect where the store held 348 of
EI's 827 PRs because the sync truncated at fixed windows.

**Order matters on first build:** `init` → `import-jsonl` (fast, from the harvested corpus) or
`sync` → `link-sessions` → `refresh`. `refresh` after ingest, always: it recomputes the governance
projections (Rule 11) and enqueues new historical work (Rule 4). It is idempotent.

**Bootstrap all repos at once:** `init-all`, then loop `link-sessions` + `refresh`.

## 2. Query recipes

```sql
-- What is live, what does it need? (no closure action exists in this view)
SELECT * FROM v_actionable ORDER BY ci_failing_checks DESC, age_days DESC;

-- Historical work, by outcome (Rule 4 / Rule 6)
SELECT historical_outcome, count(*), sum(churn) FROM v_historical GROUP BY 1 ORDER BY 2 DESC;

-- Which PRs have a Jules session behind them?
SELECT * FROM v_jules_linked WHERE state = 'open' ORDER BY age_days DESC;

-- PRs whose work may already exist elsewhere (lineage candidates, NOT duplicates)
SELECT * FROM v_lineage_candidates ORDER BY candidate_count DESC;

-- Recovery accounting (replaces closure efficiency)
SELECT month, merged, restored_elsewhere, merged_via_successor,
       pending_analysis, recovered_churn, churn_awaiting_evaluation
FROM v_restoration_efficiency ORDER BY month DESC LIMIT 12;

-- Anything over a year old is historical work awaiting evaluation, not stale
SELECT pr_number, title, age_days, historical_outcome, queue_status
FROM v_historical WHERE is_historical = 1 ORDER BY age_days DESC;

-- Files: conflict surface and lockfile exposure
SELECT path, count(DISTINCT pr_number) AS prs FROM pr_file
WHERE is_lockfile = 0 GROUP BY path ORDER BY prs DESC LIMIT 20;
```

**Freshness — informational, deliberately not a gate.**

```sql
SELECT key, value FROM sync_meta WHERE key LIKE 'last_sync:%' OR key LIKE 'files_synced:%';
```

There is **no automatic staleness gate, and there will not be one.** This is a design decision, not
an unfinished item:

- The work happens in bursts against repositories that legitimately sit unchanged for a year. A
  timer that invalidates, re-fetches, or downgrades data on a clock would fire almost exclusively
  when nothing has actually changed, spending API budget and attention on the wrong signal.
- It would also contradict the model one level up. Rule 1 says age is informational for a PR; the
  same holds for the store. **Age is a fact to report, never a behaviour to trigger.**
- The timestamps exist so a caller can *state* freshness when it matters ("as of <ts>"), not so the
  system can act on it unprompted.

Sync when you want current data. If a decision depends on freshness, read the timestamp and say so
in the answer.

## 3. Governance constraints — do not work around these

The rules are seeded **into the database** (`SELECT * FROM governance_rule`) and enforced in
schema:

| Rule | How it is enforced here |
|---|---|
| Age is informational only (R1) | `is_historical` is a flag; no action is derived from it |
| No automatic abandonment (R2/R12) | `intentionally_abandoned` requires failed checks in `historical_validation` plus an auditable decision |
| No closure by stale/CI/duplicate (R3/R5) | **no CHECK domain contains a `close_*` value** — closure is unrepresentable, not merely unused |
| Closed-unmerged = historical candidate (R4) | `refresh` enqueues every one into `restoration_queue` as `pending_analysis` |
| Historical work retained forever (R8) | rows are never deleted; `pr_lineage` records ancestry instead |
| Derived truth dominates cached truth (R11) | `restoration_status` / `historical_outcome` are **projections** — recompute, never hand-edit |
| Task codes immutable (R10) | `judgment.task_code` meaning may never change; new semantics get new codes |

**Never** hand-edit `restoration_status` or `historical_outcome` — run `refresh`. The single
exception is setting `intentionally_abandoned`, which is a human decision and is sticky across
refreshes by design.

## 4. Integration with the rest of the repo

| Consumer | How it uses the DB |
|---|---|
| `skills/jules-sessions` | joins session state to PR state — see `references/pr_tracking_queries.md` |
| `skills/wrapup-session` | before wrapping up, read `v_actionable` + `v_jules_linked` for the session's PR to confirm the PR state matches the claimed outcome |
| `skills/jules-session-manager` | bulk operations: group sessions by the PR state behind them rather than by session state alone |
| `docs/runbooks/session_runbook.md` | session triage gains a PR dimension: `AWAITING_USER_FEEDBACK` sessions on PRs that already merged are stale sessions |
| `docs/runbooks/pr_verification_runbook.md` | `verify` is the DB-side counterpart of PR verification |
| `docs/runbooks/session_recovery.md` | recovery candidates ranked by `restoration_queue.priority_score` |
| `tools/store/staleness.py` | the session store's existing 12h gate — **not** extended to these DBs by design (see §2) |

**The one-line join that matters** — session state and PR state were previously two separate
worlds:

```sql
-- age_days / idle_days exist only on v_pr (computed at read time), NOT on the
-- base table. Join v_pr, or use the pre-joined view.
SELECT * FROM v_jules_linked WHERE state = 'open' AND idle_days > 30
ORDER BY idle_days DESC;
```

## 4b. Reopening historical PRs — guardrails

Reopening is an **action on live repos**, not a reporting operation. Use the tool's subcommand, not
an ad-hoc `gh` loop, so the filters are auditable:

```bash
python3 tools/store/repo_pr_db.py reopen --repo <repo> --scope candidates --require-session
# dry run by default. Add --confirm to execute.
```

Standing exclusions, enforced in code:

| Exclusion | Why |
|---|---|
| **trunk / mergify branches** | merge-queue machinery, not authored work. Never reopen. (`--include-trunk` is required to override, and should not be used.) |
| `changed_files > 300` | whole-repo-diff artifacts (contaminated branches) |
| `churn > 2000` | too large to review as a restoration unit |
| **empty diff** | a closed PR with no diff is *evidence the work already landed* — Rule 6 classification material (`restored_elsewhere` / `merged_via_successor`), not a restoration target |
| branch deleted | GitHub cannot reopen; needs branch reconstruction instead |

**Automation exposure is per-repo, so check before scaling:** `gemini-fullstack-langgraph-quickstart`
has all eight Jules workflows ACTIVE and `jules-pr-review` fires on `reopened`, so each reopen there
starts a workflow. EmailIntelligence and kaggle-notebooks have the same set `.DISABLED`.

## 5. Failure modes and what they mean

| Symptom | Cause | Action |
|---|---|---|
| `verify` reports MISMATCH | sync truncated or was interrupted | re-run `sync` — it resumes from `sync_meta` cursors |
| `fetch-files` very slow | per-PR GraphQL call (~4s each) | run detached: `setsid nohup … &`, then read the log |
| `Variable $number of type Int! was provided invalid value` | used `gh -f` (string) for an Int variable | `gql()` already selects `-F` for typed values — don't hardcode `-f` |
| A PR with thousands of files | whole-repo-diff contamination (135 such PRs portfolio-wide) | skipped by the artifact guard (`changed_files > 300`); its size is still on `pull_request` |
| `v_historical` missing a column | view change not applied to an existing DB | re-run `init` — views are dropped and recreated; tables use `IF NOT EXISTS` so data survives |
| Linked sessions look wrong | session store's `repo` column is NULL for some rows | the linker parses owner/repo from `pr_url`; PR-number existence alone is **not** safe (numbers collide across repos) |

## 6. Status at time of writing

| Repo | PRs | open | historical | queued | session links |
|---|---|---|---|---|---|
| EmailIntelligence | 827 | 407 | 123 | 123 | 479 |
| gemini-fullstack | 385 | 59 | 66 | 66 | 360 |
| kaggle-notebooks | 120 | 28 | 14 | 14 | 64 |
| gemini-cli-prompt-library | 63 | 25 | 0 | 0 | 46 |
| **Total** | **1395** | 519 | **203** | **203** | **949** |

Verified: import parity exact (1395); API parity confirmed for kaggle and prompt-library. File
detail is populated incrementally and skipped for artifact PRs.
