# Desync Worktree Recovery (2026-09-11)

Recovered from the uncommitted working tree of `wt-local` (branch
`desync/local-state`, fully merged into main before cleanup). These files
were never committed on any branch; preserved here because they contain
unique analysis content:

- `EVOLUTION_MAP.md` — 3-phase visual diff of `jules-pr-review.yml`
  (Waves 1–2 problems → Wave 3 gates)
- `TRIGGER_MATRIX.md` — trigger/session routing matrix for all 8 deployed
  workflows; `@jules` vs `/jules` routing comparison
- `BASELINE_SMOKE_REPORT.md` — zero-session smoke test vs PR #737
  (MasumRab/EmailIntelligence), 8/8 PASS, 2026-07-24
- `BASELINE_SMOKE_TEST.sh` — the smoke test script

Everything else in that working tree (workflow yml renames, classifier
copy, EDGE_CASES/HANDOFF_PATTERNS/SMOKE_TEST_PLAN/AUTOREVIEW_JULES_PLAN
copies) duplicated older versions of content already superseded on main
and was discarded. The classifier in `.github/scripts/` on main is the
canonical, newer version.
