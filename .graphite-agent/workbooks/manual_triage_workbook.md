# Manual Triage Workbook: Systematic Branch Diagnosis

## Purpose

This workbook guides systematic diagnosis of branches requiring human review.

It ensures that instead of dumping branches into `manual_triage` and expecting humans to rediscover all evidence from raw Git commands, the agent provides prepared diagnostic context.

***

# 1. Branch Identification

When you see a branch in `manual_triage` or blocked status, start here.

### Basic Info
- **Branch name**:
- **Local branch exists**: Yes / No
- **Remote tracking branch**: origin/
- **Target/root branch**:

### PR Context
- **GitHub PR number**:
- **PR title**:
- **PR author**:
- **PR state**: open / closed / merged
- **PR base (declared target)**:

***

# 2. Target Analysis

Compare and reason about target intent.

| Field | Value | Source |
|-------|-------|--------|
| Declared PR target | | GitHub PR API, `.branch-config.json` |
| Inferred Git target | | `git merge-base --fork-point`, ancestry analysis |
| Candidate targets (auto-discovered) | | `target_candidates.json`, PR base frequency |
| Confirmed target | | Human decision or auto-high-confidence |

### Diagnostic Categories for Target Issues

Check which applies:

```text
[ ] wrong_pr_target_candidate
    PR base differs from inferred target based on ancestry

[ ] target_root_mismatch
    Branch claims target but ancestry suggests different root

[ ] declared_target_not_ancestor
    Branch merged target but target is not ancestry ancestor

[ ] target_intent_required
    No clear target signal; requires user decision
```

***

# 3. Root Branch Status

Analyze the health of the target/root.

### Root Health Summary
- **Root branch**:
- **Root health**: current / stale / unknown
- **Compared against baseline**: main / scientific / orchestration-tools
- **Commit delta HEAD~..HEAD** | Ahead: | Behind: |

### Evidence for Staleness
```text
[ ] main contains commits not present in target
[ ] Multiple branches from target show trunk_updates flags
[ ] Merge commits from other roots detected in branch range
[ ] Branches share stale merge-base patterns
[ ] No recent commits (older than X days)
[ ] Shared missing fix indicators detected
```

### Merge-Contamination Evidence
```text
[ ] Merge commit(s) detected in target..branch
[ ] Merge parent matches declared target → likely conflict-resolution merge
[ ] Merge parent differs from target → cross-root contamination
[ ] Branch is non-linear after merge
```

***

# 4. Status & Diagnostic Category

Record the current diagnostic state.

### Status
| Value | Meaning |
|-------|---------|
| safe | Safe to execute, parent confirmed |
| needs_restack | Parent exists but not ancestry parent |
| manual_triage | Requires human decision |
| cross_root_conflict | Merged foreign root history |
| blocked_merge_commits | Contains merge commits blocking Graphite |
| unrooted | No clear root/target signal |

### Diagnostic Category
If not `safe` or `needs_restack`:
- **Category**:
- **Classification**: blocked / triage_only
- **Confidence**: high / medium / low

***

# 5. Relationship Evidence

List relationship edges that inform the diagnosis.

```
Edge ID     | From       | To         | Type                            | Classification | Evidence
------------|------------|------------|---------------------------------|---------------|-----------------------------
rel-000001  | main       | feature/x  | existing_plan_parent              | executable    | Declared base is an ancestor
rel-000002  | main       | feature/y  | in_target_conflict_resolution_merge | blocked     | Merge commit with main found in branch range
rel-000003  | main       | feature/z  | cross_root_contamination          | blocked       | Contains merged history from release/1.0
```

### Key Evidence Types
- `existing_plan_parent` — safe parent edge from analysis
- `non_executable_parent_signal` — parent signal but not executable
- `in_target_conflict_resolution_merge` — merged target into branch
- `cross_root_contamination` — merged foreign root
- `unknown_merge_contamination` — merge but parent unclear

***

# 6. Merge Analysis

If merges detected, analyze them thoroughly.

### Target Conflict-Resolution Merge Detection
```text
[ ] git log --oneline --merges target..branch exists
[ ] Merge parent SHA matches target branch SHA
[ ] Branch is non-linear (has merge commit)
[ ] trunk_updates field contains target → classified same-target merge
[ ] No cross-root merge parents → not contamination
```

### Cross-Root Contamination Detection
```text
[ ] Merge commit in branch range
[ ] Merge parent NOT target branch
[ ] branch targets one root, merged another
[ ] foreign_dag_merges or known_pr_merges lists non-target roots
[ ] Root branch field differs from merge parent root
```

### Merge Parents
```
Parent SHA | Branch Name | Root | Classification
-----------|-------------|------|-----------------
```

***

# 7. Candidate Parents & Targets

List potential parent/target combinations.

### Candidate Parents
| Parent | Confidence | Evidence |
|--------|------------|----------|
|  | high / medium / low |  |

### Candidate Targets (for target_questions.py)
| Target | Confidence | Evidence |
|--------|------------|----------|
|  | high / medium / low |  |

***

# 8. Open Questions

List generated questions for this branch.

| Question ID | Type | Priority | Question | Options | Recommended |
|-------------|------|----------|----------|---------|-------------|
| q-000001 | parent_intent | high / medium / low |  | parent=X, leave_triage, exclude_from_migration |  |
| q-target-000001 | target_intent | high |  | target=X, targets=X+Y, leave_triage, exclude_from_migration |  |

***

# 9. Decision Record

Capture the human decision.

### Primary Decision
- **Decision ID**:
- **Question ID**:
- **Branch**:
- **Choice**:
- **Reason**:
- **Timestamp**:
- **Source**: human / auto-promoted

### Secondary Decisions (if any)
```
Decision ID | Type | Branch | Choice | Reason
------------|------|--------|--------|-----------------
```

### Decision Log Reference
```bash
grep <branch> .graphite-agent/outputs/decision_log.jsonl
```

***

# 10. Recommended Remediation

Select from the following options.

### For Target Ambiguity
```text
[ ] Track only (if target confirmed)
[ ] Track and restack (if parent differs from target)
[ ] Linearise before Graphite tracking (if merged target)
[ ] Create clean branch from target (if heavily tangled)
[ ] Retarget PR (if declared target wrong)
[ ] Exclude from migration (if not needed)
```

### For Merge Contamination
```text
[ ] Linearise with rebase (human-approved)
[ ] Recreate clean branch from target
[ ] Retarget to merged root (if backport intent)
[ ] Leave in triage (defer decision)
```

### For Stale Root
```text
[ ] Refresh root before stacking
[ ] Do not refresh root
[ ] Create clean integration base
[ ] Leave affected branches in triage
```

***

# 11. Validation Result

After remediation, validate.

### Validation Checks
| Script | Result | Failed Items |
|--------|--------|--------------|
| validate_targets.py | pass / blocked |  |
| validate_roots.py | pass / blocked |  |
| validate_stack_order.py | pass / blocked |  |
| validate_plan.py | pass / blocked |  |

### Failed Checks Detail
```
ID | Branch | Severity | Message
---|--------|----------|--------
```

### Validation Commands
```bash
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

***

# 12. Execution Status

Final determination.

- **Execution allowed**: Yes / No
- **Blocking reasons**:
- **Required actions before execution**:

### Next Commands (if blocked)
```bash
python .graphite-agent/tools/target_questions.py --branch <name>
python .graphite-agent/tools/root_questions.py --target <target>
python .graphite-agent/tools/target_decide.py --branch <name> --choice <option> --reason "<reason>"
```

***

# 13. Commands Reference

```bash
# Diagnose branch
python .graphite-agent/tools/query.py --branch <branch>
python .graphite-agent/tools/explain.py --branch <branch>
python .graphite-agent/tools/target_questions.py --branch <branch>

# Record decision
python .graphite-agent/tools/target_decide.py \
  --question <q-id> \
  --branch <branch> \
  --choice <option> \
  --reason "<reason>"

# Rebuild plan
python .graphite-agent/tools/rebuild_plan.py

# Validate
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

***

# 14. Example Output

After completing this workbook, the branch should have:

```text
[ ] diagnostic category identified
[ ] evidence collected and documented
[ ] recommendation generated
[ ] next command identified
[ ] question generated if user intent needed
[ ] validation status determined
[ ] execution status determined
```