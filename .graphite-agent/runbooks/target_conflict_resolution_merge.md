# Runbook: Target Conflict-Resolution Merge

## Overview

Detect branches that merged their target to resolve conflicts. These branches have `blocked_merge_commits` status with `diagnostic_category: in_target_conflict_resolution_merge`. Do not execute directly.

## Prerequisites
- `outputs/triage_packets.json` exists
- Branch status is `blocked_merge_commits`
- `audit.merge_analysis.trunk_updates` contains the target root

## Steps

1. **Confirm merge evidence**
   Open `outputs/triage_packets.json` and locate the branch. Verify:
   - `status` is `blocked_merge_commits`
   - `diagnostic_category` is `in_target_conflict_resolution_merge`
   - `primary_reason` mentions merge commits

2. **Assess linearisation feasibility**
   Determine whether the branch can be recreated cleanly from the target:
   - If the merge commit is a fast-forward, linearisation is safe
   - If the merge commit contains divergent changes, recreate the branch

3. **Recommend action**
   - **Preferred**: Recreate branch from target with changes applied as a linear series of commits
   - **Alternative**: Human-approved linearisation using `git rebase -i`

4. **Update execution plan**
   If the branch is recreated, update `outputs/execution_plan.json` to reflect the new parent and status.

5. **Re-run validation**
   ```bash
   python .graphite-agent/tools/validate_plan.py
   ```

## Failure Modes
- **Cannot determine original changes**: Use `git show` on the merge commit to extract patches.
- **Target has moved forward**: Re-run `python .graphite-agent/tools/analyse.py` before recreating.

## References
- `checklists/conflict_resolution_merge_checklist.md`
- `prompts/agent_complex_triage_prompt.md`
