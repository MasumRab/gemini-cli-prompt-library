# Jules Tools — Complete Reference

Comprehensive inventory of all interaction modalities, tools, and files in the consolidated `jules/` folder.

> **Inventory snapshot:** File counts and source comparisons describe the original
> consolidation and can drift. Use [`../README.md`](../README.md) for current document
> ownership and inspect runtime code before relying on a capability claim.

Consolidates 68 unique items from 7 scattered locations (kaggle-notebooks-analysis, EmailIntelligence, gemini-fullstack-langgraph-quickstart, gemini-cli-prompt-library, ~/.agents/, ~/.gemini/extensions/, ~/.jules/).

---

## 11 Interaction Modalities

Each modality is a distinct way to interact with the Jules API (`jules.googleapis.com/v1alpha`).

### 1. Python REST Client (`JulesAPIClient`)
- **File:** `tools/api/jules_api_client.py`
- **Pattern:** Class-based wrapper around `urllib` HTTP calls to `jules.googleapis.com/v1alpha`
- **Features:** Exponential backoff (429/5xx), automatic pagination via `nextPageToken`
- **Dual interface:** Functional (`jules_request()`) and OOP (`JulesAPIClient` class)
- **Auth:** `x-goog-api-key` header from `JULES_API_KEY` env var
- **Used by:** All `tools/sessions/*.py`, `tools/pr/*.py` scripts
- **Source:** kaggle-notebooks-analysis `scripts/jules_tools/jules_api_client.py`

### 2. Raw curl / HTTP (no wrapper)
- **Pattern:** Direct `curl` calls with `X-Goog-Api-Key` header
- **Auth:** Same API key approach
- **Used in:** `commands/jules_triage.sh` (curl fallback when Python unavailable), `tools/shell/jules_sync_all.sh`, runbook examples, `skills/jules-api/SKILL.md` reference
- **Endpoints:** `GET /sessions`, `GET /sessions/{id}`, `POST /sessions/{id}:sendMessage`, `POST /sessions/{id}:approvePlan`, `GET /sessions/{id}/activities`

### 3. Individual Python Session Scripts
- **Location:** `tools/sessions/` (7 scripts)
- **Pattern:** One script per operation, all import `JulesAPIClient`
- **Scripts:**
  - `jules_list_sessions.py` — list with A+ grading, `--active-only`, `--json`, `--limit`, `--with-activity`
  - `jules_list_activities.py` — session chat history (plan steps, agent messages, progress updates)
  - `jules_monitor.py` — background daemon with PID lock (`/tmp/jules_monitor.pid`), periodic health checks, auto-recovery
  - `jules_recovery_manager.py` — state-based hypothesis engine: maps session state to recovery action (retry/approve/AUDIT)
  - `jules_approve_plan.py` — approve pending plan via `:approvePlan`
  - `jules_send_message.py` — send message to unblock via `:sendMessage`
  - `analyze_unanswered.py` — detect if agent is waiting for user (scans activities for trailing `?`)
- **Source:** kaggle-notebooks-analysis `scripts/jules_tools/`

### 4. Python PR Tooling
- **Location:** `tools/pr/` (4 scripts)
- **Pattern:** PR analysis, safety auditing, session-to-PR correlation
- **Scripts:**
  - `jules_pr_context.py` — extract PR context (files changed, diff stats) via GitHub API
  - `jules_pr_triage.py` — PR triage automation (from gemini-fullstack)
  - `jules_audit_session_pr.py` — safety auditor: checks for build artefacts, shell variables, read-only file violations, missing tests, stub implementations
  - `session_pr_triage.py` — session-to-PR bidirectional correlation: scans activities for PR URLs/branch names, matches session IDs in branch names, outputs `session_pr_map.json`
- **Dependencies:** Some use `PyGithub` for GitHub API correlation

### 5. Unified Python CLI (`jules-manager.py`)
- **File:** `tools/cli/jules-manager.py`
- **Pattern:** Subcommand CLI with 4 commands — `list`, `session <id>`, `send <id> <msg>`, `approve <id>`
- **Note:** Uses `requests` library (different from `JulesAPIClient` which uses `urllib`)
- **Auth:** `x-goog-api-key` header from `JULES_API_KEY`
- **Source:** ~/.agents/commands/ (global), also copied to gemini-fullstack

### 6. Shell Command Wrappers
- **Location:** `commands/` (15 wrappers)
- **Pattern:** Thin shell scripts that call Python tools with curl fallback
- **Wrappers:**
  - `jules-list` — list sessions with grading
  - `jules_triage.sh` — triage sessions (`jules_list_sessions` with curl fallback)
  - `jules_audit.sh` — audit a session's PR (with curl fallback)
  - `jules_recover.sh` — send recovery message (with curl fallback)
  - `jules_pr_context.sh` — extract PR context (with `gh` CLI fallback)
  - `jules_discovery.sh` — list available commands
  - `jules-triage-activities` — triage session activities
  - `jules-triage-analyze` — analyze triage results
  - `jules-triage-list` — list triage items
  - `jules-triage-recover` — recovery from triage
  - `jules-intent` — extract intent metadata (`jules_intent_metadata`)
  - `jules-pending` — list sessions likely needing attention (`jules_list_sessions --pending`)
  - `jules-create` — create a new Jules session (`jules-manager create`)
  - `jules-ask` — ask a question and wait for the agent reply (`jules-manager ask`)
  - `jules-pr-feedback` — post PR feedback (`post_pr_feedback`)
- **All wrappers** differ from kaggle originals only in Python module path (`tools/...` vs `scripts/jules_tools/`)
- **Source:** kaggle-notebooks-analysis `.agents/commands/`

### 7. Operational Shell Scripts
- **Location:** `tools/shell/` (6 scripts)
- **Pattern:** Bash-level operations for session cache management and automation
- **Scripts:**
  - `jules_sync_all.sh` — syncs local `jules_sessions/*.json` with API (refresh existing + discover new), uses `curl` + `jq`
  - `jules_audit.sh` — audits all sessions from disk cache, categories: AWAITING_ACTION, COMPLETED_WITHOUT_PR, FAILED, IN_PROGRESS
  - `jules_commands.sh` — `gemini-cli-prompt-library` command reference (Jules session creation, status checking, diff export)
  - `check_all_repos.sh` — multi-repo consistency check (wrapper around `jules_multi_repo.py`)
  - `setup_jules_env.sh` — environment setup helper
  - `retrieve_sessions.sh` — reads problematic session IDs from `.jules/session_analysis/tmp/problematic_sessions.txt`, fetches full metadata to `details/session_{id}.json`

### 8. MCP Server (Model Context Protocol)
- **File:** `extensions/gemini-cli-jules/mcp-server/src/jules.ts`
- **Pattern:** TypeScript MCP server using `@google/jules-sdk`
- **Auth:** `JULES_API_KEY` environment variable
- **Tools exposed (6):**
  - `start_new_jules_task` — fire-and-forget task creation
  - `send_message` — send message to existing session
  - `ask_jules` — **synchronous request/response** (blocks for agent reply — not possible with REST API alone)
  - `approve_plan` — approve pending plan
  - `get_session_info` — retrieve session state
  - `wait_for_state` — **block until session reaches target state** (with timeout — not possible with REST API alone)
- **Unique capabilities:** `session.ask()`, `session.waitFor()`, `session.stream()` — higher-level abstractions from `@google/jules-sdk`
- **Source:** ~/.gemini/extensions/gemini-cli-jules/

### 9. Gemini CLI Extension Prompt
- **File:** `extensions/gemini-cli-jules/commands/jules.toml`
- **Pattern:** Agentic coding assistant prompt for Gemini CLI
- **Workflows:** Creating tasks (`jules remote new`), checking status (`jules remote list`), applying diffs (`jules remote pull --apply`)
- **Unique capability:** Repo-aware — auto-discovers repo from `git config`, presents console links
- **Trigger:** `/jules` command in Gemini CLI (installed via `gemini extensions install ...`)

### 10. Skill-based Agent Instructions
- **Location:** `skills/` (7 skill directories)
- **Pattern:** Markdown instruction files with front-matter (triggers, allowed tools, dependencies)
- **Skills:**
  - `jules-api/` — REST API v1alpha endpoint reference, Python usage patterns, session states
  - `jules-cli/` — `jules` binary CLI commands (new, remote list, remote pull, auth login)
  - `jules-session-manager/` — session lifecycle management + PR correlation, pre-flight checks, triage workflow
  - `jules-scheduling/` — task scheduling, schedule JSON management, phased orchestration
  - `jules-sessions/` — session analysis scripts, response templates, prompt tracking, WIP analysis
  - `jules-workflows/` — common workflow patterns (fire-and-forget, interactive, parallel, branch-specific, WIP recovery)
  - `wrapup-session/` — session summary reports, QA status, PR posting
- **Trigger-based:** AI agents auto-load skill when keywords like "jules session" appear
- **Source:** Consolidated from ~/.agents/skills/ and kaggle .agents/skills/

### 11. External Jules CLI Binary (referenced via skills)
- **Install:** `npm install -g @google/jules` (or via mise: `npm-google-jules`)
- **Auth:** OAuth browser login (`jules auth login`) — different from API-key approach used by Python tools
- **Commands:** `jules new`, `jules remote list --session`, `jules remote pull [--apply]`, `jules auth login/status`
- **Unique capabilities:** TUI mode, diff/patch management, repo auto-connection
- **Documented in:** `skills/jules-cli/SKILL.md`, `extensions/gemini-cli-jules/commands/jules.toml`

---

## Complete File Inventory

### `tools/api/` — REST Client
| File | Modality | Description |
|------|----------|-------------|
| `jules_api_client.py` | Python REST Client | `JulesAPIClient` class + `jules_request()` function. All HTTP to `jules.googleapis.com/v1alpha`. |

### `tools/sessions/` — Session Management
| File | Modality | Description |
|------|----------|-------------|
| `jules_list_sessions.py` | Python Session Script | List sessions with A+ grading, PR URL extraction, optional activity summary |
| `jules_list_activities.py` | Python Session Script | Session chat history (plan steps, agent messages, progress, errors); `--full` prints untruncated agent/user messages |
| `jules_monitor.py` | Python Session Script | Background daemon with PID lock, periodic state checks, auto-recovery |
| `jules_recovery_manager.py` | Python Session Script | State-based recovery: maps states → actions (retry/approve/AUDIT) |
| `jules_approve_plan.py` | Python Session Script | Approve pending plan via `:approvePlan` |
| `jules_send_message.py` | Python Session Script | Send message to unblock agent via `:sendMessage` |
| `analyze_unanswered.py` | Python Session Script | Detect if agent is waiting for user input |
| `jules_intent_metadata.py` | Python Session Script | Generalized intent metadata extractor (state/repo/date/id filters; classify/stale/anomaly flags; full-account `--snapshot`; JSON/JSONL/table output) |
| `config.py` | Shared Config | Scoring weights, base URL, `calculate_grade()`, `validate_config()`, plus shared session-state constants (`NO_ACTION_STATES`, `likely_pending`, `normalize_state`) |

### `tools/pr/` — PR Analysis
| File | Modality | Description |
|------|----------|-------------|
| `jules_pr_context.py` | Python PR Tool | Extract PR context (files, diff stats) via GitHub API |
| `jules_pr_triage.py` | Python PR Tool | PR triage automation (origin: gemini-fullstack) |
| `jules_audit_session_pr.py` | Python PR Tool | Safety auditor: build artefacts, shell variables, read-only files, stubs |
| `session_pr_triage.py` | Python PR Tool | Session-to-PR correlation: activities scan + branch matching → `session_pr_map.json` |

### `tools/cli/` — Unified CLI
| File | Modality | Description |
|------|----------|-------------|
| `jules-manager.py` | Unified Python CLI | Subcommand CLI: `list`, `session`, `send`, `approve`. Uses `requests`. |

### `tools/rebase/` — Rebase Orchestrator
| File | Modality | Description |
|------|----------|-------------|
| `jules_rebase_orchestrator.py` | Python Tool | Safe rebase + `git merge-tree` + post-rebase pytest |

### `tools/multi_repo/` — Multi-Repo
| File | Modality | Description |
|------|----------|-------------|
| `jules_multi_repo.py` | Python Tool | Source analysis across multiple repo clones (file/line counts) |

### `tools/shell/` — Operational Shell Scripts
| File | Modality | Description |
|------|----------|-------------|
| `jules_sync_all.sh` | Shell Script | Sync session cache: refresh existing + discover new via API |
| `jules_audit.sh` | Shell Script | Audit sessions from disk cache, categorize by state |
| `jules_commands.sh` | Shell Script | Command reference for gemini-cli-prompt-library |
| `check_all_repos.sh` | Shell Script | Multi-repo consistency check |
| `setup_jules_env.sh` | Shell Script | Environment setup helper |
| `retrieve_sessions.sh` | Shell Script | Fetch problem session details from text listing |

### `tools/utils/` — Shared Utilities
| File | Modality | Description |
|------|----------|-------------|
| `auth_manager.py` | Shared Utility | API key validation, GitHub token management |
| `pre_flight_check.sh` | Shared Utility | Auth check, dirty state check, branch safety check |

### `tools/sdk/` — SDK Bridge (TypeScript)
| File | Modality | Description |
|------|----------|-------------|
| `bridge.py` | SDK Bridge | Python ↔ TypeScript bridge for `@google/jules-sdk` |
| `src/bridge.ts` | SDK Bridge | TypeScript SDK integration entry point |

### `tools/tests/` — Test Suite
| File | Modality | Description |
|------|----------|-------------|
| `test_jules_api_client.py` | Tests | Unit tests for `JulesAPIClient` (sendMessage, approvePlan, empty responses) |
| `test_all_features.py` | Tests | Full feature integration tests |
| `test_api_connection.py` | Tests | API connection health check |
| `test_cli_available.py` | Tests | CLI availability verification |
| `test_imports.py` | Tests | Import path verification |
| `test_shell_scripts.py` | Tests | Shell script syntax validation |
| `test_skills_frontmatter.py` | Tests | Skill front-matter validation |
| `test_state_names.py` | Tests | Session state enum validation |
| `test_jules_api.sh` | Tests | API connectivity shell test |
| `fixtures/` | Test Data | 5 session mock fixtures (completed, awaiting_approval, awaiting_feedback, failed, in_progress) + activities_sample.json |

### `commands/` — Shell Command Wrappers (15)
| File | Calls | Fallback |
|------|-------|----------|
| `jules-list` | `jules_list_sessions.py` | Error message |
| `jules_triage.sh` | `jules_list_sessions.py` | curl API |
| `jules_audit.sh` | `jules_audit_session_pr.py` | curl API |
| `jules_recover.sh` | `jules_send_message.py` | curl API |
| `jules_pr_context.sh` | `jules_pr_context.py` | gh CLI |
| `jules_discovery.sh` | Lists commands | — |
| `jules-triage-activities` | Triage activities | — |
| `jules-triage-analyze` | Analyze triage | — |
| `jules-triage-list` | List triage items | — |
| `jules-triage-recover` | Recovery from triage | — |
| `jules-intent` | `jules_intent_metadata.py` | — |
| `jules-pending` | `jules_list_sessions.py --pending` | — |
| `jules-create` | `jules-manager.py create` | — |
| `jules-ask` | `jules-manager.py ask` | — |
| `jules-pr-feedback` | `post_pr_feedback.py` | Error message |

### `extensions/` — Gemini CLI / MCP
| File | Modality | Description |
|------|----------|-------------|
| `gemini-cli-jules/mcp-server/src/jules.ts` | MCP Server | TypeScript MCP server, 6 tools, uses `@google/jules-sdk` |
| `gemini-cli-jules/commands/jules.toml` | Gemini Extension | Agentic coding prompt for `/jules` command |

### `skills/` — Agent Skills (7)
| Directory | Description |
|-----------|-------------|
| `jules-api/` | REST API reference with examples (list, create, send, approve, activities) |
| `jules-cli/` | Jules CLI binary usage (create sessions, monitor, pull results, auth) |
| `jules-session-manager/` | Session lifecycle + PR correlation, pre-flight checks |
| `jules-scheduling/` | Task schedule JSON management, phased orchestration |
| `jules-sessions/` | Session analysis scripts, response templates, prompt tracking |
| `jules-workflows/` | 10 workflow patterns (fire-and-forget, interactive, parallel, WIP recovery) |
| `wrapup-session/` | Session summary reports, QA status, PR posting |

### `docs/` — Documentation
| Directory | Contents |
|-----------|----------|
| `docs/runbooks/` | 9 runbooks (session, failure, PR verification, orchestrator, auth, GitHub, recovery, architecture, improvement log) |
| `docs/reference/` | 5 reference docs (this file, REST API ref, tools readme, multi-repo, ecosystem map, API update guide) |
| `docs/guides/` | 3 guides (quickstart, operations, backlog template) |
| `docs/actions/` | Distributable Actions authorities, repository recommendations, and historical artifacts; see `docs/actions/README.md` |
| `docs/reviews/` | Revision-specific subsystem reviews |
| `docs/prompts/` | 4 prompt files (formatted prompts, extracted prompts, response templates, sent responses) |
| `docs/behavioral/` | Behavioral instructions for Jules |
| `docs/extracted/` | Extracted configs (bolt role, sentinel role, MCP schedule, recovery payloads) |

---

## Cross-Repo Drift Audit

All files in `jules/` were compared against their origin sources. Findings:

| Difference | Scope | Impact |
|-----------|-------|--------|
| Python module paths | All files | Expected — kaggle uses `scripts.jules_tools`, jules uses `tools.{api,sessions,pr,...}` |
| Default repo values | Docstrings in `jules_api_client.py`, `jules_rebase_orchestrator.py`, `session_pr_triage.py` | Minor — jules uses generic `<owner>/<repo>` or `MasumRab/jules` instead of kaggle-specific |
| Command script paths | All 15 commands | Expected — Python module paths updated |
| Skill paths | `jules-session-manager`, `wrapup-session` | Expected — reference paths rewritten from scripts/ to tools/ |
| New files in jules | `jules_pr_triage.py`, `jules-manager.py`, `auth_manager.py`, MCP server, Gemini extension, all skills, docs | New consolidation additions not in kaggle |

**Original consolidation result:** At the time of the source comparison, all 17 Python tools and all 10 command wrappers from kaggle were present; the 5 extra wrappers (`jules-intent`, `jules-pending`, `jules-create`, `jules-ask`, `jules-pr-feedback`) are jules additions, not kaggle origins. Re-run an inventory before using this statement as current completeness evidence.

---

## Storage Mechanisms

See `README.md` for structure overview. Key storage patterns:

- **Session cache:** `EmailIntelligence/jules_sessions/pr*_session.json` (full API response per session)
- **PR mapping:** `session_pr_map.json` (written by `session_pr_triage.py` to CWD)
- **Problematic sessions index:** `EmailIntelligence/.jules/session_analysis/tmp/problematic_sessions.txt`
- **Session details:** `EmailIntelligence/.jules/session_analysis/details/session_{id}.json`
- **Task schedule:** `skills/jules-sessions/references/task_schedule.json`
- **Prompt audit trail:** `skills/jules-sessions/references/sent_responses.md`
- **Monitor state:** `/tmp/jules_monitor.pid` + `jules_monitor.log`

**No server-side filtering** on the `GET /v1alpha/sessions` API — only `pageSize` and `pageToken`. All per-repo filtering must be done client-side by scanning PR URLs and source contexts.
