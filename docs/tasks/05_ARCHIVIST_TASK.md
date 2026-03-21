# Archivist Task: Maintain Context Awareness

**Persona:** Archivist
**Goal:** Maintain an accurate and up-to-date record of active repository state to prevent duplicate work by other agents.
**Execution Context:** `gemini-cli-prompt-library` repository.

## Daily Process

1. **Update Context**
   - Run the context updater script to fetch all currently open Pull Requests and their modified files.
   - Command: `python3 scripts/update_active_context.py`
   - *Note:* Ensure `GITHUB_TOKEN` is set in your environment if possible. If not, the script will degrade gracefully, but context will be unavailable.

2. **Verify Output**
   - Verify that `docs/ACTIVE_CONTEXT.md` was successfully updated.
   - Check if the output lists PRs correctly or states the degraded mode (e.g., "*GitHub Token missing*").

3. **Update Journal**
   - Record the execution of this task in `.jules/archivist.md`.
   - Log the timestamp, whether the context update was successful, and a summary of any open PRs discovered.

## Success Criteria
- The `docs/ACTIVE_CONTEXT.md` file reflects the current GitHub state.
- The `.jules/archivist.md` journal is appended with today's record.
