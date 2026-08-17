---
name: jules-sessions
description: "Analyze local Jules session JSON files and SQLite store to track PR status, completion state, and generate context-aware response messages for sessions needing action (approval, nudge, follow-up). Use when reviewing Jules work, responding to sessions, or checking what messages to send."
category: [ai, analysis, session-management]
type: [guide, analysis]
tags: [jules, sessions, analysis, pr-tracking, status, responses, nudge]
trigger_keywords:
  - jules session
  - jules pr
  - jules status
  - jules response
  - analyze jules
  - jules nudge
  - session analysis
dependencies: [jules-session-manager]
usage_context:
  - when: "reviewing Jules work"
    confidence: high
  - when: "responding to sessions"
    confidence: high
  - when: "checking session status"
    confidence: high
complexity: moderate
frequency: frequent
auto_load: context
---

# Jules Session Analysis

Analyze local `jules_sessions/` directory and SQLite store to track work completed by Jules.

## Dual Storage Approach

The Jules session tracking system uses a dual storage approach for redundancy and performance:

1. **Local JSON Files** (`jules_sessions/` directory): 
   - Original storage format for session metadata and activities
   - Human-readable and easily backupable
   - Used for quick analysis and debugging

2. **SQLite Store** (`jules_sessions_store.db`):
   - Enhanced storage with additional fields and indexing
   - Supports complex queries and filtering
   - Maintains session history and retry tracking
   - Provides utility functions for common operations

## Directory Structure

```
jules_sessions/
├── pr437_session.json      # Session metadata
├── pr437_activities.json   # Step-by-step actions
├─┬ jules_sessions_store.db # SQLite store with enhanced fields
│ └── (internal tables)
├── pr521_session.json
├── pr521_activities.json
└── README.md
```

## Session File Schema

### `pr{N}_session.json`

```json
{
  "id": "15863163327149061241",
  "name": "sessions/15863163327149061241",
  "title": "⚡ Bolt: Optimize Database Search",
  "state": "COMPLETED",
  "createTime": "2025-01-15T10:00:00Z",
  "updateTime": "2025-01-15T12:30:00Z",
  "sourceContext": {
    "source": "sources/github/MasumRab/EmailIntelligence",
    "githubRepoContext": { "startingBranch": "scientific" }
  },
  "prompt": "...",
  "url": "https://jules.google.com/session/...",
  "outputs": [{
    "changeSet": { "gitPatch": "diff --git a/..." },
    "pullRequest": {
      "url": "https://github.com/MasumRab/EmailIntelligence/pull/437",
      "title": "⚡ Bolt: Optimize Database Search"
    }
  }]
}
```

### SQLite Store Enhanced Fields

The SQLite store includes all original fields plus these additional columns:

| Field | Description |
|-------|-------------|
| `session_type` | Type of session (e.g., "initial", "retry", "follow-up") |
| `outcome` | Final result of the session (e.g., "success", "failed", "timeout") |
| `retry_of_session_id` | ID of the original session if this is a retry |
| `retry_count` | Number of times this session has been retried |
| `send_message_count` | Number of messages sent to this session |
| `verdict` | Final assessment of the session quality |
| `quality_score` | Numeric score (0-100) indicating session quality |

### Key Fields (JSON Files)

| Field | Description |
|-------|-------------|
| `state` | `QUEUED`, `IN_PROGRESS`, `AWAITING_PLAN_APPROVAL`, `COMPLETED`, `FAILED` |
| `outputs[].pullRequest.url` | GitHub PR link |
| `outputs[].changeSet.gitPatch` | The actual diff |
| `sourceContext.githubRepoContext.startingBranch` | Target branch |

## JulesSessionStore API Examples

### Filtering by New Fields

```python
from skills.jules-sessions.jules_session_store import JulesSessionStore

# Initialize store
store = JulesSessionStore("jules_sessions_store.db")

# Find all retry sessions
retries = store.find_sessions(session_type="retry")
print(f"Found {len(retries)} retry sessions")

# Find failed sessions that are retryable
failed_retries = store.find_retryable_failed_sessions()
print(f"Found {len(failed_retries)} retryable failed sessions")

# Find sessions with low quality scores
low_quality = store.find_sessions(quality_score__lt=50)
print(f"Found {len(low_quality)} low quality sessions")

# Find sessions with many message sends (potentially stuck)
high_message_count = store.find_sessions(send_message_count__gt=10)
print(f"Found {len(high_message_count)} sessions with high message count")

# Find sessions by outcome
timeouts = store.find_sessions(outcome="timeout")
print(f"Found {len(timeouts)} timed out sessions")
```

### Using Utility Methods

```python
from skills.jules-sessions.jules_session_store import JulesSessionStore

store = JulesSessionStore("jules_sessions_store.db")

# Find stale sessions (no updates in last 24 hours)
stale = store.find_stale_sessions(hours=24)
print(f"Found {len(stale)} stale sessions")

# Record sending a message to a session
store.record_send_message("session_12345")
print("Recorded message send for session 12345")

# Record a retry session
store.record_retry_session(
    original_session_id="session_12345",
    new_session_id="session_67890",
    retry_count=1
)
print("Recorded retry session")

# Finalize a session with outcome and quality score
store.finalize_session(
    session_id="session_12345",
    outcome="success",
    verdict="All objectives met",
    quality_score=85
)
print("Finalized session 12345")
```

## Query Commands

### List All Sessions

```bash
jq -r '"\(.id | split("/")[-1]) \(.state) \(.title)"' jules_sessions/*_session.json
```

### Get Completed Sessions

```bash
jq -r 'select(.state == "COMPLETED") | .title' jules_sessions/*_session.json
```

### Get All PR URLs

```bash
jq -r '.outputs[]?.pullRequest?.url // empty' jules_sessions/*_session.json
```

### Sessions by Branch

```bash
jq -r 'select(.sourceContext.githubRepoContext.startingBranch == "scientific") | .title' \
    jules_sessions/*_session.json
```

### Session Statistics

```bash
jq -s 'group_by(.state) | map({state: .[0].state, count: length})' \
    jules_sessions/*_session.json
```

### Extract Git Patch

```bash
jq -r '.outputs[].changeSet.gitPatch' jules_sessions/pr437_session.json > pr437.patch
git apply pr437.patch
```

### Find Sessions Awaiting Action

```bash
jq -r 'select(.state == "AWAITING_PLAN_APPROVAL" or .state == "IN_PROGRESS") | "\(.id) \(.title)"' \
    jules_sessions/*_session.json
```

## Session Response Guide

Determine what response/nudge to send based on session state and context.

### Response Categories

| Category | State | Action | Priority |
|----------|-------|--------|----------|
| Plan Approval | `AWAITING_PLAN_APPROVAL` | Approve plan | 1 |
| Nudge | `IN_PROGRESS` > 30min | Check status | 2 |
| No Changes | `COMPLETED` no diff | Ask what happened | 3 |
| No PR | `COMPLETED` no PR | Request PR creation | 3 |
| PR Stale | `COMPLETED` PR exists | Review/merge | 4 |
| Failed | `FAILED` | Restart refined | 2 |
| Timeout | Timed out | Restart refined | 2 |

### Quick Check Command

```bash
# Check all sessions needing response
python skills/jules-sessions/scripts/check_needs_response.py

# Pull latest from API first (hybrid)
python skills/jules-sessions/scripts/check_needs_response.py --api

# Output as JSON for scripting
python skills/jules-sessions/scripts/check_needs_response.py --json
```

### Manual Analysis

```bash
# Find sessions awaiting your action
jq -r 'select(.state == "AWAITING_PLAN_APPROVAL" or .state == "IN_PROGRESS") |
   "\(.name | split("/")[-1]) :: \(.state) :: \(.title)"' \
   jules_sessions/*_session.json

# Check if completed session has changes
jq '{session: .name, has_changes: (.outputs[].changeSet.gitPatch | length > 0),
     has_pr: (.outputs[].pullRequest.url != null)}' \
   jules_sessions/pr*_session.json
```

### Message Templates

Use `references/response_templates.md` for context-aware messages:

```bash
# View all templates
cat references/response_templates.md

# Quick reference for specific scenario
grep -A10 "AWAITING_PLAN_APPROVAL" references/response_templates.md
```

**Template includes:**
- Original session intent from prompt
- Current state and what happened
- Suggested response incorporating context
- Example with real session data

## Scripts

### `skills/jules-sessions/scripts/analyze_sessions.sh`

```bash
#!/bin/bash
# Usage:
#   ./skills/jules-sessions/scripts/analyze_sessions.sh --status      # All sessions with state
#   ./skills/jules-sessions/scripts/analyze_sessions.sh --pr-links    # PR URLs
#   ./skills/jules-sessions/scripts/analyze_sessions.sh --pending     # Sessions needing action
#   ./skills/jules-sessions/scripts/analyze_sessions.sh --summary      # One-line per PR
```

### `skills/jules-sessions/scripts/sync_session.sh`

```bash
#!/bin/bash
# Pull session from Jules API and save locally
# Requires: JULES_API_KEY

SESSION_ID=$1
curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  > "jules_sessions/session_${SESSION_ID}.json"
```

### `skills/jules-sessions/scripts/list_prs_by_deletions.py`

```bash
# List PRs with >300 deletions
python skills/jules-sessions/scripts/list_prs_by_deletions.py --threshold 300

# Check all PRs (open/closed/merged)
python skills/jules-sessions/scripts/list_prs_by_deletions.py --state all --limit 50

# Output as JSON
python skills/jules-sessions/scripts/list_prs_by_deletions.py --json --threshold 500
```

### `skills/jules-sessions/scripts/branch_analysis_tool.py`

```bash
# Full branch analysis
python skills/jules-sessions/scripts/branch_analysis_tool.py

# JSON output
python skills/jules-sessions/scripts/branch_analysis_tool.py --json

# Check stale branches (>30 days)
python skills/jules-sessions/scripts/branch_analysis_tool.py --check-stale --max-stale-days 30
```

### `skills/jules-sessions/scripts/check_needs_response.py`

```bash
# List sessions needing action
python skills/jules-sessions/scripts/check_needs_response.py

# Hybrid: pull latest from API first
python skills/jules-sessions/scripts/check_needs_response.py --api --stale-minutes 20

# JSON output
python skills/jules-sessions/scripts/check_needs_response.py --json
```

**Output includes:**
- Session ID, title, state
- Recommended action (approve/nudge/request PR/etc.)
- Pre-generated message template with context

## Analysis Patterns

### Find Successful Patterns

```bash
# What prompts led to success?
jq -r 'select(.state == "COMPLETED") | .prompt' jules_sessions/*_session.json | \
  head -5
```

### Find Failed Sessions

```bash
jq -r 'select(.state == "FAILED") | "\(.title)\n\(.outputs[]?.error // .state)"' \
    jules_sessions/*_session.json
```

### Extract File Changes

```bash
# What files were modified?
jq -r '.outputs[].changeSet.gitPatch' jules_sessions/pr437_session.json | \
  grep "^diff --git" | sed 's/diff --git a\///' | cut -d' ' -f1 | sort -u
```

## Bundled References

The skill includes reference files in `references/`:

| File | Usage |
|------|-------|
| `wip_analysis.md` | Patterns for recovering timed-out Jules sessions |
| `task_schedule.json` | Example 11-task orchestration schedule |
| `prompts.md` | Pre-formatted prompts for EmailIntelligence |

Load when needed:

```bash
# View WIP patterns
cat references/wip_analysis.md

# Use schedule schema
jq '.' references/task_schedule.json

# Copy ready-made prompts
grep "^## Task" references/prompts.md
```

## Integration with Other Skills

- **CLI**: Use [[jules-cli]] to create new sessions based on analysis
- **API**: Use [[jules-api]] to fetch session data from Jules
- **Workflows**: Use [[jules-workflows]] for follow-up patterns
- **Scheduling**: Use [[jules-scheduling]] for multi-task orchestration

## References

- `jules_sessions/README.md` — Local session documentation
- `references/wip_analysis.md` — Timeout recovery patterns
- `references/task_schedule.json` — Schedule schema example
- `references/prompts.md` — Pre-formatted task prompts (planned)
- `references/sent_responses.md` — **Log of actual prompts sent** (continuously updated)
- `references/response_templates.md` — Context-aware message templates for:
  - Plan approval
  - Nudging stuck sessions
  - Follow-up when no changes made
  - Requesting PR creation
  - Restarting failed/timed-out sessions
- Session files use the same schema as Jules API responses

## Prompt Tracking Workflow

After sending a response, log it for future reference:

```bash
# View existing sent prompts
cat references/sent_responses.md

# Format for new entry
### Entry YYYY-MM-DD-XXX
session_id: "<id>"
prompt_type: "<initial|follow-up|nudge|approve|rectification>"
prompt_sent: |
  <your message>
outcome: "<result or PENDING>"
```

### When Jules Makes Mistakes

If the outcome was undesirable and required follow-up to fix:

1. **Document the pattern** in `references/sent_responses.md` under "Prompt Improvements Log"
2. **Include:**
   - Original prompt
   - What went wrong
   - Follow-up required
   - Improved prompt formulation
3. **Check before future prompts:**
   ```bash
   cat references/sent_responses.md | grep -A20 "prompt_improvement"
   ```

**Recorded patterns from WIP analysis:**

| Problem | Prevention |
|---------|-----------|
| Timeout from broad scope | Break into subtasks, specify files |
| Over-deletion | "Do NOT delete, only modify" |
| Broken test paths | "Verify these paths remain valid" |
| Circular dependencies | "Avoid circular imports between X and Y" |
| Lost documentation content | "Preserve ALL content from source" |

**Why track?**
- Learn what prompts lead to success
- Reference similar past situations
- Avoid repeating failed approaches
- Build institutional knowledge
- Improve prompts proactively