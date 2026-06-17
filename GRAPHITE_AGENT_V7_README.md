# Graphite Multi-Root Agentic Retrofit V7

## Install into a repo

Copy `.graphite-agent/` into the repository root. Run:

```bash
python -m py_compile .graphite-agent/tools/*.py .graphite-agent/*.py
```

## Command flow

```bash
python .graphite-agent/tools/analyse.py
python .graphite-agent/tools/checklist.py
python .graphite-agent/tools/query.py --branch <branch>
python .graphite-agent/tools/explain.py --branch <branch>
python .graphite-agent/tools/questions.py --branch <branch>
python .graphite-agent/tools/decide.py --question q-000001 --branch <branch> --choice parent=<parent> --reason "human rationale"
python .graphite-agent/tools/rebuild_plan.py
python .graphite-agent/tools/validate_plan.py
python .graphite-agent/tools/execute_approved.py
```

## Undo/rework

```bash
python .graphite-agent/tools/decision_history.py --branch <branch>
python .graphite-agent/tools/revise_decision.py --decision dec-000001 --question q-000001 --branch <branch> --choice parent=<other-parent> --reason "updated rationale"
python .graphite-agent/tools/revoke_decision.py --decision dec-000001 --branch <branch> --reason "need more evidence"
python .graphite-agent/tools/rework.py --branch <branch> --choice parent=<other-parent> --dry-run
```
