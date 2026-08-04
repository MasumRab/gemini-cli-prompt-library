# .github/ — Jules Workflow Templates & Shared Scripts

This directory contains the **canonical templates** that are distributed to all deployed repos.

## Structure

```
.github/
├── workflows/                              # GitHub Actions workflow templates
│   ├── jules-pr-review.yml                 # Auto review on PR open/sync + deferred review
│   ├── jules-pr-force-review.yml           # Label/label-triggered review + deferred review
│   ├── jules-pr-walkthrough.yml            # PR walkthrough via label or /jules-walkthrough
│   ├── jules-pr-auto-fix.yml               # Plan/approve auto-fix via label or /jules-fix
│   ├── jules-pr-resolve-conflicts.yml      # Conflict resolution via label or /jules-resolve
│   ├── jules-pr-rebuild.yml                # Rebuild from base via label or /jules-rebuild
│   ├── jules-pr-address-comments.yml       # @jules on unresolved review threads
│   ├── jules-pr-automerge-label.yml        # Hourly cron: label Jules PRs for auto-merge
│   ├── jules-dispatch.yml                  # @jules central command router
│   ├── jules-issue-triage.yml              # Single + batch issue triage (hourly + on-demand)
│   └── jules-backlog-review.yml            # Weekly stale PR functional review (never closes)
├── scripts/                                # Shared scripts loaded by workflows
│   └── jules-comment-classifier.cjs        # Comment classification & filtering
└── README.md                               # This file
```

## Distribution

To deploy to a target repo:

1. Copy all 11 `.github/workflows/jules-*.yml` files → target repo's `.github/workflows/`
2. Copy `.github/scripts/jules-comment-classifier.cjs` → target repo's `.github/scripts/`
3. Reconcile target-repository policy and intentional overlays under T-24 before
   replacing any existing target workflow.
4. No path adjustments are needed for classifier consumers — the `require()` path
   `./_helpers/.github/scripts/jules-comment-classifier.cjs` works in every repo
   because `.github/` is a standard GitHub directory.

Use `docs/actions/REVIEW_RECOMMENDATION.md` for readiness gates and content-hash
validation. Distribution is not a blind directory copy.

## Legacy worktrees

Worktrees created before commit `b706754` may still edit executable templates under
`docs/actions/workflows/` and the classifier under `docs/actions/scripts/`. GitHub does
not execute workflows from those paths. Follow
[`docs/actions/WORKTREE_MIGRATION.md`](../docs/actions/WORKTREE_MIGRATION.md) to replay
in-flight semantic changes onto the current `.github/` implementation without losing
later hardening or restoring duplicate legacy files.

## Trust Boundary

The classifier is loaded from a **trusted base-branch checkout** (`_helpers/`), never from
PR-head code. Each workflow's "Checkout helper scripts" step uses:

```yaml
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.base.ref }}
    sparse-checkout: .github/scripts
    path: _helpers
```

This ensures fork PRs and malicious PR-head modifications cannot alter the classifier code.
