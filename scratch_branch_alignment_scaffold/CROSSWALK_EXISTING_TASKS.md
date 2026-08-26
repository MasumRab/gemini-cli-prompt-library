# Crosswalk — scaffold tasks vs the existing (mutated) `tasks.md` corpus

This is the **trusted evidence mapping** so Phase 2 can grade what is still valid instead of
re-deriving from scratch. Sources are live commits/branches on EmailIntelligence (not jules).

## Clustering engine location (the "search & analyse" implementation)
| Artifact | Branch | Path | Commit / Blob |
|---|---|---|---|
| `ClusterBranchesCommand` | consolidate/cli-unification | `src/cli/commands/task/cluster_branches.py` | (cmd module) |
| `ClusterEngine` / `BranchAnalyzer` (Stage One) | consolidate/cli-unification | `src/cli/commands/task/engine/branch_clustering.py` | blob `a899049affa` (12211 bytes) |
| `Validator` (Natural Language Validation Layer) | consolidate/cli-unification | `src/cli/commands/task/engine/validation_framework.py` | blob `2aa026faba` (3807 bytes) |
| test | consolidate/cli-unification | `tests/cli/commands/task/test_cluster_branches.py` | (validates assignments schema) |

## Existing tasks.md sources (which define the process the scaffold mirrors)
| Existing task | Branch | Path (live) | Status per scaffold mapping |
|---|---|---|---|
| Task "021: Clustering" (3-stage) | origin/taskmaster | `tasks/task_002-clustering.md` | → T-01 Stages One–Three ✓ |
| Alignment execution tasks 022/023 | origin/taskmaster | `task_master_formatted_tasks_v2.md` (Initiative 4) | → T-03 ✓ |
| Validation framework (1.1–1.9) | origin/taskmaster | `guidance/reorganized_tasks.md` (Initiative 1) | → T-01.4 / T-04 ✓ |
| Pre-merge scripts | origin/taskmaster | `guidance/task_master_formatted_tasks_v2.md` ID 2 | → T-04.2 ◉ (needs wiring) |
| Branch-alignment framework (001) | origin/taskmaster | `tasks/task_001.md` | → T-00 + T-02 ✓ |
| Backup/restore mechanism | origin/taskmaster | `guidance/task_master_formatted_tasks_v2.md` ID 5 | → T-00.1 + T-03.1 ✓ |

## Process docs the scaffold is grounded in
| Doc | Branch | Path | What it gives the scaffold |
|---|---|---|---|
| Final merge strategy | origin/taskmaster | `guidance/FINAL_MERGE_STRATEGY.md` | Option 1 (cherry-pick critical commits) adopted by T-02 |
| Worktree setup integration guide | update-main-with-analysis | `WORKTREE_SETUP_INTEGRATION_GUIDE.md` | T-00 worktree set + sync rules |
| Scientific branch alignment plan | setup-worktree | `SCIENTIFIC_BRANCH_ALIGNMENT_PLAN.md` | T-03 scientific-rebase pattern (Phase 1–3) |
| Feature-branch alignment template | setup-worktree | `backlog/tasks/align-large-branches-strategy.md`, `alignment-task-template.md` | T-03 / T-06 PR hygiene (≤30-min, security-first) |
| Complete branch alignment meta-task | setup-worktree | `backlog/tasks/complete-branch-alignment.md` | T-02/T-06 extraction→merge→cleanup ordering |
| Post-merge validation | setup-worktree | `backlog/tasks/post-merge-validation.md` | T-06 |

## Rogue-work evidence (the 57-commit strand the scaffold migrates)
- `status_report.md` §3 ROGUE TASKMASTER WORK DISCOVERY — sample commit reasons include
  `chore: bump .taskmaster submodule — Phase A cross-ref fixes`,
  `docs: reference canonical BRANCH_MANAGEMENT_MODEL.md`,
  `Add .taskmaster as submodule tracking taskmaster branch` (472db8f7),
  `Remove submodule, keep shared files directly in root` (3e34e72e).
- Full SHA list (57): `rogue_taskmaster_commits.txt` (recovered).
- Target PRs named: **#492, #486** (plus #179, #659, #660 referenced in templates).

## Architecture contradiction to resolve in T-00.5
- Submodule model commits: `275045a1`, `472db8f7`, `d8ab50d4`, `fd638f41`
- Inline model commits: `3e34e72e`, `fd638f41` (remove), `cc5ee244` (exclude from index)
- Scaffold picks **pin-bump submodule model (A)** to stabilise; Phase 2 verifies `976c5e62`
  (protection commit) intent.

> Unresolved-in-scaffold marks: ◉ = wiring not yet confirmed against live content.

---

## Preliminary comparison verdicts (content-agnostic vs live `tasks.md`)

From read-only review of `origin/taskmaster` guidance/tasks + `consolidate/cli-unification` engine +
`setup-worktree` templates. These drive the Phase 2 adaptation of the scaffold.

| Live artifact | Matches scaffold? | Gap / verdict | Adjustment needed in scaffold |
|---|---|---|---|
| `guidance/task_master_formatted_tasks_v2.md` (Initiatives 1–5, IDs 001–026; clustering=Task 002 w/ 9 subtasks 02.1–02.5+test/bench) | ✅ VALID | The scaffold's T-01–T-07 numbering differs from the 001–026 numbering in this file. | Add cross-ref row in TASKS.md: scaffold T-01 ≡ ID 003; scaffold T-03 ≡ ID 002/021; scaffold T-02 ≡ ID 010(?). Phase 2 renumbers or aliases. |
| `guidance/reorganized_tasks.md` (Initiatives 1 & 2, merged IDs 9/19/54–81) | ⚠️ REGRESSED | An older numbering scheme (9/19/54–81) coexists with v2 (001–026) — two truth formats on taskmaster. | PRD S5/S6 must pin which numbering is canonical; flag as a mutation hazard. |
| `tasks/task_001.md` ("Align Feature Branches with Justified Targets — FRAMEWORK DEFINITION") | ✅ VALID | Explicitly a framework-definition task (success criteria listed), matches S1+S6. | None; T-00/T-06 already cite it. |
| `tasks/task_002-clustering.md` (5 subtasks w/ Quick-Reference signatures, return-json shape, metrics) | ⚠️ REGRESSED vs engine | Doc lists `CommitHistoryAnalyzer` etc., but the engine blob `a899049affa` uses class `BranchAnalyzer` (no `CommitHistoryAnalyzer` class). Doc is the *spec*; engine is the *impl* and diverges in naming. | S3 must use engine's actual class/methods, not the doc's Quick Reference. Flag mismatch. |
| `src/.../cluster_branches.py` + `engine/branch_clustering.py` + `validation_framework.py` (blobs a899049affa / 2aa026faba on `consolidate/cli-unification`) | ✅ VALID (source of truth) | Engine uses weights 0.35/0.35/0.30, threshold 0.25, modes id/cluster/hybrid, Validator conditions/asserts exactly as scaffold states. | None — this is why REQ-04 pins to `consolidate/cli-unification`. |
| `guidance/FINAL_MERGE_STRATEGY.md` (Options 1/2/3; recommends Option 1 cherry-pick) | ✅ VALID | Matches S5 (extract via cherry-pick, not big-merge). | Maps directly; keep Option 1 as gate. |
| `setup-worktree` templates (`alignment-task-template.md`, `alignment-main-task-template.md`, `complete-branch-alignment.md`, `post-merge-validation.md`) | ✅ VALID | Templates' sections (ID/priority/status/5 Qs/metrics/target/approach/Action Plan AC/deps) == scaffold S6 required sections exactly. `complete-branch-alignment.md` extraction→security-first→≤30-min ordering == S5/S7/S10. | None; S6/S10 already mirror them. |
| `WORKTREE_SETUP_INTEGRATION_GUIDE.md` (`update-main-with-analysis`) | ✅ VALID for setup, ⚠️ partial for sync | Defines the 5 worktrees (launch-setup-fixes canonical; docs-main/doc-only; docs-scientific/doc-only; pre/post-commit hooks; `sync_setup_worktrees.sh`); but the sync script itself was **not** readable on that branch (empty return). | S1/WORKTREE_CONFIG must add a verification step that reads `scripts/sync_setup_worktrees.sh` and confirms the doc-only exclusion before relying on it. |
| `.jules/TASKS.md` (if it exists on taskmaster) | ◉ UNCHECKED | Referenced by PRD R0.2/R0.4 but not yet located in taskmaster tree. | Phase 2 must locate and either adopt or replace it. |
| `guidance/ARCHITECTURE_ALIGNMENT_DECISION.md` | 🗑️ MISSING | S4 demands a decision doc settling inline-vs-submodule; no such file exists on taskmaster. | Jules must CREATE it (S4), citing 3e34e72e vs 472db8f7 as the case record. |
| `tasks/task-NNN-align-<branch>.md` per-target files | 🗑️ MISSING | S6 demands one task file per assigned branch; none exist on taskmaster. | Jules must CREATE them (S6) from `assignments.json` after S3. |

### Net
- **Valid backbone** = clustering engine (blobs) + FINAL_MERGE_STRATEGY (Option 1) + setup-worktree
  templates + task_001. These are the reliable spine the scaffold leans on.
- **Regressed/inconsistent** = the two task-numbering formats (v2 vs reorganized) and the
  doc-vs-engine naming mismatch in task_002. Phase 2 must pick canonical numbering + defer to engine.
- **Missing (Jules must create)** = `ARCHITECTURE_ALIGNMENT_DECISION.md`, the per-branch alignment
  task files, and the start/Stop hand-back gate in `alignment-task-template.md`.

