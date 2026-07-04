# Graphite-Agent Stacking Plan

> **Note**: This directory may not be included in the final remote repository.
> All portable context is documented in the main [README.md](../README.md).

---

## Current State

### Stack Configuration
- **Stack Root**: `main`
- **Root Health**: `stale` (from [outputs/stack_order.json](./outputs/stack_order.json))
- **Execution Allowed**: `true`

### Execution Queue
From [outputs/execution_plan.json](./outputs/execution_plan.json):

| Order | Branch | Target | Action | Status |
|-------|--------|--------|--------|--------|
| 1 | `feature/safe` | main | track_only | safe |
| 2 | `feature/restack` | feature/safe | track_and_restack | needs_restack |

### Manual Triage Queue
| Branch | Status | Reason |
|--------|--------|--------|
| `feature/merge-conflict-resolution` | blocked_merge_commits | Branch merged target to resolve conflicts |

### Target Matrix
From [outputs/target_matrix.json](./outputs/target_matrix.json):

| Branch | Declared Target | Diagnostic Category | Requires Decision |
|--------|-----------------|---------------------|-------------------|
| `feature/safe` | main | target_confirmed | No |
| `feature/restack` | feature/safe | wrong_pr_target_candidate | **Yes** (q-target-000001) |
| `feature/triage` | main | target_confirmed | No |
| `feature/cross` | main | target_confirmed | No |
| `feature/merge-conflict-resolution` | main | target_confirmed | No |

---

## Pending Decisions

### High Priority
- [ ] **feature/restack**: Choose target branch
  - **Options**: `feature/safe` (declared) or `main`
  - **Question Ref**: q-target-000001
  - **Impact**: Blocks stacking execution for this branch

---

## Key Files (All in This Directory)

### Configuration & State
- `outputs/stack_order.json` - Current stacking order and branch dependencies
- `outputs/execution_plan.json` - Execution queue with status
- `outputs/target_matrix.json` - Branch target assignments and diagnostics
- `outputs/stack_order_validation.json` - Validation results

### Tools (V7.2 Implementation)
- `tools/stack_order.py` - Calculate stacking order per target root
- `tools/validate_stack_order.py` - Validate stack ordering safety
- `tools/validate_roots.py` - Validate root health before execution
- `tools/rebuild_plan.py` - Rebuild execution plan
- `tools/validate_plan.py` - Validate execution plan
- See [IMPLEMENTATION_REPORT_V72.md](./IMPLEMENTATION_REPORT_V72.md) for full tool list (23 tools)

### Checklists
- `checklists/stale_root_stack_order_checklist.md` - Stale root handling
- `checklists/pre_execution_safety_checklist.md` - Pre-execution validation
- `checklists/conflict_resolution_merge_checklist.md` - Merge conflict resolution

### Documentation
- `IMPLEMENTATION_REPORT_V72.md` - V7.2 implementation details
- `COMPATIBILITY.md` - Version compatibility guide
- `runbooks/` - Operational runbooks
- `workbooks/` - Diagnostic workbooks
- `prompts/` - Agent prompts

---

## Git Repository State

### Current Branch
- **Branch**: `fix-scheduled-audit-report-7335934676686138146`
- **Status**: DIVERGED from `origin/fix-scheduled-audit-report-7335934676686138146`

### Divergence Summary
- **Local Ahead**: 38 commits
- **Remote Behind**: 25 commits
- **Interruption Point**: Commit `49667f8` ("continue interactive rebase")

### Recent Local Commits (Top 5)
```
6c4f48c Apply auto-formatting to resolve CI issues
49667f8 continue interactive rebase
b616132 Apply black formatting fixes
2bcf039 Style: apply black formatting
884c66b Chore: add module docstring
```

### Recent Remote Commits (Missing Locally, Top 5)
```
426aeed Apply auto-formatting to resolve CI issues
4cce151 Remove package.json
f9c2af1 Merge origin/main into pr-25 - resolve .gitignore conflict
4fe38b9 chore: update rebuilt execution plan and checklist report
666afed feat: add V7.1 diagnostic output artefacts
```

---

## Validation Status

- ✅ **stack_order_validation.json**: `status: pass`
- ✅ **All 23 required tools**: Present (V7.2)
- ✅ **All 19 required outputs**: Present
- ⚠️ **Root Health**: `stale` - needs resolution
- ⚠️ **Execution**: Ready but has pending decisions

---

## Quick Commands

```bash
# Check full stack order
cat outputs/stack_order.json | jq '.'

# Check execution plan
cat outputs/execution_plan.json | jq '.'

# Validate stack order
python tools/validate_stack_order.py

# Rebuild plan
python tools/rebuild_plan.py

# Validate roots
python tools/validate_roots.py
```

---

## References

- [Graphite-Agent Documentation](https://graphite.dev)
- [V7.2 Implementation Report](./IMPLEMENTATION_REPORT_V72.md)
- [COMPATIBILITY.md](./COMPATIBILITY.md)
