# Jules — Consolidated Tooling & Skills

Single source of truth for Jules AI coding session management: skills, tools, docs, and extensions.

> **Agent and reviewer cold start:** read [`AGENTS.md`](AGENTS.md) and
> [`JULES_REVIEW_GUIDE.md`](JULES_REVIEW_GUIDE.md). The detailed documentation map is
> [`docs/README.md`](docs/README.md).

## What This Is

Centralized repository for all Jules-related tooling, consolidating 68 unique items from 7 scattered locations into one repo. Designed for development, testing, and future integration with `@google/jules-sdk`.

## Structure

```
jules/
├── AGENTS.md        # Repository-wide cold-start instructions
├── JULES_REVIEW_GUIDE.md # Root review and implementation map
├── skills/          # 7 skills (35 files) — Jules API, CLI, sessions, workflows, scheduling, session-manager, wrapup
├── tools/           # Python tools + shell scripts
│   ├── api/         # Jules API client
│   ├── sessions/    # Session management (list, monitor, recover, approve, send)
│   ├── pr/          # PR tools (context, triage, audit)
│   ├── rebase/      # Safe rebase orchestrator
│   ├── multi_repo/  # Multi-repo operations
│   ├── cli/         # CLI entry point (jules-manager.py)
│   ├── utils/       # Shared utilities (auth, config, pre-flight check)
│   ├── shell/       # Shell scripts (audit, sync, setup, retrieve)
│   └── tests/       # Test suite
├── commands/        # 10 shell wrapper commands
├── docs/            # Documentation map and subsystem-specific authorities
│   ├── actions/     # Distributable Actions review, tasks, tests, recommendations, artifacts
│   ├── reviews/     # Revision-specific subsystem reviews
│   ├── runbooks/    # Operator procedures
│   ├── reference/   # REST and tooling reference
│   ├── guides/      # Quickstart, operations, templates, archive standard
│   ├── triage/      # Repository-specific triage material
│   ├── prompts/     # Formatted prompts and response templates
│   ├── behavioral/  # Jules behavioral instructions
│   └── extracted/   # Extracted role docs and configs
├── extensions/      # Gemini CLI extension
└── CHECKLIST.md     # Consolidation checklist (170+ checkpoints)
```
\n## Standardized Forensics Data Format

The `docs/forensics/` directory contains standardized forensics data in JSON format, including:
- `migrated_forensics_data.json`: The migrated forensics data in the standardized format.
- `forensics_data_schema.json`: The JSON schema defining the standardized format.

\n## Key Design Decisions

1. **Path mapping**: `scripts/jules_tools/` → `tools/`, `scripts/core/` → `tools/utils/`, `~/.agents/commands/` → `tools/cli/`
2. **State names**: All files use official Jules API state enum (QUEUED, PLANNING, AWAITING_PLAN_APPROVAL, AWAITING_USER_FEEDBACK, IN_PROGRESS, PAUSED, COMPLETED, FAILED, STATE_UNSPECIFIED)
3. **API payload**: All `send_message` calls use `{"prompt": "..."}` (not `{"message": {"text": "..."}}`)
4. **Skills distribution**: Custom sync script with path rewriting (not `skills` CLI, not symlinks)

## 11 Interaction Modalities

This folder implements 11 distinct ways to interact with Jules. See `docs/reference/tools_readme.md` for complete per-file inventory.

| #   | Modality                              | Entry Point                                           | Auth                   |
| --- | ------------------------------------- | ----------------------------------------------------- | ---------------------- |
| 1   | Python REST Client (`JulesAPIClient`) | `tools/api/jules_api_client.py`                       | API key                |
| 2   | Raw curl / HTTP                       | Runbook examples, `commands/jules_triage.sh` fallback | API key                |
| 3   | Individual Python Session Scripts     | `tools/sessions/*.py` (7 scripts)                     | API key                |
| 4   | Python PR Tooling                     | `tools/pr/*.py` (4 scripts)                           | API key + GitHub token |
| 5   | Unified Python CLI                    | `tools/cli/jules-manager.py`                          | API key                |
| 6   | Shell Command Wrappers                | `commands/` (10 wrappers)                             | API key                |
| 7   | Operational Shell Scripts             | `tools/shell/` (6 scripts)                            | API key                |
| 8   | MCP Server (TypeScript/SDK)           | `extensions/gemini-cli-jules/mcp-server/src/jules.ts` | API key                |
| 9   | Gemini CLI Extension Prompt           | `extensions/gemini-cli-jules/commands/jules.toml`     | OAuth                  |
| 10  | Skill-based Agent Instructions        | `skills/` (7 skill directories)                       | Any                    |
| 11  | Jules CLI Binary (referenced)         | `npm install -g @google/jules`                        | OAuth                  |

## Quick Usage

```bash
# List sessions with grading
python tools/sessions/jules_list_sessions.py

# Send message to session
python tools/sessions/jules_send_message.py <session_id> "your message"

# Approve plan
python tools/sessions/jules_approve_plan.py <session_id>

# Audit sessions from cache
bash tools/shell/jules_audit.sh

# Unified CLI
python tools/cli/jules-manager.py list
python tools/cli/jules-manager.py send <session_id> "message"

# Session-PR correlation for specific repo
python tools/pr/session_pr_triage.py --repo <owner>/<repo>
```

## Source Mapping

| Source Location                                   | Destination                                  |
| ------------------------------------------------- | -------------------------------------------- |
| `kaggle-notebooks-analysis/scripts/julius_tools/` | `tools/api/`, `tools/sessions/`, `tools/pr/` |
| `kaggle-notebooks-analysis/scripts/core/`         | `tools/utils/`                               |
| `kaggle-notebooks-analysis/scripts/skills/`       | `tools/pr/`                                  |
| `~/.agents/commands/`                             | `tools/cli/`                                 |
| `~/.agents/skills/jules-*`                        | `skills/`                                    |
| `~/.gemini/extensions/gemini-cli-jules/`          | `extensions/`                                |
| `kaggle-notebooks-analysis/docs/jules/`           | `docs/runbooks/`, `docs/reference/`          |

## License

MIT
