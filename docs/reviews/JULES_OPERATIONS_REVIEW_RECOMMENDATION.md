# Jules REST Operations, Triage, Repair, and Session Archive — Review Recommendation

**Created:** 2026-08-03
**Code revision examined:** `b93d658` on `main`
**Scope:** Operator-driven Jules REST tooling, skills, runbooks, and durable session archives
**Relationship to GitHub Actions:** Separate subsystem; findings here do not block Actions unless an Action directly depends on the affected component

## 1. Scope boundaries

This review covers interactive and unattended operations under:

- `skills/`
- `commands/`
- `tools/api/`, `tools/sessions/`, `tools/pr/`, `tools/rebase/`, and `tools/shell/`
- `docs/runbooks/`, `docs/triage/`, and operational guides
- `scripts/generate_session_summaries.py`, `data/`, and session archive policy

It does not review the distributable `.github/workflows/jules-*.yml` implementation.
That assessment lives in `docs/actions/REVIEW_RECOMMENDATION.md`.

The term **operator workflow** in this document means a sequence described by a skill,
runbook, command, or local tool. It does not mean a GitHub Actions workflow.

## 2. Classify operations before reviewing them

| Class                     | Definition                                                                    | Examples                                                        |                Archive companion required? |
| ------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------- | -----------------------------------------: |
| Transient inspection      | Reads API data and prints or pipes it without durable persistence             | Listing, polling, viewing activities                            |                                         No |
| Mutation                  | Sends a message, approves a plan, creates a session, or changes GitHub state  | Recovery and repair commands                                    | No, unless it also archives a raw response |
| Derived operational state | Locally computed map, queue, schedule, tracker, or report                     | `session_pr_map.json`, rebase queues, `session_tracking/*.json` |                                         No |
| Raw Jules archive         | Durable, substantially unmodified response from session or activity endpoints | Session metadata and activity captures                          |                                        Yes |
| Derived human report      | Markdown/JSON wrap-up assembled for review                                    | `wrapup-session` output                                         |                                         No |

Applicability is based on provenance and persistence, not filename and not the mere
presence of a key named `session` or `sessions`.

## 3. Tasks that create raw Jules archives

The current raw writers are:

| Producer                                        | Current output                                | Required treatment                                                  |
| ----------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------- |
| `skills/jules-sessions/scripts/sync_session.sh` | `pr<N>_session.json`, `pr<N>_activities.json` | Generate and validate both companions after each successful refresh |
| `tools/shell/jules_sync_all.sh`                 | `jules_<id>.json`                             | Generate and validate a single-session companion after each refresh |
| `tools/shell/retrieve_sessions.sh`              | `session_<id>.json`                           | Generate and validate a single-session companion after retrieval    |
| `jules_list_sessions.py --json > file`          | Caller-selected raw session collection        | Archive skill must require immediate generation and validation      |
| `jules_list_activities.py --raw > file`         | Caller-selected raw activity collection       | Archive skill must require immediate generation and validation      |

`session_pr_map.json`, `session_tracking/*.json`, rebase queues, task schedules, API
error bodies, temporary pipes, and wrap-up reports are explicitly excluded.

## 4. Recommended enforcement architecture

Use defense in depth, ordered from strongest to weakest:

1. **Producer enforcement:** raw writers automatically generate and validate companions.
2. **Task-scoped skill:** a `jules-session-archive` skill activates before ad hoc export,
   synchronization, retrieval, or refresh tasks.
3. **Runbook handoff:** relevant operator procedures call the hardened producer and link
   to the canonical standard.
4. **Optional repository validation:** designated archive directories may check for
   missing or stale companions; do not scan every JSON file in the repository.

Do not use a repository-wide `AGENTS.md` policy for this narrow operation. It would load
for unrelated Actions, PR, documentation, and code tasks while still failing to enforce
unattended producers.

### Canonical ownership

| Layer                                     | Responsibility                                                               |
| ----------------------------------------- | ---------------------------------------------------------------------------- |
| `docs/guides/session_summary_standard.md` | Normative applicability, schemas, limits, and retention                      |
| `skills/jules-session-archive/SKILL.md`   | Agent trigger and archive procedure; links to the standard                   |
| `scripts/generate_session_summaries.py`   | Deterministic generation and strict validation                               |
| Raw producer scripts                      | Atomic fetch, JSON/API validation, generator invocation, failure propagation |
| Existing session skills/runbooks          | Narrow links at the point where persistence becomes possible                 |

Do not copy the complete policy into every skill or runbook. Duplication creates drift.

## 5. Generator and standard corrections required first

Automatic enforcement is unsafe until these contract defects are fixed:

1. Directory discovery excludes actual names such as `pr<N>_activities.json`,
   `pr<N>_session.json`, `jules_<id>.json`, and `session_<id>.json`.
2. Explicit files outside the narrow name patterns require an interactive prompt,
   which is unsuitable for unattended producers.
3. Single-session API resources are unsupported even though they may contain large
   patches under `outputs`.
4. Collection output uses `sessions:` while the standard documents only a singular
   top-level `session:` shape.
5. Validation does not parse YAML or enforce required fields and status values.
6. The 50 KB limit warns rather than fails.
7. The standard conflicts between `MUST`, `SHOULD`, and a suggested 1 MB threshold.
8. `data/.gitignore` also ignores summaries that the standard describes as trackable.

### Correct contract

- Every durable raw Jules archive receives a companion, regardless of raw file size.
- The 50 KB threshold applies to the generated summary, not applicability.
- Explicit-file mode classifies supported JSON by schema and provenance without prompts.
- Single resources and collections have separately documented valid summary shapes.
- Unknown source metadata remains null/absent; the generator must not fabricate it.
- Refreshing raw data forces companion regeneration.
- Writes are atomic.
- Invalid JSON, API error bodies, malformed YAML, missing required fields, invalid status,
  stale output, and oversize output return nonzero.

## 6. Durable producer behavior

Each raw writer should implement this transaction:

1. Fetch to a temporary file with HTTP failure detection.
2. Parse JSON and reject Jules API error objects.
3. Atomically move the validated raw response into place.
4. Invoke the generator on that explicit file with forced refresh.
5. Strictly validate the resulting companion.
6. Return success only when both artifacts are valid.

If summary generation fails after a valid raw response was saved, preserve the raw file,
return nonzero, and print the exact missing/invalid companion path. Do not silently delete
evidence and do not report a fully successful archive.

Resolve the generator path relative to the installed Jules tooling root rather than the
caller's current working directory.

## 7. Skill and runbook integration

### New focused skill

Add `skills/jules-session-archive/SKILL.md` with a discovery description equivalent to:

> Archives raw Jules REST API session and activity responses with validated companion
> YAML summaries. Use when exporting, saving, synchronizing, retrieving, or refreshing
> Jules session/activity JSON files.

The skill should activate before persistence is chosen and remain relevant through
post-write validation. It should link to the standard rather than duplicating its schema.

### Existing skills

- `jules-workflows`: replace the Session Archive `curl > file` recipe with the hardened
  `sync_session.sh`. This is an operator workflow, not a GitHub Action.
- `jules-session-manager`: state that stdout inspection is exempt but redirecting raw
  output requires the archive skill.
- `jules-sessions`: document that `sync_session.sh` creates validated companions.
- `wrapup-session`: do not apply the raw archive policy to derived reports.

### Runbooks

Add a short archive subsection to `docs/guides/operations.md` and a pointer from the
session-management runbook. Recovery/failure guides need a pointer only where they show
durable raw-output redirection. Do not repeat the full policy.

## 8. Tests and acceptance criteria

Add focused generator/producer tests for:

- `pr<N>_activities.json`
- A single session resource
- A session collection
- Forced refresh after raw data changes
- Invalid JSON and API error JSON
- Missing required summary fields and invalid status
- 50 KB rejection
- Noninteractive explicit-file operation
- Atomic producer behavior and propagated generator failure
- Exclusion of derived JSON such as `session_pr_map.json`

Migration is complete only when:

- [ ] The standard and generator agree on applicability and schema.
- [ ] All three raw writers enforce generation and validation.
- [ ] The archive skill is discoverable through the repository's skill distribution path.
- [ ] Relevant existing skills and runbooks use or link to the hardened path.
- [ ] Representative existing archives are backfilled and validate.
- [ ] Summary ignore/tracking behavior matches the documented retention policy.
- [ ] `.cursor/rules/session-summary.mdc` is deleted.
- [ ] `.cursor/` is removed if empty.

Because Cursor is no longer supported, retaining the `.mdc` file after migration would
create a second, stale policy source. If Cursor support returns, add only a thin pointer
to the canonical skill and standard.

## 9. Operational review checklist

Beyond archival behavior, review operator tooling for:

- Centralized authentication and secret redaction
- Pagination and official Jules state enums
- Bounded retries and rate-limit handling
- HTTP and API-body error detection
- Noninteractive behavior in unattended scripts
- Safe GitHub mutation and branch protections
- Session-to-PR correlation confidence and false-positive handling
- Rebase queue durability and idempotence
- Drift between canonical and installed skill copies
- Runbook commands that match current executable paths and options

Track these findings with `OPS-*` identifiers. Track session archive findings with
`ARC-*` identifiers. Do not reuse the Actions `W-*` namespace.
