# Imported external Jules Actions evidence

These files were imported on 2026-08-03 from the parent multi-repository workspace so
that a standalone clone of `jules` retains the evidence referenced by its review and
handoff documents.

They are immutable historical snapshots, not current behavior, task status, or target
repository policy. Verify every claim against the current authorities and runtime code.

| Snapshot                                                                             | Original workspace path                        | SHA-256 at import                                                  | Use                                                              |
| ------------------------------------------------------------------------------------ | ---------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| [`GEMINI_JULES_ANALYSIS.md`](GEMINI_JULES_ANALYSIS.md)                               | `gemini_jules_analysis.md`                     | `14c5617d44d5f662ac473bd68371d2675a4b5785e6e0cd2ef7c9ba64596bca5a` | Gemini-to-Jules comparison and source for several handoff tasks  |
| [`JULES_WORKFLOW_TRIGGER_AUDIT.md`](JULES_WORKFLOW_TRIGGER_AUDIT.md)                 | `docs/JULES_WORKFLOW_TRIGGER_AUDIT.md`         | `455ef47a5e90a795ae5dfe1616d430019d3ba935ffce2cfad8a1942f6d2b96df` | Original bot-identity and trigger audit                          |
| [`JULES_WORKFLOW_REASONING_AND_CHANGES.md`](JULES_WORKFLOW_REASONING_AND_CHANGES.md) | `docs/JULES_WORKFLOW_REASONING_AND_CHANGES.md` | `53b7cda84ae99a4ab63108f20b6eb35cdf40beff14a760f898ac46d198fbf3f5` | Cross-repository repair rationale and historical findings        |
| [`JULES_WORKFLOW_FLOW_DIAGRAM.txt`](JULES_WORKFLOW_FLOW_DIAGRAM.txt)                 | `docs/JULES_WORKFLOW_FLOW_DIAGRAM.txt`         | `f1d88cf0650598ece798a394ac8b9d3374eeaa96475f4eff13864e7868da9537` | Point-in-time workflow model derived from the reasoning document |
| [`CHANGES_RECORD.md`](CHANGES_RECORD.md)                                             | `CHANGES_RECORD.md`                            | `6db9479a555052de9afcd2bb9aa3a18922210b585f0e9aed2792cb38a00d81cc` | Multi-repository commit and validation ledger                    |

Current authorities:

- Runtime: `.github/workflows/` and `.github/scripts/`
- Task status: [`../../HANDOFF.md`](../../HANDOFF.md)
- Readiness: [`../../REVIEW_RECOMMENDATION.md`](../../REVIEW_RECOMMENDATION.md)
- Validation: [`../../SMOKE_TEST_PLAN.md`](../../SMOKE_TEST_PLAN.md)

Do not copy target-repository policy from these snapshots into prompts. T-24 requires
the current policy to be read from the target repository's exact base revision and
separately classified as prompt context, a deterministic check, or operator guidance.
