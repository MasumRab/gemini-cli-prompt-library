---
name: wrapup-session
description: "Generate session summary reports and wrap-up documentation with QA status - integrated with new architectural framework"
category: [ai, documentation, reporting]
type: [guide, tool]
tags: [wrapup, sessions, summaries, reporting, qa, documentation]
trigger_keywords:
  - wrapup
  - session summary
  - /wrapup
  - generate report
  - session-pr correlation
  - wrapup session
dependencies:
  - jules-sessions
  - jules-session-manager
usage_context:
  - when: "generating session summaries"
    confidence: high
  - when: "creating wrap-up documentation"
    confidence: high
  - when: "QA status reporting"
    confidence: high
complexity: simple
frequency: occasional
auto_load: context
---

# Wrapup Session

## Overview
Enhanced wrapup session skill integrated with the new architectural framework for authentication and pre-flight validation. Generates comprehensive session summaries with PR correlation and QA status.

## Recommended Workflow
```bash
# Step 1: Run pre-flight checks
./tools/utils/pre_flight_check.sh

# Step 2: Correlate sessions with PRs first
python3 tools/pr/session_pr_triage.py --repo <owner>/<repo>

# Step 3: Generate wrapup with QA status
skills/wrapup-session/scripts/wrapup_session.sh --include-qa-status

# Step 4: Or specify output format
skills/wrapup-session/scripts/wrapup_session.sh --output-format markdown
```

## Authentication
Uses centralized auth manager for validation:
```bash
python3 tools/utils/auth_manager.py
```

Required environment variables:
- `JULES_API_KEY` - Jules API key for session data
- `GITHUB_TOKEN` - GitHub personal access token for PR data

## Pre-Flight Checks
Always run before wrapup operations:
```bash
./tools/utils/pre_flight_check.sh
```

Checks performed:
1. Authentication validation
2. Clean working directory verification
3. Branch safety (warns if on main)

## Capabilities
- Generate session summary reports
- Include QA status and test results
- Correlate sessions with GitHub PRs
- Export to multiple formats (Markdown, JSON)
- Include activity timeline
- Document code changes and decisions

## Integration with Other Skills
This skill works alongside:
- **jules-session-manager**: Fetch session activities and metadata
- **github-pr-triage**: Include PR correlation in wrapup
- **github-pr-review**: Reference review feedback in summary

## Related Runbooks
- See `docs/runbooks/SESSION_RECOVERY.md` for session troubleshooting
- See `docs/runbooks/GITHUB_INTEGRATION.md` for PR workflow guidelines
- See `docs/runbooks/AUTH_SETUP.md` for authentication troubleshooting
