# Final Message for Jules: Generate Canonical Documentation

---

## Message to Send to Jules

```
Please generate canonical REQUIREMENTS.md, DESIGN.md, and BRANCH_ALIGNMENT_REVIEW.md documents for the taskmaster branch alignment work based on your COMPLETED analysis in session 596003508416904399.

## CRITICAL CONSTRAINT: DOCUMENT ONLY - NO RE-ANALYSIS
Your analysis phase is COMPLETE. These documents must reflect your EXISTING understanding ONLY. Do NOT:
- Re-run GraphQL queries, Git history traversal, or branch scans
- Re-examine 000-* branches, consolidate/cli-unification, or PRs #492/#486/#679
- Re-identify rogue work, tooling locations, or branch relationships
- Execute ClusterEngine, Validator, Linear MCP, or any tools
- Modify repository state (future_advanced_state/, working tree, branches)
- Perform ANY investigation, discovery, or analysis work

## COMPARISON BASE
Use scratch_branch_alignment_scaffold/PRD_BRANCH_ALIGNMENT.md as the rough scaffold comparison base. Your generated documents will be compared against it.

## DOCUMENTS TO GENERATE

### 1. REQUIREMENTS.md - FORMALIZE EXISTING CONSTRAINTS
Document the hard constraints you've ALREADY identified:
- REQ-01 through REQ-08 from your completed discovery
- Any additional constraints from your COMPLETED analysis
- Reference SPECIFIC findings by citing:
  - Taskmaster root: 78dd10b5, HEAD: 1426a01c99
  - Branches sharing root: chore/cli-tooling-requirements-review-8803610982851555196, feature/recover-lost-modules
  - Rogue work: 57 commits across PRs #492, #486, etc.
  - Tooling location: consolidate/cli-unification (cluster_branches.py, branch_clustering.py, validation_framework.py)
  - State backup: ~300+ files moved to future_advanced_state/
- Format as numbered list with brief explanations
- NO new requirements from new investigation

### 2. DESIGN.md - DOCUMENT EXISTING ARCHITECTURE
Document your CURRENT architectural understanding from COMPLETED work:
- D-1: Start state with ACTUAL SHAs (root 78dd10b5, HEAD: 1426a01c99)
- D-2: Engine wiring with SPECIFIC file refs you've LOCATED (cluster_branches.py, branch_clustering.py a899049affa, validation_framework.py 2aa026fab)
- D-3: Target matrix with INTEGRATION DIRECTIONS from your branch mapping
- D-4 through D-7: Signal weights (0.35/0.35/0.30, threshold 0.25), safety invariants (I-1 through I-7), merge discipline from COMPLETED work
- Cite SPECIFIC findings: "As discovered in session 596003508416904399, only chore/cli-tooling-requirements-review-8803610982851555196 and feature/recover-lost-modules share taskmaster root 78dd10b5"
- NO new architecture from new investigation

### 3. BRANCH_ALIGNMENT_REVIEW.md - YOUR VERSION OF PRD_BRANCH_ALIGNMENT.md
Generate your own version of the branch alignment PRD based on your completed analysis, using scratch_branch_alignment_scaffold/PRD_BRANCH_ALIGNMENT.md as the rough scaffold comparison base. This document should:

- Reflect your canonical understanding of the branch alignment task specification
- Include your version of the universal rules (R0.1-R0.6), step map (S1-S10), and step-to-file responsibility map
- Incorporate your actual findings: discovered SHAs, branch relationships, tooling locations, state backup details
- Use the same structural sections as the scaffold but populated with your verified findings
- Note any divergences from the scaffold where your analysis revealed different realities
- Serve as your canonical branch alignment task specification for comparison with the rough scaffold

## PURPOSE
These three documents represent your CANONICAL understanding for comparison with scaffold versions in scratch_branch_alignment_scaffold/. They MUST reflect ONLY your COMPLETED analysis. Output as markdown files suitable for direct comparison.

## VERIFICATION
Before generating, confirm: "I am documenting completed analysis from session 596003508416904399 only. No new investigation will be performed. I will generate REQUIREMENTS.md, DESIGN.md, and BRANCH_ALIGNMENT_REVIEW.md based solely on my completed analysis."
```

---

## Usage

```bash
# Send to the completed session (we can message completed sessions)
python tools/sessions/jules_send_message.py 596003508416904399 "$(cat JULES_FINAL_MESSAGE.md)"
```
