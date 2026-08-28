# Graphite Multi-Root Agentic Retrofit — V6.2 Framework

This is a production-oriented implementation of the domain pipeline design for analysing legacy PR branches and safely converting only Graphite-compatible relationships into stack edges.

## Included

- `.graphite-agent/graphite_agent/` package
- CLI entry points and compatibility shims
- JSON contracts
- triage instructions
- V6.2 handoff documentation

## Configure

```bash
export GRAPHITE_TRUNK_BRANCHES="main,release/2.0"
export GRAPHITE_PRIMARY_REMOTE="origin"
```

## Analyse

```bash
python .graphite-agent/1_analyze_and_plan.py
```

## Execute safe plan

```bash
python .graphite-agent/2_strict_executor.py
```

## Triage unsafe branches

```bash
python .graphite-agent/4_guided_triage.py
```

## Safety rules

Only `safe` and `needs_restack` enter `execution_plan.json`. Patch equivalence, cross-root ancestry, trunk-update merges and foreign-DAG merges are never auto-converted into Graphite parent edges.
