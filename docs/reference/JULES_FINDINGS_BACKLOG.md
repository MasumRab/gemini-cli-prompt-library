# Jules Findings & Implementation Backlog

Consolidated, append-only record of findings discovered by subagents during session audits/explorations, plus pending implementation work items, so nothing is lost between sessions.

**Update convention**: append new `### Entry YYYY-MM-DD-NNN` blocks (chronological); mark backlog items as status changes, never delete history.

*Last updated: 2026-08-17*

## Current status snapshot

- Repo branch in use: `jules-pr-alignment-audit-2026-08-14`
- HEAD commit: `1760097`
- Tool suite state: generalized intent tool committed (`jules-intent-metadata`) + P0 enhancements
- Verification approach: `uv run --with pytest pytest tools/tests/`

## Findings log

### Entry 2026-08-17-001
- source: explore - framework conventions audit
- finding: `NO_ACTION_STATES` / `likely_pending` were duplicated across 5+ files; consolidated into `tools/sessions/config.py`.
- impact: Single source of truth for state classification; removes drift risk across session analysis tools.
- status: integrated
- refs: commit 1760097; `tools/sessions/config.py:7`, `tools/sessions/config.py:10`

### Entry 2026-08-17-002
- source: explore - session listing audit
- finding: `tools/sessions/jules_list_sessions.py` historically capped full-account scans at 500 sessions via `max_results=500`, undercounting accounts; new `jules_intent_metadata.py --all` removes the cap. Note: `--anomalies` only surfaces old 2025 records under `--all`.
- impact: Full account scans now complete; anomaly view scope narrows to legacy 2025 records, so newer anomalies must be queried separately.
- status: integrated
- refs: `tools/sessions/jules_list_sessions.py:74`; `tools/sessions/jules_intent_metadata.py`

### Entry 2026-08-17-003
- source: ops review - artifact inventory
- finding: `/tmp/opencode` artifacts are derived operational state; per `docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md:68` no archive companion is required.
- impact: Determines what is safe to delete vs. keep in `/tmp/opencode`; avoids losing historical evidence.
- status: open — pending cleanup decision: `jules_batch_results.json` + `jules_batch_logs/` + `jules/` per-session dumps are historical evidence to keep; `all_sessions.json` / `jules_full_500.json` / `jules_pending_500.json` are redundant raw dumps safe to delete.
- refs: `docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md:68`

### Entry 2026-08-17-004
- source: integration workflow - worktree operations
- finding: `worktrunk_*` tools fail when run from session cwd `/home/masum/github/remote` (not a git repo); subagents must run `wt -C …/jules <cmd>` or plain git inside the jules repo; worktree branches must be explicitly merged and deleted (leftover branch `p0-sessions-integration` was found post-P0).
- impact: Silent failure mode during worktree workflows; leaves stale branches if merge/delete is skipped.
- status: open
- refs: git branch metadata; `wt` toolchain

### Entry 2026-08-17-005
- source: explore - documentation structure audit
- finding: `docs/STORAGE_ARCHITECTURE.md` is orphaned (never linked from `docs/README.md` or `tools_readme.md`); `docs/forensics` naming convention (`UPPER_SNAKE_YYYY-MM-DD.md` + adjacent `snake_case_YYYY-MM-DD.json` + `scratch/`) is de-facto, not codified.
- impact: Structural documentation drift; forensics workflow not discoverable and not enforced.
- status: open — candidates for documentation follow-up.
- refs: `docs/STORAGE_ARCHITECTURE.md`; `docs/forensics/`; `docs/README.md`; `docs/reference/tools_readme.md`

### Entry 2026-08-17-006
- source: ops review - batch send workflow
- finding: `jules_batch_send` workflow (from `/tmp/opencode/jules_batch_send.py` + `jules_batch_results.json`): 12 messages sent sequentially with per-attempt rate-limit handling (60s backoff, 4 retries); HTTP retry now lives in `jules_request` — the batch orchestration + per-attempt logging + results ledger is NOT yet in `tools/`.
- impact: Batch workflow is not reproducible or auditable from the repo.
- status: open → P1 backlog below.
- refs: `/tmp/opencode/jules_batch_send.py`; `/tmp/opencode/jules_batch_results.json`

## Implementation backlog

| ID | Priority | Item | Where it lands | Status | Notes |
| -- | -------- | ---- | -------------- | ------ | ----- |
| B001 | P1 | `jules-manager send-batch FILE.jsonl` subcommand (per-attempt logs + results ledger, reuse `JulesAPIClient.send_message` backoff; port orchestration from `/tmp/opencode/jules_batch_send.py`) | `tools/cli/jules-manager.py` | pending | |
| B002 | P1 | `tools/sessions/jules_sweep.py` with `--since`/`--handled` reproducing `jules_analyze.py` categories A–G (COMPLETED-no-PR code-review-vs-execution split, stale-state, anomaly checks), HANDLED read from a file not a constant | `tools/sessions/` | pending | |
| B003 | P1 | PR-state bucketing on `tools/pr/jules_pr_metadata.py` (open/merged/closed_not_merged/missing) so sweeps can annotate `has_pr` rows | `tools/pr/jules_pr_metadata.py` | pending | |
| B004 | P1 | Generalize `docs/forensics/scratch/` md+json report generator (`gen_md.py`/`gen_drafts.py` patterns) into a template-driven builder per `docs/forensics/README.md` schema | `docs/forensics/` | pending | |
| B005 | P2 | `commands/jules-sweep` wrapper (mirror `commands/jules-pending`) once B002 lands | `commands/` | pending | |
| B006 | P2 | `skills/jules-sessions/SKILL.md` + `tools_readme.md` updates for new tools/flags; add `jules-pr-feedback` row to `commands/README.md` if missing | `skills/jules-sessions/SKILL.md`; `docs/reference/tools_readme.md`; `commands/README.md` | pending | |
| B007 | P2 | Archive 12 sent messages + `jules/` dumps as labeled historical evidence (`docs/actions/artifacts/` or `docs/forensics/scratch/`) then clean `/tmp/opencode` per the delete-keep table | `docs/actions/artifacts/`; `docs/forensics/scratch/` | pending | |
| B008 | P2 | Codify forensics naming convention in `docs/forensics/README.md`; link `docs/STORAGE_ARCHITECTURE.md` from `docs/README.md` | `docs/forensics/README.md`; `docs/README.md` | pending | |
| B009 | P2 | Decide on the 36 deferred FAILED sessions (sent-response batch was capped at 12 by user; full nudge list remains undone) + the 15 missed candidates from the 2026-08-17 full sweep (top: `7404018986702295062`, `17065719860896443446`, `14797958652014372092`, `18254541687978082373`, `1294448413598615402`, `12369636951710389217`, `11267029240983047750`, `15014477667741021080`, `10304958435902448274`, `2088004130054247653`) | n/a | pending | awaits user decision |
| B010 | P2 | Session `1122791329330329850` (Sentinel) still `AWAITING_USER_FEEDBACK` after hash-on-dump approval reply; verify pickup | n/a | pending | |
| B011 | P2 | Subermemory update v2.0.9 → v2.0.12 (interactive installer, modifies `~/.config/opencode/opencode.jsonc`) — run `bunx opencode-supermemory@latest install` manually | `~/.config/opencode/opencode.jsonc` | pending | interactive |

## Historical record of sent responses

`sent_responses.md` at `skills/jules-sessions/references/sent_responses.md` is the canonical log (committed; entries `-001…-015` in commit `5a3808b`). Batch sends skip write-through to this file and are tracked separately in `/tmp/opencode/jules_batch_results.json` pending normalisation into `tools/` (see B001).