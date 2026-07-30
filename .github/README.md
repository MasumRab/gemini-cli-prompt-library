# .github/ — Jules Workflow Templates & Shared Scripts

This directory contains the **canonical templates** that are distributed to all deployed repos.

## Structure

```
.github/
├── workflows/                          # GitHub Actions workflow templates
│   ├── jules-pr-review.yml             # Auto review on PR open/sync
│   ├── jules-pr-force-review.yml       # Manual review via label or /jules-force-review
│   ├── jules-pr-walkthrough.yml        # PR walkthrough via label or /jules-walkthrough
│   ├── jules-pr-auto-fix.yml           # Auto-fix via label or /jules-fix
│   ├── jules-pr-resolve-conflicts.yml  # Conflict resolution via label or /jules-resolve
│   ├── jules-pr-rebuild.yml            # Rebuild from base via label or /jules-rebuild
│   ├── jules-pr-address-comments.yml   # @jules on unresolved review threads
│   └── jules-pr-automerge-label.yml    # Hourly cron: label Jules PRs for auto-merge
├── scripts/                            # Shared scripts loaded by workflows
│   └── jules-comment-classifier.cjs    # Comment classification & filtering (F1 fix)
└── README.md                           # This file
```

## Distribution

To deploy to a target repo:

1. Copy `.github/workflows/jules-pr-*.yml` → target repo's `.github/workflows/`
2. Copy `.github/scripts/jules-comment-classifier.cjs` → target repo's `.github/scripts/`
3. No path adjustments needed — the `require()` path
   `./_helpers/.github/scripts/jules-comment-classifier.cjs` works in every repo
   because `.github/` is a standard GitHub directory.

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
