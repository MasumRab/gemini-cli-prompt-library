# Canonical Workflow Inventory

This document provides a comprehensive inventory of all Jules workflows, their triggers, purposes, classifier usage, dependencies, and related system components.

## Complete Workflow Inventory (11 workflows)

| Workflow File | Lines | Triggers | Purpose | Classifier Usage | Dependencies |
|---------------|-------|----------|---------|------------------|--------------|
| `jules-pr-review.yml` | 992 | `pull_request: [opened, synchronize, reopened, ready_for_review]`, `issue_comment: [created]` | Performs comprehensive code reviews using Jules AI, outputs structured review with verdict (approve/comment/block), sets jules/review commit status | Uses `jules-comment-classifier.cjs` to fetch and filter prior comments/reviews, exclude Jules-generated content, and build context for the review prompt | `actions/github-script@v7`, `actions/checkout@v4`, `actions/upload-artifact@v4`, Jules API, GitHub API |
| `jules-pr-auto-fix.yml` | 984 | `pull_request: [opened, synchronize, reopened]`, `issue_comment: [created]` | Automatically addresses review comments and findings from Jules PR review workflow by generating fix PRs | Uses classifier to identify Jules-generated review comments and findings that need addressing | Same as review workflow + additional dependencies for creating fix PRs |
| `jules-pr-walkthrough.yml` | 481 | `pull_request: [opened, synchronize, reopened]`, `issue_comment: [created]` | Generates detailed walkthrough documentation for PRs explaining changes, architectural decisions, and thematic groupings | Uses classifier to exclude walkthrough comments from prior feedback when needed | Same as review workflow |
| `jules-pr-address-comments.yml` | 269 | `pull_request: [opened, synchronize, reopened]`, `issue_comment: [created]` | Addresses general review comments (non-Jules) on PRs by making code changes | Uses classifier to identify which comments need addressing and exclude Jules-generated content | Same as review workflow |
| `jules-pr-resolve-conflicts.yml` | 647 | `pull_request: [opened, synchronize, reopened]`, `issue_comment: [created]` | Automatically resolves merge conflicts in PRs using Jules AI | Uses classifier to identify conflict-related comments and exclude Jules-generated content | Same as review workflow |
| `jules-pr-force-review.yml` | 919 | `pull_request: [opened, synchronize, reopened]`, `issue_comment: [created]` | Forces a new review session even when one exists for the current SHA (bypasses normal deduplication) | Uses classifier same as regular review workflow | Same as review workflow |
| `jules-pr-automerge-label.yml` | 78 | `pull_request: [opened, synchronize, reopened, labeled, unlabeled]`, `issue_comment: [created]` | Automatically adds/removes labels based on review verdict and handles auto-merge when approved | Minimal classifier usage (mainly for checking existing reviews) | Same as review workflow |
| `jules-issue-triage.yml` | 304 | `issues: [opened, reopened, labeled, unlabeled]`, `issue_comment: [created]` | Triages incoming issues by applying labels, assigning priorities, and identifying duplicates | Uses classifier to understand issue context and exclude Jules-generated comments | Same as review workflow |
| `jules-backlog-review.yml` | 295 | `workflow_dispatch`, `schedule: [cron: '0 2 * * 1']` (weekly) | Reviews aged/stale PRs and issues in the backlog to identify those needing attention | Uses classifier to analyze comment history and exclude Jules-generated content | Same as review workflow |
| `jules-dispatch.yml` | 118 | `repository_dispatch: [types: jules-*]` | Central dispatcher that routes specialized jules-* events to appropriate workflows | No direct classifier usage (routes events) | Workflow dependencies based on event type |
| `jules-pr-rebuild.yml` | 558 | `pull_request: [opened, synchronize, reopened]`, `issue_comment: [created]` | Rebuilds PRs from scratch when base branch has diverged significantly | Uses classifier to understand PR context and exclude Jules-generated content | Same as review workflow |

## Shared Classifier Script (.github/scripts/jules-comment-classifier.cjs) Details

### Purpose
Provides shared comment classification and filtering logic for all Jules workflows, replacing inconsistent inline logic that was previously duplicated across 6 workflows with 3 different marker arrays.

### Key Components

#### Constants
- **MARKERS**: Object containing all Jules-specific HTML comment markers used for identification
- **ALL_JULES_MARKERS**: Array of all Jules markers for filtering (15 markers)
- **THIRD_PARTY_MARKERS**: Markers from other bots (Sourcery, CodeRabbit) for exclusion
- **WALKTHROUGH_MARKERS**: Markers specific to walkthrough functionality
- **BOT_IDENTITIES**: Known bot identities (Jules, GitHub Actions, Dependabot)
- **SOURCES**: Classification of comment sources (human, jules-bot, github-actions, etc.)

#### Classification Functions
- `classifyAuthor(user)`: Determines if comment author is human or specific bot type
- `classifyContent(body)`: Analyzes comment content for Jules markers, findings, walkthrough markers, and third-party content
- `isJulesGenerated(authorSource, contentClass)`: Determines if content was generated by Jules
- `formatAttribution(user)`: Formats user attribution for display

#### Fetching Functions
- `fetchIssueComments(github, owner, repo, prNumber)`: Retrieves and processes issue comments
- `fetchReviewComments(github, owner, repo, prNumber)`: Retrieves and processes review comments
- `fetchReviews(github, owner, repo, prNumber)`: Retrieves and processes formal reviews
- `fetchUnresolvedThreads(github, owner, repo, prNumber)`: Retrieves unresolved review threads via GraphQL

#### Main Entry Point
- `classifyAndFilter(github, owner, repo, prNumber, opts)`: Main function that orchestrates fetching, filtering, and formatting of comment data for workflow consumption

#### Options
- `includeReviewComments`: Fetch pull request review comments
- `includeReviews`: Fetch formal reviews
- `includeThreads`: Fetch unresolved review threads (requires GraphQL)
- `includeWalkthrough`: Whether to include walkthrough comments in prior feedback
- `maxComments`: Maximum comments to return per surface
- `maxBodyLength`: Maximum body length to retain per comment

#### Return Value
- `priorFeedback`: Filtered issue comments (human/bot, Jules markers removed)
- `priorReviews`: Filtered line-level review comments (Jules FINDING markers + bot authors removed)
- `julesContext`: Jules-generated content only (for address-comments workflow)
- `hasWalkthrough`: Boolean indicating if walkthrough content exists
- `reviews`: Formal reviews (if requested)
- `unresolvedThreads`: GraphQL threads (if requested)
- `raw`: Raw fetched data for debugging
- `_meta`: Metadata about the filtering process

### Usage in Workflows
```javascript
const { classifyAndFilter } = require('./_helpers/.github/scripts/jules-comment-classifier.cjs');
const result = await classifyAndFilter(github, owner, repo, prNumber, {
  includeReviewComments: true,
  includeReviews: false,
  includeThreads: false,
  includeWalkthrough: false,
  maxComments: 10,
  maxBodyLength: 300,
});
```

## Workflow Markers (17 deduplication markers with workflow mapping)

| Marker | Purpose | Workflows Using This Marker |
|--------|---------|----------------------------|
| `<!-- jules-pr-reviewer -->` | Identifies Jules PR review comments | jules-pr-review.yml, jules-pr-force-review.yml, jules-pr-address-comments.yml, jules-pr-resolve-conflicts.yml, jules-issue-triage.yml, jules-backlog-review.yml, jules-pr-rebuild.yml |
| `<!-- jules-auto-fix -->` | Marks Jules auto-fix attempts | jules-pr-auto-fix.yml, jules-pr-address-comments.yml |
| `<!-- jules-auto-fix-plan -->` | Marks Jules auto-fix planning comments | jules-pr-auto-fix.yml, jules-pr-address-comments.yml |
| `<!-- jules-auto-fix-plan-denied -->` | Marks denied auto-fix plans | jules-pr-auto-fix.yml |
| `<!-- jules-auto-fix-summary -->` | Marks auto-fix summary comments | jules-pr-auto-fix.yml |
| `<!-- jules-auto-fix-plan-stale -->` | Marks stale auto-fix plans | jules-pr-auto-fix.yml |
| `<!-- jules-resolve -->` | Marks conflict resolution comments | jules-pr-resolve-conflicts.yml |
| `<!-- jules-walkthrough -->` | Marks Jules walkthrough comments | jules-pr-walkthrough.yml, jules-pr-review.yml |
| `<!-- jules-rebuild -->` | Marks PR rebuild comments | jules-pr-rebuild.yml |
| `<!-- jules-quota-exhausted -->` | Indicates Jules session quota exceeded | All workflows that create Jules sessions |
| `<!-- jules-address-comments -->` | Marks comments addressing PR feedback | jules-pr-address-comments.yml |
| `<!-- jules-review-deferred -->` | Marks deferred review comments (awaiting session completion) | jules-pr-review.yml (post-deferred job) |
| `<!-- jules-deferred-review-posted -->` | Indicates deferred review has been posted | jules-pr-review.yml (post-deferred job) |
| `<!-- jules-review-pending -->` | Indicates review is pending session completion | jules-pr-review.yml (post-deferred job) |
| `<!-- jules-session:` | Prefix for session identification markers | All workflows that create Jules sessions |
| `<!-- FINDING -->` | Marks individual review findings in PR reviews | jules-pr-review.yml |
| `<!-- walkthrough_start -->` / `<!-- walkthrough_end -->` | Demarcates walkthrough sections in review output | jules-pr-review.yml, jules-pr-walkthrough.yml |

## Bot Identity & Permissions (4 key security properties)

### Bot Identities
1. **Jules Bot**: `google-labs-jules[bot]` - Primary identity for Jules-generated comments and actions
2. **GitHub Actions**: `github-actions[bot]` - Used for workflow automation steps
3. **Dependabot**: `dependabot[bot]` - Dependency update bot (recognized but not primary)
4. **CodeRabbit/Sourcery**: Third-party review bots recognized for filtering purposes

### Key Security Properties
1. **Principle of Least Privilege**: Workflows request only minimum required permissions:
   - `pull-requests: write` (for creating reviews/comments)
   - `contents: read` (for checking out code)
   - `statuses: write` (for setting commit status)

2. **Fork Protection**: All workflows include fork-check logic to prevent executing untrusted code from forked repositories:
   ```bash
   if [ "$HEAD_REPO" != "$BASE_REPO" ]; then
     echo "skip=true" >> "$GITHUB_OUTPUT"
   else
     echo "skip=false" >> "$GITHUB_OUTPUT"
   fi
   ```

3. **Trusted Base Branch Checkout**: Helper scripts are checked out from the base (trusted) branch, not the PR branch:
   ```yaml
   - name: Checkout helper scripts (trusted base branch)
     uses: actions/checkout@v4
     with:
       ref: ${{ github.event.pull_request.base.ref }}
       sparse-checkout: |
         .github/scripts
       path: _helpers
   ```

4. **Input Validation and Sanitization**: All external inputs are validated:
   - Label checks for bypass (`jules-override`)
   - SHA verification to prevent stale state attacks
   - PR head verification before posting reviews
   - Session resource validation in deferred review handling

## External API Integration

### Jules API
- **Session Creation**: `POST https://jules.googleapis.com/v1alpha/sessions`
  - Authentication: `X-Goog-Api-Key` header with API key from secrets
  - Payload: Contains prompt, source context, and repository information
- **Session Polling**: `GET https://jules.googleapis.com/v1alpha/{session_resource}?view=FULL`
  - Used to check session state (QUEUED, RUNNING, COMPLETED, FAILED)
  - Polling interval: 15 seconds, up to 90 attempts (22.5 minutes)
- **Activity Retrieval**: `GET https://jules.googleapis.com/v1alpha/{session_resource}/activities?pageSize=100`
  - Retrieves agent messages and activities from completed sessions
  - Used to extract review/walkthrough output

### GitHub API
Used extensively through `actions/github-script@v7`:
- **Repository Information**: `github.rest.repos.getContent()` for trusted files
- **Pull Request Data**: `github.rest.pulls.get()`, `github.rest.pulls.listFiles()`
- **Issue/Comment Operations**: `github.rest.issues.listComments()`, `github.rest.issues.createComment()`
- **Review Operations**: `github.rest.pulls.createReview()`, `github.rest.pulls.listReviews()`
- **Commit Status**: `github.rest.repos.createCommitStatus()` for `jules/review` status
- **Label Management**: `github.rest.issues.listLabelsOnIssue()`, `github.rest.issues.addLabels()`
- **GraphQL**: For retrieving unresolved review threads

### Session Polling Endpoints
1. **Session Status Check**: 
   ```
   GET https://jules.googleapis.com/v1alpha/{session_name_or_id}?view=FULL
   ```
   Returns: `{ state: "QUEUED|RUNNING|COMPLETED|FAILED", ... }`

2. **Activities Fetch**:
   ```
   GET https://jules.googleapis.com/v1alpha/{session_name_or_id}/activities?pageSize=100
   ```
   Returns: `{ activities: [ { agentMessaged: { agentMessage: "..." } } ] }`

3. **Retry Logic**: Implemented in workflows with exponential backoff:
   ```bash
   retry_curl() {
     local max_retries=3 base_delay=5 attempt=1
     # ... retry logic with increasing delays
   }
   ```

## Critical Security Invariants (12 invariants from REVIEW_RECOMMENDATION.md)

Based on the review recommendations in `docs/actions/REVIEW_RECOMMENDATION.md`, these are the critical security invariants that must be maintained:

1. **Fork Execution Prevention**: Workflows must never execute untrusted code from fork PRs. All workflows implement fork-check logic that skips execution for forked repositories.

2. **Trust Boundary Enforcement**: Helper scripts and configuration must only be loaded from the trusted base branch, never from the PR branch. Workflows use `sparse-checkout` with `ref: ${{ github.event.pull_request.base.ref }}`.

3. **Credential Secrecy**: Jules API keys and other secrets must never be exposed in logs or workflow outputs. All API calls use masked environment variables and avoid echoing sensitive data.

4. **Input Validation**: All external inputs (PR numbers, SHAs, labels, etc.) must be validated before use. Workflows verify SHAs match current PR head before posting reviews.

5. **Privilege Minimization**: Workflows must request only the minimum permissions necessary. Current permissions are `pull-requests: write`, `contents: read`, `statuses: write`.

6. **Output Sanitization**: All content posted to GitHub must be properly sanitized to prevent injection attacks. Workflows use proper escaping and avoid executing untrusted content as code.

7. **Session Integrity**: Jules session resources must be properly validated and associated with the correct PR and SHA. Workflows include SHA verification in both initial review and deferred review handling.

8. **Marker-Based Filtering Reliance**: Dependence on HTML comment markers for identifying Jules-generated content must be robust against spoofing. Markers are specific and unlikely to appear organically.

9. **Atomic Status Updates**: Commit status updates must accurately reflect the review state and not be subject to race conditions. Workflows verify SHA consistency before setting status.

10. **Deferred Review Security**: Deferred review mechanisms must prevent replay attacks and ensure markers are properly validated. Workflows verify both session resource and SHA match before processing.

11. **Third-Party Isolation**: Integration with third-party bots (CodeRabbit, Sourcery) must not create privilege escalation paths. These are treated as regular bot users for filtering purposes.

12. **Audit Trail Completeness**: All Jules actions must leave an auditable trail through HTML comments and consistent naming. Every Jules action includes identifying markers like `<!-- jules-pr-reviewer -->` and session identifiers.