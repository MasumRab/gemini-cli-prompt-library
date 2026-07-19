# Jules Capability Matrix

How each implementation layer maps to user-facing capabilities.

## Legend

| Layer | Language | Backend | File(s) |
|-------|----------|---------|---------|
| **MCP Server** | TypeScript | `@google/jules-sdk` | `extensions/gemini-cli-jules/mcp-server/src/jules.ts` |
| **CLI binary** | JavaScript | `@google/jules` (npm) | External (not in repo) |
| **Python REST** | Python 3 | `urllib` → REST API | `tools/api/jules_api_client.py` |
| **SDK Bridge** | Python → Node | subprocess → `@google/jules-sdk` | `tools/sdk/bridge.py` |
| **Unified CLI** | Python 3 | Delegates to REST or SDK Bridge | `tools/cli/jules-manager.py` |
| **Shell wrappers** | Bash | Delegates to Unified CLI or curl | `commands/` |

## Capability Cross-Reference

| Capability | MCP | CLI bin | Python REST | SDK Bridge | Unified CLI | Shell wrapper |
|---|---|---|---|---|---|---|
| List sessions | — | ✅ | ✅ | — | `list` | `jules-list` |
| Get session | ✅ | ✅ | ✅ | ✅ | `session` | — |
| Send message | ✅ | ✅ | ✅ | ✅ | `send` | `jules_recover.sh` |
| Approve plan | ✅ | ✅ | ✅ | ✅ | `approve` | — |
| Create task | ✅ | ✅ | ✅ | ✅ | `create` | `jules-create` |
| Ask (sync) | ✅ | — | ✅ | ✅ | `ask` | `jules-ask` |
| Wait for state | ✅ | — | ✅ | ✅ | `wait` | — |
| Stream activities | — | — | — | ✅ | — | — |
| Archive/Unarchive | — | — | ✅ | — | `archive` | — |
| Delete session | — | — | ✅ | — | `delete` | — |
| List sources | — | — | ✅ | — | — | — |
| PR safety audit | — | — | — | — | — | `jules_audit.sh` |
| Session↔PR triage | — | — | — | — | — | `jules_triage.sh` |
| Pull diff | — | ✅ | — | — | — | — |
| Login | — | ✅ | — | — | — | — |

## When to Use Each Layer

| If you... | Use |
|-----------|-----|
| Are in Gemini CLI | MCP Server (auto via extension) |
| Want quick shell commands | Shell wrappers (`commands/jules-list`) |
| Need to script in Python | Python REST (`JulesAPIClient`) — all features |
