# Official Jules Action Audit

**Created:** 2026-08-29
**Source:** `google-labs-code/jules-action` (229 stars, official)
**Purpose:** Compare our workflows against the official Jules GitHub Action

---

## Official Action Analysis

### Source
- Repository: `https://github.com/google-labs-code/jules-action`
- Stars: 229
- Action name: `google-labs-code/jules-invoke@v1`

### Payload Structure

The official action assembles this payload:

```json
{
  "prompt": $jules_prompt,
  "sourceContext": {
    "source": "sources/github/$repo_full_name",
    "githubRepoContext": {
      "startingBranch": $starting_branch
    }
  },
  "requirePlanApproval": false,
  "automationMode": "AUTO_CREATE_PR"
}
```

### Key Observations

1. **Fire-and-forget pattern** — The official action creates a session and exits immediately
2. **No polling** — It doesn't wait for completion or return results
3. **Simple payload** — Only essential fields are set
4. **Uses composite action** — All steps in `action.yaml` with bash/shell

---

## Comparison: Our Workflows vs Official

| Feature | Official | Our Workflows |
|---------|----------|---------------|
| Session creation | ✅ | ✅ |
| Authentication | ✅ `X-Goog-Api-Key` | ✅ Same |
| Endpoint | ✅ `https://jules.googleapis.com/v1alpha/` | ✅ Same |
| `sourceContext.source` | ✅ `sources/github/...` | ✅ Same |
| `githubRepoContext.startingBranch` | ✅ | ✅ |
| **`requirePlanApproval`** | ✅ `false` | ❌ Missing |
| **`automationMode`** | ✅ `"AUTO_CREATE_PR"` | ❌ Missing |
| Polling for results | ❌ Not done | ✅ Custom implementation |
| Posting results to PR | ❌ Not done | ✅ Custom implementation |
| `?view=FULL` in polling | N/A | ⚠️ Used (potential issue) |

---

## Findings

### Finding 1: Missing `requirePlanApproval` (LOW)
**Status:** Non-critical
**Description:** Official action explicitly sets `requirePlanApproval: false`. Our workflows don't set this field.

**Impact:** Jules uses default behavior (likely `false` anyway).

**Recommendation:** Add explicitly for clarity:
```javascript
const payload = {
  prompt,
  sourceContext: { ... },
  requirePlanApproval: false,  // Add this
};
```

### Finding 2: Missing `automationMode` (MEDIUM)
**Status:** Needs verification
**Description:** Official action sets `automationMode: "AUTO_CREATE_PR"`. Our workflows don't set this.

**Impact:** Jules may not auto-create PRs when using our workflows.

**Recommendation:** Add to payloads that expect PR creation:
```javascript
const payload = {
  prompt,
  sourceContext: { ... },
  automationMode: "AUTO_CREATE_PR",  // Add this for fix workflows
};
```

### Finding 3: `?view=FULL` in Polling (MEDIUM)
**Status:** Documented in EDGE_CASES.md
**Description:** Our `jules-backlog-review.yml` uses `?view=FULL` in polling URLs.

**Recommendation:** Remove `?view=FULL` parameter per EDGE_CASES.md guidance.

---

## Action Items

| Priority | Action | File |
|----------|--------|------|
| Medium | Add `automationMode: "AUTO_CREATE_PR"` to auto-fix workflow payloads | `jules-pr-auto-fix.yml` |
| Low | Add `requirePlanApproval` explicitly to all payloads | All workflows |
| Medium | Remove `?view=FULL` from polling URLs | `jules-backlog-review.yml` |

---

## Related Documents

- `docs/actions/EDGE_CASES.md` — Contains `?view=FULL` issue
- `docs/actions/REVIEW_RECOMMENDATION.md` — Workflow review findings
- `docs/actions/HANDOFF.md` — Open task tracker
