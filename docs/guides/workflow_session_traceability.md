# GitHub workflow and Jules session traceability

**Status:** Canonical guidance; implementation is not yet uniform across workflows
**Applies to:** GitHub Actions that create or request Jules sessions, and operators
investigating those runs

## 1. Goal

For every relevant GitHub workflow execution, answer these questions from durable,
machine-readable evidence:

1. What exact event and repository revision triggered the run?
2. What workflow revision and policy inputs constructed the Jules prompt?
3. Which Jules session or sessions were created or requested?
4. What content and state transitions did each session produce?
5. What GitHub side effects resulted: comments, reviews, labels, commits, or PRs?

Do not correlate records only by title, prompt text, creation time, branch prefix, or PR
number. Those are useful search hints but are not stable identities.

## 2. Three records, one trace

```diagram
┌──────────────────────────────┐
│ GitHub trigger and run       │
│ run ID + attempt + event ID  │
└──────────────┬───────────────┘
               │ exact IDs
               ▼
┌──────────────────────────────┐
│ Trace manifest               │
│ prompt/policy hashes         │
│ zero, one, or many sessions  │
└──────────────┬───────────────┘
               │ session resource names
               ▼
┌──────────────────────────────┐
│ Jules session and activities │
│ state + output + resulting PR│
└──────────────────────────────┘
```

The trace manifest is derived operational state. It is not a replacement for GitHub
run logs, raw Jules API responses, or the session archive standard.

## 3. Stable correlation keys

Use these keys in descending order of authority:

| Boundary                     | Required key                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------- |
| GitHub execution             | Repository ID/name + `github.run_id` + `github.run_attempt`                                       |
| Workflow/job                 | `github.workflow_ref` or workflow path, `github.workflow_sha`, and job ID/name                    |
| Trigger object               | Event name/action plus the event object's stable database ID                                      |
| Target revision              | PR/issue number where applicable and exact PR head SHA                                            |
| Jules session                | Full resource name `sessions/<id>`; store the numeric ID separately only for convenience          |
| Multiple sessions in one run | Session ordinal plus semantic role, such as `analysis`, `execution`, `review`, or `backlog-pr-42` |
| GitHub outcome               | Comment/review/check-run/PR database ID and URL where available                                   |

The job-attempt manifest identity is:

```text
<repository>:<run_id>:<run_attempt>:<job>
```

Each session entry has the identity
`<manifest_trace_id>:<session_ordinal>`. This keeps one manifest for multi-session jobs
without losing a stable identifier for each session.

Reruns must create a new attempt record. Never overwrite attempt 1 with attempt 2.

### Trigger-specific IDs

Capture the fields that identify the actual event, before a workflow removes a label or
otherwise mutates the source object:

| Event                         | Capture                                                                                             |
| ----------------------------- | --------------------------------------------------------------------------------------------------- |
| `pull_request`                | action, PR ID/number, base ref/SHA, head ref/SHA, sender, triggering label when applicable          |
| `issue_comment`               | issue/PR ID and number, comment ID, author association, command classification; hash or redact body |
| `pull_request_review`         | PR ID/number, review ID, review state, submitted timestamp, author association                      |
| `pull_request_review_comment` | PR ID/number, review-comment ID, path/line metadata, author association                             |
| `issues`                      | issue ID/number, action, sender, triggering label when applicable                                   |
| `workflow_dispatch`           | actor, declared inputs, selected ref/SHA                                                            |
| `schedule`                    | cron expression, scheduled time, workflow SHA, and the exact selected target IDs                    |

Do not persist the complete GitHub event payload by default. Comment bodies, review
text, patches, email-derived content, and dispatch inputs may contain secrets or PII.

## 4. Canonical trace manifest

Produce one JSON document per job attempt. Scheduled and multi-stage workflows use a
`sessions` array rather than separate unlinked files.

```json
{
  "schema_version": 1,
  "trace_id": "owner/repo:123456789:2:review",
  "recorded_at": "2026-08-06T12:00:00Z",
  "github": {
    "repository": "owner/repo",
    "repository_id": 123,
    "run_id": 123456789,
    "run_attempt": 2,
    "run_url": "https://github.com/owner/repo/actions/runs/123456789",
    "workflow_ref": "owner/repo/.github/workflows/jules-pr-review.yml@refs/heads/main",
    "workflow_sha": "<40-character SHA>",
    "job": "review",
    "event_name": "pull_request",
    "event_action": "synchronize",
    "actor": "user",
    "triggering_actor": "user",
    "target": {
      "kind": "pull_request",
      "id": 456,
      "number": 42,
      "head_sha": "<40-character SHA>",
      "base_ref": "main"
    }
  },
  "prompt": {
    "sha256": "<hash of exact UTF-8 prompt bytes>",
    "stored": false,
    "policy_sources": [
      {
        "path": ".jules/INSTRUCTIONS.md",
        "revision": "<trusted base SHA>",
        "sha256": "<content hash>"
      }
    ]
  },
  "sessions": [
    {
      "ordinal": 1,
      "role": "review",
      "resource": "sessions/12345678901234567890",
      "id": "12345678901234567890",
      "created_at": "<API timestamp if returned>",
      "automation_mode": "AUTO_CREATE_PR",
      "state": "IN_PROGRESS",
      "state_observed_at": "2026-08-06T12:01:00Z",
      "result_pr_url": null
    }
  ],
  "outcomes": [],
  "correlation": {
    "status": "exact",
    "method": "create-session-response"
  }
}
```

Use `correlation.status` values:

- `exact`: session resource came from the create-session response.
- `app-mediated`: the workflow posted a Jules request but the GitHub App owns session
  creation and has not exposed an exact session resource.
- `reconciled`: an operator later joined the session using explicit metadata or a Jules
  response link.
- `unresolved`: only heuristic candidates exist. Record candidates and evidence, but do
  not promote one to the authoritative session.
- `none`: workflow intentionally created no session, such as fork, clean-conflict, quota,
  deduplication, or authorization skip paths.

## 5. Recording the exact prompt and policy context

The prompt hash must cover the exact bytes sent in the create-session request, after all
trusted-base policy and dynamic context have been assembled. Also record:

- workflow SHA;
- trusted base SHA;
- path, revision, and SHA-256 for every injected rule/instruction file;
- prompt template/version identifier, if one exists;
- target head SHA and relevant GitHub object IDs; and
- whether the full prompt was retained.

For reverse lookup from the Jules side, prefer a supported API client-metadata field if
one becomes available. The current documented create-session request has no generic
metadata field, so append a clearly delimited, non-secret trace block to the prompt with
the manifest trace ID, run URL/attempt, workflow SHA, target object ID, and target SHA.
Hash the final prompt including that block. Label it as provenance, not task instruction,
and do not include event bodies or credentials.

Do not place full prompts in PR comments, step summaries, or the manifest. Store them
only in a restricted artifact or approved archive when necessary, with secrets and PII
redacted and a deliberate retention period. A hash proves equality; it does not reveal
the content and cannot prove that unsafe content was absent.

## 6. Tracking Jules session content

For an exact session resource:

1. Save the create-session response fields needed for correlation.
2. At each meaningful transition, request `GET /sessions/<id>` and record the official
   state and observation timestamp.
3. Retrieve all pages from `GET /sessions/<id>/activities`, following
   `nextPageToken`; never assume the first page contains the beginning or final result.
4. At terminal state, capture result PR URLs, output/change-set identity, final activity
   identity, and final state.
5. Record GitHub side effects by stable ID and URL.

Avoid copying full activity streams into the trace manifest. Store only content hashes,
counts, first/last activity identifiers or timestamps, state transitions, and approved
outcome metadata there. If raw session/activity responses must be retained, follow
`session_summary_standard.md` and the operations review. Until ARC-01–ARC-07 are fixed,
do not treat the current summary generator as proof that a raw archive is valid.

## 7. GitHub Actions persistence

Each session-creating job should update the manifest at these checkpoints:

1. **Trigger captured:** before label consumption or early-exit checks.
2. **Prompt built:** after trusted-base policy loading, before the API call.
3. **Session created:** immediately after validating the API response.
4. **Polling update:** state transitions only; avoid unbounded log duplication.
5. **Finalized:** terminal, timeout, quota, failed, or skipped outcome plus side effects.

Persist the final manifest as a GitHub Actions artifact even on failure with
`if: always()`. Use a short, documented retention period appropriate to its metadata.
Also write a human-readable summary containing only the run URL, target, session
resource(s), final state, and outcome URLs.

`if: always()` cannot run after a hard job timeout or runner loss. Where creation-time
correlation must survive those failures, upload a uniquely named creation checkpoint
immediately after each successful create response or write it to an approved external
append-only sink. Finalization should produce a separate final artifact; do not rely on
overwriting an artifact in place.

Where comments are already posted, a compact hidden marker may improve operator lookup:

```html
<!-- jules-trace run="123456789" attempt="2" job="review" session="sessions/12345678901234567890" sha="<head-sha>" prompt_sha256="<hash>" -->
```

Treat comments as a secondary index, not the source of truth: comments can be edited or
deleted, and scheduled workflows may have no natural PR comment.

## 8. Current workflow-specific handling

| Workflow class                    | Trace requirement                                                                                                                                                                                       |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Review, force-review, walkthrough | Preserve existing session markers but add run/attempt and prompt/policy hashes to the artifact manifest. Deferred retrieval must reference the originating trace.                                       |
| Auto-fix                          | Record planning and execution sessions as distinct roles in the same logical PR trace; approval events begin a new GitHub run/attempt record linked to the plan marker and plan SHA.                    |
| Rebuild                           | Record analysis and rebuild sessions separately; a failed analysis must still finalize the trace.                                                                                                       |
| Resolve-conflicts                 | Record `none` for the clean path and the exact resolution session for the conflict path.                                                                                                                |
| Issue triage and backlog review   | One run can create many sessions. Assign deterministic ordinals and include the issue/PR ID for each session. Never store only the last session ID.                                                     |
| Address-comments                  | The workflow posts an `@jules` comment and does not create the session through REST. Record the posted comment ID as `app-mediated`; reconcile only when the App exposes an explicit session reference. |
| Dispatch and automerge-label      | These do not create sessions. Record routed label/comment IDs or label outcome only when tracing the downstream chain.                                                                                  |

## 9. Historical forensic inventory with current tools

The current REST and GitHub tools can inspect every session that remains visible to the
authenticated Jules account and enrich it with available GitHub evidence. They cannot
guarantee recovery of deleted sessions, expired GitHub run logs, inaccessible
repositories, or a historical Actions-run link that was never recorded.

### Evidence to record for every accessible session

| Field                      | Evidence source                                                                                                                   |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Session identity and state | Full `GET /sessions/<id>` response                                                                                                |
| Purpose                    | Original prompt, title, source context, starting branch, and plan; distinguish quoted facts from reviewer interpretation          |
| Activity history           | Every page from `/sessions/<id>/activities`, not only the latest 20 or 50 entries                                                 |
| Output                     | Session `outputs`, change sets, explicit PR URLs, final agent activity, and failure reason                                        |
| GitHub result              | PR head/base SHA, commits, files, checks, reviews, comments, conflicts, state, and merge outcome                                  |
| Actions origin             | Trace manifest/marker when present; otherwise matching run, event object, workflow SHA, and timestamps as candidate evidence only |
| Correlation confidence     | `exact`, `strong`, `probable`, or `unresolved`, with the specific method and evidence                                             |
| Recommended action         | Reviewer conclusion plus evidence, prerequisites, risk, and whether mutation requires approval                                    |
| Review provenance          | Reviewer, review timestamp, Jules/GitHub retrieval timestamp, and known missing evidence                                          |

Purpose and output may be API facts. A recommended action is a reviewer judgment and
must not be presented as a field returned by Jules.

### Current tool roles and limits

| Tool                                                 | Useful for                                                                                   | Important limit                                                                                                                                                                                   |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tools/api/jules_api_client.py`                      | Uncapped paginated session inventory, full session lookup, and complete paginated activities | Use `list_sessions(max_results=None)` and `list_activities(..., max_results=None)` for completeness; callers often add lower caps                                                                 |
| `tools/cli/jules-manager.py session <id>`            | Full metadata/prompt/output inspection for one session                                       | Does not establish a GitHub Actions run link by itself                                                                                                                                            |
| `tools/sessions/jules_list_sessions.py`              | State-filtered triage and output PR discovery                                                | Scans at most 500 sessions and returns the requested limit; not proof of an all-time inventory                                                                                                    |
| `tools/sessions/jules_list_activities.py <id> --all` | Complete activity inspection for one session                                                 | Default is only 50; use `--all` for forensics                                                                                                                                                     |
| `tools/pr/session_pr_triage.py --repo <owner/repo>`  | Candidate session/PR discovery from activity links and branch names                          | Active sessions only, at most 100 sessions, 20 activities each, and open PRs for branch matching; its High/Medium labels are leads, not the evidence scale in this guide                          |
| `tools/pr/jules_pr_context.py <pr> --json`           | PR state, diff size, checks, comments, and priority hint                                     | Run with the intended target repository selected; it does not retrieve Jules content or Actions provenance                                                                                        |
| `tools/sessions/analyze_unanswered.py <id>`          | Categorizing an awaiting-feedback session                                                    | Recommendation aid only; verify against full activities                                                                                                                                           |
| `tools/pr/jules_audit_session_pr.py`                 | Supplemental local diff checks                                                               | Run only in a target worktree with the verified PR head checked out. `--session` uses `startingBranch`, which may be the base rather than the PR head, so it is not standalone proof of PR safety |

### Forensic procedure

1. Run authentication/pre-flight checks without mutating sessions or PRs.
2. Enumerate sessions through `JulesAPIClient.list_sessions(max_results=None)` so every
   API page is consumed. Save retrieval time and any API/account boundary.
3. For each session, fetch full metadata and all activities. For individual inspection:

   ```bash
   python3 -m tools.cli.jules-manager session <session_id>
   python3 -m tools.sessions.jules_list_activities <session_id> --all
   ```

4. Extract the original purpose, source repository/branch, state transitions, outputs,
   PR URLs, patch/change identity, questions, plans, and terminal evidence.
5. Run `session_pr_triage.py` for candidate discovery, then independently verify each
   candidate against full session output and GitHub. Include closed and merged PRs; the
   triage script's open-PR branch scan is not exhaustive.
6. In the target repository, inspect each verified PR:

   ```bash
   python3 /path/to/jules/tools/pr/jules_pr_context.py <pr_number> --json
   gh run list --commit <head_sha>
   gh pr view <pr_number> --json id,url,state,headRefName,headRefOid,baseRefName,mergeable,mergeStateStatus,commits,reviews,comments,statusCheckRollup
   ```

7. Search Actions runs and existing comment markers for exact run/session IDs. If only
   repository, PR, title, and time proximity agree, record `probable`, not `exact`.
8. Assign a recommended action using the rubric below. Do not approve, message, retry,
   close, merge, or delete as part of a read-only forensic pass.
9. Record one row per session, including sessions with no PR, no output, or unresolved
   Action origin. Reconcile counts against the uncapped API inventory.

### Correlation confidence for historical data

| Confidence   | Minimum evidence                                                                                                                               |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `exact`      | Trace manifest/marker, create response, session output, or another stable ID explicitly joins both records                                     |
| `strong`     | Explicit PR URL or unique commit/branch evidence in full session activities matches GitHub exactly, but the originating Actions run is unknown |
| `probable`   | Multiple independent contextual fields agree, but none is a unique durable join                                                                |
| `unresolved` | Evidence is absent, conflicting, inaccessible, or admits multiple candidates                                                                   |

### Recommended-action rubric

| Observed state/result                  | Default reviewer recommendation                                                                                                          |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `QUEUED`, `PLANNING`, `IN_PROGRESS`    | Monitor unless stale beyond an explicitly defined service threshold                                                                      |
| `AWAITING_PLAN_APPROVAL`               | Review plan, repository policy, branch, and scope; recommend approve, request revision, or supersede—never auto-approve from state alone |
| `AWAITING_USER_FEEDBACK`               | Read the complete question/context; recommend a specific response, missing evidence request, or supersession                             |
| `PAUSED` or unknown state              | Investigate activities/API errors and avoid mutation until the state is understood                                                       |
| `COMPLETED` with PR                    | Verify PR head, checks, reviews, policy, and actual diff; recommend merge, repair, further review, or close/supersede                    |
| `COMPLETED` without expected PR/output | Determine whether the task was analysis-only; otherwise recommend output recovery or a replacement session                               |
| `FAILED`                               | Identify terminal evidence and partial changes; recommend targeted retry only when inputs remain valid, otherwise replace or archive     |
| Duplicate/stale session                | Preserve provenance and recommend one authoritative successor; do not send competing instructions                                        |

An inventory is complete only relative to a named account, retrieval timestamp, API
visibility boundary, repository set, and GitHub retention window. State those bounds in
the report instead of claiming universal coverage.

## 10. Operator reconstruction procedure

When investigating a historical trigger:

1. Locate the GitHub run by repository, workflow, target number, and run attempt.
2. Download its trace artifact and verify `workflow_sha`, target SHA, and trigger object
   ID against GitHub.
3. For each exact session resource, fetch session metadata and all activity pages.
4. Verify the prompt hash against the retained redacted/full prompt when available.
5. Verify every resulting PR/comment/review ID against GitHub.
6. If no manifest exists, search session activities and PR branches only to identify
   candidates. Mark the result heuristic or unresolved unless explicit IDs establish the
   join.
7. Never rewrite the original trace. Append a reconciliation record with operator,
   timestamp, evidence, and prior/new correlation status.

## 11. Privacy, retention, and failure rules

- Never store API keys, authorization headers, signed URLs, or raw secret values.
- Redact sensitive email/PII and repository secrets before retaining prompt or activity
  content.
- Keep hashes and stable IDs longer than full text when audit requirements permit.
- Restrict artifacts containing prompts or activities to the repository's access model.
- Record quota, authorization, fork, dedup, malformed-response, and timeout paths even
  when no session exists.
- A missing session ID after a successful REST create call is a trace failure; fail the
  creation step rather than publishing an uncorrelated success.
- Tracing must not make a successful mutation appear failed after the mutation occurred.
  Preserve the API response, report partial trace failure, and require reconciliation.

## 12. Implementation sequence

1. Define and test the versioned manifest schema and redaction rules.
2. Add a shared manifest writer that never executes code from PR head.
3. Instrument one review workflow and validate normal, skip, timeout, quota, and rerun
   paths.
4. Instrument multi-session workflows and app-mediated address-comments separately.
5. Add trace capture to `SMOKE_TEST_PLAN.md` evidence requirements.
6. Add an operator command that accepts repository/run ID and retrieves exact linked
   sessions without relying on title/time heuristics.
7. Only then consider central aggregation or dashboards.

Track implementation independently from Actions correctness findings and archive
findings:

| ID       | Deliverable                                                                                      | Initial status |
| -------- | ------------------------------------------------------------------------------------------------ | -------------- |
| TRACE-01 | Versioned JSON schema, redaction rules, and test fixtures                                        | Open           |
| TRACE-02 | Trusted shared manifest writer and single-session review pilot                                   | Open           |
| TRACE-03 | Multi-session support for backlog, triage, auto-fix, and rebuild                                 | Open           |
| TRACE-04 | App-mediated handoff and later reconciliation model                                              | Open           |
| TRACE-05 | Operator retrieval/reconciliation command keyed by repository and run ID                         | Open           |
| TRACE-06 | Artifact retention, access, prompt/activity redaction, and deletion policy                       | Open           |
| TRACE-07 | Smoke-test evidence for normal, skipped, rerun, quota, timeout, partial, and trace-failure paths | Open           |

Do not implement a central database first. Per-run versioned artifacts and exact IDs
provide a reviewable source from which an index can be rebuilt. GitHub artifacts can be
deleted and expire under retention policy, so long-term audit requirements need an
explicit approved archive rather than an assumption of permanence.
