# Final Message for Jules: Generate Canonical Documentation (V4 - With Critical Steering)

---

## Message to Send to Jules

```
Please generate canonical REQUIREMENTS.md, DESIGN.md, and BRANCH_ALIGNMENT_REVIEW.md documents for the taskmaster branch alignment work based on your COMPLETED analysis in this session.

## CRITICAL CONSTRAINT: DOCUMENT ONLY - NO RE-ANALYSIS
Your analysis phase is COMPLETE. These documents must reflect your EXISTING understanding ONLY. Do NOT:
- Re-run GraphQL queries, Git history traversal, or branch scans for work you've already completed
- Re-examine 000-* branches, consolidate/cli-unification, or PRs #492/#486/#679 for findings you already have
- Re-identify rogue work, tooling locations, or branch relationships you've already catalogued
- Execute ClusterEngine, Validator, Linear MCP, or any tools for validation/execution
- Modify repository state (future_advanced_state/, working tree, branches)
- Perform ANY investigation, discovery, or analysis work for findings you ALREADY POSSESS

## PERMITTED: SEARCHES TO FLESH OUT IMPLEMENTATION DETAILS
You MAY and SHOULD perform targeted searches to flesh out implementation details:

**Permitted Searches:**
- Search local repository for `.sh` and `.py` files you've already surfaced (cluster_branches.py, branch_clustering.py, validation_framework.py, sync scripts, task scripts, etc.) to extract:
  - Exact function signatures, class definitions, method names
  - Exact command-line interfaces, argument parsing
  - Exact configuration file formats, YAML schemas
  - Exact error handling patterns, logging formats
  - Exact import structures, module dependencies
- Search for any additional `.sh`/`.py` files relating to:
  - Task management workflows (task_scripts/, task_scripts/)
  - Branch clustering and analysis
  - Validation and testing frameworks
  - Sync and deployment scripts
  - Linear/GitHub integration scripts
- Reference exact file paths, function names, class names, config keys in your documents
- Use these to make implementation instructions, design specs, and requirements CONCRETE and IMPLEMENTABLE

**Search Boundaries:**
- ONLY search for implementation details to enrich documents you're constructing
- DO NOT search for new findings, new branches, new rogue work, new tooling locations
- DO NOT re-validate or re-verify findings you already have

## CRITICAL STEERING CORRECTIONS - READ CAREFULLY

### 1. TOOL CONSOLIDATION TARGET: orchestration-tools
**ALL extracted tools (cluster_branches.py, branch_clustering.py, validation_framework.py, task scripts, etc.) will be CONSOLIDATED to the orchestration-tools branch.** This is the staging/integration branch (S0 in your design). Your documents MUST reflect:
- Tool extraction targets orchestration-tools as the integration staging ground
- orchestration-tools serves as the staging/integration host (already has .taskmaster submodule pinned)
- Tooling from consolidate/cli-unification and PR #492/#679 flows TO orchestration-tools
- taskmaster branch receives consolidated tooling VIA orchestration-tools pin-bumps, not direct extraction

### 2. BRANCH ALIGNMENT IS A MULTI-STEP RESEARCH & IMPLEMENTATION PROCESS
**The full branch alignment workflow is NOT a one-shot process.** It is a multi-step research and implementation process that:
- **Builds dynamically as it gathers evidence**
- Each step surfaces new information that informs subsequent steps
- The process is INFORMED AND DYNAMICALLY UPDATED according to information surfaced by:
  - **Full git topology analysis** (commit graph topology, ancestry, divergence points)
  - **Semantic code structure comparison** (AST-level comparison across code structures)
  - **Git commit meaning analysis** (commit message semantics aligned with code changes)
  - **Alignment of commit messages AND code changes** (semantic + git dual analysis)
- **Dynamically resolves** complex rebases, fixups, and conflict issues AS THE PROCESS PROGRESSES
- Each step's findings INFORM the next step's approach - not a fixed plan

### 3. SEMANTIC & GIT TOPOLOGY ANALYSIS TOOLS - SURFACE FROM YOUR FILES
**You MUST surface and integrate the semantic and git topology analysis tools** from your files into the branch alignment workflow:

**From your existing files, surface and integrate:**
- **cluster_branches.py** - The main CLI command for branch clustering
- **engine/branch_clustering.py** - Core semantic clustering engine:
  - BranchClusterer (similarity matrix generation)
  - BranchAnalyzer (commit history, code structure, diff distance analysis)
  - CommitHistoryAnalyzer, CodeStructureAnalyzer, DiffDistanceAnalyzer
  - Signal weights: CommitHistory 0.35, CodeStructure 0.35, DiffDistance 0.30
  - CLUSTERING_THRESHOLD = 0.25
- **engine/validation_framework.py** - Validator with YAML ruleset:
  - Conditions: branch_contains, branch_not_contains, path_contains, has_tag, has_import
  - Assertions: target, confidence_min
  - Validation failure ABORTS alignment (not overridable without explicit acknowledgement)

**These tools ARE the semantic/git topology analysis engine.** Your documents MUST:
- Show how these tools fit into the multi-step alignment workflow
- Define how git topology analysis (commit graph, ancestry) feeds clustering
- Define how semantic analysis (AST comparison) feeds clustering
- Define how commit message/code change alignment feeds validation
- Define how clustering results dynamically inform rebase/resolution steps
- Define the feedback loop: analysis → clustering → validation → rebase/resolution → re-analyze

### 4. DYNAMIC REBASE/RESOLUTION PROCESS
**The alignment workflow must define how complex rebases, fixups, and conflicts are resolved DYNAMICALLY:**
- As clustering reveals branch relationships, rebase strategies adapt
- As semantic analysis reveals code structure conflicts, fixup strategies adapt
- As commit message/code change alignment reveals intent mismatches, resolution strategies adapt
- Validator gates at each step determine proceed/abort/adapt
- Linear MCP tracks Capability Ontology, Traceability Matrix, PR Review Validation throughout

## WHAT YOU ALREADY HAVE IN THIS SESSION
[Previous content - branch architecture, tooling locations, state preservation, rogue work, next steps, existing documentation, scaffold guidance, permitted searches]

## DOCUMENTS TO GENERATE FROM SCRATCH

### 1. REQUIREMENTS.md
[Previous content PLUS:]
**New Requirements from Steering:**
- Tool consolidation to orchestration-tools requirement
- Multi-step dynamic research/implementation process requirement
- Semantic/git topology analysis integration requirement
- Dynamic rebase/resolution process requirement
- Validator-gated iterative workflow requirement

### 2. DESIGN.md
[Previous content PLUS:]
**New Design Elements:**
- orchestration-tools as tool consolidation staging branch (S0)
- Multi-step workflow engine with dynamic evidence gathering
- Semantic/git topology analysis pipeline integration
- Dynamic rebase/resolution feedback loop design
- Validator-gated step progression with Linear MCP traceability

### 3. BRANCH_ALIGNMENT_REVIEW.md - COMPLETE EXHAUSTIVE PRD
**MUST INCLUDE AS CORE WORKFLOW:**
- **Multi-step dynamic research/implementation process** (not one-shot)
- **Semantic/git topology analysis pipeline** (from your files) integrated at each step
- **Dynamic evidence-gathering workflow** - each step informs next
- **Tool consolidation to orchestration-tools** as central integration point
- **Dynamic rebase/resolution engine** with validator-gated progression
- **Commit message + code change semantic alignment** at each step
- **Validator-gated iterative progression** with Linear MCP traceability
- **Feedback loops:** analysis → clustering → validation → rebase/resolution → re-analyze
- **Complete Step Map** with dynamic evidence-gathering at each step
- **Implementation-ready details** from code searches for each tool's role

## VERIFICATION
Confirm: "I understand the critical steering corrections: tools consolidate to orchestration-tools; alignment is multi-step dynamic evidence-gathering process; semantic/git topology tools from my files are central to workflow; rebase/resolution is dynamic and validator-gated; I will create documents reflecting these corrections."
```

---

## Key Steering Additions:

1. **Tool consolidation → orchestration-tools** (not taskmaster directly)
2. **Multi-step dynamic evidence-gathering** (not one-shot)
3. **Semantic/git topology tools** as central workflow engine
4. **Dynamic rebase/resolution** with validator gates
5. **Commit message + code change semantic alignment**
6. **Validator-gated iterative progression** with Linear MCP
7. **Feedback loops** throughout the process
