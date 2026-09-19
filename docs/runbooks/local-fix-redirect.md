# Jules Session Local Fix & Redirect Runbook

Fix a Jules session's work by making **local direct changes** to its files,
push the corrected state back to the session's branch, and redirect the
session to continue from that state.

**Authorization gate:** Before materializing or modifying anything, record the
explicit implementation authorization, target repository, existing PR/branch,
base ref, and exact file scope. Review-only work may inspect and report, but
must not edit, commit, push, or authorize implementation.

## When to use

- The session produced wrong, stale, or regressed work and orchestrator-side
  fixes are faster or safer than explaining them to the session.
- The session is FAILED/stuck and its branch needs correcting before a
  wake-up message is useful.
- Conflict resolution required because the session's snapshot predates
  current main (see the Drift Protocol below).
- You want to review/inspect a session's exact working state before deciding
  whether to intervene.

## 1. Locate the session

```bash
cd ~/github/remote/jules
uv run python3 -m tools.sessions.jules_list_sessions --state FAILED AWAITING_USER_FEEDBACK --json
# or match by repo: --state COMPLETED (filter by pr_url / repo)
```

## 2. Materialize the session's working state

**Resolve the target repo first.** The session's repository comes from the API
(`sourceContext.source`, e.g. `sources/github/MasumRab/EmailIntelligence`) or the
PR URL — never from the directory you happen to be in. Map it to the workspace:
`MasumRab/EmailIntelligence` → `workspaces/EmailIntelligence/`.

**CWD contract (verified CLI behavior):** `jules teleport` and
`jules remote pull --apply` bind to the Git repository in the current working
directory. If cwd is inside a repo matching the session's repository, the
patch is applied **directly to that working tree** (no new folder). If cwd is
not inside a matching repo, `teleport` creates a fresh clone
`./jules-<repo>-<sessionid>/` in cwd and applies the patch as uncommitted
changes. Therefore:

| Need | Procedure |
|------|-----------|
| Inspect patch only (repo-independent) | `mkdir -p workspaces/<repo>/sessions/<id> && jules remote pull --session <id> > workspaces/<repo>/sessions/<id>/pull.diff` |
| **Apply into a disposable worktree (recommended)** | Create the worktree from the admin clone first, then apply inside it: `git -C workspaces/<repo>/.target-repo fetch origin <branch> && git -C workspaces/<repo>/.target-repo worktree add workspaces/<repo>/state/<id> origin/<branch>` → `cd workspaces/<repo>/state/<id> && git status --short` (must be empty) `&& git remote get-url origin` (must be the target repo) `&& jules remote pull --session <id> --apply` |
| Bootstrap a workspace with no admin clone yet | Run `jules teleport <id>` from a **neutral cwd** (never the Jules repo root, never an unpushed sibling), then move the created `jules-<repo>-<id>/` clone to `workspaces/<repo>/state/<id>/` and record it in INDEX.yaml |

Rules:

- **Never run `teleport` or `remote pull --apply` from the Jules repo root** —
  it materializes the session's patch into a jules-repo checkout (the legacy
  wrong-repo worktree failure mode).
- **Never run `teleport` from inside `.target-repo/`** — the admin clone matches
  the session's repo, so the patch would be applied directly to the admin
  clone's main checkout, dirtying the worktree owner. The admin clone stays
  clean; patches land in disposable `state/<id>/` worktrees.
- **Never run them from an unpushed sibling checkout** of the target repo.
- If the workspace has no `.target-repo` admin clone yet, create it first:
  `git clone https://github.com/<owner>/<repo>.git workspaces/<repo>/.target-repo`

Notes:

- CLI pull returns a patch only for sessions that **made commits/pushes**.
  Chat-only sessions return `No diff found`.
- A pullable patch is an artifact, not proof of a current remote branch. Before
  treating it as branch state or pushing, resolve and verify the target repo,
  PR, branch, remote URL, base ref, and current remote head with GitHub/Git.
- The patch is the session's exported state; its VM scratch is unreachable.

## 3. Make the local direct changes

In the teleported checkout (or worktree), edit the files, then commit on the
session's branch:

```bash
git add <files>
git commit -m "fix: correct <what> for session <id>"
```

Keep the change surgical: fix the defect, don't refactor the session's
approach unless the task requires it.

## 4. Hand the fixes back — two routes

### Route A — you push, then wake the session (recommended for surgical fixes)

Sessions read their PR branch state. Push your corrected commit to the
session's PR branch, then send a wake-up message:

```bash
git push origin HEAD:<session-pr-branch>

# Log before sending; use the repo-scoped prompt log and preserve the exact body.
cat >> workspaces/<repo>/prompts/sent_responses.md <<'EOF'
session_id: <session_id>
prompt_type: local-fix-wakeup
prompt_sent: <paste exact message below>
outcome: pending
EOF
uv run python3 -m tools.sessions.jules_send_message <session_id> \
  "Wake-up: your work on <branch> needs adjustment. I pushed corrected state
   (commit <sha>): fixed <a>, <b>. The branch was verified at <base-ref> before
   the fix; no claim of current-main ancestry is made unless it was merged or
   rebased. Please fetch the target base, re-verify <x>, run lint/tests, and
   push any follow-up.
   Drift protocol: fetch the target base and diff \$(git merge-base HEAD
   <base-ref>)..<base-ref> for every file you touch — never work from
   memory or cached snapshots. Record the response outcome in the prompt log."
```

### Route B — the session fixes it (for explainable fixes)

Log the exact message before sending, then send precise instructions (exact
files, expected behavior, target base, and drift protocol). After the send,
append the delivery/outcome to the same repo-scoped prompt log. Let the session
change and push its own branch; this keeps session ownership. Do not claim the
branch contains current main unless the session explicitly merged or rebased
that verified base. Always include the drift protocol for stale snapshots.

```bash
cat >> workspaces/<repo>/prompts/sent_responses.md <<'EOF'
session_id: <session_id>
prompt_type: local-fix-guidance
prompt_sent: <paste exact message below>
outcome: pending
EOF
uv run python3 -m tools.sessions.jules_send_message <session_id> \
  "Fix only <files> for <finding>. Fetch and verify <base-ref> first; report
   current head, base, checks, and push SHA. Do not claim current-main ancestry
   unless you merge or rebase it. Record delivery outcome in the prompt log."
```


## 5. Verify — against GitHub, never the session's claims

```bash
jules remote pull --session <id>     # its updated diff
gh pr diff <n> && gh pr checks <n>   # ground truth: PR content + CI state
```

Sessions can hallucinate GitHub-side actions (e.g. "posted review via gh
CLI") — VMs have no GitHub write access. Confirm with GitHub before
accepting any completion claim.

## Constraints & mechanics

| Constraint | Detail |
|------------|--------|
| `sendMessage` state | Works on ANY state — FAILED/COMPLETED sessions can be woken; that is the standard recovery path |
| Session push access | Sessions CAN push to their PR branch (verified); they CANNOT post PR comments from the VM |
| Logging invariant | Append every message to `workspaces/<repo-name>/prompts/sent_responses.md` before/after sending (see `workspace_isolation.md`) |
| Rate limits | 429 → wait 30s; exponential backoff; don't batch 10+ messages (quota exhaustion blocks you, not the session) |
| Stale snapshots | Sessions with old snapshots revert/destroy newer files from cached memory — always send the drift protocol, never trust "reverted to origin/main" claims |
| Worktree home | Session materializations for review/fix belong in `workspaces/<repo>/state/` (or repo `wt/`), not the canonical checkout |

## See also

- `docs/runbooks/workspace_isolation.md` — workspace layout, logging invariant, transport fallbacks
- `docs/runbooks/session_recovery.md` — state→action recovery map
- `docs/runbooks/failure_runbook.md` — task failure / timeout / over-deletion
- `docs/runbooks/session_runbook.md` — daily triage & recovery playbook