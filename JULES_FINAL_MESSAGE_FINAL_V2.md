# Final Message for Jules: Generate Canonical Documentation from Scratch

---

## Message to Send to Jules (FOR REVIEW - NOT YET SENT)

```
Please generate canonical REQUIREMENTS.md, DESIGN.md, and BRANCH_ALIGNMENT_REVIEW.md documents for the taskmaster branch alignment work based on your COMPLETED analysis in session 596003508416904399.

## CRITICAL CONSTRAINT: DOCUMENT ONLY - NO RE-ANALYSIS OF COMPLETED WORK
Your analysis phase is COMPLETE. These documents must reflect your EXISTING understanding ONLY. Do NOT:
- Re-run GraphQL queries, Git history traversal, or branch scans for work you've already completed
- Re-examine 000-* branches, consolidate/cli-unification, or PRs #492/#486/#679 for findings you already have
- Re-identify rogue work, tooling locations, or branch relationships you've already catalogued
- Execute ClusterEngine, Validator, Linear MCP, or any tools for validation/execution
- Modify repository state (future_advanced_state/, working tree, branches)
- Perform ANY investigation, discovery, or analysis work for findings you ALREADY POSSESS

## PERMITTED: SEARCHES TO FLESH OUT IMPLEMENTATION DETAILS
You MAY and SHOULD perform targeted searches to flesh out implementation details for the documents you construct:

**Permitted Searches:**
- Search local repository for `.sh` and `.py` files you've already surfaced in your analysis (cluster_branches.py, branch_clustering.py, validation_framework.py, sync scripts, task scripts, etc.) to extract:
  - Exact function signatures, class definitions, method names
  - Exact command-line interfaces, argument parsing
  - Exact configuration file formats, YAML schemas
  - Exact error handling patterns, logging formats
  - Exact import structures, module dependencies
- Search for any additional `.sh`/`.py` files in the repository that relate to:
  - Task management workflows (task_scripts/, task_scripts/)
  - Branch clustering and analysis
  - Validation and testing frameworks
  - Sync and deployment scripts
  - Linear/GitHub integration scripts
- Reference exact file paths, function names, class names, config keys from these files in your documents
- Use these details to make implementation instructions, design specs, and requirements CONCRETE and IMPLEMENTABLE

**Search Boundaries:**
- ONLY search for implementation details to enrich documents you're constructing
- DO NOT search for new findings, new branches, new rogue work, new tooling locations
- DO NOT re-validate or re-verify findings you already have

## WHAT YOU ALREADY UNDERSTAND (from completed session 596003508416904399)

**Branch Architecture:**
- origin/taskmaster is an isolated branch with root commit 78dd10b5, HEAD at 1426a01c99
- It does NOT share history with main or scientific branches
- Only chore/cli-tooling-requirements-review-8803610982851555196 and feature/recover-lost-modules share its root
- Previous attempts were compromised by mixing main and taskmaster histories

**Stranded Tooling Locations:**
- Consolidate/cli-unification branch contains the correct clustering tooling:
  - cluster_branches.py (main CLI command)
  - engine/branch_clustering.py (core clustering engine, blob a899049affa)
  - engine/validation_framework.py (Validator class, blob 2aa026fab)
- PR #679 produced cli_tooling_requirements_review.md (alignment plan)

**State Preservation:**
- ~300+ files backed up to future_advanced_state/:
  tasks/, task_scripts/, .taskmaster/, docs/, scripts/, templates/
- No files deleted; state safely preserved

**Rogue Work Identified:**
- 57 commits across PRs #492, #486, etc. modified taskmaster files in main-rooted branches
- These represent stranded work that should be extracted to origin/taskmaster

**Next Steps Identified (pending):**
- Initialize Linear MCP for Capability Ontology, Traceability Matrix, PR Review Validation
- Extract missing tooling from main-rooted branches
- Extract incorrectly committed task work
- Review PR contexts and integrate
- Complete pre-commit steps and submit

## DOCUMENTATION YOU HAVE ALREADY CREATED
Your completed analysis has already produced substantial documentation that forms the basis for these new documents:

- TASKMASTER_ELUCIDATION.md - Your comprehensive elucidation of the taskmaster implementation
- Evidence-based status report with branch ancestry, rogue work discovery, 000-* investigation
- Evidence-based status report with future_advanced_state verification
- Multiple plan generations and progress updates showing your architectural decisions
- Your elucidation of task schema, naming conventions, subtask dependencies, lifecycle, gaps
- Your comprehensive branch alignment plan with universal rules, step map, responsibility map
- Your evidence-based status report with Linear traceability requirements

## LOCAL SCAFFOLD GUIDANCE (for steering only)
The scratch_branch_alignment_scaffold/ contains rough scaffold documents (REQUIREMENTS.md, DESIGN.md, PRD_BRANCH_ALIGNMENT.md) that were used for initial investigation. These are ROUGH SCAFFOLDS ONLY - NOT canonical. Use them ONLY as steering guidance for:
- General structure and terminology to maintain consistency
- Reminder of investigation categories already explored
- Terminology conventions (taskmaster, future_advanced_state, etc.)
- DO NOT copy their requirement numbers, design sections, or specific formulations
- DO create your own from scratch based on your actual understanding

## DOCUMENTS TO GENERATE FROM SCRATCH

### 1. REQUIREMENTS.md - CREATE FROM YOUR UNDERSTANDING
Create a canonical requirements document that captures ALL hard constraints necessary for correct taskmaster branch alignment. Draw from your COMPLETED analysis and the documentation you've already created:

**Core Constraints (from your understanding):**
- Isolation requirements (taskmaster isolation, no main↔scientific merges)
- Tooling provenance (verbatim extraction from consolidate/cli-unification)
- Determinism requirements (reproducible clustering given identical inputs)
- Validation gating (YAML ruleset must pass; failure aborts alignment)
- Worktree sync integrity (launch-setup-fixes as canonical, docs-only worktrees excluded)
- PR hygiene (single-concern, security-first, ≤30-min review)
- Scope discipline (only task-system paths restored from future_advanced_state/)
- Merge discipline (free-to-integrate ≠ merge-anything; rebase not merge; pin-bumps only data exchange)

**Additional constraints from your analysis and created documentation:**
- Any constraints from your branch architecture understanding and TASKMASTER_ELUCIDATION.md
- Any from stranded tooling locations and your elucidation of tooling gaps
- Any from rogue work patterns and your status report findings
- Any from state preservation requirements and your future_advanced_state verification
- Any from Linear MCP integration needs and your traceability requirements

**Enrich with implementation details from code searches:**
- Exact YAML validation schema keys from validation_framework.py
- Exact CLI command structures from cluster_branches.py
- Exact config file formats from any .yaml/.json files you've seen
- Exact error types, validation rules from validation_framework.py

**Format:** Numbered list with brief explanations. Create YOUR OWN requirement numbering from scratch.

### 2. DESIGN.md - CREATE FROM YOUR ARCHITECTURAL UNDERSTANDING
Create a canonical design document capturing your architectural understanding from your completed analysis and created documentation:

**Start State (D-1 equivalent):**
- Actual branch relationships and SHAs you discovered
- Worktree scaffold needed
- Staging branch decision (orchestration-tools as S0)

**Engine Wiring (D-2 equivalent):**
- Actual command structure with file refs you located
- Engine components you identified (ClusterEngine, BranchAnalyzer, Validator)
- Output locations and formats

**Enrich with code-level details:**
- Exact class hierarchies from branch_clustering.py, validation_framework.py
- Exact method signatures, public APIs from cluster_branches.py, branch_clustering.py
- Exact data structures passed between components
- Exact configuration loading patterns from code you've seen

**Target Matrix (D-3 equivalent):**
- Actual integration directions from your branch mapping
- Gates for each target
- Pin-bump model for main↔scientific

**Signal Processing (D-4 equivalent):**
- Signal weights and thresholds from your analysis
- Clustering logic flow

**Enrich with implementation specifics:**
- Exact similarity calculation methods from branch_clustering.py
- Exact threshold values, weight constants from code
- Exact data structures for assignments.json

**Safety Invariants (D-5/6 equivalent):**
- No-merge invariants
- .taskmaster policy lock
- Tooling verbatim constraint
- Merge discipline rules

**Enrich with implementation enforcement:**
- Exact validation checks from validation_framework.py
- Exact git operations from sync scripts
- Exact error handling from task scripts

### 3. BRANCH_ALIGNMENT_REVIEW.md - CREATE A COMPLETE, EXHAUSTIVE PRD FROM SCRATCH
Generate YOUR canonical, complete, and exhaustive PRD document for the branch alignment task. This is NOT a copy of any scaffold - it is YOUR canonical PRD created from scratch based on ALL the documentation you have already created in this session (TASKMASTER_ELUCIDATION.md, status reports, plans, elucidations, etc.).

Your BRANCH_ALIGNMENT_REVIEW.md MUST be a complete, exhaustive PRD document that includes:

**Universal Rules (your canonical version):**
- Process isolation, no-merge rule, evidence requirements, tooling extraction, source attribution, file organization
- Drawn from your actual analysis, not copied from any scaffold

**Complete Step Map (S1-S10 equivalent - YOUR canonical steps):**
- Your canonical step map with goals, expected outcomes, quality gates
- Populated with YOUR actual findings (SHAs, branch names, tooling locations, file counts from your actual work)
- Each step with clear goals, expected outcomes, quality gates, acceptance criteria

**Enrich step details with implementation specifics:**
- Exact commands to run at each step (from cluster_branches.py, sync scripts, task scripts)
- Exact file paths to create/modify (from your code searches)
- Exact validation commands to run (from validation_framework.py, test files)
- Exact git operations (from sync scripts, task scripts)

**Complete Step-to-File Responsibility Map:**
- What Jules owns at each step
- Actions Jules takes at each step

**Complete Content-Agnostic Definitions (your precise definitions):**
- Your precise definitions for: feature branch, primary branch, stray taskmaster work, alignment, clean run
- Any additional definitions needed for complete understanding

**Complete Start/Stop Conditions:**
- Your precise start conditions (fresh clone, worktree scaffold, policy decision)
- Your precise stop conditions (validated targets, extractable tooling, Validator gate)
- Any additional conditions from your analysis

**Complete Traceability Requirements:**
- Linear MCP integration for Capability Ontology, Traceability Matrix, PR Review Validation
- Requirement→issue→commit→review chain requirements
- From your Linear MCP initialization needs identified in your analysis

**Complete Quality Gates:**
- Validation requirements for each step
- Acceptance criteria for each deliverable
- Rejection criteria for non-compliance

**Complete Divergence Notes:**
- Where your analysis revealed different realities from any rough scaffolds
- What your actual findings revealed vs. initial assumptions

**Completeness Requirements:**
- Every requirement from your REQUIREMENTS.md must be addressed
- Every design element from your DESIGN.md must be implemented
- Every step must have clear acceptance criteria
- Every deliverable must have verification method

**Enrich with implementation-ready details:**
- Exact command sequences for each step
- Exact file paths and expected outputs
- Exact validation commands and expected results
- Exact rollback procedures from sync/task scripts

## PURPOSE
These three documents represent YOUR CANONICAL understanding created from scratch based on your COMPLETED analysis AND the documentation you've already created (TASKMASTER_ELUCIDATION.md, status reports, plans, elucidations). They will be compared against the rough scaffold. Output as markdown files suitable for direct comparison.

## VERIFICATION
Before generating, confirm: "I am creating these documents from scratch based ONLY on my completed analysis from session 596003508416904399 and the documentation I've already created (TASKMASTER_ELUCIDATION.md, status reports, plans, elucidations). I will perform targeted code searches to enrich implementation details. I will not re-analyze, re-investigate, or copy from scaffolds. I will generate REQUIREMENTS.md, DESIGN.md, and BRANCH_ALIGNMENT_REVIEW.md from my existing understanding. BRANCH_ALIGNMENT_REVIEW.md will be a complete, exhaustive PRD document meeting all requirements of a production-ready PRD with implementation-ready detail."
```
