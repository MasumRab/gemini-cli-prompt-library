# .github/ — Jules Workflow Templates & Distribution

**⚠️ IMPORTANT: This directory contains templates for DISTRIBUTION to target repos, NOT implementation in this repo.**

The workflows and documentation here are staged for distribution to:
- `workspaces/EmailIntelligence/` — EmailIntelligence project
- `workspaces/kaggle-notebooks-analysis/` — Kaggle notebooks project
- `workspaces/gemini-projects/` — Gemini projects

## Purpose

This Jules repository (`jules`) serves as the **canonical source** for:
1. GitHub Actions workflow templates
2. Shared scripts and classifiers
3. Documentation for deployment and configuration

**The workflows in `.github/workflows/` are NOT executed here.** They are templates that get copied to target repos during distribution.

## Distribution Status

| Component | Status | Target Repos |
|-----------|--------|--------------|
| Workflow templates | ✅ Complete | EmailIntelligence, Kaggle, Gemini |
| Documentation | ⚠️ In progress | Needs TARGET_REPOSITORY_ADJUSTMENTS.md per repo |
| Validation | ⚠️ Pending | SMOKE_TEST_PLAN.md not executed |
| Security review | ❌ Open | `contents: write` permissions need review |

## Structure

```
.github/
├── docs/                                 # Distribution documentation
│   ├── README.md                        # This file
│   ├── REVIEW_RECOMMENDATION.md         # Review authority
│   ├── HANDOFF.md                       # Task definitions (W-01 through W-23)
│   ├── EDGE_CASES.md                   # Known edge cases
│   ├── TARGET_REPOSITORY_ADJUSTMENTS.md # Per-repo modifications required
│   ├── SMOKE_TEST_PLAN.md             # Validation requirements
│   ├── HANDOFF_PATTERNS.md             # Implementation patterns
│   ├── WORKTREE_MIGRATION.md           # Legacy migration guide
│   └── OFFICIAL_JULES_ACTION_AUDIT.md # Official action comparison
├── workflows/                           # GitHub Actions workflow templates
│   ├── jules-pr-review.yml             # Auto review on PR open/sync
│   ├── jules-pr-force-review.yml       # Label-triggered review
│   ├── jules-pr-walkthrough.yml       # PR walkthrough
│   ├── jules-pr-auto-fix.yml           # Plan/approve auto-fix
│   ├── jules-pr-resolve-conflicts.yml # Conflict resolution
│   ├── jules-pr-rebuild.yml           # Rebuild from base
│   ├── jules-pr-address-comments.yml  # @jules on threads
│   ├── jules-pr-automerge-label.yml   # Auto-label for merge
│   ├── jules-dispatch.yml             # Command router
│   ├── jules-issue-triage.yml        # Issue triage
│   └── jules-backlog-review.yml       # Weekly stale PR review
├── scripts/                            # Shared scripts
│   └── jules-comment-classifier.cjs   # Comment classification
├── TASKS.md                            # Quick task reference
├── emailintelligence/                  # EmailIntelligence workspace (local)
├── robin/                             # Robin agent workspace
└── robin-workflow-archive/            # Archived workflows
```

## Distribution Checklist

Before copying to target repos:

1. **Review readiness gates** — `docs/REVIEW_RECOMMENDATION.md`
2. **Apply per-repo adjustments** — `docs/TARGET_REPOSITORY_ADJUSTMENTS.md`
3. **Validate YAML** — actionlint + `docs/SMOKE_TEST_PLAN.md`
4. **Security review** — `contents: write` permissions
5. **Branch governance** — Check target's CONTRIBUTING.md
6. **Test in staging** — Don't deploy untested workflows

## How Distribution Works

1. Copy `.github/workflows/*.yml` → target repo's `.github/workflows/`
2. Copy `.github/scripts/*` → target repo's `.github/scripts/`
3. Set required secrets in target repo:
   - `JULES_API_KEY` — Jules API authentication
4. Validate with `docs/SMOKE_TEST_PLAN.md`

## Trust Boundary

The classifier is loaded from a **trusted base-branch checkout** (`_helpers/`), never from
PR-head code. Each workflow uses:

```yaml
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.base.ref }}
    sparse-checkout: .github/scripts
    path: _helpers
```

## Related Documents

| Document | Purpose |
|----------|---------|
| `docs/REVIEW_RECOMMENDATION.md` | Readiness gates and review authority |
| `docs/HANDOFF.md` | Task definitions (W-01 through W-23) |
| `docs/EDGE_CASES.md` | Known edge cases and patterns |
| `docs/TARGET_REPOSITORY_ADJUSTMENTS.md` | Per-repo modifications |
| `docs/SMOKE_TEST_PLAN.md` | Validation requirements |
| `docs/JULES_TASKS.md` | Jules repository tasks (not distribution) |
