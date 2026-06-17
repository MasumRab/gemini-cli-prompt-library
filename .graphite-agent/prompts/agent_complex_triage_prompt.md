# Agent Complex Triage Prompt

When diagnosing complex branches:

1. Start with summary, target matrix, root health, triage packet
2. Show relationship evidence for blocked branches
3. Ask only generated bounded questions
4. Record decisions append-only to `decision_log.jsonl`
5. Validate before execution

Do not start from raw Git commands unless targeted inspection needed.