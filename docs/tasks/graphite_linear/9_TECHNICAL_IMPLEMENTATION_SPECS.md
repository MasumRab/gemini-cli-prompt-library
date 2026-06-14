# Phase: 9 TECHNICAL IMPLEMENTATION SPECS

> **ARCHITECTURAL MANDATE:** These specs provide the mathematical and logical "how-to" for the most complex components of the Graphite-Agent system.

## 9.1 Target Discovery Scoring Algorithm

To convert raw Git evidence into a `confidence` score for `target_candidates.json`, use the following weighted formula.

### Base Weights (Cumulative)
| Signal | Weight | Notes |
| :--- | :--- | :--- |
| **Origin HEAD** | 100 | The default target of the remote. |
| **PR Base Frequency** | +15 per PR | Up to +60. Count of open PRs targeting this branch. |
| **Ancestry Depth** | +10 per branch | Up to +50. Count of branches that are descendants. |
| **Semantic Match** | +30 | Case-insensitive match for "main", "master", "scientific", "orchestration". |
| **Proximity Score** | +20 | If `merge-base` is < 5 commits from branch HEAD. |
| **Short-Lived Check** | -80 | If branch was created < 48h ago and has 0 descendants. |

### Confidence Mapping
- **High:** Score >= 85
- **Medium:** Score 50 - 84
- **Low:** Score < 50

***

## 9.2 Conflict-Resolution Merge Classification

To distinguish between a "Target Update" and "Cross-Root Contamination," tools must use the following logic when inspecting merge commits (`M`).

### The Detection Loop
For each merge commit in the range `target..branch`:
1.  Identify the "Merged Parent" (`P2`). `P1` is the branch history, `P2` is the side-loaded commit.
2.  **Logic A (Same-Target):** 
    - `git merge-base --is-ancestor P2 origin/<declared_target>`
    - If `True` -> Classify as `in_target_conflict_resolution_merge`.
3.  **Logic B (Cross-Root):**
    - `git merge-base --is-ancestor P2 origin/<other_candidate_target>`
    - If `True` -> Classify as `cross_root_contamination`.
4.  **Logic C (Unknown):**
    - If neither -> Classify as `unknown_merge_contamination`.

***

## 9.3 State Projection Algorithm (`rebuild_plan.py`)

This algorithm "projects" the append-only `decision_log.jsonl` onto the static `analysis_snapshot.json` to produce the dynamic `execution_plan.json`.

### Projection Steps:
1.  **Initialize Decision Map:** Create an empty dictionary `active_decisions = {}`.
2.  **Process Log (Oldest to Newest):**
    - Read `outputs/decision_log.jsonl`.
    - On `decision_recorded`: 
        - Store/Overwrite: `active_decisions[subject] = entry`.
    - On `decision_revoked`:
        - Remove: `del active_decisions[subject]`.
3.  **Apply Overlay:**
    - Load `outputs/analysis_summary.json` (The base state).
    - For each branch in the summary:
        - If `branch_name` exists in `active_decisions`:
            - Update `status` to `safe` or `needs_restack`.
            - Update `resolved_parent` to the user's `choice`.
            - Inject `decision_provenance` metadata.
4.  **Recalculate Stacks:**
    - Call `stack_order.py` logic to re-sort branches based on the new `resolved_parent` values.
5.  **Output:** Write to `outputs/execution_plan.json`.

***

## 9.4 Git Core Library Interface (`lib/git_core.py`)

The following helper functions are mandatory to ensure consistent result formatting:

```python
def get_patch_id(commit_hash: str) -> str:
    # Must pipe 'git show' to 'git patch-id' and return the first 40 chars
    pass

def is_ancestor(ancestor: str, descendant: str) -> bool:
    # Returns True if ancestor exists in descendant's history
    pass

def get_merge_parents(commit_hash: str) -> list[str]:
    # Returns parents using 'git rev-list --parents -n 1 <hash>'
    pass
```
