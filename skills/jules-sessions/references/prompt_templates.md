# Jules Prompt Templates (Workspace-Generic)

Reusable, parameterized prompts for every workspace. Instantiate per repo —
a workspace's `prompts/` dir holds **sent** (logged) prompts and
session-specific artifacts; this library holds the generic patterns.

Convention: `{placeholders}` are filled at send time. Log every sent prompt to
`workspaces/<repo-name>/prompts/sent_responses.md` per the workspace isolation
runbook, with `prompt_type` from the categories below.

---

## Prompt Type Categories

Matches the logging invariant's `prompt_type` enum, extended with task-shape
prompts. Response-side templates (approve/nudge by session state) live in
[`response_templates.md`](response_templates.md); these are prompt-side.

| prompt_type | When | Template |
|-------------|------|----------|
| nudge | IN_PROGRESS stuck | Nudge (§1) |
| rectification | Wrong direction detected | Steering Correction (§2) |
| follow-up | Need deliverable/verification | Verification Request (§3) |
| follow-up | Need docs/analysis output | Requirements/Design Generation (§4) |
| follow-up | Analysis-only session | Analysis-Only Constraints (§5) |
| approve | Plan approval | see `response_templates.md` §1 |
| task | New focused work | Task Assignment (§6) |

---

## §1 Nudge (IN_PROGRESS_STUCK)

```
Status update on {task_summary}? If you are blocked, name the blocker and
what you need to proceed. If the current approach is failing, say so —
do not keep retrying silently. Continue with {next_expected_step} unless
blocked.
```

## §2 Steering Correction (rectification)

For when a session is working but in the wrong direction. Never restart —
extend.

```
This message extends your current task. Do NOT restart or interrupt your
current process. Incorporate these corrections and RESET/RECREATE any files
created under the previous instructions if they do not meet the updated
guidelines.

## CORRECTION 1: {correction_title}
{what_is_wrong} → {what_is_required}. Your work product must reflect {constraint}.

## CORRECTION 2: {correction_title}
{...}

Apply these now; keep everything already done that is still correct.
```

## §3 Verification Request (follow-up)

Send when work is claimed complete, before trusting it.

```
Please confirm the following for {deliverable}:

## COMPLETENESS
- [ ] {deliverable_item_1} exists and is complete
- [ ] {deliverable_item_2} exists and is complete

## BOUNDARIES
- [ ] No re-analysis performed beyond what was already established
- [ ] No scope added beyond the stated requirements

## ACCURACY
- [ ] Claims are backed by the evidence already gathered
- [ ] File paths and identifiers referenced are real

Report any item you cannot confirm rather than implying completion.
```

## §4 Requirements/Design Generation (follow-up)

When a session has completed discovery and should now produce canonical docs.

```
Generate canonical {REQUIREMENTS|DESIGN}.md for {work_area} based on your
analysis from session {source_session_id}.

For REQUIREMENTS:
- Formalize the hard constraints you identified (label them REQ-01, REQ-02, …)
- Include any additional requirements discovered during analysis

For DESIGN:
- Map each requirement to concrete implementation steps
- Name exact files, branches, and PRs; no vague references

Constraints: analysis-only conclusions from {source_session_id}; do not
re-run discovery. Output the documents; do not modify any files.
```

## §5 Analysis-Only Constraints (follow-up / task)

Prepend to any session that must produce reports, not changes.

```
## CONSTRAINT: ANALYSIS AND DOCUMENTATION ONLY
This session must produce reports and analysis findings ONLY. No file
modifications, extractions, engine runs, validations, or session creations
are permitted. All work product must be analyzable reports.

### {analysis_area_1}
Objective: {objective}
Deliverable: {report_name}
Analysis points:
- {point_1}
- {point_2}

### {analysis_area_2}
{...}
```

## §6 Task Assignment (task)

For a new, focused session. One task per session.

```
Execute: {task_title}.

Context: {one_paragraph_what_and_why}. Key commands: {commands}.
Branch: {target_branch}. Constraints: {limits}.

Deliverable: {deliverable}. Document the result in {log_path}.
```

---

## Instantiation Rules

1. **Fill every placeholder** — no `{...}` survives into a sent prompt.
2. **Reference code by path**, not description (token economy).
3. **One task per session** — split multi-part asks into separate sessions.
4. **Reuse over rewrite** — check this library and `response_templates.md`
   before drafting a new prompt; extend the library when a genuinely new
   pattern emerges, then log the sent instance in the workspace.
5. **Session-specific prompts are workspace artifacts** — the filled
   instance goes in `workspaces/<repo>/prompts/`, never back here.
