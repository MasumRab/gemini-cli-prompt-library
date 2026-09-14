# launch.py Branch Variants — Intentional Differences and Conflict Resolution

**Purpose**: Document the intentional differences between `main` and `scientific` branch `launch.py`, provide a conditional template for resolving conflicts, and track historical regressions.

**Last Updated**: 2026-09-14

---

## Intentional Differences (DO NOT REGRESS)

### 1. Scientific Branch Enhancements

| Feature | Description | Lines | Purpose |
|---------|-------------|-------|---------|
| **sys.path manipulation** | Adds project root to `sys.path` at module load | 17-20 | Allows running as script (`python3 setup/launch.py`) without PYTHONPATH issues |
| **Different import order** | `validation` → `services` → `environment` → `utils` | 22-35 | Cleaner dependency ordering; services layer separated |
| **Additional imports** | `atexit`, `threading`, `List` from typing | 44-46 | Required for scientific-specific cleanup and threading |
| **`check` subcommand** | Orchestration environment validation | 925-932 | Scientific branch has orchestration tooling not present in main |
| **`test` subcommand** | Granular test execution (unit/integration/e2e/performance) | ~960-970 | Advanced testing workflow for ML/research features |

### 2. Main Branch Baseline

| Feature | Description | Notes |
|---------|-------------|-------|
| **Standard import order** | `environment` → `utils` → `validation` | Original structure; works but less modular |
| **No sys.path hack** | Relies on proper PYTHONPATH or `python -m` | More correct but less convenient for ad-hoc runs |
| **No orchestration check** | Missing `check` subcommand | Main doesn't have orchestration tooling |
| **No granular test command** | Basic `test` command only | Simpler workflow for non-ML features |

### 3. Shared Baseline (BOTH branches have)

- Core validation functions: `check_python_version`, `check_required_components`, `validate_environment`
- Service startup: `start_backend`, `start_gradio_ui`, `start_services`
- Argument parser structure: `setup`, `run`, `test`, `clean` commands
- `initialize_all_services` and `get_container` integration

---

## Conflict Resolution History

### Regression Pattern

| Commit | Date | Issue | Resolution |
|--------|------|-------|------------|
| `352dc590` | Jul 28, 2026 | Merge conflict markers left in launch.py | Manual resolution — removed markers |
| `eec04785` | Apr 19, 2026 | Conflict markers during main sync | Manual resolution |
| `6f3f86bd` | Aug 17, 2026 | Backend merge conflict lints | Cleaned imports |
| `0580661a` | Aug 17, 2026 | Duplicate `main()` and imports | Cherry-pick from `9cbe607d` (the fix) |
| `cf7b2855` | Scientific | Duplicate `main()` removed | Same fix as main, but earlier |

### Root Cause

1. **Branch divergence**: `main` and `scientific` have different intentional structures
2. **Merge conflicts**: When syncing, naive resolution drops branch-specific features
3. **Stale snapshots**: Sessions working on old snapshots produce large diffs that fail
4. **No tracking**: Orchestration tools don't track that launch.py should differ per branch

---

## Conditional Template for Resolving launch.py Conflicts

### Decision Tree

```
IF resolving launch.py conflict:
  1. FETCH current state of BOTH branches:
     - git show origin/main:setup/launch.py > /tmp/launch-main-current.py
     - git show origin/scientific:setup/launch.py > /tmp/launch-scientific-current.py

  2. DETERMINE target branch:
     - IF target == main:
         base = main baseline
         additions = ONLY features that should be in main (no orchestration check, no granular test)
     - IF target == scientific:
         base = scientific baseline
         additions = ALL scientific enhancements (sys.path, check command, test subcommands)

  3. CHECK for intentional changes:
     - IF session modified validation/service logic:
         PRESERVE those changes (don't revert to template blindly)
     - IF session added new subcommands:
         ADD to appropriate branch (main: general; scientific: research-specific)

  4. RESOLVE conflicts:
     - TAKE branch-specific imports from target branch baseline
     - TAKE shared functions from whichever side is more recent/correct
     - TAKE session-specific changes if intentional
     - NEVER take conflict markers or duplicate definitions

  5. VALIDATE:
     - python3 -m py_compile setup/launch.py  # syntax check
     - grep -c "<<<<<<\|======\|>>>>>>" setup/launch.py  # should be 0
     - grep -c "^def main" setup/launch.py  # should be 1
     - IF target == scientific:
         grep -n "check.*parser" setup/launch.py  # should find check subcommand
```

### Template Files

Save these as reference templates:

```bash
# For main branch conflicts:
git show origin/main:setup/launch.py > ~/.jules/templates/launch-main-template.py

# For scientific branch conflicts:
git show origin/scientific:setup/launch.py > ~/.jules/templates/launch-scientific-template.py
```

---

## Session Instructions (for sessions struggling with launch.py)

If a session reports launch.py conflict markers or duplicate definitions:

1. **Send the current baseline**:
   ```
   Your launch.py has conflict markers. Here is the CURRENT correct baseline for [branch]:
   [paste relevant template]
   ```

2. **Instruct conditional preservation**:
   ```
   Compare your changes against this baseline:
   - PRESERVE any intentional changes you made (new validation, new service startup logic)
   - ADOPT the baseline's import structure and function definitions
   - DO NOT duplicate main() or leave conflict markers
   ```

3. **Validate after resolution**:
   ```
   After fixing, run:
   - python3 -m py_compile setup/launch.py
   - grep -c "<<<<<<\|======\|>>>>>>" setup/launch.py  # must be 0
   - grep -c "^def main" setup/launch.py  # must be 1
   ```

---

## Orchestration Tool Gap

**Current State**: Orchestration tools (workmux, conductor) don't track that `launch.py` should differ per branch.

**Impact**: Sessions may accidentally regress scientific features when merging/syncing.

**Recommendation**:
1. Add to `.workmux.yaml`:
   ```yaml
   branch_templates:
     scientific:
       - setup/launch.py  # has check subcommand + sys.path hack
     main:
       - setup/launch.py  # baseline version
   ```
2. Add validation to branch health checks:
   ```bash
   # In branch health script:
   if branch == "scientific":
     assert grep -q "check.*parser" setup/launch.py
     assert grep -q "sys.path.insert" setup/launch.py
   ```
3. Document in AGENTS.md (branch-specific files section)

---

## Findings Log

### 2026-09-14 Analysis

- **Main launch.py**: 1209 lines, baseline structure
- **Scientific launch.py**: 1138 lines, 71 lines shorter despite more features (cleaner imports)
- **Both cleaned**: Duplicate `main()` removed from both branches (commits `0580661a` and `cf7b2855`)
- **Intentional divergence**: Scientific has `check` and granular `test` subcommands; main does not
- **Historical regressions**: Multiple conflict marker incidents, all manually resolved
- **Pattern**: Conflicts occur during branch syncs; resolution often drops branch-specific features

### Recommendations for Sessions

1. **Always fetch current state** before resolving launch.py conflicts
2. **Check target branch**: Use appropriate template (main vs scientific)
3. **Preserve intentional changes**: Don't blindly revert to template
4. **Validate**: No conflict markers, no duplicate `main()`, correct subcommands for branch
5. **Report findings**: If you discover a regression, document it

---

## Quick Reference

```bash
# Get current launch.py from each branch:
git show origin/main:setup/launch.py
git show origin/scientific:setup/launch.py

# Check for conflict markers:
grep -n "<<<<<<\|======\|>>>>>>" setup/launch.py

# Check for duplicate main():
grep -n "^def main" setup/launch.py

# Syntax check:
python3 -m py_compile setup/launch.py

# Scientific-specific checks:
grep -n "check.*parser\|sys.path.insert" setup/launch.py
```
