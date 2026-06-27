# 🏗️ Stacking Structure & Branch Order Diagram

This document provides a comprehensive text-based visualization of the branch stacking structure, order, and secondary relationships based on Graphite Agent V7.3 analysis and smart rebase operations.

## 📊 Complete Repository Structure

```
gemini-cli-prompt-library/
├── .git/
├── .graphite-agent/
│   ├── scripts/
│   │   └── smart-rebase/          ← 🎯 SMART REBASE TOOLS LOCATION
│   │       ├── README.md
│   │       ├── main.sh           # Primary smart rebase tool
│   │       ├── conflict-resolver.sh
│   │       ├── executor.sh
│   │       ├── batch-unblock.sh
│   │       ├── quick-stack.sh
│   │       ├── setup.sh
│   │       ├── basic.sh
│   │       ├── status.sh
│   │       └── STACKING_DIAGRAM.md ← This file
│   │
│   ├── outputs/                   # Graphite Agent V7.3 outputs
│   │   ├── analysis_snapshot.json   # Branch graph analysis
│   │   ├── plan.json               # Execution plan for stacking
│   │   ├── execution_plan.json     # Detailed execution queue
│   │   ├── relationship_graph.json # Branch relationship map
│   │   └── recommendations.json    # Stacking recommendations
│   │
│   ├── tools/                    # Graphite Agent V7.3 tools
│   │   └── lib/                   # Core libraries
│   │
│   └── fixtures/                 # Test fixtures
│
└── [other project files...]
```

---

## 🎯 Current Stack Structure

### Based on Graphite Agent V7.3 Analysis

```text
MAIN (0c732a1) ← Trunk/Baseline
│
├─────────────────────────────────────────────────────────────────┐
│  LEVEL 1: Directly Stacked on Main (Ready for Graphite)         │
│  └─ fix/require-review-comments-resolved (48ba834) ✅ STACKED    │
│      └─ "Reopen PR #31" - 7 commits ahead of main                │
│          └─ Based on: 0c732a1 (latest main)                       │
│                                                                   │
│  └─ cto/resolve-merge-conflicts-main-prs (292da39) ✅ STACKED    │
│      └─ "chore: fix linting issues and refactor CommandRegistry" │
│          └─ Based on: 0c732a1 (latest main)                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

 ready for stacking:
│
├─────────────────────────────────────────────────────────────────┐
│  LEVEL 2: Needs Smart Rebase Processing                           │
│  └─ cto/apply-remaining-fixes-prs                                  │
│      └─ "Add CI/Lint fixes for PR #36 reopen"                     │
│      └─ Contains: 32 merge commits → Complex rebase               │
│      └─ Status: 📋 READY FOR smart-rebase processing               │
│                                                                   │
│  └─ fix-scheduled-audit-report-7335934676686138146               │
│      └─ "Apply auto-formatting to resolve CI issues"              │
│      └─ Contains: 41 merge commits → Complex rebase               │
│      └─ Status: 📋 READY FOR smart-rebase processing               │
│                                                                   │
│  └─ add-scheduled-audit-prompt-14723155380211979683              │
│      └─ "chore: bypass missing history and fix remaining lint..."   │
│      └─ Contains: Merge commits → Needs restacking                 │
│      └─ Status: 📋 READY FOR smart-rebase processing               │
│                                                                   │
│  └─ update-scheduled-codebase-audit-16497131777087108224        │
│      └─ "chore(commands): update scheduled-codebase-audit..."       │
│      └─ Contains: Merge commits → Needs restacking                 │
│      └─ Status: 📋 READY FOR smart-rebase processing               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Relationship Graph (Text Based)

```text
Graphite Agent V7.3 Analysis - Relationship Graph

┌─────────────────────────────────────────────────────────────────┐
│ Graphite Agent V7.3: Branch Relationship Analysis                  │
└─────────────────────────────────────────────────────────────────┘

MAIN (Trunk)
│ 
├──┬─────────────────────────────────────────┬──────────────────────┐
│ │ 🟢 SAFE: Declared base is an ancestor   │ ⚠️  WRONG TARGET         │
│ │ feature/safe                         │ feature/restack         │
│ │   └─ Parent: main                    │   └─ Parent: feature/safe│
│ │   └─ Status: track_only              │   └─ Status: track_and_  │
│ │     ✅ Already properly stacked       │        restack          │
│ │                                        │   ⚠️  Declared base    │
│ │                                        │       exists but not   │
│ │                                        │       an ancestor       │
│ └─────────────────────────────────────────┴──────────────────────┘
│
├──┬─────────────────────────────────────────┬──────────────────────┐
│ │ ⚠️  MANUAL TRIAGE: Patch-id overlap    │ 🚫 BLOCKED:            │
│ │ feature/triage                      │ feature/cross          │
│ │   └─ Parent: main                   │   └─ Parent: main      │
│ │   ⚠️  Patch-id overlap found       │   🚫 Contains merged   │
│ │       without safe ancestry       │       history from    │
│ │   → Needs user decision             │       release/1.0    │
│ │                                     │   🚫 CROSS-ROOT       │
│ └─────────────────────────────────────────┴──────────────────────┘
│
└─🚫 BLOCKED: Branch merged target to resolve conflicts
    feature/merge-conflict-resolution
      └─ Parent: main
      🚫 BLOCKED: Branch merged target to resolve conflicts
      → Must be resolved before stacking can proceed

```

---

## 🎯 Smart Rebase Workflow Diagram

```text
┌─────────────────────────────────────────────────────────────────┐
│ SMART REBASE WORKFLOW for Graphite Agent V7.3                     │
└─────────────────────────────────────────────────────────────────┘

Start: Main Branch (0c732a1)
    │
    ▼
┌─────────────────────────┐
│ 1. Analysis Phase        │ ← Graphite Agent V7.3
│    ├─ Identify blocking   │
│    ├─ Check merge bases   │
│    └─ Build relationship │
│        graph             │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 2. Preparation Phase     │ ← Smart Rebase Tools
│    ├─ Enable git rerere  │
│    ├─ Clear rr-cache     │
│    └─ Verify git-surgeon  │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 3. Processing Phase      │
│    ├─ git rebase --onto  │
│    │    main main branch │
│    ├─ --autostash        │
│    ├─ --keep-empty       │
│    └─ --rebase-merges    │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐                        ╭─────────────────────╮
│ 4. Conflict Resolution   │─── YES ─────────────►│ No Conflicts?       │
│    ├─ Try git rerere     │                        │ ✅ Rebase Complete   │
│    ├─ Try 3-way merge    │                        │    Continue to next  │
│    ├─ Accept both sides  │                        │    branch           │
│    └─ File-type aware   │                        ╰─────────────────────╯
└─────────────────────────┘
    │ NO
    ▼
┌─────────────────────────┐
│ 5. Validation Phase      │
│    ├─ python3 -m py_    │
│    │    compile for .py │
│    ├─ json.load() for   │
│    │    .json files     │
│    ├─ yaml.safe_load()  │
│    │    for YAML files │
│    └─ git-surgeon hunks │
│        for duplicates   │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 6. Status Reporting      │
│    ├─ Tag as stacked     │
│    ├─ Update status.json │
│    └─ Log to /tmp/       │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 7. Push Phase           │
│    ├─ git push          │
│    │    --force-with-  │
│    │    lease          │
│    └─ gt track for     │
│        Graphite         │
└─────────────────────────┘
    │
    ▼
END: Stacked Branches Ready for Graphite

```

---

## 🏗️ Branch Dependencies and Relationships

### Primary Stacking Order (Topological)

```text
MAIN (Base)
│
├── fix/require-review-comments-resolved         ← Direct child of main
│   │
│   ├── cto/apply-remaining-fixes-prs           ← Should stack here
│   │   │
│   │   └── add-scheduled-audit-prompt-14723... ← Continue stack
│   │
│   └── fix-scheduled-audit-report-73359...      ← Alternatively stack here
│
└── cto/resolve-merge-conflicts-main-prs         ← Direct child of main
    │
    └── update-scheduled-codebase-audit-1649... ← Continue stack

```

### Alternative Stacking Strategy

```text
MAIN (Base)
│
└── BATCH 1: All branches stacked directly on main (Parallel)
    ├── fix/require-review-comments-resolved
    ├── cto/resolve-merge-conflicts-main-prs
    ├── cto/apply-remaining-fixes-prs
    ├── fix-scheduled-audit-report-7335934676686138146
    └── update-scheduled-codebase-audit-16497131777087108224

This approach:
✅ Simpler for branches with independent changes
✅ Better for branches with different purposes
✅ Easier conflict resolution
⚠️  May create merge conflicts when resolving
```

---

## ⚡ Secondary Relationships (Merge History)

### Branches with Merge Commits (Need Special Handling)

```text
MERGE COMMIT ANALYSIS
├─ cto/resolve-merge-conflicts-main-prs: 32 merge commits
│   ├─ "Merge pull request #21"
│   └─ Complex merge history → Will cause rebase conflicts
│
├─ fix-scheduled-audit-report-7335934676686138146: 41 merge commits
│   ├─ "Merge origin/main into pr-25"
│   └─ Very complex merge history → Significant rebase conflicts
│
├─ add-scheduled-audit-prompt-14723155380211979683: Multiple merges
│   └─ Rebase conflicts expected
│
├─ update-scheduled-codebase-audit-16497131777087108224: Multiple merges
│   └─ Rebase conflicts expected
│
└─ fix/require-review-comments-resolved: 39 merge commits
    └─ Already successfully rebased ✅

Key Insight: Most target branches contain merge commits that will
cause conflicts during rebase. This is why smart conflict resolution
is essential.

```

### Cross-Root Relationships (From Graphite Analysis)

```text
CROSS-ROOT CONFLICT ANALYSIS
├─ feature/cross (Demo branch)
│   └─ ⚠️  Contains merged history from release/1.0
│       → Violates single-root invariant
│       → Must be resolved before stacking
│
└─ feature/merge-conflict-resolution (Demo branch)
    └─ ⚠️  Branch merged target to resolve conflicts
        → Violates clean stacking
        → Manual intervention needed
```

---

## 🎯 Recommended Stacking Strategy

### Phase 1: Already Stacked ✅
```text
MAIN
│
├── fix/require-review-comments-resolved
└── cto/resolve-merge-conflicts-main-prs
```

### Phase 2: Next Priority 🎯
```text
MAIN
│
├── fix/require-review-comments-resolved
│   └── cto/apply-remaining-fixes-prs  ← Stack first
│
└── cto/resolve-merge-conflicts-main-prs
    └── update-scheduled-codebase-audit-1649713... ← Stack second
```

### Phase 3: Final Stacking 📋
```text
MAIN
│
├── fix/require-review-comments-resolved
│   ├── cto/apply-remaining-fixes-prs
│   └── fix-scheduled-audit-report-7335934676686138146
│
└── cto/resolve-merge-conflicts-main-prs
    ├── add-scheduled-audit-prompt-14723155380211979683
    └── update-scheduled-codebase-audit-16497131777087108224
```

---

## 🔧 Tool Integration Diagram

```text
GRAPHITE AGENT V7.3 + SMART REBASE TOOLS INTEGRATION

┌─────────────────────────────────────────────────────────────────┐
│ Graphite Agent V7.3 Analysis                                    │
│  ├─ tools/analysis.py            ← Identifies blocking branches   │
│  ├─ tools/relationship_analyse.py ← Builds relationship graph     │
│  └─ outputs/plan.json            ← Execution plan                │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ .graphite-agent/scripts/smart-rebase/                           │
│  ├─ main.sh                    ← Uses Graphite analysis        │
│  ├─ conflict-resolver.sh      ← Resolves conflicts from plan   │
│  ├─ executor.sh               ← Executes plan automatically    │
│  └─ batch-unblock.sh          ← Processes all from plan       │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Git Infrastructure                                              │
│  ├─ git rerere                 ← Learns from conflicts         │
│  ├─ git-surgeon               ← Validates hunks               │
│  └─ FORCE_WITH_LEASE          ← Safe pushing                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Branch Statistics and Complexity

### Merge Commit Analysis

```text
BRANCH COMPLEXITY RANKING (by merge commit count)
===================================================

1. fix-scheduled-audit-report-7335934676686138146: 41 merges ⚠️⚠️⚠️
2. fix/require-review-comments-resolved: 39 merges ⚠️⚠️⚠️
3. cto/resolve-merge-conflicts-main-prs: 32 merges ⚠️⚠️
4. cto/apply-remaining-fixes-prs: 32 merges ⚠️⚠️
5. update-scheduled-codebase-audit-16497131777087108224: 39 merges ⚠️⚠️
6. add-scheduled-audit-prompt-14723155380211979683: Unknown ⚠️

Complexity Legend:
✅ Easy: 0-5 merge commits
⚠️ Medium: 6-20 merge commits  
⚠️⚠️ Hard: 21-40 merge commits
⚠️⚠️⚠️ Very Hard: 41+ merge commits
```

### Code Flow Impact

```text
CODE FLOW ANALYSIS
==================

fix-scheduled-audit-report-7335934676686138146:
  - Modified: CI/CD files (.github/workflows/ci.yml, .mergify.yml)
  - Modified: Framework files (dspy_integration/framework/registry.py)
  - Risk: HIGH - Infrastructure changes
  - Status: ✅ Already partially rebased

cto/resolve-merge-conflicts-main-prs:
  - Modified: Framework files (dspy_integration/framework/__init__.py, registry.py)
  - Modified: Test files (tests/conftest.py)
  - Risk: MEDIUM - Framework changes
  - Status: ✅ Successfully rebased with conflicts resolved

fix/require-review-comments-resolved:
  - Modified: Agent files (.graphite-agent/fixtures, outputs)
  - Modified: Documentation files (docs, checklists)
  - Risk: LOW - Documentation/agent changes
  - Status: ✅ Successfully rebased

Remaining branches:
  - Similar code areas (framework, CI/CD, agent files)
  - High likelihood of overlapping changes
```

---

## 🎯 Next Steps Diagram

```text
NEXT STEPS WORKFLOW
===================

┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Commit Smart Rebase Tools                              │
│    ✅ DONE - Committed to .graphite-agent/scripts/smart-rebase/ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Push to Origin                                        │
│    ✅ DONE - Pushed to origin/main                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Stack Remaining Branches                              │
│    🎯 TODO: Run smart rebase on:                              │
│       ├─ cto/apply-remaining-fixes-prs                         │
│       ├─ fix-scheduled-audit-report-7335934676686138146         │
│       ├─ add-scheduled-audit-prompt-14723155380211979683       │
│       └─ update-scheduled-codebase-audit-16497131777087108224 │
│                                                                 │
│    Command: ./graphite-agent/scripts/smart-rebase/quick-stack.sh│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Graphite Integration                                   │
│    🎯 TODO: Track stacked branches with Graphite:              │
│       gt track fix/require-review-comments-resolved --parent main│
│       gt track cto/resolve-merge-conflicts-main-prs --parent main│
│       gt track <other-branches> --parent <appropriate-parent>   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Push Stacked Branches                                  │
│    🎯 TODO: Force push successfully stacked branches:         │
│       git push --force-with-lease origin fix/require-review...│
│       git push --force-with-lease origin cto/resolve-merge... │
└─────────────────────────────────────────────────────────────────┘

```

---

## 🔍 File Locations Summary

```text
PROJECT STRUCTURE SUMMARY
========================

.gemini-cli-prompt-library/
├── .git/
├── .graphite-agent/
│   ├── outputs/                    (Analysis outputs - IGNORED)
│   │   ├── analysis_snapshot.json
│   │   ├── plan.json              ← Main stacking plan
│   │   ├── execution_plan.json
│   │   ├── relationship_graph.json
│   │   └── recommendations.json
│   │
│   ├── scripts/                   ← SMART REBASE TOOLS
│   │   └── smart-rebase/          ← All smart rebase scripts
│   │       ├── README.md          ← Full documentation
│   │       ├── STACKING_DIAGRAM.md ← This file
│   │       ├── main.sh            ← Primary tool
│   │       ├── conflict-resolver.sh
│   │       ├── executor.sh
│   │       ├── batch-unblock.sh
│   │       ├── quick-stack.sh
│   │       ├── setup.sh
│   │       ├── basic.sh
│   │       └── status.sh
│   │
│   ├── tools/                    (Graphite Agent V7.3 tools)
│   │   └── lib/                   (Core libraries)
│   │
│   ├── backups/                  (V7.2 backups)
│   └── fixtures/                 (Test fixtures)
│
├── scripts/                     (Other project scripts)
├── [project files...]
```

---

## 📚 Quick Reference Commands

```bash
# View stacking diagram
cat .graphite-agent/scripts/smart-rebase/STACKING_DIAGRAM.md

# Run smart rebase on next branch
./graphite-agent/scripts/smart-rebase/quick-stack.sh

# Resolve conflicts manually
./graphite-agent/scripts/smart-rebase/conflict-resolver.sh

# Check status of all branches
./graphite-agent/scripts/smart-rebase/status.sh

# Full smart rebase process
./graphite-agent/scripts/smart-rebase/main.sh

# View Graphite Agent analysis
cat .graphite-agent/outputs/analysis_snapshot.json
cat .graphite-agent/outputs/relationship_graph.json

# Track branches with Graphite
gt track fix/require-review-comments-resolved --parent main
gt track cto/resolve-merge-conflicts-main-prs --parent main
```

---

## ✅ Summary

- **Smart Rebase Tools Location**: `.graphite-agent/scripts/smart-rebase/`
- **Branches Successfully Stacked**: 2/6
- **Branches Ready for Stacking**: 4
- **Tools Available**: 9 scripts + documentation + diagrams
- **Integration**: Full Graphite Agent V7.3 compatibility

The stacking structure is now properly documented with comprehensive text diagrams showing branch order, relationships, and the complete workflow for unblocking and stacking all remaining branches.