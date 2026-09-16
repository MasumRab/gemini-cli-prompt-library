# Jules Failure & Recovery Runbook

This runbook provides guidance on what to do when a Jules session enters a `FAILED` state, gets stuck, or goes off-track.

## Pre-recovery checklist

Before recovering a session, confirm you are working in the correct per-repo
workspace. See `docs/runbooks/workspace_isolation.md` for the layout.

1. **Repo scoping.** Confirm the session's `sourceContext.source` matches your
   workspace (`<owner>/<repo>`).
2. **Prompt logging.** Ensure `workspaces/<owner>/<repo>/prompts/sent_responses.md`
   is writable — every recovery message must be logged there.
3. **Transport choice.** If REST polling has timed out in recent turns, see the
   Transport fallbacks section in `session_recovery.md` and use the SDK bridge
   or CLI instead.

## 1. Identifying the Failure

First, determine why the session failed. Was it a bash command error? A linter failure? Or did the agent give up?

Use the activities list to find the last action:

```bash
uv run python -m tools.sessions.jules_list_activities <SESSION_ID>
```

Look for the `progressUpdated` or `artifacts.bashOutput.exitCode` in the most recent activities.

### Common Failure Modes

- **Bash Error (Exit Code > 0):** Jules ran a command (like `npm install` or `pytest`) that failed. Often this is due to missing dependencies, syntax errors, or failing tests.
- **Tool Error:** Jules attempted to use an internal tool incorrectly.
- **Context Exhaustion / Timeout:** The session ran too long or hit an API limit.
- **Large Diff Exhaustion:** Jules failed to process or track a large number of files, or became overwhelmed by massive log files / datasets inside the repo.

## 2. Recovering with `sendMessage`

If the session is still active but stuck, or if you want to course-correct Jules before it completes:

```bash
uv run python -m tools.sessions.jules_send_message <SESSION_ID> "Your recovery prompt here"
```

### Effective Prompting for Recovery

When sending a message to recover a session, be explicit and explore all avenues for problem-solving:

- **If a build failed:** "The build failed because `package-x` is missing. Please run `npm install package-x` and try building again."
- **If a test failed:** "The test `test_edge_case` failed because it expects a `ValueError`. Update the function in `src/module.py` to raise `ValueError` on bad input."
- **If Jules modified the wrong file:** "You modified `config.json`, but you were only supposed to modify `src/app.js`. Please revert `config.json` and make the changes to `src/app.js`."
- **If Jules is struggling with large diffs or unrelated file tracking:** "You seem to be tracking thousands of files which is overwhelming your context. Create a `.gitignore` (or update the existing one) to properly exclude build outputs, data directories, or virtual environments (`__pycache__`, `venv/`, etc.) before proceeding."

## 2.5 Jules Memory Diagnostics (Stale Prompt Pattern)

If Jules repeatedly fails or introduces regressions, it may be operating on outdated internal memory rather than live file state.

**Diagnosis Workflow:**

1. Run `uv run python -m tools.sessions.jules_list_activities <SESSION_ID> --raw | grep -i "planGenerated"`
2. If Jules says "I will add X to `old_file.py`" but `old_file.py` was renamed to `new_file.py` days ago, Jules is using outdated memory.

**Resolution Strategy (Via `sendMessage`):**
The recovery prompt must explicitly clear the memory.

- "Forget your previous understanding of `old_file.py`. It has been renamed to `new_file.py`. Re-read the file using your `read_file` tool before proceeding."

## 3. When to Abandon a Session

Sessions should rarely be abandoned automatically. Almost all issues can be resolved with correct usage of `sendMessage` and smart repository management (like creating `.gitignore` overrides).

However, if a session is completely broken, you may need to abandon it.

**Indicators that a session MIGHT need to be abandoned:**
*   Jules has made the exact same mistake 4+ times in a row despite explicit corrections via `sendMessage`.
*   The session status is permanently `FAILED` and the API **refuses new messages** on that specific session (e.g. returns 4xx/5xx the moment you call `sendMessage`). Note: a `FAILED` state **alone does not block messaging** — `sendMessage` is accepted on `FAILED` sessions and is the standard recovery path (see `session_recovery.md`). Only treat a session as terminal if the live API call is actually rejected.

**Action:**

1.  **Do NOT close the session automatically via a script.**
2.  Human intervention is required: A human user should review the session history and make the decision to close the session or close any generated PRs on GitHub.
3.  If abandoned by a user, start a new session using the Jules web UI or API. Adjust the initial prompt to be more specific, add strict `.gitignore` rules in advance, and include constraints (refer to the "Constraints" section in `JULES_PR_HANDOFF.md`).
