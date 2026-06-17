# Diff-style report: V6.4 -> V7 Agentic Diagnostic Command Layer

This bundle is intentionally additive. It avoids replacing the existing V6.4 analyser/executor fast path and adds diagnostic tools around the cached JSON artefacts.

```diff
+ .graphite-agent/tools/agent_core.py
+ .graphite-agent/tools/analyse.py
+ .graphite-agent/tools/checklist.py
+ .graphite-agent/tools/query.py
+ .graphite-agent/tools/explain.py
+ .graphite-agent/tools/questions.py
+ .graphite-agent/tools/decide.py
+ .graphite-agent/tools/revise_decision.py
+ .graphite-agent/tools/revoke_decision.py
+ .graphite-agent/tools/decision_history.py
+ .graphite-agent/tools/recommend.py
+ .graphite-agent/tools/rebuild_plan.py
+ .graphite-agent/tools/rework.py
+ .graphite-agent/tools/validate_plan.py
+ .graphite-agent/tools/validate_cache.py
+ .graphite-agent/tools/execute_approved.py
+ .graphite-agent/contracts/*.contract.json
+ .graphite-agent/prompts/triage_instructions.md
~ .graphite-agent/1_analyze_and_plan.py       # compatibility wrapper to command layer
~ .graphite-agent/2_strict_executor.py        # compatibility wrapper to execute-approved
```

## Behavioural changes

```diff
+ Manual-triage branches now get triage packets.
+ Non-executable relationships are preserved in relationship_graph.json.
+ Ambiguous branches can produce bounded user questions.
+ User answers are append-only events in decision_log.jsonl.
+ Decisions can be revised or revoked without erasing history.
+ Execution plans can be rebuilt from current decisions.
+ validate_plan blocks unsafe execution before Graphite mutation.
+ query/explain/questions provide narrow context slices to reduce agent context flooding.
```

## Non-regression rules

```diff
= V6.4 safe branches remain executable.
= V6.4 needs_restack branches remain executable.
= Cross-root, merge-blocked, unrooted, and manual_triage branches remain blocked by default.
= Existing .graphite-agent/analysis_snapshot.json and .graphite-agent/plan.json remain supported.
```

## New command loop

```text
analyse -> checklist -> query/explain/questions -> decide/revise/revoke -> recommend -> rebuild_plan -> validate_plan -> execute_approved
```

## Decision rework support

A choice like `parent=feature/x` is not treated as permanent truth. It is recorded as an event. Later commands can revise, revoke, preview rework, and rebuild plans from the active decision projection.
