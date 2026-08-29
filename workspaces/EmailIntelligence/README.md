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
└── state/            # Per-agent scratch (patches, worktrees)
```

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
