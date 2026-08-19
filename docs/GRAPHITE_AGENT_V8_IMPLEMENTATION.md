# V8 Graphite Agent Implementation: Per-ZIP Folder Mapping

## Overview
This document maps each Graphite Agent V8 zip version to repository branches, using **verifiable** branch contents. All module counts and presence/fidelity metrics below were re-verified via `git ls-tree` after earlier mistakes were corrected.

## Branch Fidelity Scores (V8 Focus - VERIFIED)

| Branch | lib modules | Has semantic stack? | Notes |
|--------|------------|---------------------|-------|
| `v8-surgical-integration` | **37** | ✅ (7+ funcs in semantic.py) | Full stack incl. core.py, zip_manager.py |
| `graphite-agent-v8` | **30** | ⚠️ (3 DIFFERENT funcs) | Different implementation; no core.py |

> **⚠️ Architecture warning:** The two branches' `semantic.py` implementations are **architecturally incompatible**:
> - `v8-surgical` semantic.py exposes: `discover, topology, replay, recommend, command_plan, report, all_cmd`
> - `graphite-agent-v8` semantic.py exposes: `analyze_semantics, detect_semantic_conflicts, generate_semantic_questions`
> They share **0% function names**. **Do NOT cherry-pick across these two lineages** — imports will break.

## 📁 V8 Semantic Stack - Corrected Status Table

| Module | `v8-surgical` | `graphite-v8` | 
|--------|:---:|:---:|
| `semantic.py` | ✅ (7 funcs) | ⚠️ (3 different funcs) |
| `core.py` | ✅ present | ❌ missing |
| `dispatcher.py` | ✅ present | ✅ present |
| `validation.py` | ✅ present | ✅ **present** |
| `execution.py` | ✅ present | ✅ present |
| `zip_manager.py` | ✅ present | ❌ missing |
| `semantic_conflicts.py` | ✅ present | ✅ present |
| `semantic_questions.py` | ✅ present | ✅ present |
| `semantic_recommendations.py` | ✅ present | ⚠️ differing impl |
| `analysis.py` | ✅ present | ❌ missing |
| `projection.py` | ✅ present | ❌ missing |
| `trajectory.py` | ✅ present | ❌ missing |
| `lsp_adapter.py` | ✅ present | ❌ missing |

Legend: ✅ Complete | ⚠️ Partial/Different | ❌ Missing

## 🗺️ ZIP Version Implementation Mapping

> **Correct git usage:** To bring specific files from another branch, use `git checkout <branch> -- <paths>` or `git restore --source=<branch> <paths>`. `git cherry-pick` does **not** accept a pathspec.

### 1. `graphite_agent_v8_full_implementation.zip`
**Best Base:** `v8-surgical-integration` (holds the full 37-module stack, incl. core.py/zip_manager.py)

```bash
git worktree add -B impl-v8-full ../impl-v8-full v8-surgical-integration
# v8-surgical already contains the full V8 stack. graphite-agent-v8 is NOT a
# suitable base here because it lacks core.py, zip_manager.py, analysis.py,
# projection.py, trajectory.py and uses an incompatible semantic.py.
```

### 2. `graphite_agent_v8_semantic_final_patch.zip`
**Best Base:** `v8-surgical-integration`

```bash
git worktree add -B impl-v8-sem-final ../impl-v8-sem-final v8-surgical-integration
# semantic.py (7 funcs) + semantic_questions.py + sibling modules already present.
```

### 3. `graphite_agent_v8_targeted_complete.zip`
**Best Base:** `v8-surgical-integration`

```bash
git worktree add -B impl-v8-targeted ../impl-v8-targeted v8-surgical-integration
# dispatcher.py, execution.py, validation.py needed for targeted completion present.
```

### 4. `graphite_agent_v8_complete_missing_features.zip`
**Best Base:** `v8-surgical-integration`

```bash
git worktree add -B impl-v8-missing ../impl-v8-missing v8-surgical-integration
# Note: Missing "features" here means zip content not yet on branch; compare
# against the zip and add any genuinely absent files via git checkout.
```

### 5. `graphite_agent_v8_semantic_scaffold_regenerated.zip`
**Best Base:** `v8-surgical-integration`

```bash
git worktree add -B impl-v8-scaffold ../impl-v8-scaffold v8-surgical-integration
# Base provides the semantic scaffold (semantic.py + core.py).
```

### 6. `graphite_agent_v8_capability_verification_pack.zip`
**Best Base:** `v8-surgical-integration`

```bash
git worktree add -B impl-v8-verify ../impl-v8-verify v8-surgical-integration
# Verification-only — reference/review tooling, not a full implementation target.
```

## 📊 Base Branch Summary (Verified, No Fabricated Fidelity Numbers)

| ZIP Version | Best Base | Reason |
|-------------|-----------|--------|
| v8_full_implementation | `v8-surgical-integration` | Full 37-module stack |
| v8_semantic_final_patch | `v8-surgical-integration` | Full semantic modules |
| v8_targeted_complete | `v8-surgical-integration` | dispatcher/execution/validation present |
| v8_complete_missing_features | `v8-surgical-integration` | Most complete feature set |
| v8_semantic_scaffold_regenerated | `v8-surgical-integration` | semantic.py + core.py present |
| v8_capability_verification_pack | `v8-surgical-integration` | Verification tooling |

> All V8 zips map best to `v8-surgical-integration` because it is the only branch
> holding the complete, coherent V8 semantic stack. None of these are suitable
> from `graphite-agent-v8` due to its divergent semantic.py and missing modules.

## 🛠️ Validation Commands For All V8 Implementations

```bash
# Run from within the worktree, by adding the lib dir to PYTHONPATH
cd <worktree>/impl-v8-*
PYTHONPATH=.graphite-agent/tools/lib python -c "
from semantic import discover, topology, replay, recommend
from core import main
from dispatcher import semantic_stage
print('Semantic stack imports OK')
"

# Run V8 verification script (exists on v8-surgical-integration)
python .graphite-agent/tools/verify_v8_implementation.py
```