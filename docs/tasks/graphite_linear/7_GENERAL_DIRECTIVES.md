# General Directives & Safety Rules

> **CRITICAL ARCHITECTURAL MANDATE:** Branch names are EXAMPLES ONLY. Implementation must dynamically discover targets via topological analysis.

### Query branch

```bash
python .graphite-agent/tools/query.py --branch <branch>
```

### Explain branch

```bash
python .graphite-agent/tools/explain.py --branch <branch>
```

## Rework and undo workflow

A user decision is not permanent truth. It is an append-only event.

### View decision history

```bash
python .graphite-agent/tools/decision_history.py --branch <branch>
```

### Revoke a decision without replacing it

```bash
python .graphite-agent/tools/revoke_decision.py \
  --decision <decision_id> \
  --branch <branch> \
  --reason "<reason for revocation>"
```

After any revision or revocation, run:

```bash
python .graphite-agent/tools/rebuild_plan.py
python .graphite-agent/tools/validate_plan.py
```

Do not execute a plan generated from superseded or revoked decisions.

***

## Expected command summary

Use this sequence for a normal implementation:

```bash

# 1. Back up existing files

mkdir -p .graphite-agent/backups
cp .graphite-agent/1_analyze_and_plan.py .graphite-agent/backups/1_analyze_and_plan.pre_v7_1.py 2>/dev/null || true
cp .graphite-agent/1_analyze_and_plan.py .graphite-agent/1_analyze_and_plan_v64.py 2>/dev/null || true
cp .graphite-agent/2_strict_executor.py .graphite-agent/backups/2_strict_executor.pre_v7_1.py 2>/dev/null || true

# 3. Install files

cp -R /tmp/graphite-v7_1/.graphite-agent/. .graphite-agent/
cp /tmp/graphite-v7_1/README.md ./GRAPHITE_AGENT_V7_1_README.md
cp /tmp/graphite-v7_1/DIFF_REPORT.md ./GRAPHITE_AGENT_V7_1_DIFF_REPORT.md

## 14. Execution safety

SAFE_TO_EXECUTE / NOT_SAFE_TO_EXECUTE
Reason:
- ...

## 15. Required fixes before use

- ...

## 16. Recommended next command

<single next command>
```

Do not omit any section.

***

## 15. Execution safety

SAFE/NOT_SAFE
Reason:
- ...

## 18. Recommended next command

<one command>
```

Do not omit any section.

***

## 12.7 Cycle

Fixture:

```text
A depends on B
B depends on A
```

Expected:

```text
cycle detected
both blocked
no execution
```

***

# 15. Final implementation report

After implementing, produce:

```text

# 16. Full Command Flow

```bash

# 1. Analyse

python .graphite-agent/tools/analyse.py

# 5. Analyse relationships

python .graphite-agent/tools/relationship_analyse.py


## 7.18 Phase Isolation & Progression Policy (CRITICAL)

To prevent LLM confusion and 'unwinding' of features, implementation agents must adhere to these rules:

1.  **Situational Awareness:** Before starting any phase, determine the *actual* version already present in the repo.
2.  **No Unwinding:** If a feature from a *later* phase (e.g., V7.2 logic) is already implemented and working, **DO NOT REMOVE OR REVERT IT**. Simply verify its presence and ensure it is compatible with the current phase's requirements.
3.  **Additive Implementation:** All file operations must be **ADDITIVE** (merging/patching). Do not use 'Wipe and Replace' or 'Delete and Re-copy' methods for directories unless explicitly instructed to perform a cleanup of specific orphaned files.
4.  **Phase Gating:** Do not implement features from a later phase (e.g., Target Discovery) while working on an earlier phase (e.g., Repo Hygiene), even if the phase file mentions them as future dependencies.
5.  **Procedural Correctness vs. Functional Integrity:** Prioritize **Functional Integrity**. If a procedural step (like 'Copy ZIP') would overwrite a more advanced local enhancement, **SKIP** the overwrite and perform a manual delta merge instead.
