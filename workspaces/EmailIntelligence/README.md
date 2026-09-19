# EmailIntelligence Workspace

Workspace for operating on the EmailIntelligence repository via Jules sessions.

## Session Information

| Session ID | Status | Task |
|-----------|--------|------|
| `596003508416904399` | COMPLETED | Integrate Taskmaster Branches and Reorganize Task Files |

## Directory Structure

```
workspaces/EmailIntelligence/
├── sessions/         # Session summaries and sync reports
├── analysis/         # Analysis artifacts, branch alignment work
│   ├── branch-alignment/       # Canonical branch alignment docs
│   ├── scratch_branch_alignment_scaffold/  # Initial scaffold for comparison
│   ├── REPO_SPECIFIC_STRATEGY_2026-08-06.md
│   ├── PR_MIGRATION_PLAN_2026-08-06.md
│   └── EMAILINTELLIGENCE_TRIAGE.md
├── prompts/          # Prompt drafts and session guidance
│   ├── JULES_FINAL_MESSAGE*.md  # Drafts for final message
│   ├── JULES_UPDATE_MESSAGE.md
│   └── SESSION_GUIDANCE_REPORT.md
├── .target-repo/     # Ignored EmailIntelligence Git admin clone
├── state/INDEX.yaml  # Tracked session/worktree coordination metadata
└── state/<session-id>/ # Ignored target-repository worktrees, isolated by branch
```

## Canonical paths and operations

The canonical target remote is `MasumRab/EmailIntelligence`.
`/home/masum/github/remote/EmailIntelligence` is a sibling canonical checkout
that may contain unpushed user changes and is not a default worktree source.
Raw Jules artifacts belong under `sessions/<session-id>/`; the entire
`sessions/` directory is local-only and ignored. Move durable findings to
`analysis/`. Disposable editable worktrees belong at
`/home/masum/github/remote/jules/workspaces/EmailIntelligence/state/<session-id>/`,
with one branch per session. Existing registered worktrees are intentionally left
in place during this pass;
see the migration note in `docs/README.md` before relocating any dirty worktree.

```bash
# Run from /home/masum/github/remote/jules.
jules remote list --repo
jules remote list --session
mkdir -p workspaces/EmailIntelligence/sessions/<session-id>
jules remote pull --session <session-id> \\
  > workspaces/EmailIntelligence/sessions/<session-id>/pull.diff
jules teleport <session-id>
# Confirm teleport used the matching localized state worktree.
git worktree list --porcelain
```

Create target worktrees only from the workspace-owned admin clone, never from
the Jules root or unpushed sibling checkout:

```bash
git -C workspaces/EmailIntelligence/.target-repo fetch origin <pr-branch> <base>
git -C workspaces/EmailIntelligence/.target-repo worktree add \\
  workspaces/EmailIntelligence/state/<session-id> origin/<pr-branch>
git -C workspaces/EmailIntelligence/state/<session-id> remote get-url origin
```

Record the resulting repository, branch, base, and head in
`state/INDEX.yaml`; never reuse a state directory for another session or
branch. A verified target worktree may be edited, committed, and pushed to the
existing PR branch after explicit authorization.

`jules teleport` is available; run `jules teleport --help` for current options.
The canonical remote is `https://github.com/MasumRab/EmailIntelligence.git`.

### Review boundary

This README is Jules orchestration documentation tracked in the Jules
repository. Running CodeRabbit from `/home/masum/github/remote/jules`—including
from this workspace directory—reviews Jules repository changes, not
EmailIntelligence source. Do not `cd` into a workspace artifact directory and
mistake it for a target checkout.

For target-session inspection, use `jules remote list|pull` and a localized
`state/<session-id>/` worktree only after verifying its actual Git root and
remote. Existing state entries in this workspace currently check out the Jules
repository, despite the workspace name; recreate or replace an entry from the
EmailIntelligence target repository before repair. Once verified as an
EmailIntelligence worktree, it is the approved repair surface: agents may edit,
commit, and push to the existing PR branch after explicit authorization,
branch/PR, base-ref, and remote-head verification. A target review/fix still
requires those checks before editing. Do not read, edit,
test, or stage the unpushed sibling `/home/masum/github/remote/EmailIntelligence`
by default; it may contain unrelated user changes. Workspace `sessions/`,
`state/`, caches, generated files, and temporary exports are disposable and
ignored; they are not application source and must not be included in a Jules
review or repair. Use `git status --short --ignored` and `git check-ignore` to
confirm the boundary. Review findings are hypotheses: verify each path against
the current localized target worktree before editing.

## Key Context

### Branch Governance

- `origin/taskmaster` is isolated (root: 78dd10b5, HEAD: 1426a01c99)
- Main/scientific never merge (no-merge rule)
- Tooling stranded in `consolidate/cli-unification`
- ~300+ files backed up to `future_advanced_state/`

### Session Continuation

To continue the branch alignment work:

1. Check session status: `python3 tools/sessions/jules_list_sessions.py --state COMPLETED --limit 5`
2. Review prior work: See `sessions/` for session summaries
3. Check analysis progress: See `analysis/branch-alignment/` for canonical docs
4. Send continuation prompt using one of the drafts in `prompts/`

### Tooling References

- Clustering engine: `engine/branch_clustering.py` (blob: a899049affa)
- Validator: `engine/validation_framework.py` (blob: 2aa026fab)
- Main CLI: `cluster_branches.py` (in consolidate/cli-unification)
