# Jules GitHub Actions historical artifacts

Files in this directory preserve design history, copied source evidence, and dated
assessments. They are intentionally retained for traceability, but their paths,
workflow names, implementation counts, and completion claims may be obsolete.

| Artifact                                                         | Status                                                                   | Superseded by / current authority                                                                 |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| [`AUTOREVIEW_JULES_PLAN.md`](AUTOREVIEW_JULES_PLAN.md)           | Completed initial remediation plan; paths and scope are stale            | [`../HANDOFF.md`](../HANDOFF.md) and [`../REVIEW_RECOMMENDATION.md`](../REVIEW_RECOMMENDATION.md) |
| [`CHANGELOG.md`](CHANGELOG.md)                                   | Point-in-time implementation history                                     | Runtime code and [`../HANDOFF.md`](../HANDOFF.md)                                                 |
| [`cross_repo_assessment.md`](cross_repo_assessment.md)           | 2026-07-08 pre-installation assessment                                   | [`../REVIEW_RECOMMENDATION.md`](../REVIEW_RECOMMENDATION.md) plus repository recommendations      |
| [`jules_actions_traceability.md`](jules_actions_traceability.md) | Copied source dump from four repositories                                | Files under [`../recommendations/`](../recommendations/) and the active task tracker              |
| [`kaggle-notebooks-analysis.md`](kaggle-notebooks-analysis.md)   | Legacy recommendation containing dated PR state and third-party examples | Reassess the target repository at distribution time                                               |
| [`external/`](external/)                                         | Workspace-level audits, reasoning, diagrams, and change ledger           | [`../HANDOFF.md`](../HANDOFF.md) and [`../REVIEW_RECOMMENDATION.md`](../REVIEW_RECOMMENDATION.md) |

Historical artifacts must not be silently rewritten to appear current. Add a new
revision-specific review or update an active authority when behavior changes.
