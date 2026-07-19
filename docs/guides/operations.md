# Jules Operations — Standard Workflows

This document establishes the official workflows for managing, updating, and recovering Google Jules sessions within this repository.

---

## Workflow 1: Metadata Synchronization
**Goal:** Ensure local `.json` files in `jules_sessions/` match the ground truth in the Jules API.

1.  **Sync Single Session:**
    ```bash
    SESSION_ID="<id>"
    curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID" \
      -H "x-goog-api-key: $JULES_API_KEY" > "jules_sessions/jules_${SESSION_ID}.json"
    ```
2.  **Sync All Active Sessions:**
    Use the `tools/shell/jules_sync_all.sh` helper to refresh all local metadata.
3.  **Validate State:**
    Check if sessions marked `COMPLETED` have a corresponding PR URL. If not, proceed to **Workflow 2**.

---

## Workflow 2: Triage & Action
**Goal:** Resolve sessions in "blocking" states (`AWAITING_PLAN_APPROVAL`, `AWAITING_USER_FEEDBACK`).

1.  **Identify Blockers:**
    ```bash
    jq -r 'select(.state | startswith("AWAITING")) | "\(.id) :: \(.state) :: \(.title)"' jules_sessions/jules_*.json
    ```
2.  **Approve Plans:**
    If the state is `AWAITING_PLAN_APPROVAL` and the plan in `activities` looks sound:
    ```bash
    curl -X POST "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:approvePlan" \
      -H "x-goog-api-key: $JULES_API_KEY" -H "Content-Type: application/json" -d '{}'
    ```
3.  **Provide Feedback:**
    If the state is `AWAITING_USER_FEEDBACK`, send a message to unblock:
    ```bash
    curl -X POST "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:sendMessage" \
      -H "x-goog-api-key: $JULES_API_KEY" -H "Content-Type: application/json" \
      -d '{"prompt": "Your technical answer here..."}'
    ```

---

## Workflow 3: PR Quality Guard
**Goal:** Ensure Jules PRs are high-quality and free of common pitfalls.

1.  **Forward PR Comments:**
    Use `gh pr-review review view <number> --unresolved` to find actionable feedback and forward it to the session using `sendMessage`.
2.  **Check for Over-Deletion:**
    Flag PRs with >1,000 deletions. Demand a rationale before merging.
3.  **Merge Marker Audit:**
    If a PR contains `<<<<<<<`, `=======`, or `>>>>>>>`, instruct Jules to resolve the conflict immediately.
4.  **`.gitignore` Validation:**
    Ensure Jules doesn't commit build artifacts or large log files. Instruct to update `.gitignore` if found.

---

## Workflow 4: Schedule Management
**Goal:** Track long-term progress against `jules_sessions/task_schedule.json`.

1.  **Mark Tasks Complete:**
    Once a PR is merged, update the `status` field in the schedule to `completed`.
2.  **Start Next Task:**
    Identify tasks with `status: null` whose dependencies are met. Create a new session using the `jules_prompt` provided in the template.
    ```bash
    PROMPT=$(jq -r '.task_schedule[] | select(.task_id == "task_11_2") | .jules_prompt' jules_sessions/task_schedule.json)
    jules new "$PROMPT"
    ```

---

## Workflow 5: WIP & Timeout Recovery
**Goal:** Continue work from sessions that timed out or were interrupted.

1.  **Detect Timeout:**
    Look for "Jules was unable to complete the task in time" in commit messages.
2.  **Refine & Restart:**
    - If task was too broad: Break into smaller sub-tasks.
    - If task hit blockers: Provide missing context or specify a path to ignore.
    - If logic was partial: Tell Jules to "Continue from branch <name>".

---

## Logging Standards
All prompts sent to Jules (nudges, approvals, rectifications) **must** be logged in:
`/home/masum/.agents/skills/jules-sessions/references/sent_responses.md`

**Format:**
```yaml
session_id: "<id>"
prompt_type: "nudge|rectification|approve"
prompt_sent: "Verbatim text"
outcome: "QUEUED|COMPLETED|FAILED"
```
