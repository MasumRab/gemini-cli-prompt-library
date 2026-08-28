# Worktree Setup for Parallel Version Development

## Overview

This document describes how to set up isolated worktrees for parallel development of `.graphite-agent` versions (v64, v72, v73).

## Prerequisites

- Git 2.5+ with worktree support
- Python 3.9+
- Sufficient disk space for N+1 copies of the repository

## Version Definitions

| Version | Branch | Description | Status |
|---------|--------|-------------|--------|
| v64 | `version/v64` | V6.4 Topology Audit - base topology audit engine with multi-root support | Implemented |
| v72 | `version/v72` | V7.2 Human-in-the-Loop Automation - target analysis, root health, stack ordering | Partially implemented |
| v73 | `version/v73` | V7.3 Derived-Output Mode - reads existing snapshot/plan, writes derived outputs | Fixtures created |

## Setup Instructions

### 1. Run the Setup Script

```bash
cd /path/to/gemini-cli-prompt-library
bash .graphite-agent/scripts/setup_worktrees.sh
```

This creates:
- `.worktrees/v64/` - isolated worktree for V6.4 development
- `.worktrees/v72/` - isolated worktree for V7.2 development
- `.worktrees/v73/` - isolated worktree for V7.3 development

### 2. Verify Worktrees

```bash
git worktree list
```

Expected output:
```
/path/to/gemini-cli-prompt-library          abc1234 [main]
/path/to/gemini-cli-prompt-library/.worktrees/v64  def5678 [version/v64]
/path/to/gemini-cli-prompt-library/.worktrees/v72  ghi9012 [version/v72]
/path/to/gemini-cli-prompt-library/.worktrees/v73  jkl3456 [version/v73]
```

### 3. Switch Between Versions

```bash
# Work on V6.4
cd .worktrees/v64

# Work on V7.2
cd .worktrees/v72

# Work on V7.3
cd .worktrees/v73
```

## Comparing Versions

### Run Comparison Script

```bash
# Compare all versions
bash .graphite-agent/scripts/compare_versions.sh v64 v72 v73

# Compare specific versions
bash .graphite-agent/scripts/compare_versions.sh v64 v72
```

### Manual Comparison

Each worktree is fully independent. You can:

1. **Run tests in parallel**:
   ```bash
   # Terminal 1
   cd .worktrees/v64 && python3 -m unittest discover -s .graphite-agent/tests/ -v

   # Terminal 2
   cd .worktrees/v72 && python3 -m unittest discover -s .graphite-agent/tests/ -v

   # Terminal 3
   cd .worktrees/v73 && python3 -m unittest discover -s .graphite-agent/tests/ -v
   ```

2. **Compare outputs**:
   ```bash
   # Generate outputs in each worktree
   cd .worktrees/v64 && python3 .graphite-agent/tools/analyse.py > /tmp/v64_out.json
   cd .worktrees/v72 && python3 .graphite-agent/tools/analyse.py > /tmp/v72_out.json
   cd .worktrees/v73 && python3 .graphite-agent/tools/analyse.py > /tmp/v73_out.json

   # Compare
   diff /tmp/v64_out.json /tmp/v72_out.json
   diff /tmp/v72_out.json /tmp/v73_out.json
   ```

3. **Compare specific features**:
   ```bash
   # Compare target analysis
   cd .worktrees/v64 && python3 .graphite-agent/tools/discover_targets.py > /tmp/v64_targets.json
   cd .worktrees/v72 && python3 .graphite-agent/tools/discover_targets.py > /tmp/v72_targets.json
   diff /tmp/v64_targets.json /tmp/v72_targets.json
   ```

## Worktree Cleanup

### Remove All Worktrees

```bash
git worktree remove .worktrees/v64 --force
git worktree remove .worktrees/v72 --force
git worktree remove .worktrees/v73 --force
rm -rf .worktrees
```

### Remove Specific Worktree

```bash
git worktree remove .worktrees/v72 --force
```

## Architecture Notes

### Version Isolation

Each worktree contains:
- Complete git history
- Version-specific fixtures in `.graphite-agent/fixtures/<version>/`
- Version-specific README in `.graphite-agent/VERSION_README.md`
- Shared tools and libraries from the main branch

### Shared vs Version-Specific Files

**Shared across all versions:**
- `.graphite-agent/tools/*.py` - all tool scripts
- `.graphite-agent/tools/lib/*.py` - shared libraries
- `.graphite-agent/tests/*.py` - test suite
- `.graphite-agent/contracts/*.json` - output contracts
- `.graphite-agent/prompts/*.md` - agent prompts
- `.graphite-agent/runbooks/*.md` - operational runbooks
- `.graphite-agent/workbooks/*.md` - diagnostic workbooks
- `.graphite-agent/checklists/*.md` - checklists

**Version-specific:**
- `.graphite-agent/fixtures/<version>/*.json` - test fixtures
- `.graphite-agent/README.md` - version-specific readme
- `.graphite-agent/VERSION_README.md` - worktree-specific notes

### Development Workflow

1. **Implement feature in version worktree**
   ```bash
   cd .worktrees/v72
   # Make changes to .graphite-agent/tools/...
   ```

2. **Run tests**
   ```bash
   python3 -m unittest discover -s .graphite-agent/tests/ -v
   ```

3. **Compare with other versions**
   ```bash
   cd .worktrees/v64
   # Run same tests to verify behavior differences
   ```

4. **Merge back to main** (if desired)
   ```bash
   cd .worktrees/v72
   git checkout main
   git merge version/v72
   ```

## Troubleshooting

### Worktree Already Exists

If a worktree already exists:
```bash
git worktree remove .worktrees/v64 --force
bash .graphite-agent/scripts/setup_worktrees.sh
```

### Branch Already Exists

If a version branch already exists:
```bash
git branch -D version/v64
git worktree remove .worktrees/v64 --force
bash .graphite-agent/scripts/setup_worktrees.sh
```

### Conflicts During Merge

If merging version changes back to main causes conflicts:
1. Use `git merge --abort` to cancel
2. Review differences with `git diff main..version/v72`
3. Resolve conflicts manually
4. Consider whether changes should be shared or version-specific
