# Update Message for Jules: Extended Guidance with Critical Steering

---

## Update Message to Send to Jules

```
## UPDATE: Extended Guidance with Critical Steering Corrections

This message extends your current documentation generation task. Do NOT restart or interrupt your current process. Instead, incorporate these critical steering corrections into your ongoing work and RESET/RECREATE any files (REQUIREMENTS.md, DESIGN.md, BRANCH_ALIGNMENT_REVIEW.md) that were created under the initial instructions if they do not meet these updated guidelines.

## CRITICAL STEERING CORRECTIONS - INCORPORATE IMMEDIATELY

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

## ACTION REQUIRED
1. **Continue your current document generation** - do not stop
2. **RESET/RECREATE** REQUIREMENTS.md, DESIGN.md, BRANCH_ALIGNMENT_REVIEW.md if they don't incorporate these steering corrections
2. **INCORPORATE THESE STEERING CORRECTIONS** into all three documents:
   - Tool consolidation → orchestration-tools (not taskmaster directly)
   - Multi-step dynamic evidence-gathering process (not one-shot)
   - Semantic/git topology tools as central workflow engine
   - Dynamic rebase/resolution with validator gates
   - Commit message + code change semantic alignment
   - Validator-gated iterative progression with Linear MCP
   - Feedback loops: analysis → clustering → validation → rebase/resolution → re-analyze
4. **RESET/RECREATE any files** created under initial instructions that don't meet these guidelines
5. **CONTINUE** - do not interrupt your current process

## VERIFICATION
Confirm: "I have incorporated the critical steering corrections: tools consolidate to orchestration-tools; alignment is multi-step dynamic evidence-gathering; semantic/git topology tools are central to workflow; rebase/resolution is dynamic and validator-gated; commit message + code change semantic alignment is required; I am resetting/recreating any non-compliant files and continuing."
```

---

## Usage

```bash
python tools/sessions/jules_send_message.py 596003508416904399 "$(cat JULES_UPDATE_MESSAGE.md)"
```
