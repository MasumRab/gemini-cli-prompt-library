# Workspace Isolation Runbook

## Purpose

Jules sessions are stored in a single global SQLite store + JSON archive
(`jules_sessions_store.db`, `session_tracking/`). Multiple agents working on
sessions for different repositories share that store. This runbook establishes a
per-repo workspace convention so that local scratch, logging, and parallel-agent
work do not collide, while the global store remains the canonical source of
truth.

## Workspace layout

`workspaces/` is for **target repositories being operated on** — each subdirectory
is named after the repo (not the owner). The jules repo itself uses its own
`session_tracking/` structure; it does not nest under `workspaces/`.

```text
workspaces/<repo-name>/
├── sessions/        fully ignored raw session projections
├── analysis/        tracked findings and summaries
├── prompts/         sent_responses.md and message proposals
├── state/INDEX.yaml tracked session/worktree coordination metadata
└── state/<id>/      ignored per-session worktree
```

Examples:
- `workspaces/EmailIntelligence/` — target repo workspace
- `workspaces/kaggle-notebooks-analysis/` — target repo workspace
- `session_tracking/` — **jules repo own** session artifacts, prompts, and analysis

## Rules

1. **Repo scoping first.** Every query/list/activity-pull must filter by repo
   (store `repo` column or `sourceContext.source`).
2. **Logging invariant.** Every message sent to a live Jules session is appended
   to `workspaces/<repo-name>/prompts/sent_responses.md` (or the store) _before
   or immediately after_ sending. Format follows
   `skills/jules-sessions/references/sent_responses.md`:
   ```yaml
   session_id: "<id>"
   prompt_type: "nudge|rectification|approve|follow-up"
   prompt_sent: "Verbatim text"
   outcome: "QUEUED|COMPLETED|FAILED"
   ```
3. **Scratch hygiene.** Scratch artifacts never live in repo root or `/tmp`
   alone. Promote anything valuable to `analysis/`.
4. **Parallel-agent etiquette.** Each agent uses its own `state/<session-id>/`
   subdir; `state/INDEX.yaml` records only verified portable metadata. The
   materialized worktree contents and `sessions/` are ignored local state;
   `prompts/sent_responses.md` is append-only when tracked.

## Transport fallback matrix

| Situation                | Primary fails when                | Fallback                      | Command                                                            |
| ------------------------ | --------------------------------- | ----------------------------- | ------------------------------------------------------------------ |
| Poll timeout (REST)      | `list_activities` times out       | SDK bridge `stream`/`history` | `node tools/sdk/dist/bridge.js history <sid>`                      |
| Synchronous reply needed | REST `send_message` + manual poll | SDK bridge `ask`              | `node tools/sdk/dist/bridge.js ask <sid> "question"`               |
| API key quota/auth       | REST returns 401/429/403          | Jules CLI                     | `jules remote list --session`, `jules remote pull --session <sid>` |
| Full local checkout      | Need session patch locally        | CLI pull                      | `jules remote pull --session <sid> --apply` (review before apply)  |

All transports write into the same workspace layout.

## Session-ID recovery (if lost to compaction)

1. Check `session_tracking/YYYY/MM/` for a JSON/YAML pair.
2. Query the store: `SELECT session_id FROM sessions WHERE repo='<repo-name>'`
3. List live: `uv run python -m tools.sessions.jules_list_sessions --repo <repo-name> --json`
4. Last resort: `uv run python -m tools.sessions.sync_all_sessions` then retry.

## Session Worktree Checkout

Retrieve a session's work locally for inspection or manual conflict resolution.

### When to use CLI pull

`jules remote pull --session <id>` returns a patch for **any session that made
commits/pushes** — implementation *or* review. Sessions that only chatted (no
pushes) return "No diff found". The session type does not matter; whether the
session pushed changes does.

```bash
# Inspect the patch (no changes applied); keep raw output in the ignored workspace
mkdir -p workspaces/<repo>/sessions/<session_id>
jules remote pull --session <session_id> \
  > workspaces/<repo>/sessions/<session_id>/pull.diff

# Apply only after verifying a clean localized worktree
 git -C workspaces/<repo>/state/<session_id> status --short
jules remote pull --session <session_id> --apply
```

### Worktree-based manual fix (for conflicts the session cannot resolve)

```bash
# 1. Create isolated worktree from the PR branch under the Jules workspace
mkdir -p workspaces/<repo>/state
git worktree add \
  workspaces/<repo>/state/session-$pr-fix \
  origin/$branch -b fix/pr-$pr-rebase

# 2. Merge current base to surface conflicts
cd workspaces/<repo>/state/session-$pr-fix
git merge origin/$base --no-edit

# 3. Resolve per hunk (3-way: merge-base, ours, theirs) — never checkout --ours/--theirs wholesale

# 4. Verify: git diff origin/$base...HEAD must show ONLY intended changes

# 5. Push back to the PR branch
git push origin HEAD:$branch
```

### Lock file conflicts (package-lock.json, client/package-lock.json, uv.lock)

Stale session snapshots produce massive lock-file churn: the session's cached
lockfile predates dependency updates on main, so its "conflict resolution"
regresses dependency state. Identify and discard:

```bash
# What changed on the actual target base since the session's snapshot?
git diff $(git merge-base HEAD origin/$base)..origin/$base -- <lockfile>

# If the session's lockfile changes are pure snapshot noise (no intentional
# dependency changes in the PR scope), take the verified target-base version:
git restore --source=origin/$base -- <lockfile>
```

Take `origin/$base`'s lockfile when the PR does not intentionally change
dependencies. Take the session's version only when the PR's scope explicitly
includes dependency updates — then regenerate the lockfile from the manifest
(`npm install` / `uv lock`) rather than hand-merging.

### Extracting file content not present in activities/messages

Review comments only sometimes migrate to session `agentMessage` entries. When
the full content (per-finding severity tags, suggestion blocks, AI prompts) is
missing from session chat:

1. **GitHub is authoritative**: `gh pr view <n> --json comments,reviews` and
   `gh api repos/<owner>/<repo>/pulls/<n>/comments`
2. **Session artifacts**: activity entries with `artifacts[].changeSet.gitPatch.unidiffPatch`
   contain the session's actual diff — pull via CLI (above)
3. **Branch git history**: throwaway artifacts sessions committed
   (e.g. `cr_review_prompts.txt`) are recoverable from the commit before deletion:
   `git show <deletion-commit>^:<file>`

## See also

- `docs/guides/operations.md` — the original prompt-logging directive
- `docs/runbooks/session_recovery.md` — state→action map
- `docs/runbooks/session_runbook.md` — daily triage & recovery playbook
- `docs/guides/workflow_session_traceability.md` — cross-system correlation
- `skills/jules-sessions/SKILL.md` — local analysis patterns & templates
- `tools/reviews/` — review-session pipeline CLI (discover/download/audit/aggregate/deliver/authorize-fix/refresh); see `docs/runbooks/session_runbook.md` § Review-Session Pipeline
