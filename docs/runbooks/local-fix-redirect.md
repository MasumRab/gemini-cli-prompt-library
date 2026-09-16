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

| Need | Command | Result |
|------|---------|--------|
| Inspect only | `jules remote pull --session <id> > workspaces/<repo>/sessions/<id>/pull.diff` | Session diff to ignored local storage |
| **Editable isolated copy (recommended)** | `jules teleport <id>` | Create/inspect only under the matching `workspaces/<repo>/state/<id>/` worktree |
| Apply into an existing worktree | `jules remote pull --session <id> --apply` | Applies in place. Use only inside the verified target-repo worktree under `workspaces/<repo>/state/`, **never** an unpushed sibling or canonical checkout |

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

uv run python3 -m tools.sessions.jules_send_message <session_id> \
  "Wake-up: your work on <branch> needs adjustment. I pushed corrected state
   (commit <sha>): fixed <a>, <b>. The branch now reflects current main plus
   the fixes. Please re-verify <x>, run lint/tests, and push any follow-up.
   Drift protocol: fetch origin main and diff \$(git merge-base HEAD
   origin/main)..origin/main for every file you touch — never work from
   memory or cached snapshots."
```

### Route B — the session fixes it (for explainable fixes)

Send precise instructions (exact files, expected behavior, drift protocol)
and let the session change and push its own branch. Keeps session ownership;
always include the drift protocol for sessions with stale snapshots.

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