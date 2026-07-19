# Architecture

## Consolidation Design

### Problem
68 unique Jules-related items scattered across 7 locations:
- `~/.agents/skills/` (7 skills)
- `~/.agents/commands/` (wrapper commands)
- `~/.gemini/extensions/` (Gemini CLI extension)
- `kaggle-notebooks-analysis/scripts/julius_tools/` (Python tools)
- `kaggle-notebooks-analysis/docs/jules/` (documentation)
- `EmailIntelligence/` (operations docs, prompts)
- `gemini-cli-prompt-library/` (shell scripts)

Duplicates, stale paths, invalid state names, and inconsistent API payload formats across copies.

### Solution
Single consolidated repo with canonical paths, fixed bugs, and verified state names.

## CLI/API Split

```
tools/
├── api/          # Low-level API client (jules_api_client.py)
│   └── JulesAPIClient — HTTP client for Jules REST API (jules.googleapis.com/v1alpha)
├── sessions/     # Session operations (built on api/)
│   ├── jules_list_sessions.py
│   ├── jules_list_activities.py
│   ├── jules_monitor.py
│   ├── jules_recovery_manager.py
│   ├── jules_approve_plan.py
│   ├── jules_send_message.py
│   └── analyze_unanswered.py
├── pr/           # PR analysis tools
│   ├── jules_pr_context.py
│   ├── jules_pr_triage.py
│   ├── jules_audit_session_pr.py
│   └── session_pr_triage.py
├── rebase/       # Safe rebase orchestrator
├── multi_repo/   # Multi-repo operations
├── cli/          # High-level CLI entry point
│   └── jules-manager.py — subcommands: list, send, approve, triage, audit
├── utils/        # Shared utilities
│   ├── auth_manager.py
│   └── pre_flight_check.sh
├── shell/        # Shell scripts
│   ├── jules_audit.sh
│   ├── jules_sync_all.sh
│   ├── jules_commands.sh
│   ├── check_all_repos.sh
│   ├── setup_jules_env.sh
│   └── retrieve_sessions.sh
└── tests/        # Test suite
```

### Dependency Graph

```
jules-manager.py (CLI)
    ├── tools/api/jules_api_client.py
    ├── tools/sessions/*.py
    ├── tools/pr/*.py
    └── tools/utils/auth_manager.py

tools/sessions/*.py
    └── tools/api/jules_api_client.py

tools/pr/*.py
    └── tools/api/jules_api_client.py
```

## API Integration

### Jules REST API
- Base URL: `https://jules.googleapis.com/v1alpha`
- Auth: Bearer token (OAuth2)
- Key endpoints:
  - `GET /sessions` — list sessions
  - `GET /sessions/{id}` — get session
  - `GET /sessions/{id}:listActivities` — list activities
  - `POST /sessions/{id}:sendMessage` — send message (body: `{"prompt": "..."}`)
  - `POST /sessions/{id}:approvePlan` — approve plan (body: `{}`)

### Official State Enum
```
QUEUED, PLANNING, AWAITING_PLAN_APPROVAL, AWAITING_USER_FEEDBACK,
IN_PROGRESS, PAUSED, COMPLETED, FAILED, STATE_UNSPECIFIED
```

## Skills Architecture

7 skills, each self-contained with `SKILL.md` + supporting files:

| Skill | Purpose | Files |
|-------|---------|-------|
| jules-api | API reference docs | 8 |
| jules-cli | CLI usage guide | 1 |
| jules-session-manager | Session lifecycle management | 4 |
| jules-sessions | Session analysis scripts | 9 |
| jules-workflows | Merge/rebase workflows | 3 |
| jules-scheduling | Task scheduling | 1 |
| wrapup-session | Session wrap-up | 4 |

### Skills Distribution
Skills are NOT distributed via the `skills` CLI (agent-skills-cli). That CLI only tracks skills it installed via `.git/` metadata. Instead, a custom sync script copies skills to target locations with path rewriting:
- `~/.letta/skills/` (Letta Code)
- `~/.agents/skills/` (system-wide)

The sync script rewrites `tools/` paths to absolute paths or `$JULES_TOOLS_DIR` variable.

## Future SDK Integration

The consolidated structure is designed for future integration with `@google/jules-sdk`:

1. `tools/api/jules_api_client.py` can be replaced by the SDK's client
2. `tools/sessions/*.py` can use SDK's `session.send()` and `session.ask()` methods
3. `tools/cli/jules-manager.py` can delegate to SDK's CLI
4. Skills can reference SDK types instead of custom type definitions

### Migration Path
```
Phase 1 (current): Standalone tools with direct REST API calls
Phase 2 (future): Wrap tools with SDK client as optional backend
Phase 3 (future): SDK as primary, REST API as fallback
```

## Testing

Test suite at `tools/tests/`:
- `test_jules_api_client.py` — API client unit tests
- `test_api_connection.py` — live API connection test
- `test_all_features.py` — grading + connection test
- `test_jules_api.sh` — shell test wrapper
- `test_state_names.py` — validate state references (NEW)
- `test_imports.py` — validate import structure (NEW)
- `test_shell_scripts.py` — shell script validation (NEW)
- `test_skills_frontmatter.py` — SKILL.md YAML validation (NEW)
- `test_cli_available.py` — CLI binary availability (NEW)

Run: `python -m pytest tools/tests/ -v`
