---
name: jules-workflows
description: Common Jules workflow patterns for automated tasks, interactive sessions, and analysis-driven follow-ups. Use when planning Jules sessions, setting up automated workflows, or responding to completed Jules work. Trigger keywords: jules workflow, jules automation, jules follow-up.
---

# Jules Workflows

Common patterns for working with Jules AI coding agent.

---

## Workflow 1: Fire and Forget

Fully automated task execution.

```bash
# Create session with auto-PR
jules new --repo MasumRab/EmailIntelligent --branch main \
  "Add input validation to all API endpoints" \
  --auto-pr

# Or via API
curl -X POST "https://jules.googleapis.com/v1alpha/sessions" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Add input validation to all API endpoints",
    "source": { "github": "MasumRab/EmailIntelligence", "baseBranch": "main" },
    "autoPr": true
  }'

# Poll for completion (API)
while true; do
  STATE=$(curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID" \
    -H "x-goog-api-key: $JULES_API_KEY" | jq -r '.state')
  [[ "$STATE" == "COMPLETED" || "$STATE" == "FAILED" ]] && break
  sleep 30
done
```

---

## Workflow 2: Interactive with Approval

Review plan before execution.

```bash
# 1. Create session
SESSION_ID=$(curl -s -X POST "https://jules.googleapis.com/v1alpha/sessions" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Refactor authentication module"}' \
  | jq -r '.name')

# 2. Poll until plan ready
while true; do
  STATE=$(curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID" \
    -H "x-goog-api-key: $JULES_API_KEY" | jq -r '.state')
  [[ "$STATE" == "AWAITING_PLAN_APPROVAL" ]] && break
  sleep 5
done

# 3. Review plan
curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID/activities" \
  -H "x-goog-api-key: $JULES_API_KEY" | jq '.[] | select(.type == "PLAN_GENERATED")'

# 4. Approve or reject
curl -X POST "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID:approve" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" -d '{}'
```

---

## Workflow 3: Analysis → Follow-up

Use completed session insights to create new tasks.

```bash
# 1. Analyze what was done
jq '.outputs[].pullRequest' jules_sessions/pr437_session.json
# Output: {"url": "https://github.com/.../pull/437", "title": "..."}

# 2. Check files modified
jq -r '.outputs[].changeSet.gitPatch' jules_sessions/pr437_session.json | \
  grep "^diff --git" | sed 's/diff --git a\///' | cut -d' ' -f1

# 3. Craft follow-up prompt
jules new --repo MasumRab/EmailIntelligence \
  "Continue optimization work from PR #437. Focus on query caching in the files that were modified."
```

---

## Workflow 4: Parallel Sessions

Run multiple agents on variations.

```bash
# Create 3 parallel sessions
for task in "optimize queries" "add caching" "improve indexes"; do
  jules new --repo MasumRab/EmailIntelligence --parallel 3 "$task"
done

# Or sequential with dependencies
jules new "Add database connection pooling"
# Wait for completion, then:
jules new "Add query result caching on top of connection pooling"
```

---

## Workflow 5: Session → Local Patch

Apply Jules changes locally without PR.

```bash
# 1. Pull session patch
jules remote pull --session SESSION_ID > .jules/diff.patch

# 2. Review
git apply --stat .jules/diff.patch

# 3. Apply to working directory
git apply .jules/diff.patch

# Or apply and stage
git apply --index .jules/diff.patch && git commit -m "Apply Jules changes"
```

---

## Workflow 6: Branch-Specific Work

Target specific branches.

```bash
# Work on scientific branch
jules new --repo MasumRab/EmailIntelligence \
  --branch scientific \
  "Optimize ML model inference"

# Work on feature branch
jules new --repo MasumRab/EmailIntelligence \
  --branch feature/new-api \
  "Add new endpoint for user preferences"
```

---

## Workflow 7: From Issue to PR

Convert GitHub issue to Jules task.

```bash
# Get issue title
ISSUE_TITLE=$(gh issue view 123 --json title -q .title)

# Create session
jules new --repo MasumRab/EmailIntelligence \
  "Fix issue #123: $ISSUE_TITLE"

# Or with full issue body
gh issue view 123 --json body,title | \
  jq -r '"Fix issue #123: \(.title)\n\n\(.body)"' | \
  jules new --repo MasumRab/EmailIntelligence
```

---

## Workflow 8: Session Archive

Save session data for future reference.

```bash
# After session completes, save to project
SESSION_ID="15863163327149061241"
PR_NUM="571"

mkdir -p jules_sessions

# Get session data
curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  > "jules_sessions/pr${PR_NUM}_session.json"

# Get activities
curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID/activities" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  > "jules_sessions/pr${PR_NUM}_activities.json"
```

---

## Error Recovery

### Session Stuck in `IN_PROGRESS`

```bash
# Check activities for last update
curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID/activities?pageSize=1&orderBy=createTime%20desc" \
  -H "x-goog-api-key: $JULES_API_KEY"

# Cancel if needed
curl -X POST "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID:cancel" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" -d '{}'
```

### Plan Not Approved

```bash
# Approve immediately
curl -X POST "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID:approve" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" -d '{}'
```

---

## Workflow 9: Handling Timeouts (WIP Recovery)

When Jules times out ("unable to complete task in time"), recover and continue.

### Pattern: Identify WIP State

```bash
# Find commits mentioning Jules timeout
git log --oneline --grep="Jules was unable to complete"

# Check session files for incomplete state
jq 'select(.state != "COMPLETED") | {id, state, title}' jules_sessions/*_session.json
```

### Pattern: Continue from WIP

```bash
# 1. Check what was accomplished
git log --oneline FEATURE_BRANCH | head -5

# 2. Review partial changes
git diff main...FEATURE_BRANCH --stat

# 3. Create follow-up session
jules new --repo owner/repo \
  "Continue work from timed-out session. Branch has partial implementation." \
  --branch FEATURE_BRANCH
```

### Common WIP Scenarios

| Scenario | State | Recovery |
|----------|-------|----------|
| Partial commit | Some files committed | Review commit, create follow-up |
| No commit | No changes saved | Check session, restart with refined prompt |
| Plan approved, not executed | `AWAITING_PLAN_APPROVAL` | Re-create session with same prompt |
| Build/test failures | Changes don't pass | Fix locally, create focused follow-up |

### Refining Prompts After Timeout

Based on WIP analysis:

```bash
# If task was too broad:
jules new "Perform ONLY step 1 of the previous task: Setup database schema"

# If task hit blockers:
jules new "Complete the same task, but skip the failing test module"

# If task needs more context:
jules new "Same task. Key context: The auth module uses OAuth2, not Basic auth."
```

---

## Workflow 10: Project-Specific Patterns

### EmailIntelligence Examples

Based on `jules_sessions/prompts.md`:

```bash
# Foundation tasks (sequential)
jules new --repo MasumRab/EmailIntelligence --branch scientific \
  "Execute Task 1: Recover Lost Backend Modules. Audit Git history for lost commits..."

jules new --repo MasumRab/EmailIntelligence --branch scientific \
  "Execute Task 2: Backend Migration from 'backend' to 'src/backend'..."

# Enhancement tasks (parallel, max 3)
jules new --repo MasumRab/EmailIntelligence --branch scientific \
  "Execute Task 11.1: Refactor High-Complexity AI Modules..."

jules new --repo MasumRab/EmailIntelligence --branch scientific \
  "Execute Task 11.3: Leverage Scientific Security Framework..."
```

### Pre-Formatted Prompts

See `jules_sessions/prompts.md` for copy-paste ready prompts:

```bash
# List available prompts
grep "^## Task" jules_sessions/prompts.md

# Extract specific prompt
sed -n '/^## Task 1:/,/^## Task 2:/p' jules_sessions/prompts.md
```

---

## Error Recovery

### Session Stuck in `IN_PROGRESS`

```bash
# Check activities for last update
curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID/activities?pageSize=1&orderBy=createTime%20desc" \
  -H "x-goog-api-key: $JULES_API_KEY"

# Cancel if needed
curl -X POST "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID:cancel" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" -d '{}'
```

### Plan Not Approved

```bash
# Approve immediately
curl -X POST "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID:approve" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" -d '{}'
```

---

## References

- CLI commands: [[jules-cli]]
- API reference: [[jules-api]]
- Session analysis: [[jules-sessions]]
- Scheduling: [[jules-scheduling]]
- WIP analysis: `jules_sessions/wip_analysis.md`
- Task prompts: `jules_sessions/prompts.md`
- Schedule JSON: `jules_sessions/task_schedule.json`

---

## Scripts

### `skills/jules-workflows/scripts/conflict_predictor.py`

Predict merge conflicts before they occur.

```python
from conflict_predictor import ConflictPredictor, ConflictType, ConflictSeverity

predictor = ConflictPredictor()
prediction = predictor.predict_conflicts([file_change1, file_change2])

# Returns: file_path, conflict_type, severity, confidence, suggested_resolution
```

### `skills/jules-workflows/scripts/intelligent_merge_analyzer.py`

Analyze merge strategies and identify optimal approaches.

```bash
# Analyze potential merge between branches
python skills/jules-workflows/scripts/intelligent_merge_analyzer.py --source feature/abc --target main

# Get merge recommendations
python skills/jules-workflows/scripts/intelligent_merge_analyzer.py --analyze --json
```
