# Branch Alignment Scaffold — how to use this folder

This is a **sparse, hypothesis-driven scaffold** for the EmailIntelligence branch-alignment effort.
It is **untracked and uncommitted** — it is planning material, not source code, and is intentionally
kept separate from the `jules` repo's git so the live jules git is never mutated.

> Scope rule (from the existing guidance): the actual process runs in a working copy of the
> **EmailIntelligence** repo, **not** the `jules` repo. The `.taskmaster` branch holds task
> outline/definitions only; execution happens in the EI root clone.

## Files
| File | Purpose |
|---|---|
| `PRD_BRANCH_ALIGNMENT.md` | Overarching Product Requirements Doc |
| `REQUIREMENTS.md` | Hard constraints (REQ-01…REQ-06) |
| `DESIGN.md` | Architecture of the alignment process |
| `WORKTREE_CONFIG.md` | The 4 worktrees + sync rules + start state |
| `CLUSTERING_PROCESS.md` | The 4-stage search/analyse pipeline + I/O schema |
| `TASKS.md` | Linear task breakdown T-00…T-06 with sparse ACs |
| `CROSSWALK_EXISTING_TASKS.md` | Maps this scaffold to the mutated `tasks.md` on the real branches |
| `PHASE_2_INVESTIGATION_PLAN.md` | What to do after the scaffold: reconcile vs existing tasks.md |

## Phase plan
- **Phase 1 (this scaffold):** define the correct process from first principles of the real tooling.
- **Phase 2 (next):** read the mutated `tasks.md` files, grade which pieces are still valid, and adapt these files.
