# Target Conflict Resolution Merge Handling

## Purpose

This runbook explains how to identify, diagnose, and remediate branches that have merged their target branch into themselves to resolve conflicts.

***

# 1. Identifying Target Conflict Resolution Merges

## Detection Method

Check the `trunk_updates` field in branch audit data:

```bash
python .graphite-agent/tools/query.py --branch <branch>
```

Or examine merge commits directly:

```bash
git log --oneline --merges <target>..<branch>
```

## Evidence Indicators

A branch that merged its target shows:

```text
[ ] merge commit exists in target..branch range
[ ] merge parent SHA matches target branch
[ ] branch is non-linear (has merge commit in history)
[ ] trunk_updates contains the target branch name
[ ] status may be blocked_merge_commits
```

## Example Output

```json
{
  "branch": "feature/x",
  "status": "blocked_merge_commits",
  "audit": {
    "merge_analysis": {
      "trunk_updates": ["main"]
    }
  }
}
```

***

# 2. Why This Blocks Graphite

Graphite requires linear history for safe stacking. Merged target branches create:

| Problem | Description |
|---------|-------------|
| Duplicate commits | Both branch and target commits exist |
| Non-linear ancestry | Merge commit breaks clean parent chain |
| Ambiguous parent | Which is the real parent for stacking? |
| Conflict resolution noise | Merge brings in unrelated changes |

***

# 3. Distinguishing Same-Target vs Cross-Root

| Same-Target Merge | Cross-Root Contamination |
|-------------------|--------------------------|
| Merge parent IS declared/inferred target | Merge parent is DIFFERENT target root |
| `trunk_updates` contains current target | Branch targets one root, merged another |
| Diagnostic: `in_target_conflict_resolution_merge` | Diagnostic: `cross_root_contamination` |
| Remediation: linearise against same target | Remediation: target intent required |

## Detection Logic

```python
if merge_parent_sha == target_branch_sha:
    classification = "in_target_conflict_resolution_merge"
elif merge_parent_root != branch_root:
    classification = "cross_root_contamination"
else:
    classification = "unknown_merge_contamination"
```

***

# 4. Remediation Options

## Option A — Linearise with Rebase

Use when target is correct but branch has merge noise.

```text
Human-owned steps:
1. Confirm target branch with `explain.py --branch <branch>`
2. Create backup branch: git branch <branch>-backup
3. Rebase interactively: git rebase -i <target>
4. Remove/squash merge commits
5. Verify clean linear history
6. Rerun diagnostics
```

Do not auto-rebase; this requires human review.

## Option B — Recreate Clean Branch

Use when branch history is too tangled.

```text
Human-owned steps:
1. Confirm target branch
2. Create new branch: git switch -c <branch>-clean <target>
3. Cherry-pick intended commits
4. Verify patch content matches original intent
5. Delete old branch, rename clean branch
6. Rerun diagnostics
```

## Option C — Retarget (Backport Scenario)

Use when merge indicates intentional backport.

```text
Human-owned steps:
1. Confirm backport intent via PR description/comments
2. Record target decision for both roots
3. Create separate stacks per target
4. Rerun diagnostics
```

## Option D — Leave in Triage

Use when intent unclear or high risk.

```text
No immediate Graphite action.
Branch remains in manual_triage_queue.
Evidence preserved for later analysis.
```

***

# 5. Commands for Inspection

```bash
# Query branch state
python .graphite-agent/tools/query.py --branch <branch>

# Get human-readable explanation
python .graphite-agent/tools/explain.py --branch <branch>

# Check target questions
python .graphite-agent/tools/target_questions.py --branch <branch>

# View triage packet
cat .graphite-agent/outputs/triage_packets.json | jq '.["<branch>"]'
```

***

# 6. Validation After Remediation

```bash
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_plan.py
```

Expected:

```json
{
  "status": "pass",
  "failed_checks": []
}
```

***

# 7. Example Triage Packet

For a branch that merged main for conflict resolution:

```json
{
  "branch": "feature/x",
  "status": "blocked_merge_commits",
  "diagnostic_category": "in_target_conflict_resolution_merge",
  "primary_reason": "Branch appears to have merged its target branch to resolve conflicts.",
  "recommended_action": "linearise_before_graphite_tracking",
  "next_steps": [
    "Confirm target is main",
    "Human-approved rebase to remove merge commits",
    "Or recreate clean branch from target",
    "Rerun validation"
  ]
}
```

***

# 8. Safety Reminders

```text
[ ] Do not auto-rebase
[ ] Do not auto-merge targets
[ ] Do not execute until validated
[ ] Record human decision before remediation
[ ] Verify linear history after fix
[ ] Rerun full diagnostics
```