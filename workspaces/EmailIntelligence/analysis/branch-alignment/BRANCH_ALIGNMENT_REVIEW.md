# Branch Alignment Review — Taskmaster Branch Integration PRD

**Canonical Version:** 1.0
**Based on:** Jules session 596003508416904399 analysis
**Status:** Production-ready PRD

## 1. Overview

This document defines the complete PRD for the taskmaster branch alignment task.
Goal: safely extract, consolidate, and integrate orphaned taskmaster tooling and stray
commits while preserving branch isolation and governance rules.

## 2. Universal Rules

| Rule | Description |
|------|-------------|
| R0.1 | **Process Isolation:** All alignment work in dedicated worktrees |
| R0.2 | **No-Merge Rule:** main ↔ scientific never merged |
| R0.3 | **Evidence Requirements:** All decisions evidence-based (topology, structure, semantics, Validator) |
| R0.4 | **Tooling Extraction:** Extract verbatim, no reimplementation |
| R0.5 | **Source Attribution:** Preserve original commit attribution |
| R0.6 | **File Organization:** Files go to logical home by function, not history |

## 3. Step Map (S1-S10)

### S1: Bootstrap & Start State
- Fetch all remote branches
- Create worktrees: main, scientific, taskmaster, orchestration-tools, docs-*, setup
- Verify no-merge rule enforced
- **Gate:** All worktrees created, no dirty working trees

### S2: Git Topology Analysis
- Run commit graph topology analysis
- Identify root commits for each branch family
- Map commit relationships across branches
- **Gate:** Complete ancestry map documented

### S3: Semantic Code Structure Analysis
- AST-level comparison across branches
- Function signature, class definition matching
- Import structure analysis
- **Gate:** Code structure similarity matrix with confidence

### S4: Clustering Engine Execution
- Execute `taskmaster branch-cluster` with weighted signals (0.35/0.35/0.30)
- Apply threshold (0.25) for cluster membership
- Generate `assignments.json`
- **Gate:** assignments.json passes Validator

### S5: Validation
- Run Validator against assignments.json
- Check all conditions: branch_contains, branch_not_contains, path_contains, has_tag, has_import
- Verify assertions: target, confidence_min
- **Gate:** Validator passes OR explicit acknowledgement

### S6: Rogue Work Extraction
- Extract 57 commits across PRs #492, #486, etc.
- Create single-concern PRs, security first
- Track full provenance
- **Gate:** Each PR ≤30-min review

### S7: Tooling Consolidation
- Extract cluster_branches.py from consolidate/cli-unification
- Extract engine/branch_clustering.py (blob a899049affa)
- Extract engine/validation_framework.py (blob 2aa026fab)
- Place under alignment/ subtree in orchestration-tools
- **Gate:** All tools verbatim, tests pass

### S8: Dynamic Rebase & Resolution
- Apply clustering for rebase strategies
- Execute rebases with semantic conflict resolution
- Apply fixups based on intent vs implementation


## 6. Start/Stop Conditions

**Start Conditions:**
- Fresh clone with all remotes fetched
- Worktree scaffold prepared (per D-1)
- Policy decision on no-merge rule documented

**Stop Conditions:**
- All Validator gates passed (or explicitly acknowledged)
- Extractable tooling located and moved
- Taskmaster branch ready for integration

## 7. Traceability Requirements

### Linear MCP Integration:
- **Capability Ontology:** Track capability mapping across branches
- **Traceability Matrix:** Link requirements to implementation
- **PR Review Validation:** Verify all PRs meet criteria

### Requirement Chain:
Every change traceable from requirement → implementation → review.

## 8. Quality Gates Summary

| Gate | Criteria | Fail Condition |
|------|----------|----------------|
| S1 | Worktrees created | Dirty working tree |
| S2 | Ancestry map complete | Unknown divergence |
| S3 | Similarity matrix | Low confidence |
| S4 | assignments.json valid | Threshold not met |
| S5 | Validator passes | Override w/o ack |
| S6 | Single-concern PRs | Multi-concern PRs |
| S7 | Verbatim extraction | Reimplementation |
| S8 | Conflicts resolved | Validator failures |
| S9 | Pin bumps merged | Force-push |
| S10 | All requirements met | Incomplete docs |

## 9. Divergence Notes

**From Initial Scaffold:**

1. **Staging Branch:** orchestration-tools (not taskmaster directly) serves as staging/integration
   host because it already has .taskmaster as a submodule.

2. **Tool Consolidation Path:** Tools flow to orchestration-tools first, then taskmaster receives
   via pin-bumps (not direct extraction).

3. **Dynamic Process:** Alignment is NOT one-shot — builds dynamically as evidence gathered.

4. **Validator Centrality:** Validator gates are central, not optional. Every step must pass
   or be explicitly overridden.

---

**Sources:** Session 596003508416904399 (COMPLETED), `scratch_branch_alignment_scaffold/PRD_BRANCH_ALIGNMENT.md`
- Validate each step with Validator gates
- **Gate:** All conflicts resolved, Validator passes

### S9: Pin Bump Integration
- Update .taskmaster submodule pins
- Create pin bump PRs for main↔scientific exchange
- Verify green status checks
- **Gate:** All pin bumps merged, no force-pushes

### S10: Final Validation & Closure
- Run final Validator gate
- Archive process artifacts
- Document final state
- **Gate:** All requirements satisfied

## 4. Step-to-File Responsibility Map

| Step | Jules Owns | Human Owns |
|------|-----------|------------|
| S1-S4 | Analysis, clustering | - |
| S5 | Validation | Acknowledgement if override |
| S6 | Extraction | PR review |
| S7 | Tooling extraction | - |
| S8 | Dynamic resolution | Conflict decisions |
| S9 | Pin bumps | PR approval |
| S10 | Final check | - |

## 5. Definitions

**Feature Branch:** Any branch other than main/scientific/taskmaster with project code.

**Primary Branch:** main or scientific — protected, non-mergeable pair.

**Stray Taskmaster Work:** Commits modifying taskmaster files (tasks/, task_scripts/, .taskmaster/, guidance/) in non-taskmaster branches.

**Alignment:** Routing code to intended branch based on evidence.

**Clean Run:** Alignment where all Validator gates pass without override.
