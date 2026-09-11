# Docs Conformance Findings (T1/T2/T3/T4/T5 audit — 2026-08-11)

Evidence log for documented contradictions identified by the static conformance scan
(`scripts/audit_docs_conformance.py`) and validated by session-corpus analysis
(`scripts/analyze_session_corpus.py`) and live trials (`scripts/live_message_trials.py`).

## CONFIRMED — 7 docs violations (T1, static + code review)

All in `skills/jules-workflows/SKILL.md`:

| Line | Kind | Violation | Canonical form |
|------|------|-----------|----------------|
| 47 | payload key | `"baseBranch"` | `sourceContext.githubRepoContext.startingBranch` |
| 48 | payload key | `"autoPr"` | `automationMode: "AUTO_CREATE_PR"` (optional) |
| 87 | endpoint | `:approve` | `:approvePlan` |
| 224 | endpoint | `:cancel` | no cancel endpoint documented; use `DELETE /sessions/{id}` |
| 233 | endpoint | `:approve` | `:approvePlan` |
| 341 | endpoint | `:cancel` | see 224 |
| 350 | endpoint | `:approve` | `:approvePlan` |

Baseline: `tools/api/jules_api_client.py` (canonical) and `skills/jules-api/references/*`.

## CONFIRMED — FAILED sessions accept sendMessage (T5b, live, 2/2 trials per session)

- Sessions tested: 10865630989900669675, 13005011563799472129 (retry text),
  9164742845732374282 (recovery-directive text) — all `FAILED` for 110+ days.
- All 6 attempts returned empty HTTP 200. Verdict: SUPPORTED.
- Docs corrected: `docs/runbooks/failure_runbook.md` (abandon checklist wording),
  `docs/reference/rest_api_reference.md` (Notes).

## SUPPORTED with caveat — message method effectiveness (T4, live, N=2/repo)

| Arm | Session | Outcome at first poll (~100 min) |
|-----|---------|-----------------------------------|
| surgical | 6551222913502603426 (PR #724) | AWAITING -> **IN_PROGRESS** (agent working) |
| generic | 16994837303056291039 | AWAITING -> **FAILED** |
| surgical-2 | 3921006696662628935 (PR #727) | pending poll |
| generic-2 | 13172420826211369022 | pending poll |

Verdict: INCONCLUSIVE at N=1; directionally favors surgical messages. Re-poll before acting.

## PARTIAL — PR-creation decision dead-end (T3, corpus)

- 3/21 sessions explicitly await a PR-creation decision (14823980629961743161,
  3620294950430015682, 11122169390008224115) — contradicts the "we NEVER create new PRs"
  policy in `skills/jules-sessions/references/response_templates.md` in spirit, but no
  session text quotes the NEVER-create rule, so the earlier "10/19" estimate was an
  overstatement. Corrected to 3/21 asking; 12/21 await *any* operator decision.

## CONFIRMED — stalls dominate over crashes (T2, corpus)

- 12/21 sessions in `AWAITING_USER_FEEDBACK`, 13 with ZERO user replies; 5 FAILED;
  median age of untouched awaiting sessions > 100 days. 6 of 6 ci-fix sessions failed
  or stalled; 5/6 FAILED+stalled attributed to decisions never being made.

## CONFIRMED — corpus schema drift (T2b)

- 6/21 tracking files carry `context_analysis` (2026-07 schema); 15/21 are raw session
  payloads (2026-04 schema, no analysis fields). Cross-schema comparison is lossy;
  `scripts/analyze_session_corpus.py` requires SUMMARY.json overlay to compensate.
- 1 benign variant: 14586978430582998057 has `sourceContext` without
  `githubRepoContext` (repoless/env-only session) — valid API, not a doc error.

Run commands:
    python3 scripts/audit_docs_conformance.py
    python3 scripts/analyze_session_corpus.py
    python3 scripts/live_message_trials.py   # sends messages; needs JULES_API_KEY
### T4 update — second poll (2/2 concordant, 2026-08-11)
- surgical arm: 3921006696662628935 + 6551222913502603426 -> IN_PROGRESS (2/2)
- generic arm: 13172420826211369022 + 16994837303056291039 -> FAILED (2/2)
- Confound noted: arm correlates with repo (EmailIntelligence vs stale kaggle sessions);
  verdict remains directional, not causal.
