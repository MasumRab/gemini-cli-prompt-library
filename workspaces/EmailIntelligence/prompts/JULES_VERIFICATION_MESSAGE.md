# Follow-up Verification Message for Jules

---

## Verification Message to Send Once Work is Complete

```
## VERIFICATION REQUEST: Confirm All Requirements Met

Please confirm the following for each generated document:

## DOCUMENT EXISTENCE & COMPLETENESS
- [ ] REQUIREMENTS.md exists and is complete
- [ ] DESIGN.md exists and is complete
- [ ] BRANCH_ALIGNMENT_REVIEW.md exists and is complete (exhaustive PRD)

## NO RE-ANALYSIS PERFORMED
- [ ] No GraphQL queries, Git history traversal, or branch scans were re-run
- [ ] No re-examination of 000-* branches, consolidate/cli-unification, or PRs #492/#486/#679
- [ ] No re-identification of rogue work, tooling locations, or branch relationships
- [ ] No ClusterEngine, Validator, Linear MCP execution for validation/execution
- [ ] No repository state modifications (future_advanced_state/, working tree, branches)
- [ ] No new investigation, discovery, or analysis work performed

## CODE SEARCHES PERFORMED FOR IMPLEMENTATION DETAILS
- [ ] Searched cluster_branches.py, branch_clustering.py, validation_framework.py
- [ ] Searched sync scripts, task scripts, Linear/GitHub integration scripts
- [ ] Extracted exact function signatures, class definitions, method names
- [ ] Extracted CLI interfaces, argument parsing, config formats, YAML schemas
- [ ] Extracted error handling patterns, logging formats, import structures
- [ ] Referenced exact file paths, function names, class names, config keys in documents
- [ ] Used details to make documents CONCRETE and IMPLEMENTABLE

## CRITICAL STEERING CORRECTIONS INCORPORATED

### 1. Tool Consolidation → orchestration-tools
- [ ] REQUIREMENTS.md: Tool consolidation to orchestration-tools requirement present
- [ ] DESIGN.md: orchestration-tools as tool consolidation staging branch (S0)
- [ ] BRANCH_ALIGNMENT_REVIEW.md: Tool consolidation to orchestration-tools as central integration point
- [ ] NO direct extraction to taskmaster branch

### 2. Multi-Step Dynamic Evidence-Gathering Process
- [ ] REQUIREMENTS.md: Multi-step dynamic research/implementation process requirement
- [ ] DESIGN.md: Multi-step workflow engine with dynamic evidence gathering
- [ ] BRANCH_ALIGNMENT_REVIEW.md: Multi-step dynamic evidence-gathering as core workflow
- [ ] NOT a one-shot process - builds dynamically as evidence gathered

### 4. Semantic/Git Topology Analysis Tools Central to Workflow
- [ ] REQUIREMENTS.md: Semantic/git topology analysis integration requirement
- [ ] DESIGN.md: Semantic/git topology analysis pipeline integration
- [ ] BRANCH_ALIGNMENT_REVIEW.md: Semantic/git topology analysis pipeline integrated at each step
- [ ] Tools surfaced: cluster_branches.py, branch_clustering.py (BranchClusterer, BranchAnalyzer), validation_framework.py (Validator)
- [ ] Tools shown as central workflow engine with git topology + semantic analysis

### 5. Dynamic Rebase/Resolution Process
- [ ] REQUIREMENTS.md: Dynamic rebase/resolution process requirement
- [ ] DESIGN.md: Dynamic rebase/resolution feedback loop design
- [ ] BRANCH_ALIGNMENT_REVIEW.md: Dynamic rebase/resolution engine with validator-gated progression
- [ ] Feedback loops: analysis → clustering → validation → rebase/resolution → re-analyze

### 5. Commit Message + Code Change Semantic Alignment
- [ ] REQUIREMENTS.md: Commit message + code change semantic alignment requirement
- [ ] DESIGN.md: Commit message + code change semantic alignment pipeline
- [ ] BRANCH_ALIGNMENT_REVIEW.md: Commit message + code change semantic alignment at each step

### 6. Validator-Gated Iterative Progression with Linear MCP
- [ ] REQUIREMENTS.md: Validator-gated iterative workflow requirement
- [ ] DESIGN.md: Validator-gated step progression with Linear MCP traceability
- [ ] BRANCH_ALIGNMENT_REVIEW.md: Validator-gated iterative progression with Linear MCP traceability
- [ ] Feedback loops: analysis → clustering → validation → rebase/resolution → re-analyze

### 6. Tool Consolidation Target: orchestration-tools
- [ ] Tool consolidation to orchestration-tools (staging branch S0)
- [ ] orchestration-tools as staging/integration host with .taskmaster submodule pinned
- [ ] Tooling flows TO orchestration-tools, taskmaster receives via pin-bumps

### 2. Multi-Step Dynamic Evidence-Gathering Process
- [ ] Not a one-shot process - builds dynamically as evidence gathered
- [ ] Each step informs next - not a fixed plan
- [ ] Dynamic evidence-gathering workflow in BRANCH_ALIGNMENT_REVIEW.md

### 3. Semantic/Git Topology Analysis Tools Central
- [ ] cluster_branches.py, branch_clustering.py, validation_framework.py surfaced as core tools
- [ ] Git topology analysis (commit graph, ancestry) feeds clustering
- [ ] Semantic analysis (AST comparison) feeds clustering
- [ ] Commit message/code change alignment feeds validation
- [ ] Feedback loop: analysis → clustering → validation → rebase/resolution → re-analyze

### 4. Dynamic Rebase/Resolution Process
- [ ] Complex rebases, fixups, conflicts resolved DYNAMICALLY
- [ ] Rebase strategies adapt as clustering reveals relationships
- [ ] Fixup strategies adapt as semantic analysis reveals conflicts
- [ ] Resolution strategies adapt as commit message/code alignment reveals mismatches
- [ ] Validator gates at each step determine proceed/abort/adapt
- [ ] Linear MCP tracks Capability Ontology, Traceability Matrix, PR Review Validation

## DOCUMENT QUALITY CHECKS

### REQUIREMENTS.md
- [ ] Created from scratch (not copied from scaffold)
- [ ] Own requirement numbering from scratch
- [ ] Core constraints: isolation, tooling provenance, determinism, validation gating, worktree sync, PR hygiene, scope discipline, merge discipline
- [ ] Additional constraints from analysis: branch arch, tooling locations, rogue work, state preservation, Linear MCP
- [ ] Enriched with code search details: YAML schema keys, CLI structures, config formats, error types
- [ ] Own requirement numbering from scratch

### DESIGN.md
- [ ] Created from scratch (not copied from scaffold)
- [ ] Start State: branch relationships, SHAs, worktree scaffold, staging branch (orchestration-tools)
- [ ] Engine Wiring: command structure, ClusterEngine/BranchAnalyzer/Validator, outputs
- [ ] Enriched with code details: class hierarchies, method signatures, data structures, config loading
- [ ] Target Matrix: integration directions, gates, pin-bump model
- [ ] Signal Processing: weights, thresholds, clustering flow
- [ ] Enriched: similarity methods, threshold constants, assignments.json structure from code
- [ ] Safety Invariants: no-merge, .taskmaster lock, verbatim tooling, merge discipline
- [ ] Enriched: validation checks, git ops, error handling from code

### BRANCH_ALIGNMENT_REVIEW.md (COMPLETE EXHAUSTIVE PRD)
- [ ] Created from scratch - NOT a copy of scaffold
- [ ] Universal Rules (canonical version from analysis)
- [ ] Complete Step Map (S1-S10 equivalent) with goals, outcomes, quality gates, acceptance criteria
- [ ] Step-to-File Responsibility Map
- [ ] Content-Agnostic Definitions (feature branch, primary branch, stray work, alignment, clean run)
- [ ] Start/Stop Conditions
- [ ] Traceability Requirements (Linear MCP integration)
- [ ] Quality Gates (validation, acceptance, rejection criteria)
- [ ] Divergence Notes (findings vs scaffolds)
- [ ] Completeness Requirements (every req addressed, every design implemented, every step with criteria, every deliverable verifiable)
- [ ] Enriched: exact commands, file paths, validation commands, rollback procedures from code searches
- [ ] Multi-step dynamic evidence-gathering as core workflow
- [ ] Semantic/git topology analysis pipeline at each step
- [ ] Tool consolidation to orchestration-tools as central integration point
- [ ] Dynamic rebase/resolution engine with validator-gated progression
- [ ] Commit message + code change semantic alignment at each step
- [ ] Validator-gated iterative progression with Linear MCP traceability
- [ ] Feedback loops: analysis → clustering → validation → rebase/resolution → re-analyze
- [ ] Complete Step Map with dynamic evidence-gathering at each step
- [ ] Implementation-ready details from code searches for each tool's role

## NO SCAFFOLD COPYING
- [ ] No scaffold requirement numbers copied
- [ ] No scaffold design sections copied
- [ ] No scaffold formulations copied
- [ ] Scaffold used only for steering (structure, terminology, categories)

## CREATED FROM SCRATCH
- [ ] All three documents created from scratch
- [ ] Based on completed analysis and created documentation (TASKMASTER_ELUCIDATION.md, status reports, plans, elucidations)
- [ ] Enriched with code search implementation details
- [ ] No re-analysis, no re-investigation, no scaffold copying

## FILE OUTPUT
- [ ] REQUIREMENTS.md output as markdown
- [ ] DESIGN.md output as markdown
- [ ] BRANCH_ALIGNMENT_REVIEW.md output as markdown
- [ ] Suitable for direct comparison with scaffold versions

## REPORT
Please provide a summary report confirming:
1. Which documents were generated/reset
2. Which steering corrections were incorporated
3. Which code searches were performed and what details were extracted
4. Confirmation that no re-analysis was performed
5. Confirmation that documents are complete, exhaustive, and implementation-ready
6. Any divergences from scaffold noted in BRANCH_ALIGNMENT_REVIEW.md
```
