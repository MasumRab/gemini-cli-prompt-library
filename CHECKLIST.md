# Jules Centralization Checklist

Track the complete implementation of the `~/github/jules/` consolidated repo.

---

## 1. Repo Creation

- [ ] `git init ~/github/jules/`
- [ ] `.gitignore` (session data, `__pycache__`, `.skill` zips, `node_modules/`, `dist/`)
- [ ] `README.md` — what this repo is, how it's organized
- [ ] `ARCHITECTURE.md` — consolidation design, CLI/API split, future SDK integration notes

## 2. Skills (7 skills, source directories not zipped)

### 2.1 jules-api
- [ ] `skills/jules-api/SKILL.md`
- [ ] `skills/jules-api/references/overview.md`
- [ ] `skills/jules-api/references/sessions.md`
- [ ] `skills/jules-api/references/activities.md`
- [ ] `skills/jules-api/references/authentication.md`
- [ ] `skills/jules-api/references/quickstart.md`
- [ ] `skills/jules-api/references/sources.md`
- [ ] `skills/jules-api/references/types.md`
- [ ] Verify: all use `{"prompt": "..."}` for sendMessage
- [ ] Verify: all state names match official enum (QUEUED, PLANNING, AWAITING_PLAN_APPROVAL, AWAITING_USER_FEEDBACK, IN_PROGRESS, PAUSED, COMPLETED, FAILED, STATE_UNSPECIFIED)

### 2.2 jules-session-manager
- [ ] `skills/jules-session-manager/SKILL.md` (merge global + kaggle enhanced copy — kaggle has more triggers)
- [ ] `skills/jules-session-manager/GEMINI.md`
- [ ] `skills/jules-session-manager/README.md`
- [ ] `skills/jules-session-manager/agents/openai.yaml` (if exists)
- [ ] Verify: merged version has all triggers from both copies

### 2.3 jules-cli
- [ ] `skills/jules-cli/SKILL.md` (unzip from `jules-cli.skill`)
- [ ] Verify: CLI commands match installed `jules` binary version
- [ ] Verify: covers `jules new`, `jules remote list`, `jules remote pull`, `jules auth login`, `jules --version`

### 2.4 jules-sessions
- [ ] `skills/jules-sessions/SKILL.md` (unzip from `jules-sessions.skill`)
- [ ] `skills/jules-sessions/scripts/analyze_sessions.sh`
- [ ] `skills/jules-sessions/scripts/sync_session.sh`
- [ ] `skills/jules-sessions/scripts/list_prs_by_deletions.py`
- [ ] `skills/jules-sessions/scripts/branch_analysis_tool.py`
- [ ] `skills/jules-sessions/scripts/check_needs_response.py`
- [ ] `skills/jules-sessions/references/prompts.md`
- [ ] `skills/jules-sessions/references/wip_analysis.md`
- [ ] `skills/jules-sessions/references/task_schedule.json`
- [ ] `skills/jules-sessions/references/response_templates.md`
- [ ] `skills/jules-sessions/references/sent_responses.md`
- [ ] Verify: `sync_session.sh` uses `{"prompt": "..."}` payload (curl)

### 2.5 jules-workflows
- [ ] `skills/jules-workflows/SKILL.md` (unzip from `jules-workflows.skill`)
- [ ] `skills/jules-workflows/scripts/conflict_predictor.py`
- [ ] `skills/jules-workflows/scripts/intelligent_merge_analyzer.py`
- [ ] Verify: all `jules new`/`jules remote pull` commands match current CLI syntax

### 2.6 jules-scheduling
- [ ] `skills/jules-scheduling/SKILL.md` (unzip from `jules-scheduling.skill`)
- [ ] Verify: schedule schema JSON is valid

### 2.7 wrapup-session
- [ ] `skills/wrapup-session/SKILL.md` (from kaggle `.agents/skills/wrapup-session/`)
- [ ] Verify: references to `session_pr_triage.py` and `pre_flight_check.sh` have correct paths

## 3. Tools — Python (19 files)

### 3.1 API Client
- [ ] `tools/api/jules_api_client.py` (from kaggle, commit `4ca0f65` — the fixed version)
- [ ] Verify: `send_message` uses `{"prompt": text}` (line ~159)
- [ ] Verify: exponential backoff for 429/5xx
- [ ] Verify: pagination support
- [ ] Verify: `JulesAPIClient` class + `jules_request` backward-compat function

### 3.2 Session Management
- [ ] `tools/sessions/jules_list_sessions.py` (with A+ grading)
- [ ] `tools/sessions/jules_list_activities.py`
- [ ] `tools/sessions/jules_monitor.py` (daemon + PID lock)
- [ ] `tools/sessions/jules_recovery_manager.py` (state-based recovery)
- [ ] `tools/sessions/jules_approve_plan.py`
- [ ] `tools/sessions/jules_send_message.py`
- [ ] `tools/sessions/analyze_unanswered.py`
- [ ] `tools/sessions/config.py` (shared config, `calculate_grade`)
- [ ] Verify: all use official state names (no RUNNING/PENDING/WAITING_FOR_USER)
- [ ] Verify: all import from `tools.api.jules_api_client` (not relative imports)

### 3.3 PR Tools
- [ ] `tools/pr/jules_pr_context.py` (dedupe kaggle + gemini-fullstack copies)
- [ ] `tools/pr/jules_pr_triage.py` (dedupe kaggle root + gemini-fullstack copies)
- [ ] `tools/pr/jules_audit_session_pr.py`
- [ ] Verify: no duplicate copies remain in source repos

### 3.4 Rebase
- [ ] `tools/rebase/jules_rebase_orchestrator.py` (safe rebase + merge-tree + pytest)

### 3.5 Multi-Repo
- [ ] `tools/multi_repo/jules_multi_repo.py`

### 3.6 CLI Entry Point
- [ ] `tools/cli/jules-manager.py` (from `~/.agents/commands/`)
- [ ] Verify: `cmd_send` uses `{"prompt": message}` (line ~65)
- [ ] Verify: `cmd_approve` sends empty `{}`
- [ ] Verify: handles `sessions/` prefix normalization

### 3.7 Tests
- [ ] `tools/tests/test_jules_api_client.py` (existing 3 unit tests)
- [ ] `tools/tests/test_api_connection.py` (existing connection test)
- [ ] `tools/tests/test_all_features.py` (existing grading + connection test)
- [ ] `tools/tests/test_jules_api.sh` (existing shell test wrapper)
- [ ] `tools/tests/test_state_names.py` — NEW: validate all state references against official enum
- [ ] `tools/tests/test_imports.py` — NEW: every Python tool imports from new structure
- [ ] `tools/tests/test_shell_scripts.py` — NEW: jules_audit.sh, jules_sync_all.sh produce valid output with mock data
- [ ] `tools/tests/test_skills_frontmatter.py` — NEW: all SKILL.md files have valid YAML frontmatter
- [ ] `tools/tests/test_cli_available.py` — NEW: `jules --version` succeeds if binary installed
- [ ] `tools/tests/conftest.py` — NEW: shared fixtures (mock API responses, mock session JSON)
- [ ] `tools/tests/fixtures/` — NEW: mock session JSON files for offline testing

## 4. Tools — Shell (6 files)

- [ ] `tools/shell/jules_audit.sh` — FIX: line 34 `RUNNING`→`IN_PROGRESS`, `PENDING`→`QUEUED`
- [ ] `tools/shell/jules_sync_all.sh`
- [ ] `tools/shell/jules_commands.sh` (from gemini-cli-prompt-library)
- [ ] `tools/shell/check_all_repos.sh`
- [ ] `tools/shell/setup_jules_env.sh` — MERGE: `setup_jules_env_compact.sh` + `setup_jules_env_unified.sh` into one with `--compact` flag
- [ ] `tools/shell/retrieve_sessions.sh` (from EmailIntelligence `.jules/session_analysis/`)
- [ ] Verify: `jules_audit.sh` uses only official state names after fix
- [ ] Verify: `jules_sync_all.sh` uses `{"prompt": "..."}` if it sends messages
- [ ] Verify: all shell scripts have `set -e` or `set -euo pipefail`

## 5. Commands — Shell Wrappers (10 files)

- [ ] `commands/jules-list`
- [ ] `commands/jules_triage.sh`
- [ ] `commands/jules_audit.sh`
- [ ] `commands/jules_recover.sh`
- [ ] `commands/jules_pr_context.sh`
- [ ] `commands/jules_discovery.sh`
- [ ] `commands/jules-triage-activities`
- [ ] `commands/jules-triage-analyze`
- [ ] `commands/jules-triage-list`
- [ ] `commands/jules-triage-recover`
- [ ] Verify: each wrapper calls the correct Python tool in `tools/`
- [ ] Verify: each wrapper has correct execute permissions

## 6. Docs — Runbooks (9 files)

- [ ] `docs/runbooks/session_runbook.md` (from kaggle `docs/jules/JULES_SESSION_RUNBOOK.md`)
- [ ] `docs/runbooks/failure_runbook.md`
- [ ] `docs/runbooks/pr_verification_runbook.md`
- [ ] `docs/runbooks/orchestrator_runbook.md`
- [ ] `docs/runbooks/improvement_log.md`
- [ ] `docs/runbooks/architecture.md`
- [ ] `docs/runbooks/auth_setup.md`
- [ ] `docs/runbooks/github_integration.md`
- [ ] `docs/runbooks/session_recovery.md`
- [ ] Verify: all runbook references to Python tools use new paths (`tools/sessions/`, `tools/pr/`, etc.)
- [ ] Verify: all state names in runbooks match official enum
- [ ] Verify: session_runbook.md recovery table has correct state→action mapping

## 7. Docs — Reference (5 files)

- [ ] `docs/reference/rest_api_reference.md` (from kaggle `docs/jules/JULES_REST_API_REFERENCE.md`)
- [ ] `docs/reference/tools_readme.md`
- [ ] `docs/reference/multi_repo_tools.md`
- [ ] `docs/reference/api_update_guide.md` (from kaggle `JULES_API_UPDATE.md`)
- [ ] `docs/reference/ecosystem_map.md` (from `~/github/remote/jules-ecosystem-map.md`, 42KB)
- [ ] Verify: `rest_api_reference.md` uses `{"prompt": "..."}` for sendMessage
- [ ] Verify: `ecosystem_map.md` paths updated to reflect new structure

## 8. Docs — Guides (3 files)

- [ ] `docs/guides/quickstart.md` (from kaggle `JULES_QUICKSTART.md`)
- [ ] `docs/guides/operations.md` (from EmailIntelligence `docs/JULES_OPERATIONS.md`)
- [ ] `docs/guides/backlog_task_template.md` (from EmailIntelligence `.gemini/JULES_TEMPLATE.md`)
- [ ] Verify: quickstart references new tool paths
- [ ] Verify: operations.md `jules new` command in Workflow 4 is correct CLI syntax
- [ ] Verify: operations.md curl commands use `{"prompt": "..."}` payload

## 9. Docs — Actions (6 files)

- [ ] `docs/actions/cross_repo_assessment.md` (from `~/github/remote/docs/jules-actions-cross-repo-assessment.md`)
- [ ] `docs/actions/emailintelligence.md` (from EmailIntelligence `JULES_ACTION.md`)
- [ ] `docs/actions/kaggle-notebooks-analysis.md` (from kaggle `JULES_ACTION.md`)
- [ ] `docs/actions/gemini-fullstack-langgraph-quickstart.md`
- [ ] `docs/actions/gemini-cli-prompt-library.md`
- [ ] `docs/actions/jules_actions_traceability.md` — merge the 4 per-repo `docs/jules_actions.md` files into one comparison doc

## 10. Docs — Prompts (4 files)

- [ ] `docs/prompts/prompts_formatted.txt` (from EmailIntelligence `jules_prompts_formatted.txt`)
- [ ] `docs/prompts/response_templates.md` (from jules-sessions skill references)
- [ ] `docs/prompts/sent_responses.md` (from jules-sessions skill references)
- [ ] `docs/prompts/extracted_prompts_formatted.txt` (from kaggle `docs/jules/`)

## 11. Docs — Behavioral (1 file)

- [ ] `docs/behavioral/instructions.md` (from kaggle `.jules/INSTRUCTIONS.md`, 26KB)
- [ ] Verify: no project-specific paths in instructions (should be generic)

## 12. Docs — Extracted (4 files)

- [ ] `docs/extracted/bolt_role.md`
- [ ] `docs/extracted/sentinel_role.md`
- [ ] `docs/extracted/mcp_schedule.json`
- [ ] `docs/extracted/recovery_payloads.json`

## 13. Extensions (1 extension)

- [ ] `extensions/gemini-cli-jules/GEMINI.md`
- [ ] `extensions/gemini-cli-jules/README.md`
- [ ] `extensions/gemini-cli-jules/CONTRIBUTING.md`
- [ ] `extensions/gemini-cli-jules/gemini-extension.json`
- [ ] `extensions/gemini-cli-jules/commands/jules.toml`
- [ ] `extensions/gemini-cli-jules/mcp-server/src/jules.ts`
- [ ] `extensions/gemini-cli-jules/mcp-server/dist/jules.js`
- [ ] Verify: `jules.toml` CLI commands match current `jules` binary syntax
- [ ] Verify: MCP server TypeScript compiles without errors

## 14. Bug Fixes Applied

- [ ] `jules_audit.sh` line 34: `RUNNING` → `IN_PROGRESS`, `PENDING` → `QUEUED`
- [ ] `setup_jules_env_compact.sh` + `setup_jules_env_unified.sh` merged into single `setup_jules_env.sh`
- [ ] Duplicate `jules_pr_triage.py` (kaggle root + gemini-fullstack) — canonical version chosen, other removed
- [ ] Duplicate `jules_pr_context.py` (kaggle + gemini-fullstack) — canonical version chosen, other removed
- [ ] `jules-session-manager` SKILL.md — global and kaggle copies merged (kaggle has more triggers)

## 15. Test Suite — New Tests

### 15.1 State Name Validation
- [ ] `test_state_names.py` — scans all `.py`, `.sh`, `.md` files for state references
- [ ] Catches `RUNNING`, `PENDING`, `WAITING_FOR_USER` as invalid
- [ ] Validates against official enum: `QUEUED`, `PLANNING`, `AWAITING_PLAN_APPROVAL`, `AWAITING_USER_FEEDBACK`, `IN_PROGRESS`, `PAUSED`, `COMPLETED`, `FAILED`, `STATE_UNSPECIFIED`

### 15.2 Import Validation
- [ ] `test_imports.py` — every Python tool imports from new structure
- [ ] `tools/api/jules_api_client.py` imports successfully
- [ ] All `tools/sessions/*.py` import successfully
- [ ] All `tools/pr/*.py` import successfully
- [ ] `tools/rebase/jules_rebase_orchestrator.py` imports successfully
- [ ] `tools/multi_repo/jules_multi_repo.py` imports successfully
- [ ] `tools/cli/jules-manager.py` imports successfully

### 15.3 API Client Tests
- [ ] `test_jules_api_client.py` — existing 3 tests pass
- [ ] Add: test `list_sessions` with mock response
- [ ] Add: test `list_activities` with mock response
- [ ] Add: test `approve_plan` sends empty `{}`
- [ ] Add: test backoff retries on 429
- [ ] Add: test backoff retries on 5xx
- [ ] Add: test pagination with `pageToken`
- [ ] Add: test `get_session` returns session object
- [ ] Add: test resource name normalization (`sessions/` prefix)

### 15.4 Shell Script Tests
- [ ] `test_shell_scripts.py` — `jules_audit.sh` produces valid output with mock session JSON
- [ ] `test_shell_scripts.py` — `jules_sync_all.sh` dry-run mode (if possible)
- [ ] `test_shell_scripts.py` — `retrieve_sessions.sh` skips existing files

### 15.5 Skill Frontmatter Tests
- [ ] `test_skills_frontmatter.py` — all 7 SKILL.md files have valid YAML frontmatter
- [ ] Required fields: `name`, `description`
- [ ] No invalid fields (only `name`, `description`, `metadata`, `license`, `compatibility` allowed)
- [ ] Description fields with colons are quoted

### 15.6 CLI Integration Tests
- [ ] `test_cli_available.py` — `jules --version` succeeds (skip if not installed)
- [ ] `test_cli_available.py` — `jules remote list --session` succeeds (skip if no API key)

### 15.7 Test Infrastructure
- [ ] `conftest.py` — shared fixtures: mock API responses, mock session JSON, mock activity JSON
- [ ] `fixtures/session_completed.json` — mock completed session with PR
- [ ] `fixtures/session_awaiting_approval.json` — mock session needing plan approval
- [ ] `fixtures/session_awaiting_feedback.json` — mock session needing user input
- [ ] `fixtures/session_failed.json` — mock failed session
- [ ] `fixtures/session_in_progress.json` — mock active session
- [ ] `fixtures/activities_sample.json` — mock activity list
- [ ] `pytest.ini` or `pyproject.toml` — test config, markers for live vs offline tests

## 16. What Stays in Project Repos (not moved)

- [ ] Session JSON data (`jules_sessions/*.json`) — confirm left in place
- [ ] `.jules/session_analysis/details/*.json` — confirm left in place
- [ ] `.Jules/antigravity.md`, `bolt.md`, `palette.md`, `sentinel.md` — confirm left in place
- [ ] `.JULES_ARCHIVE.md` — confirm left in place
- [ ] `JOBS_FOR_JULES.md`, `JULES_ENHANCEMENT_TASKS.md` — confirm left in place
- [ ] `JULES_PR_HANDOFF.md` — confirm left in place
- [ ] `jules_prompts_formatted.txt` — confirm left in place (project-specific)
- [ ] `.jules/INSTRUCTIONS.md` — confirm copied (not moved) since it may be referenced by kaggle tools

## 17. Source Mapping Verification

- [ ] `tools/api/jules_api_client.py` matches kaggle commit `4ca0f65` (sendMessage fix)
- [ ] `tools/sessions/*.py` match kaggle commit `100abe4` (6 state/field fixes)
- [ ] `docs/runbooks/session_runbook.md` matches kaggle commit `b5aff10` (state name fix)
- [ ] `tools/cli/jules-manager.py` matches `~/.agents/commands/jules-manager.py` (line 65: `{"prompt": message}`)
- [ ] `skills/jules-api/references/` matches `~/.agents/skills/jules-api/references/` (all 7 docs)
- [ ] `extensions/gemini-cli-jules/` matches `~/.gemini/extensions/gemini-cli-jules/`

## 18. Final Verification

- [ ] `git status` — all files committed, no untracked files
- [ ] `python -m pytest tools/tests/ -v` — all tests pass
- [ ] `bash tools/shell/jules_audit.sh` — runs without error on mock data
- [ ] `python tools/cli/jules-manager.py list` — connects to API (if key set) or shows help
- [ ] `jules --version` — CLI binary available
- [ ] No references to old paths (`scripts/jules_tools/`, `.agents/commands/`, `.kilo/commands/`)
- [ ] No duplicate files (same content in multiple locations)
- [ ] `README.md` accurately describes the structure
- [ ] `ARCHITECTURE.md` documents the CLI/API split and future SDK integration plan
