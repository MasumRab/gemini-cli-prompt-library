# Handoff, Branch Analysis & Git Diff Patterns

## Core Patterns

### Pattern A: Branch Viability Check
```yaml
steps:
  - name: Verify branch exists and is reachable
    shell: bash
    run: |
      git fetch origin "$HEAD_REF" 2>/dev/null || {
        echo "branch_missing=true" >> "$GITHUB_OUTPUT"
        exit 0
      }
      BEHIND=$(git rev-list --count origin/$BASE_REF..origin/$HEAD_REF 2>/dev/null || echo "0")
      echo "commits_behind=$BEHIND" >> "$GITHUB_OUTPUT"
```
**Use when:** Any scenario where the PR head may not exist (fork, deleted branch, rebase force-push)

### Pattern B: Safe Diff Strategy
```yaml
# Three-dot diff (changes introduced by PR branch):
git diff origin/$BASE_REF...HEAD -- <file>

# Two-dot diff (current state vs base, inaccurate for PR review):
git diff origin/$BASE_REF HEAD -- <file>

# Conflict detection:
git merge-tree --write-tree HEAD origin/$BASE_REF
```
**Use when:** Review, auto-fix, rebuild — always prefer three-dot diff for PR analysis

### Pattern C: Session Handoff Report
```
<!-- jules-handoff -->
## Session Handoff
- Session: sessions/123
- Status: FAILED | TRUNCATED | STUCK
- Completed: Phase 1 (analysis)
- Failed: Phase 2 (rebuild)
- PR: #365
- Target branch: main
- PR head: feature/foo
- Remaining work: [list of unprocessed findings]
- Artifacts: /tmp/handoff-123.json
```
**Use when:** Session fails mid-task, output is truncated, or manual intervention is needed

### Pattern D: Quota-Aware Scheduling
```yaml
steps:
  - name: Check session quota
    run: |
      COUNT=$(curl -s -H "X-Goog-Api-Key: $JULES_API_KEY" \
        "https://jules.googleapis.com/v1alpha/sessions" | jq '.sessions | length')
      if [ "$COUNT" -ge 15 ]; then
        echo "quota_exhausted=true" >> "$GITHUB_OUTPUT"
      fi
```
**Use when:** Any label-triggered workflow — check before creating a session

---

## Edge Case → Pattern Mapping

| # | Edge Case | Branch Analysis | Diff Handling | Handoff |
|---|-----------|----------------|---------------|---------|
| 1 | **Quota exhausted** | None | None | **D** — check before session creation, post comment, skip |
| 2 | **Stuck IN_PROGRESS** | **A** — verify session still active | None | **C** — generate handoff report with session ID and last known state |
| 3 | **Wrong branch target** | **A** — verify `outputs.pullRequest.baseRef` matches expected branch | **B** — compare actual vs expected base |
| 4 | **Polling 404** | None — infrastructure issue | None | **C** — log the resource URL being polled |
| 5 | **Activity null** | None — API schema issue | None | **C** — dump raw activity JSON for debugging |
| 6 | **Token expired** | None | None | **C** — log token expiry, suggest regeneration |
| 7 | **PR already merged** | **A** — check `pr.state` before any action | None | Skip — no handoff needed |
| 8 | **0 changed files** | **A** — trivial | None | Skip — "Nothing to review" comment |
| 9 | **100+ changed files** | **A** — categorize files by risk level | **B** — three-dot per file, focus on high-risk | **C** — note which files were skipped |
| 10 | **Fork PR** | **A** — `isFork` check, skip session | None | Skip — "Secrets unavailable" comment |
| 11 | **Prompt injection** | None — content safety | None | Sanitize `pr.body` before injection |
| 12 | **Non-PR label** | Not possible — workflow uses `pull_request` | None | N/A |
| 13 | **Double label** | **A** — check if label still exists before session creation | None | Second run is no-op |
| 14 | **Label removed manually** | None — `.catch()` handles it | None | Safe |
| 15 | **Output truncation** | None | **B** — check for `<!-- meta-prompt: truncated -->` | **C** — list completed findings, identify what was truncated |
| 16 | **False negative** | None | **B** — cross-check `ruff` output | **C** — flag potential missed findings |
| 17 | **False positives** | None | None | Manual — `@jules` correction |
| 18 | **Token bloat** (large files) | **A** — detect generated/large files before payload | Filter `linguist-generated=true` files, skip binaries | **C** — note which files were excluded; Pattern 4 |
| 19 | **Concurrent commits** mid-review | **A** — compare original `headSha` vs current PR head | Pin review to original commit, not floating HEAD | **C** — warn that review may be stale; Pattern 6 |
| 20 | **GitHub API rate limits** | None | Batch comments into single call | **C** — fall back to markdown list in body |
| 21 | **Fork secrets unavailable** | **A** — `isFork` check | None — skip session | Skip with explanatory comment |
| 22 | **Malformed HTML comments** | None — content quality | Forgiving regex with variations; Pattern 5 | **C** — dump raw output if parsing fails |
| 18 | **Token bloat** (large files) | **A** — detect generated/large files before payload | Filter `linguist-generated=true` files, skip binaries | **C** — note which files were excluded |
| 19 | **Concurrent commits** mid-review | **A** — compare original `headSha` vs current PR head | Pin review to original commit not floating HEAD | **C** — warn that review may be stale |
| 20 | **GitHub API rate limits** | None | Batch comments into single call | **C** — fall back to markdown list in body |
| 21 | **Fork secrets unavailable** | **A** — `isFork` check | None — skip session | Skip with explanatory comment |
| 22 | **Malformed HTML comments** | None — content quality | Forgiving regex with variations | **C** — dump raw output if parsing fails |

---

## Implementation Recommendations

### 1. Pre-Flight Check Step (add to all workflows)
```yaml
- name: Pre-flight checks
  id: preflight
  shell: bash
  env:
    HEAD_REF: ${{ github.event.pull_request.head.ref }}
    BASE_REF: ${{ github.event.pull_request.base.ref }}
  run: |
    # Check PR state
    if [ "${{ github.event.pull_request.merged }}" = "true" ]; then
      echo "pr_already_merged=true" >> "$GITHUB_OUTPUT"
      exit 0
    fi
    # Check branch exists
    git fetch origin "$HEAD_REF" 2>/dev/null || {
      echo "branch_missing=true" >> "$GITHUB_OUTPUT"
      exit 0
    }
    # Check quota (if after this step, we create a session)
    # COUNT=$(...) — see Pattern D
```

### 2. Stuck Session Recovery
```yaml
- name: Attempt stuck session recovery
  if: steps.poll.outputs.session_state == 'TIMEOUT'
  shell: bash
  env:
    JULES_API_KEY: ${{ secrets.JULES_API_KEY }}
    SESSION_RESOURCE: ${{ steps.create.outputs.session_name }}
  run: |
    curl -s -X POST "https://jules.googleapis.com/v1alpha/${SESSION_RESOURCE}:sendMessage" \
      -H "Content-Type: application/json" \
      -H "X-Goog-Api-Key: ${JULES_API_KEY}" \
      -d '{"prompt": "This session has exceeded the time limit. Please provide a summary of any work completed so far and stop."}'
    sleep 30
    # Check if we got a response
```

### 3. Truncation-Aware Posting
```javascript
// After extracting output
if (output.includes('<!-- meta-prompt: truncated due to limits -->')) {
  core.warning('Output was truncated — review may be incomplete');
  commitStatus.description += ' (truncated)';
}
```

### 4. File Filtering for Token Bloat Prevention
```yaml
- name: Filter large/generated files
  shell: bash
  run: |
    # Files to exclude from payload (token waste)
    SKIP_PATTERNS='\.(lock|min\.js|svg|png|jpg|jpeg|gif|ico|woff2?|eot|ttf|zip|tar|gz|map|css\.map)$'
    SAFE_FILES=$(echo "$FILES" | grep -v -E "$SKIP_PATTERNS")
    echo "total_files=$FILES_COUNT" >> "$GITHUB_OUTPUT"
    echo "safe_files=$SAFE_FILES_COUNT" >> "$GITHUB_OUTPUT"
```
**Use when:** Any review or analysis workflow — run before constructing the prompt payload

### 5. Forgiving HTML Comment Parser
```javascript
// Accept <!-- FINDING, <!--- FINDING, <!--finding (case-insensitive)
const findingRegex = /<!--{1,2}\s*FINDING\s+severity=(["'])?([^"'\s]+)\1?\s+file=(["'])?([^"'\s]+)\3?\s+line=?["']?(\d+)/gi;
```
**Use when:** Parsing Jules output — prevents fragile regex from losing findings due to minor formatting variations

### 6. Concurrent Commit Safety
```yaml
- name: Check PR head hasn't changed since review started
  run: |
    CURRENT_SHA=$(gh pr view $PR --json headRefOid --jq '.headRefOid')
    if [ "$CURRENT_SHA" != "$ORIGINAL_SHA" ]; then
      echo "PR was updated during review — comments may be stale"
      echo "review_stale=true" >> "$GITHUB_OUTPUT"
    fi
```
**Use when:** Posting review comments — warn if the PR head changed during the session

### 7. Branch Analysis Before Auto-Fix/Resolve
```yaml
- name: Analyze branch state
  run: |
    # How far behind is the PR head?
    BEHIND=$(git rev-list --count origin/$BASE_REF...origin/$HEAD_REF 2>/dev/null || echo "0")
    # Does it have merge conflicts?
    git merge-tree --write-tree HEAD origin/$BASE_REF && CONFLICTS=$? || CONFLICTS=$?
    echo "commits_behind=$BEHIND" >> "$GITHUB_OUTPUT"
    echo "has_conflicts=$([ $CONFLICTS = 1 ] && echo true || echo false)" >> "$GITHUB_OUTPUT"
```
