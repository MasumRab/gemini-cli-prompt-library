# Jules Workflow Smoke Test Plan

Use a disposable PR on one of the target repos (e.g., `gemini-fullstack-langgraph-quickstart`). The PR can be either a same-repository PR or a fork PR depending on the test scenario. The Fork Skip test below must use a fork PR.

## 1. Fork Skip

1. Create a PR from a fork (any branch with a trivial change)
2. Verify the workflow exits early with "Fork PR detected — skipping"
3. Verify no Jules session was created (check API)
4. Verify no checkout occurred (runner logs show `if: steps.fork-check.outputs.skip != 'true'` → skipped)

## 2. Comment Ordering

1. Create a PR, add 15+ issue comments (alternating useful and marker comments)
2. Trigger `jules-force-review` label
3. Verify the prompt contains the 10 newest non-marker comments, not the oldest

## 3. Final Reporting Under `always()`

1. Create a PR, trigger `jules-force-review`
2. Let the session poll time out (or force a failure by setting an invalid SESSION_NAME)
3. Verify the post step still runs under `always()` and posts a failure comment
4. Verify the workflow step result shows the failure message, not a silent skip

## 4. Rebuild Job Gating

1. Create a PR with conflicts, apply `jules-rebuild`
2. Let the analyze session time out (or force a failure)
3. Verify the rebuild job is skipped because `session_state != 'COMPLETED'`
4. Verify the skip message references the analyze job output

## 5. Automerge Provenance

1. Create a PR with a `jules-*` branch name from a non-jules user
2. Run the automerge-label workflow manually (`workflow_dispatch`)
3. Verify the PR does NOT receive the `automerge` label
4. Verify the log shows the same-repo + jules-user check failing

## 6. Trusted-Base Rules Loading

1. Create a `.jules/INSTRUCTIONS.md` on a feature branch with a unique test instruction
2. Do NOT merge it to the base branch
3. Create a PR from that feature branch
4. Trigger review/auto-fix
5. Validate that policy loading uses the base-branch version via `repos.getContent(path, ref: baseRef)` — the head-only rule must NOT be honored (it should not affect the review)
6. Note that the instruction may appear when Jules inspects the PR diff (this is expected)
7. Merge the file to base, trigger again — verify it now appears as a loaded rule

## 7. Address-Comments GraphQL Threads

1. Create a PR, have a reviewer post 2+ review comments
2. Resolve 1 thread, leave 1 unresolved
3. Post a new review comment on the unresolved thread
4. Confirm the workflow produces a consolidated PR comment that references unresolved threads
5. Verify the comment excludes resolved-thread references

## 8. Conflict Detection

1. Create two branches that produce a content conflict
2. Create a PR from the conflicting branch, apply `jules-resolve`
3. Verify `has_conflicts=true` is written
4. Verify a resolution session is created (watch + build + create steps all run)

## 9. Clean Resolution Path

1. Create a PR with initial conflicts, then push a fix that resolves them
2. Apply `jules-resolve`
3. Verify the watch step detects the SHA change
4. Verify the re-check writes `has_conflicts=false`
5. Verify no resolution session is created

## 10. Quota Error Handling

1. Exhaust the daily quota (15 sessions) or mock a 429 response
2. Create a new PR, trigger any label workflow
3. Verify the workflow posts "session cap reached" comment
4. Verify the workflow exits 0 (not a failure)
