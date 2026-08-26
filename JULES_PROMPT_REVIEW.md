# Review: Jules Message Structure for Documentation Generation

## Current Proposed Message Analysis

### Strengths
1. **Clear scope**: Specifies exactly which documents to generate (REQUIREMENTS.md, DESIGN.md)
2. **References prior work**: Explicitly cites session 596003508416904399 and scratch_branch_alignment_scaffold/
3. **Structured requirements**: Lists specific sections for each document
4. **Purpose statement**: Clarifies these are for comparison with scaffold versions

### Risks of Misinterpretation

| Risk | Current Message Issue | Potential Jules Behavior |
|------|----------------------|-------------------------|
| **Re-running analysis** | "based on your analysis from session..." | Jules might re-run branch analysis, GraphQL queries, Git history traversal |
| **Re-discovering tooling** | "Use actual findings from your branch analysis..." | Jules might re-scan branches, re-identify rogue commits, re-examine 000-* branches |
| **Re-creating state** | "actual findings from your branch analysis..." | Jules might re-backup files to future_advanced_state/ or re-examine 000-* branches |
| **Re-doing clustering** | References to engine wiring, target matrix | Jules might re-run ClusterEngine, re-generate assignments.json |

## Recommended Message Structure

### Core Principle: "DOCUMENT, DON'T REDISCOVER"

```
# DOCUMENTATION GENERATION REQUEST - ANALYSIS PHASE COMPLETE

## CONTEXT: ANALYSIS PHASE COMPLETED
You have already completed the discovery and analysis phase in session 596003508416904399.
Your work is DONE for: branch analysis, rogue work discovery, tooling location identification, 
state preservation, and next steps identification.

## DIRECTIVE: DOCUMENT ONLY - NO RE-ANALYSIS
Generate the following documents based EXCLUSIVELY on your completed analysis. 
DO NOT re-run queries, re-scan branches, re-identify rogue work, or re-examine files.

## DOCUMENTS TO GENERATE

### REQUIREMENTS.md - FORMALIZE EXISTING CONSTRAINTS
Document the hard constraints you've already identified (REQ-01 through REQ-08) and any 
additional ones from your completed analysis. Reference actual SHAs and file counts 
you've already discovered.

### DESIGN.md - DOCUMENT EXISTING ARCHITECTURE
Document the system architecture as you currently understand it from completed work.
Include actual SHAs, branch relationships, and tooling locations you've already found.
NO new investigation required.

## CRITICAL BOUNDARIES
- ❌ NO GraphQL queries, Git history traversal, or branch scanning
- ❌ NO re-examination of 000-* branches, consolidate/cli-unification, or PRs
- ❌ NO file operations on future_advanced_state/ or any repository state
- ❌ NO ClusterEngine execution, validation runs, or Linear MCP initialization
- ✅ YES: Reference findings by citing your completed work (e.g., "As discovered in 
     session 596003508416904399, the taskmaster root is 78dd10b5...")
- ✅ YES: Cite specific files, SHAs, and branch names from completed work
- ✅ YES: Structure documents for clarity and comparison with existing scaffold
```

## Improved Message Template

```markdown
Please generate canonical REQUIREMENTS.md and DESIGN.md documents documenting 
the taskmaster branch alignment work based on your COMPLETED analysis in 
session 596003508416904399.

## CRITICAL CONSTRAINT: DOCUMENT ONLY - NO RE-ANALYSIS
Your analysis phase is COMPLETE. These documents should reflect your existing 
understanding ONLY. Do NOT:
- Re-run any queries, scans, or investigations
- Re-examine branches, commits, or files
- Re-identify rogue work or tooling locations
- Execute any tools, engines, or validation
- Modify any repository state

## REQUIREMENTS.md - FORMALIZE EXISTING CONSTRAINTS
Document the hard constraints you've already identified:
- REQ-01 through REQ-08 (from your completed discovery)
- Any additional constraints from your completed analysis
- Reference actual SHAs, file counts, and branch names you've already found
- Format as numbered list with brief explanations

## DESIGN.md - DOCUMENT EXISTING ARCHITECTURE
Document your current architectural understanding from completed work:
- D-1: Start state with actual SHAs (taskmaster root 78dd10b5, HEAD 1426a01c99)
- D-2: Engine wiring with specific file references you've already located
- D-3: Target matrix with integration directions from your branch mapping
- D-4 through D-7: Signal processing, safety invariants, merge discipline from completed work
- Cite specific findings: "As discovered, only chore/cli-tooling-requirements-review 
  and feature/recover-lost-modules share taskmaster root 78dd10b5"

## PURPOSE
These documents represent your canonical understanding for comparison with 
existing scaffold versions. They must reflect ONLY completed analysis.
```

## Key Structural Principles

### 1. Explicit "Analysis Phase Complete" Declaration
- States upfront that investigation is done
- Prevents Jules from thinking it needs to "finish" the work

### 2. Negative Constraints Before Positive Instructions
- Lists what NOT to do before what TO do
- Leverages instruction-following priority patterns

### 3. Citation-Based Documentation
- Requires Jules to cite specific completed findings
- Forces document to reflect actual work, not new investigation

### 4. Purpose Framing
- Positions output as "documentation of completed work" not "next step in process"
- Aligns with user requirement: findings as reports, not triggers

### 5. Specific Citation Examples
- Provides concrete examples of how to reference completed work
- Reduces ambiguity about what constitutes "completed analysis"

## What to Avoid

| ❌ Avoid | ✅ Use Instead |
|---------|----------------|
| "based on your analysis..." | "Document the constraints you identified in session 596003508416904399" |
| "Use actual findings..." | "Cite specific SHAs and branch names from your completed discovery" |
| "Include additional requirements discovered..." | "Include any additional constraints from your completed analysis" |
| "Based on your branch analysis..." | "Reference the branch relationships you already mapped" |
| "Document the system architecture" | "Document your current architectural understanding from completed work" |

## Verification Checklist for Message Review

- [ ] Explicitly states "analysis phase complete" / "no re-analysis"
- [ ] Lists specific prohibited actions (queries, scans, executions)
- [ ] Requires citation of specific completed findings
- [ ] Provides concrete examples of expected citations
- [ ] Frames output as documentation of completed work
- [ ] Specifies document structure without implying new investigation
- [ ] Aligns with "findings as reports" requirement
- [ ] References specific session ID and completed work artifacts
