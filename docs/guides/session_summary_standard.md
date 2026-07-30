# Session Summary Standard

## Problem

Jules AI agent activity and session files can grow to **hundreds of megabytes** — they contain full `unidiffPatch` git diffs, raw file changes, and detailed conversation transcripts. While this detailed data is valuable for auditing and reconstruction, it is impractical for:

- Quick review of what happened in a session
- Triaging multiple sessions at once
- Sharing session outcomes with team members
- Building dashboards or reports

## Solution

Every extensive session/activity file MUST have a companion **summary file** that captures the essential information in a compact, human-readable format.

---

## Summary File Specification

### Naming Convention

| Full file pattern                    | Summary file pattern                      |
| ------------------------------------ | ----------------------------------------- |
| `activities_<id>.json`                 | `activities_<id>_summary.yaml`              |
| `activities_pr_<id>.json`              | `activities_pr_<id>_summary.yaml`           |
| `current_sessions.json`                | `current_sessions_summary.yaml`             |
| `jules_sessions.json`                  | `jules_sessions_summary.yaml`               |

Summary files MUST be placed in the **same directory** as the full file they summarize.

### Format

Use **YAML** (`.yaml` extension). YAML is chosen because:

- More human-readable than JSON for summaries
- Supports comments
- Diff-friendly in code review
- Easy to parse with standard libraries

### Required Fields

Every summary file MUST contain these top-level keys:

```yaml
session:
  id: "<string>"                    # Session ID from the original file
  title: "<string>"                 # Session title/headline
  repository: "<string>"            # Target repository name (e.g., "EmailIntelligence")
  created: "<ISO 8601 timestamp>"   # Session creation time
  updated: "<ISO 8601 timestamp>"   # Last update time
  status: "<enum>"                  # One of: completed, failed, in_progress, awaiting_approval, awaiting_feedback, paused
  source: "<string>"                # Source context (e.g., "pr", "issue", "manual")
```

### Optional but Recommended Fields

```yaml
purpose: "<string>"                 # Brief description of the session goal (1-3 sentences)
  
summary: |
  <multi-line string>               # Free-text narrative summary of what happened
  Key decisions, outcomes, and
  notable events.

participants:                       # Ordered list of key interactions
  - role: user                      # "user" or "agent"
    message: "<truncated message>"  # First 200 chars of important messages
  - role: agent
    message: "<truncated message>"

changes:                            # List of file changes made
  - file: "<file path>"            # Path to changed file
    summary: "<string>"            # Brief description of the change (1 sentence)
    change_type: "<enum>"          # One of: added, modified, deleted, renamed
    suggested_commit: "<string>"   # The suggested commit message from the agent
    base_commit: "<string>"        # The base commit SHA before the change

plan:                               # The session's plan if available
  steps:                            # Ordered list of plan steps
    - "<string>"                    # Step description
    - "<string>"

pr:                                 # If the session resulted in a PR
  url: "<string>"                  # Full GitHub PR URL
  title: "<string>"                # PR title
  number: <int>                    # PR number (optional)

errors:                             # If the session failed or had errors
  - type: "<string>"               # Error type
    message: "<string>"            # Error message (truncated to 200 chars)
```

### Field Constraints

| Field                | Max length | Why                                  |
| -------------------- | ---------- | ------------------------------------ |
| `purpose`              | 500 chars  | Forces concise goal description      |
| `summary`              | 2000 chars | Enough for a solid narrative         |
| `message` (per message) | 200 chars  | Prevents bloated summaries           |
| `changes[].summary`    | 200 chars  | One sentence per change              |
| Total file size       | 50 KB      | Keeps summaries fast to load/review  |

### What goes in the SUMMARY vs the FULL file

| Data                                | Summary | Full file |
| ----------------------------------- | ------- | --------- |
| Session ID and metadata             | ✅       | ✅         |
| Session purpose / goal              | ✅       | ❌         |
| High-level narrative summary        | ✅       | ❌         |
| List of changed files + descriptions | ✅       | ✅         |
| Key conversation messages           | ✅ (truncated) | ✅ (full)  |
| Plan steps                          | ✅       | ✅         |
| Final status / outcome              | ✅       | ✅         |
| Full `unidiffPatch` git diffs        | ❌       | ✅         |
| Complete conversation transcript    | ❌       | ✅         |
| Raw API response data               | ❌       | ✅         |
| Full error stack traces             | ❌       | ✅         |
| Redundant timestamp snapshots       | ❌       | ✅         |

---

## Example Summary File

```yaml
session:
  id: "8645133856938915124"
  title: "fix: auth bypass in registration endpoint"
  repository: "EmailIntelligence"
  created: "2026-03-27T15:08:25.118093Z"
  updated: "2026-03-27T16:45:12.340912Z"
  status: completed
  source: pr

purpose: >
  Fix a critical security vulnerability where unauthenticated users could
  bypass registration validation due to incorrect middleware ordering.

summary: |
  The agent analyzed the auth middleware chain and discovered that the
  session validation middleware was running before the registration
  validation middleware, allowing requests with invalid sessions to skip
  registration checks entirely.
  
  Fix: Reordered the middleware registration so registration validation
  runs first. Added comprehensive regression tests.
  
  Outcome: PR created and merged successfully. No regressions detected.

participants:
  - role: user
    message: "We have a critical auth bypass in the registration endpoint"
  - role: agent
    message: "Found the issue — middleware ordering is incorrect in auth/chain.py"
  - role: user
    message: "Approved. Go ahead and fix it."

changes:
  - file: src/auth/middleware.py
    summary: "Reordered middleware checks — registration validation now runs before session check"
    change_type: modified
    suggested_commit: "fix: reorder middleware checks to prevent auth bypass"
    base_commit: "387b2d02fdebe89f414a3f0a69bdb784b4b5d5ad"
  - file: tests/test_auth.py
    summary: "Added regression tests for registration with invalid session tokens"
    change_type: modified
    suggested_commit: "test: add regression tests for auth bypass fix"

plan:
  steps:
    - "Analyze current middleware ordering in auth chain"
    - "Identify the ordering vulnerability"
    - "Reorder checks: registration validation before session validation"
    - "Add regression tests"
    - "Run existing test suite to verify no regressions"

pr:
  url: "https://github.com/MasumRab/EmailIntelligence/pull/632"
  title: "fix: auth bypass in registration endpoint"
```

---

## Automation

Use the companion script `scripts/generate_session_summaries.py` to:

- **Batch-generate** summaries for existing activity/session files
- **Update** summaries when full files are refreshed
- **Validate** existing summaries against the standard

See the script's `--help` for usage details.

---

## Compliance

- All newly generated session/activity files SHOULD include a companion summary
- Existing files SHOULD have summaries generated retroactively using the automation script
- CI or pre-commit hooks MAY validate that summary files exist alongside any full activity files exceeding 1 MB
- Summary files SHOULD be tracked in git (unlike the full files which may be gitignored)

---

## Retention Policy

| Scenario                                  | Keep full file? | Keep summary? |
| ----------------------------------------- | --------------- | ------------- |
| Active session (in progress)              | ✅ Yes           | ✅ Yes         |
| Completed session with PR merged          | ❌ No (data in git) | ✅ Yes      |
| Completed session without PR              | ✅ Yes           | ✅ Yes         |
| Failed session (need debugging)           | ✅ Yes           | ✅ Yes         |
| Failed session (resolved, no longer needed) | ❌ Delete       | ⚠️ Optional  |
| Redundant snapshot (newer version exists) | ❌ Keep newest   | ✅ Keep        |
