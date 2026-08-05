# Jules Centralization Checklist

Track the complete implementation of the `~/github/jules/` consolidated repo.

> **Historical consolidation record:** Checked items describe the original import and
> verification pass, not current subsystem readiness. Paths below may predate the
> documentation reorganization. Use [`docs/README.md`](docs/README.md) for current
> authorities and active reviews.

---

## 1. Repo Creation

- [x] `git init ~/github/jules/`
- [x] `.gitignore` (session data, `__pycache__`, `.skill` zips, `node_modules/`, `dist/`)
- [x] `README.md` — what this repo is, how it's organized
- [x] `ARCHITECTURE.md` — consolidation design, CLI/API split, future SDK integration notes

## 2. Skills (7 skills, source directories not zipped)

### 2.1 jules-api
- [x] `skills/jules-api/SKILL.md`
- [x] `skills/jules-api/references/overview.md`
- [x] `skills/jules-api/references/sessions.md`
- [x] `skills/jules-api/references/activities.md`
- [x] `skills/jules-api/references/authentication.md`
- [x] `skills/jules-api/references/quickstart.md`
- [x] `skills/jules-api/references/sources.md`
- [x] `skills/jules-api/references/types.md`
- [x] Verify: all use `{"prompt": "..."}` for sendMessage
- [x] Verify: all state names match official enum (QUEUED, PLANNING, AWAITING_PLAN_APPROVAL, AWAITING_USER_FEEDBACK, IN_PROGRESS, PAUSED, COMPLETED, FAILED, STATE_UNSPECIFIED)

### 2.2 jules-session-manager
- [x] `skills/jules-session-manager/SKILL.md` (merge global + kaggle enhanced copy — kaggle has more triggers)
- [x] `skills/jules-session-manager/GEMINI.md`
- [x] `skills/jules-session-manager/README.md`
- [x] `skills/jules-session-manager/agents/openai.yaml` (if exists)
- [x] Verify: merged version has all triggers from both copies

### 2.3 jules-cli
- [x] `skills/jules-cli/SKILL.md` (unzip from `jules-cli.skill`)
- [x] Verify: CLI commands match installed `jules` binary version
- [x] Verify: covers `jules new`, `jules remote list`, `jules remote pull`, `jules auth login`, `jules --version`

### 2.4 jules-sessions
- [x] `skills/jules-sessions/SKILL.md` (unzip from `jules-sessions.skill`)
- [x] `skills/jules-sessions/scripts/analyze_sessions.sh`
- [x] `skills/jules-sessions/scripts/sync_session.sh`
- [x] `skills/jules-sessions/scripts/list_prs_by_deletions.py`
- [x] `skills/jules-sessions/scripts/branch_analysis_tool.py`
- [x] `skills/jules-sessions/scripts/check_needs_response.py`
- [x] `skills/jules-sessions/references/prompts.md`
- [x] `skills/jules-sessions/references/wip_analysis.md`
- [x] `skills/jules-sessions/references/task_schedule.json`
- [x] `skills/jules-sessions/references/response_templates.md`
- [x] `skills/jules-sessions/references/sent_responses.md`
- [x] Verify: `sync_session.sh` uses `{"prompt": "..."}` payload (curl)

### 2.5 jules-workflows
- [x] `skills/jules-workflows/SKILL.md` (unzip from `jules-workflows.skill`)
- [x] `skills/jules-workflows/scripts/conflict_predictor.py`
- [x] `skills/jules-workflows/scripts/intelligent_merge_analyzer.py`
- [x] Verify: all `jules new`/`jules remote pull` commands match current CLI syntax

### 2.6 jules-scheduling
- [x] `skills/jules-scheduling/SKILL.md` (unzip from `jules-scheduling.skill`)
- [x] Verify: schedule schema JSON is valid

### 2.7 wrapup-session
- [x] `skills/wrapup-session/SKILL.md` (from kaggle `.agents/skills/wrapup-session/`)
- [x] Verify: references to `session_pr_triage.py` and `pre_flight_check.sh` have correct paths

## 3. Tools — Python (19 files)

### 3.1 API Client
- [x] `tools/api/jules_api_client.py` (from kaggle, commit `4ca0f65` — the fixed version)
- [x] Verify: `send_message` uses `{"prompt": text}` (line ~159)
- [x] Verify: exponential backoff for 429/5xx
- [x] Verify: pagination support
- [x] Verify: `JulesAPIClient` class + `jules_request` backward-compat function

### 3.2 Session Management
- [x] `tools/sessions/jules_list_sessions.py` (with A+ grading)
- [x] `tools/sessions/jules_list_activities.py`
- [x] `tools/sessions/jules_monitor.py` (daemon + PID lock)
- [x] `tools/sessions/jules_recovery_manager.py` (state-based recovery)
- [x] `tools/sessions/jules_approve_plan.py`
- [x] `tools/sessions/jules_send_message.py`
- [x] `tools/sessions/analyze_unanswered.py`
- [x] `tools/sessions/config.py` (shared config, `calculate_grade`)
- [x] Verify: all use official state names (no RUNNING/PENDING/WAITING_FOR_USER)
- [x] Verify: all import from `tools.api.jules_api_client` (not relative imports)

### 3.3 PR Tools
- [x] `tools/pr/jules_pr_context.py` (dedupe kaggle + gemini-fullstack copies)
- [x] `tools/pr/jules_pr_triage.py` (dedupe kaggle root + gemini-fullstack copies)
- [x] `tools/pr/jules_audit_session_pr.py`
- [x] Verify: no duplicate copies remain in source repos

### 3.4 Rebase
- [x] `tools/rebase/jules_rebase_orchestrator.py` (safe rebase + merge-tree + pytest)

### 3.5 Multi-Repo
- [x] `tools/multi_repo/jules_multi_repo.py`

### 3.6 CLI Entry Point
- [x] `tools/cli/jules-manager.py` (from `~/.agents/commands/`)
- [x] Verify: `cmd_send` uses `{"prompt": message}` (line ~65)
- [x] Verify: `cmd_approve` sends empty `{}`
- [x] Verify: handles `sessions/` prefix normalization

### 3.7 Tests
- [x] `tools/tests/test_jules_api_client.py` (existing 3 unit tests)
- [x] `tools/tests/test_api_connection.py` (existing connection test)
- [x] `tools/tests/test_all_features.py` (existing grading + connection test)
- [x] `tools/tests/test_jules_api.sh` (existing shell test wrapper)
- [x] `tools/tests/test_state_names.py` — NEW: validate all state references against official enum
- [x] `tools/tests/test_imports.py` — NEW: every Python tool imports from new structure
- [x] `tools/tests/test_shell_scripts.py` — NEW: jules_audit.sh, jules_sync_all.sh produce valid output with mock data
- [x] `tools/tests/test_skills_frontmatter.py` — NEW: all SKILL.md files have valid YAML frontmatter
- [x] `tools/tests/test_cli_available.py` — NEW: `jules --version` succeeds if binary installed
- [x] `tools/tests/conftest.py` — NEW: shared fixtures (mock API responses, mock session JSON)
- [x] `tools/tests/fixtures/` — NEW: mock session JSON files for offline testing

## 4. Tools — Shell (6 files)

- [x] `tools/shell/jules_audit.sh` — FIX: line 34 `RUNNING`→`IN_PROGRESS`, `PENDING`→`QUEUED`
- [x] `tools/shell/jules_sync_all.sh`
- [x] `tools/shell/jules_commands.sh` (from gemini-cli-prompt-library)
- [x] `tools/shell/check_all_repos.sh`
- [x] `tools/shell/setup_jules_env.sh` — MERGE: `setup_jules_env_compact.sh` + `setup_jules_env_unified.sh` into one with `--compact` flag
- [x] `tools/shell/retrieve_sessions.sh` (from EmailIntelligence `.jules/session_analysis/`)
- [x] Verify: `jules_audit.sh` uses only official state names after fix
- [x] Verify: `jules_sync_all.sh` uses `{"prompt": "..."}` if it sends messages
- [x] Verify: all shell scripts have `set -e` or `set -euo pipefail`

## 5. Commands — Shell Wrappers (10 files)

- [x] `commands/jules-list`
- [x] `commands/jules_triage.sh`
- [x] `commands/jules_audit.sh`
- [x] `commands/jules_recover.sh`
- [x] `commands/jules_pr_context.sh`
- [x] `commands/jules_discovery.sh`
- [x] `commands/jules-triage-activities`
- [x] `commands/jules-triage-analyze`
- [x] `commands/jules-triage-list`
- [x] `commands/jules-triage-recover`
- [x] Verify: each wrapper calls the correct Python tool in `tools/`
- [x] Verify: each wrapper has correct execute permissions

## 6. Docs — Runbooks (9 files)

- [x] `docs/runbooks/session_runbook.md` (from kaggle `docs/jules/JULES_SESSION_RUNBOOK.md`)
- [x] `docs/runbooks/failure_runbook.md`
- [x] `docs/runbooks/pr_verification_runbook.md`
- [x] `docs/runbooks/orchestrator_runbook.md`
- [x] `docs/runbooks/improvement_log.md`
- [x] `docs/runbooks/architecture.md`
- [x] `docs/runbooks/auth_setup.md`
- [x] `docs/runbooks/github_integration.md`
- [x] `docs/runbooks/session_recovery.md`
- [x] Verify: all runbook references to Python tools use new paths (`tools/sessions/`, `tools/pr/`, etc.)
- [x] Verify: all state names in runbooks match official enum
- [x] Verify: session_runbook.md recovery table has correct state→action mapping

## 7. Docs — Reference (5 files)

- [x] `docs/reference/rest_api_reference.md` (from kaggle `docs/jules/JULES_REST_API_REFERENCE.md`)
- [x] `docs/reference/tools_readme.md`
- [x] `docs/reference/multi_repo_tools.md`
- [x] `docs/reference/api_update_guide.md` (from kaggle `JULES_API_UPDATE.md`)
- [x] `docs/reference/ecosystem_map.md` (from `~/github/remote/jules-ecosystem-map.md`, 42KB)
- [x] Verify: `rest_api_reference.md` uses `{"prompt": "..."}` for sendMessage
- [x] Verify: `ecosystem_map.md` paths updated to reflect new structure

## 8. Docs — Guides (3 files)

- [x] `docs/guides/quickstart.md` (from kaggle `JULES_QUICKSTART.md`)
- [x] `docs/guides/operations.md` (from EmailIntelligence `docs/JULES_OPERATIONS.md`)
- [x] `docs/guides/backlog_task_template.md` (from EmailIntelligence `.gemini/JULES_TEMPLATE.md`)
- [x] Verify: quickstart references new tool paths
- [x] Verify: operations.md `jules new` command in Workflow 4 is correct CLI syntax
- [x] Verify: operations.md curl commands use `{"prompt": "..."}` payload

## 9. Docs — Actions (6 files)

- [x] `docs/actions/cross_repo_assessment.md` (from `~/github/remote/docs/jules-actions-cross-repo-assessment.md`)
- [x] `docs/actions/emailintelligence.md` (from EmailIntelligence `JULES_ACTION.md`)
- [x] `docs/actions/kaggle-notebooks-analysis.md` (from kaggle `JULES_ACTION.md`)
- [x] `docs/actions/gemini-fullstack-langgraph-quickstart.md`
- [x] `docs/actions/gemini-cli-prompt-library.md`
- [x] `docs/actions/jules_actions_traceability.md` — merge the 4 per-repo `docs/jules_actions.md` files into one comparison doc

## 10. Docs — Prompts (4 files)

- [x] `docs/prompts/prompts_formatted.txt` (from EmailIntelligence `jules_prompts_formatted.txt`)
- [x] `docs/prompts/response_templates.md` (from jules-sessions skill references)
- [x] `docs/prompts/sent_responses.md` (from jules-sessions skill references)
- [x] `docs/prompts/extracted_prompts_formatted.txt` (from kaggle `docs/jules/`)

## 11. Docs — Behavioral (1 file)

- [x] `docs/behavioral/instructions.md` (from kaggle `.jules/INSTRUCTIONS.md`, 26KB)
- [x] Verify: no project-specific paths in instructions (should be generic)

## 12. Docs — Extracted (4 files)

- [x] `docs/extracted/bolt_role.md`
- [x] `docs/extracted/sentinel_role.md`
- [x] `docs/extracted/mcp_schedule.json`
- [x] `docs/extracted/recovery_payloads.json`

## 13. Extensions (1 extension)

- [x] `extensions/gemini-cli-jules/GEMINI.md`
- [x] `extensions/gemini-cli-jules/README.md`
- [x] `extensions/gemini-cli-jules/CONTRIBUTING.md`
- [x] `extensions/gemini-cli-jules/gemini-extension.json`
- [x] `extensions/gemini-cli-jules/commands/jules.toml`
- [x] `extensions/gemini-cli-jules/mcp-server/src/jules.ts`
- [x] `extensions/gemini-cli-jules/mcp-server/dist/jules.js`
- [x] Verify: `jules.toml` CLI commands match current `jules` binary syntax
- [x] Verify: MCP server TypeScript compiles without errors

## 14. Bug Fixes Applied

- [x] `jules_audit.sh` line 34: `RUNNING` → `IN_PROGRESS`, `PENDING` → `QUEUED`
- [x] `setup_jules_env_compact.sh` + `setup_jules_env_unified.sh` merged into single `setup_jules_env.sh`
- [x] Duplicate `jules_pr_triage.py` (kaggle root + gemini-fullstack) — canonical version chosen, other removed
- [x] Duplicate `jules_pr_context.py` (kaggle + gemini-fullstack) — canonical version chosen, other removed
- [x] `jules-session-manager` SKILL.md — global and kaggle copies merged (kaggle has more triggers)

## 15. Test Suite — New Tests

### 15.1 State Name Validation
- [x] `test_state_names.py` — scans all `.py`, `.sh`, `.md` files for state references
- [x] Catches `RUNNING`, `PENDING`, `WAITING_FOR_USER` as invalid
- [x] Validates against official enum: `QUEUED`, `PLANNING`, `AWAITING_PLAN_APPROVAL`, `AWAITING_USER_FEEDBACK`, `IN_PROGRESS`, `PAUSED`, `COMPLETED`, `FAILED`, `STATE_UNSPECIFIED`

### 15.2 Import Validation
- [x] `test_imports.py` — every Python tool imports from new structure
- [x] `tools/api/jules_api_client.py` imports successfully
- [x] All `tools/sessions/*.py` import successfully
- [x] All `tools/pr/*.py` import successfully
- [x] `tools/rebase/jules_rebase_orchestrator.py` imports successfully
- [x] `tools/multi_repo/jules_multi_repo.py` imports successfully
- [x] `tools/cli/jules-manager.py` imports successfully

### 15.3 API Client Tests
- [x] `test_jules_api_client.py` — existing 3 tests pass
- [x] Add: test `list_sessions` with mock response
- [x] Add: test `list_activities` with mock response
- [x] Add: test `approve_plan` sends empty `{}`
- [x] Add: test backoff retries on 429
- [x] Add: test backoff retries on 5xx
- [x] Add: test pagination with `pageToken`
- [x] Add: test `get_session` returns session object
- [x] Add: test resource name normalization (`sessions/` prefix)

### 15.4 Shell Script Tests
- [x] `test_shell_scripts.py` — `jules_audit.sh` produces valid output with mock session JSON
- [x] `test_shell_scripts.py` — `jules_sync_all.sh` dry-run mode (if possible)
- [x] `test_shell_scripts.py` — `retrieve_sessions.sh` skips existing files

### 15.5 Skill Frontmatter Tests
- [x] `test_skills_frontmatter.py` — all 7 SKILL.md files have valid YAML frontmatter
- [x] Required fields: `name`, `description`
- [x] No invalid fields (only `name`, `description`, `metadata`, `license`, `compatibility` allowed)
- [x] Description fields with colons are quoted

### 15.6 CLI Integration Tests
- [x] `test_cli_available.py` — `jules --version` succeeds (skip if not installed)
- [x] `test_cli_available.py` — `jules remote list --session` succeeds (skip if no API key)

### 15.7 Test Infrastructure
- [x] `conftest.py` — shared fixtures: mock API responses, mock session JSON, mock activity JSON
- [x] `fixtures/session_completed.json` — mock completed session with PR
- [x] `fixtures/session_awaiting_approval.json` — mock session needing plan approval
- [x] `fixtures/session_awaiting_feedback.json` — mock session needing user input
- [x] `fixtures/session_failed.json` — mock failed session
- [x] `fixtures/session_in_progress.json` — mock active session
- [x] `fixtures/activities_sample.json` — mock activity list
- [x] `pytest.ini` or `pyproject.toml` — test config, markers for live vs offline tests

## 16. What Stays in Project Repos (not moved)

- [x] Session JSON data (`jules_sessions/*.json`) — confirm left in place
- [x] `.jules/session_analysis/details/*.json` — confirm left in place
- [x] `.Jules/antigravity.md`, `bolt.md`, `palette.md`, `sentinel.md` — confirm left in place
- [x] `.JULES_ARCHIVE.md` — confirm left in place
- [x] `JOBS_FOR_JULES.md`, `JULES_ENHANCEMENT_TASKS.md` — confirm left in place
- [x] `JULES_PR_HANDOFF.md` — confirm left in place
- [x] `jules_prompts_formatted.txt` — confirm left in place (project-specific)
- [x] `.jules/INSTRUCTIONS.md` — confirm copied (not moved) since it may be referenced by kaggle tools

## 17. Source Mapping Verification

- [x] `tools/api/jules_api_client.py` matches kaggle commit `4ca0f65` (sendMessage fix)
- [x] `tools/sessions/*.py` match kaggle commit `100abe4` (6 state/field fixes)
- [x] `docs/runbooks/session_runbook.md` matches kaggle commit `b5aff10` (state name fix)
- [x] `tools/cli/jules-manager.py` matches `~/.agents/commands/jules-manager.py` (line 65: `{"prompt": message}`)
- [x] `skills/jules-api/references/` matches `~/.agents/skills/jules-api/references/` (all 7 docs)
- [x] `extensions/gemini-cli-jules/` matches `~/.gemini/extensions/gemini-cli-jules/`

## 18. Final Verification

- [x] `git status` — all files committed, no untracked files
- [x] `python -m pytest tools/tests/ -v` — all tests pass
- [x] `bash tools/shell/jules_audit.sh` — runs without error on mock data
- [x] `python tools/cli/jules-manager.py list` — connects to API (if key set) or shows help
- [x] `jules --version` — CLI binary available
- [x] No references to old paths (`scripts/jules_tools/`, `.agents/commands/`, `.kilo/commands/`)
- [x] No duplicate files (same content in multiple locations)
- [x] `README.md` accurately describes the structure
- [x] `ARCHITECTURE.md` documents the CLI/API split and future SDK integration plan
