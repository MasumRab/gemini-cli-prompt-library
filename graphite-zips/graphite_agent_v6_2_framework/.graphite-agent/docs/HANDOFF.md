# V6.2 Handoff

## Architecture

```text
Adapters collect facts.
Collectors emit evidence.
Classifiers assign branch state.
Verifiers enforce invariants.
Policies decide executability.
Compilers generate artefacts.
Executors act only on compact plans.
```

## Decision tree

```text
Start branch
  |-- no configured root owner?          -> unrooted -> triage
  |-- multiple configured root owners?   -> cross_root_conflict -> triage
  |-- cycle detected?                    -> cycle -> triage
  |-- blocked merge evidence?            -> blocked_merge_commits -> triage
  |-- declared base same-root ancestor?  -> safe -> execution
  |-- declared base same-root stale?     -> needs_restack -> execution
  |-- nearest same-root ancestor exists? -> needs_restack -> execution
  |-- patch-id overlap only?             -> patch_equivalence_only -> triage
  |-- otherwise                          -> ambiguous_relationship -> triage
```

## Runbooks

- Cross-root conflict: do not auto-track; recreate/rebase under exactly one configured root.
- Blocked merge commits: strip or rebuild branch to remove trunk-update or foreign-DAG evidence.
- Cycle: choose true parent manually and rewrite history.
- Patch equivalence only: do not infer parentage from patch IDs.
- Complex hub / DAG dependency: flatten, extract shared base, split, or linearise, then rerun analysis.
