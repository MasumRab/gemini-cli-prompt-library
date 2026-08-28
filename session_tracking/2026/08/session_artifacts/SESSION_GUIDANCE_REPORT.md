# SESSION GUIDANCE REPORT: Taskmaster Branch Alignment Analysis

## Summary

This report provides guidance on how the current Jules session should proceed with work already completed (session 596003508416904399) to align with the goals and intentions found in the requirements, design, and PRD documents from the scratch_branch_alignment_scaffold/ directory.

## Current Session Status (596003508416904399)

Based on the session status report and activities log, Jules session 596003508416904399 has:

- ✅ Completed initial discovery and analysis phases
- ✅ Identified branches sharing ancestry with origin/taskmaster
- ✅ Identified rogue taskmaster work in main-rooted branches
- ✅ Examined 000-\* and consolidate/cli-unification branches for plans and tooling
- ✅ Backed up advanced state of task files into future_advanced_state/
- ⏳ Pending: Extraction, cherry-picking, or merging of missing tooling
- ⏳ Pending: PR comments or Linear MCP issue creation
- ⏳ Pending: Initialization of Linear MCP for Capability Ontology, Traceability Matrix, and PR Review Validation

## Alignment with Documentation

### How Current Work Aligns with Requirements/Design/PRD

**Requirements Alignment:**

- REQ-01 (Isolation): Session operated on origin/taskmaster branch - compliant
- REQ-02 (Tooling provenance): Session identified need to extract from consolidate/cli-unification - on track
- REQ-03 (Determinism): Analysis phase supports reproducible inputs - foundation laid
- REQ-04 (Validation gating): Session identified need for Validator - prerequisites identified
- REQ-05-08: Worktree and scope discipline maintained in analysis

**Design Alignment:**

- D-1 Start state: Session began with isolated origin/taskmaster branch - correct
- D-2 Engine wiring: Session identified required tooling components - ready for extraction
- D-3 Target matrix: Session discovered branch relationships - mapping possible
- D-4-D-7: Safety invariants and merge discipline concepts understood in analysis

**PRD Alignment:**

- R0.1-R0.6: Universal rules understood and followed in analysis phase
- Steps S1-S4: Bootstrap, inventory, rogue map, clustering preparation - completed/in progress
- Steps S5-S10: Tooling extraction, task file creation, alignment execution, validation, restoration, cleanup - pending

## What Files Need Adaptation for Current Session Findings

### 1. REQUIREMENTS.md

**Current Status**: Provides hard constraints for the alignment process
**Adaptation Needed**:

- Add verification checkpoints based on session findings
- Include specific SHA references from discovered branches
- Document validation criteria for the rogue work identified in PR #492/#486
- Reference the actual file counts from future_advanced_state/ backup (~300+ files)

### 2. DESIGN.md

**Current Status**: Provides system design and architecture
**Adaptation Needed**:

- Update D-1 diagram with actual SHAs discovered (78dd10b5 root, 1426a01c99 HEAD)
- Add discovered branches to staging/ref analysis (chore/cli-tooling-requirements-review-\*, feature/recover-lost-modules)
- Document actual tooling locations found (PR #492, PR #679)
- Include validation framework requirements based on session's identified needs

### 3. PRD_BRANCH_ALIGNMENT.md

**Current Status**: Provides task specification and step map
**Adaptation Needed**:

- Update Step S5 with actual PR numbers and file paths discovered
- Add specific validation requirements from session's Linear MCP initialization need
- Update expected outcomes based on actual file counts and branch mappings
- Add quality gates derived from session's discovered rogue work patterns

## How Current Session Should Proceed with Completed Work

### Immediate Actions (Analysis-Focused)

1. **Document Current State**: Create a comprehensive analysis report that:
   - Maps session findings to requirements/design/PRD
   - Identifies gaps and next steps
   - Provides verification criteria for future implementation

2. **Create Verification Framework**: Document what would constitute successful completion of:
   - Tooling extraction (byte-identical verification)
   - Branch mapping accuracy
   - Validation framework readiness
   - Linear MCP initialization prerequisites

3. **Risk Assessment**: Document potential issues and mitigation strategies based on:
   - Divergent branch histories discovered
   - Potential conflicts in file extraction
   - Validation rule complexity
   - Restoration scope creep risks

### Deliverable for Current Session

The current session should produce a **Taskmaster Alignment Analysis Report** that includes:

- Executive summary of current state vs. target state
- Detailed gap analysis between session progress and documentation requirements
- Verification checklist for each PRD step
- Risk assessment and mitigation strategies
- Recommended sequence for next implementation session
- Open questions requiring clarification

**CRITICAL**: This session must NOT perform any actual extractions, modifications, engine runs, validations, or session creations. All work product must be analytical/report-based only.

## Next Session Prompt Structure

Based on the analysis, here is the recommended structure for the next Jules session prompt:

```
# TASKMASTER ALIGNMENT IMPLEMENTATION SESSION - READY FOR EXECUTION

## Session Focus: CONTROLLED IMPLEMENTATION WITH VERIFICATION GATES
**Objective**: Execute specific, verified steps from the PRD step map with quality gates
**Constraint**: Each step must pass its quality gate before proceeding to the next

## Prerequisites Verified (from previous analysis session)
- [ ] Tooling extraction requirements documented (PR #492, PR #679 file lists and SHAs)
- [ ] Clustering engine requirements documented (command structure, inputs, outputs)
- [ ] Validation framework requirements documented (ruleset schema, assertions)
- [ ] Branch mapping analysis completed (target assignments, integration directions)
- [ ] Quarantined state assessment completed (restoration criteria, scope boundaries)

## Session Workflow: Execute PRD Steps with Quality Gates

### STEP S5: Extract Stranded Tooling
**Goal**: Bring PR #492/#486 tooling into isolated taskmaster root
**Expected Outcome**:
  - src/cli/commands/task/{cluster_branches, analyze_tasks, list_tasks, taskmaster}.py
  - engine/{branch_clustering, validation_framework}.py
  - tests/cli/commands/task/test_cluster_branches.py
  - All files byte-identical to consolidate/cli-unification source
**Quality Gate**:
  - FINAL_MERGE_STRATEGY.md (Option 1)
  - complete-branch-alignment.md (extraction verification)
  - Reject if any file differs from source SHA; reject if duplicate task IDs
**Allowed Actions**:
  - File copies from consolidate/cli-unification to taskmaster branch
  - SHA verification checks
  - No file edits or modifications permitted

### STEP S1-S4 Verification (if needed)
**Goal**: Confirm bootstrap, inventory, and preparation are complete
**Expected Outcome**:
  - worktrees/ created with 7 worktrees
  - clustering_rules.yaml seeded
  - .taskmaster/policy locked per DESIGN.md D-2
  - archive/rogue_commit_map.txt and 000_branches_report.tsv populated
**Quality Gate**:
  - task_001.md + FINAL_MERGE_STRATEGY.md + WORKTREE_SETUP_INTEGRATION_GUIDE.md
  - Reject if main/scientific merged; reject if .taskmaster policy not locked
**Allowed Actions**:
  - Verification checks only
  - No modifications unless correcting pre-existing issues from previous sessions

### STEP S6: Generate Per-Target Alignment Task Files
**Goal**: Create tasks/task-NNN.md files per branch per assignments.json
**Expected Outcome**:
  - One tasks/task-NNN-align-<branch>.md per non-primary branch
  - Files include: ID, priority, status, assessment Qs, metrics, target branch, approach, Phase 1/2/3 plan, AC, dependencies
**Quality Gate**:
  - alignment-task-template.md / alignment-main-task-template.md
  - Reject if any file missing required section; reject if approach merges main↔scientific
**Allowed Actions**:
  - File creation based on verified assignments.json (from S5 output if generated)
  - Template population only
  - No content invention or deviation from templates

## Success Criteria for This Session
- [ ] All executed steps pass their respective quality gates
- [ ] Zero unauthorized modifications or creations
- [ ] All work product is either verified outputs or analytical reports
- [ ] Clear documentation of what was accomplished vs. what remains
- [ ] Prepared foundation for subsequent sessions to continue the PRD step map

## Emergency Abort Conditions
- Any attempt to merge main↔scientific directly
- Any file edits to extracted tooling (must be byte-identical)
- Any validation rule modifications without explicit documentation
- Any restoration of non-task-system paths from future_advanced_state/
- Any session creation without explicit user approval

---
*This guidance report synthesized from:*
- Session 596003508416904399 status report and activities log
- REQUIREMENTS.md, DESIGN.md, PRD_BRANCH_ALIGNMENT.md from scratch_branch_alignment_scaffold/
- Session tool analysis and activity patterns
*Provides actionable guidance for aligning current session work with documented intentions*
*Ensures findings are presented as reports, not triggers for unintended code changes or session creation*
```
