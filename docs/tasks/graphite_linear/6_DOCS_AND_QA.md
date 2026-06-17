# Phase: 6 DOCS AND QA

> **CRITICAL ARCHITECTURAL MANDATE:** Branch names are EXAMPLES ONLY. Implementation must dynamically discover targets via topological analysis.

## 6.1 — Run syntax validation

Run:

```bash
python -m py_compile .graphite-agent/tools/*.py .graphite-agent/*.py
```

If this fails, stop and report the exact Python file and syntax error.

Do not continue to Graphite execution if syntax validation fails.

***

## 6.2 Validate syntax and tests

python -m py_compile .graphite-agent/tools/*.py .graphite-agent/*.py
python .graphite-agent/tests/run_tests.py

## 6.3 Syntax validation

Run:

```bash
python -m py_compile .graphite-agent/tools/*.py .graphite-agent/*.py
```

Expected result:

```text
pass
```

If it fails, report:

```text
file
line number
error
suggested fix
```

Do not continue to execution validation if syntax validation fails.

***

## 6.4 Cache validation

Run:

```bash
python .graphite-agent/tools/validate_cache.py
```

Expected result:

```json
{
  "status": "pass"
}
```

or equivalent.

If it fails, report:

```text
missing artefact
why it matters
command to regenerate it
```

***

## 6.5 Decision revocation test

Revoke the revised decision:

```bash
python .graphite-agent/tools/revoke_decision.py \
  --decision <decision_id> \
  --branch <branch> \
  --reason "QA revoke decision"
```

Verify:

```text
[ ] a decision_revoked event is appended.
[ ] current_decisions.json no longer treats the revoked decision as active.
[ ] execution_plan.json is rebuilt.
[ ] the branch returns to triage unless another active decision applies.
```

***

## 6.6 Rebuild plan test

Run:

```bash
python .graphite-agent/tools/rebuild_plan.py
```

Verify:

```text
[ ] outputs/execution_plan.json is updated.
[ ] .graphite-agent/plan.json is updated.
[ ] decisions are reflected in execution entries.
[ ] decision_provenance appears where decisions affected the plan.
```

***

## 6.7 Final QA report format

After testing, produce a final report with this exact structure:

```text

## 6.8 File presence

PASS/FAIL
Missing files:
- ...

## 6.9 Syntax validation

PASS/FAIL
Details:
- ...

## 6.10 Question queue

PASS/FAIL/NOT_APPLICABLE
Open question count:
- ...

## 6.11 Decision lifecycle

PASS/FAIL
Verified:
- decide
- revise
- revoke
- history
- current decision projection

## 6.12 Local enhancement compatibility

PASS/FAIL/NOT_APPLICABLE
Details:
- ...

## 6.13 Decision lifecycle validation

Test decision lifecycle on a non-executable branch.

## 6.14 Revoke

```bash
python .graphite-agent/tools/revoke_decision.py ...
```

Verify:

```text
[ ] revoked decision is no longer active
[ ] branch returns to triage unless another active decision applies
[ ] plan validation reflects the revocation
```

Fail if decisions are overwritten instead of append-only.

***

## 6.15 Required QA report

Produce the final report in this exact format:

```text

## 6.16 File and command presence

PASS/FAIL
Missing:
- ...

## 6.17 Decision lifecycle

PASS/FAIL
Verified:
- record
- revise
- revoke
- history
- current projection

## 6.18 Rework dry-run

PASS/FAIL
Mutation observed:
- yes/no

## 6.19 Required workbooks and runbooks

Implement these documentation/runbook files.

## 6.20 Required unit tests

Add tests for the following fixtures.
