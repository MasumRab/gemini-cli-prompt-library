# Next Session Analysis Prompt - Taskmaster Branch Alignment

## Session Focus: ANALYSIS AND DOCUMENTATION ONLY

**Constraint**: This session must produce reports and analysis findings ONLY.
No actual file modifications, extractions, engine runs, validations, or session creations are permitted.
All work product must be in the form of analyzable reports suitable for review.

## Analysis Areas Based on Session 596003508416904399 Findings

### 1. Tooling Extraction Readiness Analysis

**Objective**: Document what needs to be extracted to satisfy REQ-02 and PRD S5
**Deliverable**: Tooling Extraction Readiness Report
**Analysis Points**:

- List exact files needed from PR #492: `src/cli/commands/task/cluster_branches.py`, `src/cli/commands/task/engine/branch_clustering.py`, `src/cli/commands/task/engine/validation_framework.py`
- List exact files needed from PR #679: `cli_tooling_requirements_review.md`
- Document source SHAs for verification (from `consolidate/cli-unification` branch)
- Describe byte-identical verification methodology
- Reference PRD S5: "Tooling is moved verbatim, never edited"
- **DO NOT PERFORM EXTRACTION** - only document what would be needed

### 2. Clustering Engine Preparedness Analysis

**Objective**: Document requirements for running ClusterEngine to generate assignments.json (PRD S3)
**Deliverable**: Clustering Engine Preparedness Report
**Analysis Points**:

- Document exact command structure: `taskmaster branch-cluster --primary origin/main --mode hybrid --output worktrees/taskmaster/output/assignments.json --validate .taskmaster/clustering_rules.yaml`
- Reference required inputs from extraction analysis (cluster_branches.py, engine/branch_clustering.py, validation_framework.py)
- Document expected outputs: assignments.json, clustering_report.tsv, validation_report.md
- Reference DESIGN.md D-2 engine wiring diagram
- Reference PRD S3: "Turn inventory into validated per-branch targets"
- **DO NOT RUN ENGINE** - only document the process and requirements

### 3. Validation Framework Requirements Analysis

**Objective**: Document validation requirements for PRD S8
**Deliverable**: Validation Framework Requirements Report
**Analysis Points**:

- Document clustering_rules.yaml schema requirements
- Reference Validator conditions: `branch_contains`, `branch_not_contains`, `path_contains`, `has_tag`, `has_import`
- Document assertions: `target`, `confidence_min`
- Reference PRD S8: "Prove stability; record requirement→issue→commit→review chain"
- Document how Linear MCP would be initialized for:
  - Capability Ontology tracking
  - Traceability Matrix recording
  - PR Review Validation monitoring
- Reference status report's "NEXT STEP": "initialize Linear MCP to track the Capability Ontology, Traceability Matrix, and PR Review Validation"
- **DO NOT INITIALIZE LINEAR MCP OR RUN VALIDATION** - only document requirements

### 4. Branch Mapping Analysis

**Objective**: Document branch targets based on session findings
**Deliverable**: Branch Mapping Analysis Report
**Analysis Points**:

- Document branches identified in status report:
  - `chore/cli-tooling-requirements-review-8803610982851555196` (shares taskmaster root)
  - `feature/recover-lost-modules` (shares taskmaster root)
  - Rogue work in `main`-rooted branches (PR #492, #486, etc.)
- Reference status report Section 2: "BRANCH ANCESTRY INVESTIGATION"
- Reference status report Section 3: "ROGUE TASKMASTER WORK DISCOVERY"
- Reference status report Section 4: "000-\* / SPECKIT BRANCH INVESTIGATION"
- Map to DESIGN.md D-3 target matrix integration directions and gates
- Document which branches would be considered non-primary vs primary per PRD definitions
- **DO NOT CREATE TASK FILES OR ASSIGNMENTS** - only document the mapping

### 5. Quarantined State Assessment Analysis

**Objective**: Document restoration decisions for future_advanced_state/ (PRD S9)
**Deliverable**: Quarantined State Assessment Report
**Analysis Points**:

- Document what was backed up per status report Section 6 and 11:
  - `tasks/`, `task_scripts/`, `.taskmaster/`, `docs/`, `scripts/`, `templates/`
- Reference REQ-07: "Restoring future_advanced_state/ must restore only genuinely task-system paths"
- Reference PRD S9: "Bring back ONLY task-system paths; leave over-reach quarantined"
- Reference PRD S9 rejection criteria: "Reject if restored count ≠ canonical task-system set; reject if docs/scripts/archive re-enter tree"
- Document what constitutes "genuinely task-system paths" vs over-reach
- Reference status report Section 6: "File Count: ~300+ files moved successfully"
- Document the restoration decision process and criteria
- **DO NOT RESTORE OR MODIFY ANY FILES** - only document the assessment

### 6. Synthesis Report Generation

**Objective**: Produce comprehensive analysis report
**Deliverable**: Taskmaster Branch Alignment Analysis Report
**Report Contents**:

- Executive Summary of session 596003508416904399 findings vs requirements/design/PRD
- Detailed findings from each of the 5 analysis areas above
- Risk assessment and mitigation strategies for implementation
- Verification checklist for future implementation sessions
- Recommended sequence of steps based on PRD step map
- Open questions and areas needing clarification
- **THIS REPORT IS THE ONLY WORK PRODUCT** - no files modified, no sessions created

## Implementation Constraints for This Session

- **Analysis Only Mode**: Zero file modifications, zero extractions, zero command executions
- **Report Generation Focus**: All output must be in the form of readable/analyzable documents
- **Reference Existing Documents**: Cite REQUIREMENTS.md, DESIGN.md, PRD_BRANCH_ALIGNMENT.md, and session status report
- **Future Action Orientation**: Prepare findings that can inform actual implementation sessions
- **Quality Gate**: Report must be suitable for presentation and decision-making without triggering unintended actions

## Success Criteria for This Session

- [ ] Produces comprehensive analysis report covering all 5 areas
- [ ] Makes zero modifications to repository state
- [ ] References all source documents accurately
- [ ] Provides clear foundation for future implementation work
- [ ] Aligns with user requirement: findings as reports, not triggers for code changes/session creation

---

_This prompt designed for session following 596003508416904399_
_Based on findings from session status report and requirements/design/PRD documents_
_Constraints: Analysis-only session producing report work product only_
