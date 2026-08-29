# Worktree Configuration (authoritative source: WORKTREE_SETUP_INTEGRATION_GUIDE.md on update-main-with-analysis)

## Canonical set
| Worktree path | Branch | Role | Sync target? |
|---|---|---|---|
| `worktrees/launch-setup-fixes` | launch-setup-fixes | Canonical shared setup/ scripts | SOURCE (never pull into) |
| `worktrees/main` | main | code | YES (non-doc) |
| `worktrees/scientific` | scientific | code | YES (non-doc) |
| `worktrees/orchestration-tools` | orchestration-tools | code | YES (non-doc) |
| `worktrees/taskmaster` | taskmaster | alignment execution | YES (non-doc) |
| `worktrees/docs-main` | docs-main | **documentation-only** | NO (excluded) |
| `worktrees/docs-scientific` | docs-scientific | **documentation-only** | NO (excluded) |

## Start procedure (fresh isolated state)
1. `git clone <EI origin> /tmp/ei-align-<timestamp>`  (never clone into ~/github/remote/jules)
2. `cd /tmp/ei-align-*`
3. `git fetch origin '+refs/heads/*:refs/remotes/*' --prune --quiet`
4. `git worktree add worktrees/launch-setup-fixes launch-setup-fixes`
5. `git worktree add worktrees/main main`
6. `git worktree add worktrees/scientific scientific`
7. `git worktree add worktrees/orchestration-tools orchestration-tools`
8. `git worktree add worktrees/taskmaster taskmaster`
9. `git worktree add worktrees/docs-main docs-main`
10. `git worktree add worktrees/docs-scientific docs-scientific`

## Sync process
- `scripts/sync_setup_worktrees.sh` synchronizes setup files from `launch-setup-fixes` → all
  **code** worktrees, **excluding** `docs-main` / `docs-scientific`.
- Hooks: pre-commit validates doc placement; post-commit dispatches sync.
- Config: `.worktree_sync_scientific.json` drives scientific-worktree sync rules.

## Start gate (must be TRUE before S3 clustering)
- [ ] All 7 worktrees checked out clean (incl. `orchestration-tools` staging host)
- [ ] `.taskmaster/clustering_rules.yaml` seed present on staging host
- [ ] `sync_setup_worktrees.sh` + validation deps present
- [ ] `main` and `scientific` both on true tips, **no merge between them performed**
- [ ] staging host (`orchestration-tools`) chosen and `output/` + `alignment/` paths reserved

> Sparse — exact script path/flag list confirmed in Phase 2 against the live `sync_setup_worktrees.sh`.
