---
name: jules-session-manager
description: Manage Google Jules AI sessions - list, inspect activities, send messages, and track PR tasks with integrated session-PR correlation
triggers:
  - jules session
  - jules api
  - inspect jules sessions
  - session-pr mapping
  - /jules-triage
allowed-tools:
  - terminal
  - python3
  - tools/pr/session_pr_triage.py
  - tools/utils/auth_manager.py
  - tools/utils/pre_flight_check.sh
  - tools/api/jules_api_client.py
dependencies:
  - PyGithub
  - python-dotenv
---

# Jules Session Manager

## Overview
Enhanced session manager with integrated Session-PR correlation capabilities. Uses the new architectural framework for authentication and bidirectional mapping between Jules sessions and GitHub PRs.

## Usage

### Recommended Workflow
```bash
# Step 1: Run pre-flight checks
./tools/utils/pre_flight_check.sh

# Step 2: List all active sessions
python3 tools/sessions/jules_list_sessions.py

# Step 3: Correlate sessions with PRs (comprehensive triage)
python3 tools/pr/session_pr_triage.py --repo <owner>/<repo>

# Step 4: Inspect specific session activities
python3 tools/sessions/jules_list_activities.py <SESSION_ID>
```

### Legacy Scripts
```bash
# Basic session listing (legacy bash script)
skills/jules-session-manager/scripts/list_sessions.sh

# Dry-run mode for testing
skills/jules-session-manager/scripts/list_sessions.sh --dry-run
```

### Agent Invocation
- "List Jules sessions"
- "Inspect session activities"
- "Check Jules API"
- "Map sessions to PRs"
- "/jules-list"
- "/jules-inspect"
- "/jules-triage"

## Capabilities
- **Session Listing**: Fetch all Jules sessions with state filtering
- **Activity Inspection**: Retrieve detailed session activity logs
- **Message Sending**: Send messages to active sessions
- **Session-PR Correlation**: Bidirectional mapping between sessions and PRs
- **Branch Name Extraction**: Extract session IDs from branch names
- **PR Link Detection**: Scan activities for PR creation links
- **JSON Export**: Save session-PR mappings to session_pr_map.json

## Authentication
Uses centralized auth manager for validation:
```bash
python3 tools/utils/auth_manager.py
```

Required environment variables:
- `JULES_API_KEY` - Jules API key (validated against placeholder patterns)
- `GITHUB_TOKEN` - GitHub personal access token with repo scope

## Pre-Flight Checks
Always run before session operations:
```bash
./tools/utils/pre_flight_check.sh
```

Checks performed:
1. Authentication validation
2. Clean working directory verification
3. Branch safety (warns if on main)

## Examples

### Full Session-PR Triage
```bash
# Run comprehensive correlation analysis
python3 tools/pr/session_pr_triage.py --repo <owner>/<repo>
```

Output:
```
================================================================================
SESSION ID           PR #       CONFIDENCE   METHOD
================================================================================
2977177834934208195  #66        High         Activity Log: PR Link Detected
2977177834934208196  #65        Medium       PR Branch Name Match
================================================================================
Total Mapped: 2
💾 Saved detailed map to session_pr_map.json
```

### List Sessions by State
```bash
python3 tools/sessions/jules_list_sessions.py --state IN_PROGRESS
```

### Inspect Session Activities
```bash
python3 tools/sessions/jules_list_activities.py 2977177834934208195 --limit 50
```

## Session-PR Mapping Methods

The triage tool uses multiple methods to correlate sessions with PRs:

1. **Activity Log: Branch Creation** - Detects `git checkout -b` commands in session activities
2. **Activity Log: PR Link Detected** - Scans for GitHub PR URLs in agent messages
3. **PR Branch Name Match** - Matches session IDs in branch names (session-*, jules-*, task-*)

## Related Runbooks
- See `docs/runbooks/SESSION_RECOVERY.md` for recovery procedures
- See `docs/runbooks/GITHUB_INTEGRATION.md` for PR workflow guidelines
- See `docs/runbooks/AUTH_SETUP.md` for authentication troubleshooting
