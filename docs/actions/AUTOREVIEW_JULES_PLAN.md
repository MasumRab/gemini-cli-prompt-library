# Jules Workflow Remediation Plan

**Created:** 2026-07-30
**Scope:** Centralized fixes in the `jules` template repo (`docs/actions/workflows/`). Distribution to deployed repos (KNA, GFLQ, GCPL, EI) happens after all template fixes are validated.
**Principle:** Solve every problem once in the template, verify, then propagate.

---

## 1. Current State Census

### 1.1 Template Workflows (`jules/docs/actions/workflows/`)

| Workflow | Lines | Trigger | Polls? | Posts? |
|---|---|---|---|---|
| `jules-pr-review.yml` | 513 | `pull_request` | Yes (60×15s) | Review + commit status |
| `jules-pr-force-review.yml` | 505 | `pull_request` + `issue_comment` | Yes (60×15s) | Review + commit status |
| `jules-pr-walkthrough.yml` | 375 | `pull_request` + `issue_comment` | Yes (60×15s) | Issue comment (update-in-place) |
| `jules-pr-rebuild.yml` | 499 | `pull_request` + `issue_comment` | Analysis only (40×15s) | Analysis comment + fire-and-forget rebuild |
| `jules-pr-auto-fix.yml` | 283 | `pull_request` + `issue_comment` | No (fire-and-forget) | Quota comment only |
| `jules-pr-resolve-conflicts.yml` | 462 | `pull_request` + `issue_comment` | PR stability only | Monitoring comment |
| `jules-pr-address-comments.yml` | 231 | `pull_request_review_comment` | No (delegates to @jules) | @jules issue comment |
| `jules-pr-automerge-label.yml` | 78 | `schedule` + `workflow_dispatch` | No | Labels + auto-merge mutation |

### 1.2 Classifier (`docs/actions/scripts/jules-comment-classifier.cjs`)

356 lines, tracked. Exports `classifyAndFilter`, `classifyAuthor`, `classifyContent`, `isJulesGenerated`, markers, and sources. **Not imported by any workflow.**

---

## 2. Defect Inventory

### 2.1 Systemic Defects (affect all or most workflows)

| ID | Defect | Severity | Affected Workflows |
|---|---|---|---|
| **F1** | `priorReviews` unfiltered — Jules-generated line-level comments fed back to Jules (feedback loop) | 🔴 Critical | review, force-review, walkthrough, auto-fix, resolve-conflicts |
| **F2** | `comment` verdict sets `statusState = 'success'` (green) instead of neutral | 🟠 High | review, force-review |
| **F3** | No Jules API retry/backoff — transient 5xx/network errors kill the run | 🟠 High | review, force-review, walkthrough, rebuild, auto-fix, resolve-conflicts |
| **F4** | Single-message capture — only `[-1].agentMessage` is kept; earlier messages lost | 🟠 High | review, force-review, walkthrough, rebuild |
| **F5** | No cross-session dedup — repeated triggers create duplicate sessions | 🟡 Medium | review, force-review, walkthrough, auto-fix, resolve-conflicts, rebuild |
| **F6** | Review comments not paginated — `per_page: 20` without `github.paginate` | 🟡 Medium | review, force-review, walkthrough, auto-fix, resolve-conflicts |
| **F7** | Broad 403=quota classification — masks auth/permission errors | 🟡 Medium | all workflows that call the Jules API |
| **F8** | No artifact upload — session output lost after workflow ends | 🟢 Low | all polling workflows |
| **F9** | Classifier not integrated — the fix for F1 exists but is not wired in | 🔴 Critical | all workflows |

### 2.2 Workflow-Specific Defects

| ID | Defect | Severity | Workflow |
|---|---|---|---|
| **W1** | Broken `issue_comment` path — accesses `payload.pull_request` which doesn't exist for `issue_comment` events | 🔴 Critical | auto-fix |
| **W2** | Unauthenticated slash commands — no `author_association` or PR check | 🟠 High | auto-fix, rebuild, resolve-conflicts |
| **W3** | Missing `<!-- jules-walkthrough -->` in skipMarkers | 🟡 Medium | resolve-conflicts |
| **W4** | Stale marker comment selection — `find()` returns oldest, not newest | 🟡 Medium | rebuild, walkthrough |
| **W5** | Post step reads nonexistent file when create/poll fails | 🟡 Medium | force-review, walkthrough |
| **W6** | Prompt defaults to `[VERDICT]: comment`, biasing output | 🟢 Low | review, force-review |
| **W7** | Review always posted as `event: 'COMMENT'` even for approve/block | 🟢 Low | review, force-review |
| **W8** | No fork guard on conflict check step | 🟡 Medium | resolve-conflicts |
| **W9** | Concurrency key missing for `issue_comment` events | 🟡 Medium | auto-fix |
| **W10** | Unsafe multiline `$GITHUB_OUTPUT` for slash commands | 🟢 Low | auto-fix, rebuild, resolve-conflicts |

### 2.3 Classifier Defects

| ID | Defect | Severity |
|---|---|---|
| **C1** | `excludeWalkthrough` semantics inverted — `true` includes walkthroughs, should be `includeWalkthrough` | 🟠 High |
| **C2** | `filteredReviewComments` metadata counts retained, not filtered — misnamed | 🟡 Medium |
| **C3** | GraphQL thread pagination capped at 100, no cursor pagination | 🟡 Medium |
| **C4** | Thread author type inferred solely from `[bot]` suffix — Apps without suffix misclassified | 🟡 Medium |
| **C5** | `Promise.all` makes optional fetches fatal — if threads query fails, all results lost | 🟠 High |
| **C6** | File path in docs says `.js` but actual file is `.cjs` | 🟢 Low |
| **C7** | `WALKTHROUGH_END` marker defined but never used in `classifyContent` | 🟢 Low |
| **C8** | `WALKTHROUGH_MARKERS` exported but duplicates logic in `classifyContent` | 🟢 Low |

---

## 3. Remediation Plan

### Phase 1: Classifier Hardening (prerequisite for all workflow fixes)

**Goal:** Fix all classifier defects so it can be safely integrated into workflows.

1. **C1 fix:** Rename `excludeWalkthrough` → `includeWalkthrough`, invert logic. `includeWalkthrough=true` means walkthrough comments are *included* in `priorFeedback` (i.e., NOT filtered out). Default `false`.
2. **C2 fix:** Rename `filteredReviewComments` → `retainedReviewComments` in `_meta`.
3. **C3 fix:** Add cursor-based pagination to `fetchUnresolvedThreads` — loop `after` cursor until all threads fetched.
4. **C4 fix:** Use GitHub GraphQL `author.__typename` instead of `[bot]` suffix inference.
5. **C5 fix:** Replace `Promise.all` with `Promise.allSettled` — optional fetches that fail return `[]` with a warning, do not crash.
6. **C6 fix:** Update header docs to reference `.cjs` path.
7. **C7 fix:** Use `WALKTHROUGH_END` in `classifyContent` for completeness.
8. **C8 fix:** Refactor `classifyContent` to use `WALKTHROUGH_MARKERS` array.

### Phase 2: Workflow Trust Boundary (prerequisite for classifier integration)

**Goal:** Ensure workflows can safely load the classifier from a trusted source.

Every workflow that will `require()` the classifier needs a **trusted base-branch checkout** of the `docs/actions/scripts/` directory. The classifier must never be loaded from PR-head code.

Add a step before the prompt-preparation step:

```yaml
- name: Checkout helper scripts (trusted base branch)
  uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.base.ref }}
    sparse-checkout: |
      .github/scripts
    path: _helpers
```

Then in `github-script` steps, load via:
```javascript
const { classifyAndFilter } = require('./_helpers/.github/scripts/jules-comment-classifier.cjs');
```

**Note:** For `issue_comment` triggered workflows, the base ref must be resolved from the PR API since `github.event.pull_request` is not available. See Phase 3 event normalization.

### Phase 3: Systemic Workflow Fixes (apply to all workflows)

**F9 + F1 fix — Integrate classifier, filter priorReviews:**
Replace inline `skipMarkers` arrays and manual `priorFeedback`/`priorReviews` construction with:
```javascript
const result = await classifyAndFilter(github, owner, repo, prNumber, {
  includeReviewComments: true,
  includeReviews: false,
  includeThreads: false,
  includeWalkthrough: false,  // true for auto-fix only
  maxComments: 10,
  maxBodyLength: 300,
});
const { priorFeedback, priorReviews, hasWalkthrough } = result;
```

**F2 fix — comment verdict = neutral:**
In review and force-review workflows:
```javascript
// BEFORE:
statusState = 'success';   // comment verdict
// AFTER:
statusState = 'neutral';   // comment verdict — not blocking, not approved
```

**F3 fix — Jules API retry/backoff:**
Wrap session creation and polling curl calls in a retry function:
```bash
retry_curl() {
  local max_retries=3
  local base_delay=5
  for attempt in $(seq 1 $max_retries); do
    RESPONSE=$(curl -sS --fail-with-body --connect-timeout 10 --max-time 60 "$@")
    local rc=$?
    if [ $rc -eq 0 ]; then echo "$RESPONSE"; return 0; fi
    if [ $attempt -lt $max_retries ]; then
      sleep $((base_delay * attempt))
    fi
  done
  echo "$RESPONSE"
  return 1
}
```

**F4 fix — multi-message capture:**
Replace `[-1].agentMessage` with join of all agentMessages:
```bash
echo "$ACTS" | jq -r '[
  (.activities // [])[]
  | select(.agentMessaged.agentMessage != null)
  | .agentMessaged.agentMessage
] | join("\n\n---\n\n") // "Review unavailable"'
```

**F5 fix — cross-session dedup:**
Before creating a new session, check for an existing issue comment with the workflow's marker and the same head SHA:
```javascript
const existing = issueComments.find(c =>
  c.body?.includes(MARKER) &&
  c.body?.includes(`head_sha:${headSha}`)
);
if (existing) {
  core.info('Session already created for this SHA — skipping');
  core.setOutput('skip', 'true');
  return;
}
```
Include `<!-- head_sha: <sha> -->` in posted output comments.

**F6 fix — review comment pagination:**
Already fixed by the classifier's `fetchReviewComments` which uses `github.paginate`.

**F7 fix — precise quota detection:**
Only treat 429 and specific quota messages as quota exhaustion:
```bash
if [ "$ERROR_CODE" = "429" ] || echo "$ERROR_MSG" | grep -qiE 'quota|limit|exceeded|capacity|daily'; then
  # quota
elif [ "$ERROR_CODE" = "403" ]; then
  # could be permissions — log differently
  echo "::warning::HTTP 403 — may be permissions, not quota: $ERROR_MSG"
  exit 1
fi
```

**F8 fix — artifact upload:**
After polling completes, upload the session output:
```yaml
- name: Upload session output
  if: always() && steps.prepare.outputs.skip != 'true'
  uses: actions/upload-artifact@v4
  with:
    name: jules-${{ workflow.name }}-${{ github.event.pull_request.number }}
    path: /tmp/jules-*-output.txt
    retention-days: 30
```

### Phase 4: Workflow-Specific Fixes

**W1 fix — auto-fix broken issue_comment path:**
Add a PR resolution step at the top of the prepare script:
```javascript
let pr;
if (context.eventName === 'issue_comment') {
  if (!context.payload.issue?.pull_request) {
    core.setOutput('skip', 'true');
    return;
  }
  const { data } = await github.rest.pulls.get({
    owner: context.repo.owner, repo: context.repo.repo,
    pull_number: context.payload.issue.number,
  });
  pr = data;
} else {
  pr = context.payload.pull_request;
}
```

**W2 fix — authenticate slash commands:**
Add to the `if` condition for `issue_comment` events:
```yaml
if: >
  github.event.label.name == 'jules-fix' ||
  (github.event_name == 'issue_comment' &&
   github.event.issue.pull_request &&
   startsWith(github.event.comment.body, '/jules-fix') &&
   contains('OWNER,MEMBER,COLLABORATOR', github.event.comment.author_association))
```

**W3 fix — add walkthrough skipMarker to resolve-conflicts:**
Add `'<!-- jules-walkthrough -->'` to the `skipMarkers` array.

**W4 fix — newest marker comment selection:**
Replace `comments.find(...)` with:
```javascript
const existing = comments
  .filter(c => c.body?.includes(MARKER))
  .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];
```

**W5 fix — guard file read:**
```javascript
let reviewText = 'Review unavailable';
try {
  reviewText = fs.readFileSync('/tmp/jules-review-output.txt', 'utf8');
} catch (e) {
  core.warning(`Output file not found: ${e.message}`);
  // still post a status indicating failure
}
```

**W6 fix — remove default verdict from prompt:**
Change `[VERDICT]: comment` to `[VERDICT]: <approve|comment|block>` in the prompt template.

**W7 fix — use APPROVE/REQUEST_CHANGES for verdicts:**
```javascript
let reviewEvent = 'COMMENT';
if (verdict === 'approve') reviewEvent = 'APPROVE';
else if (verdict === 'block') reviewEvent = 'REQUEST_CHANGES';
```

**W8 fix — fork guard on conflict check:**
Add `if: steps.fork-check.outputs.skip != 'true'` to the conflict check step.

**W9 fix — concurrency key for issue_comment:**
```yaml
concurrency:
  group: jules-fix-${{ github.event.pull_request.number || github.event.issue.number }}
```

**W10 fix — multiline GITHUB_OUTPUT:**
```bash
{
  echo "custom_instructions<<EOF"
  echo "$CUSTOM"
  echo "EOF"
} >> "$GITHUB_OUTPUT"
```

### Phase 5: Event Normalization (for issue_comment workflows)

Workflows triggered by both `pull_request` and `issue_comment` need to normalize the PR context:

```javascript
async function resolvePullRequest(github, context) {
  if (context.eventName === 'pull_request') {
    return context.payload.pull_request;
  }
  if (context.eventName === 'issue_comment') {
    if (!context.payload.issue?.pull_request) return null;
    const { data } = await github.rest.pulls.get({
      owner: context.repo.owner, repo: context.repo.repo,
      pull_number: context.payload.issue.number,
    });
    return data;
  }
  return null;
}
```

This function should be inlined in each workflow's prepare step (or eventually in the classifier as a utility).

---

## 4. Implementation Order

| Step | What | Files | Status |
|---|---|---|---|
| 1 | Fix classifier defects C1–C8 | `jules-comment-classifier.cjs` | ✅ Done |
| 2 | Fix F2 (comment verdict), W6 (default verdict), W7 (review event) | `jules-pr-review.yml`, `jules-pr-force-review.yml` | ✅ Done |
| 3 | Fix W1 (auto-fix issue_comment), W2 (slash auth), W9 (concurrency), W10 (multiline output) | `jules-pr-auto-fix.yml`, `jules-pr-rebuild.yml`, `jules-pr-resolve-conflicts.yml` | ✅ Done |
| 4 | Fix W4 (stale marker), W5 (file read guard), W8 (fork guard) | `jules-pr-rebuild.yml`, `jules-pr-walkthrough.yml`, `jules-pr-resolve-conflicts.yml` | ✅ Done |
| 5 | Fix F3 (retry/backoff), F4 (multi-message), F7 (quota detection), F8 (artifact upload) | all polling workflows | ✅ Done |
| 6 | Fix F5 (cross-session dedup) | all session-creating workflows | ✅ Done (review, force-review, walkthrough, rebuild, auto-fix) |
| 7 | Integrate classifier (F9+F1, F6) — add trusted checkout + replace inline logic | all workflows with priorReviews | ✅ Done (review, force-review, walkthrough, auto-fix, resolve-conflicts) |
| 8 | Add event normalization (Phase 5) | issue_comment workflows | ✅ Done (auto-fix, force-review, walkthrough, resolve-conflicts) |

### Remaining work (not blocking distribution)

| Item | Workflow | Notes |
|---|---|---|
| Classifier integration for address-comments | `jules-pr-address-comments.yml` | Different pattern — uses marker-based Jules context, not priorReviews. Needs its own integration approach. |
| F5 dedup for resolve-conflicts | `jules-pr-resolve-conflicts.yml` | Has PR stability check as partial dedup. Full SHA dedup would need a "session started" comment. |
| F8 artifact for resolve-conflicts | `jules-pr-resolve-conflicts.yml` | Fire-and-forget — no output file to upload. |
| Unresolved thread filtering in address-comments | `jules-pr-address-comments.yml` | Currently includes all unresolved threads even if latest comment is Jules-generated. |

---

## 5. Distribution Plan (post-template validation)

After all template fixes are complete and validated:

1. Copy the 8 workflow YAMLs from `jules/.github/workflows/` to each repo's `.github/workflows/`
2. Copy the classifier from `jules/.github/scripts/` to each repo's `.github/scripts/`
3. The `require()` path `./_helpers/.github/scripts/jules-comment-classifier.cjs` works in every repo because `.github/` is a standard GitHub directory
4. Verify each repo's Mergify/branch protection rules are compatible
5. For EI: use curated per-file cherry-picks (T1/T2 pattern), NEVER merge `scientific` → `main`

### 5.1 Per-repo distribution notes

| Repo | Branch | Special handling |
|---|---|---|
| KNA | `main` | Already has some hardening (dedup, retry) — merge carefully, don't regress |
| GFLQ | `main` | Clean, straightforward copy |
| GCPL | `main` | Clean, straightforward copy |
| EI | `scientific` + `main` (separate) | T1/T2 cherry-picks; NEVER merge branches |

---

## 6. Validation Criteria

Each fix must pass:

1. **YAML lint:** `yq eval '.' <workflow>.yml` parses without error
2. **Shell lint:** `shellcheck` on embedded bash (where feasible)
3. **Logic review:** Manual trace of each changed code path
4. **Classifier unit test:** `node -e "require('./jules-comment-classifier.cjs')"` loads without error
5. **Dry-run check:** Verify workflow `if:` conditions resolve correctly for each trigger type

---

## 7. Key Constraints

- **Finding #29:** Never merge EI `scientific` → `main`. Use curated per-file cherry-picks.
- **Trust boundary:** Classifier must always be loaded from base-branch checkout, never from PR-head code.
- **Bot identity:** All workflows use `google-labs-jules[bot]` (not bare `'jules'`).
- **Fork safety:** All workflows must check `head.repo.full_name === base.repo.full_name` before running.
- **No new dependencies:** Workflows run on `ubuntu-latest` with only pre-installed tools (curl, jq, node, ruff, eslint).
