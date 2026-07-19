# Jules Action Recommendations – Gemini CLI Prompt Library

## Project Overview
This repository holds a curated collection of ready‑to‑use prompt templates for the Gemini CLI, organised by category (code‑generation, Q&A, summarisation, etc.). The files are mostly markdown/YAML with occasional helper scripts. Key expectations:
- Every prompt file must contain a front‑matter block:
  ```yaml
  ---
  category: <string>
  tags: [...]
  version: "1.0"
  ---
  ```
- Examples should use relative paths (relative to the repo root) and demonstrate the intended CLI usage.
- No duplicate files (identical content) should exist.
- Documentation should be clear and concise.

Because the repo is primarily a collection of static files, the most valuable Jules capability is the **generic Jules Invoke** (schedule‑ or workflow_dispatch‑driven) that can audit the library for duplicates, missing front‑matter, deprecated CLI flags, etc., and then either open a PR with fixes or post a summary comment on the relevant PR(s) via the **Jules PR Comment** action.

### Recommended Workflow (Scheduled Audit + PR Comment)
Create two workflows:

#### 1. Scheduled Invoke (audit the library)
File: `.github/workflows/jules-prompt-library-audit.yml`

```yaml
name: Jules Prompt Library Audit
on:
  schedule:
    - cron: '0 4 * * 0'   # Every Sunday at 04:00 UTC
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    permissions:
      contents: read

write: # needed if Jules will create a PR
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Load environment (mise + .env)
        run: |
          eval "$(mise activate bash)"
          source ~/.env

      - name: Run Jules Invoke – Prompt Library Auditor
        id: jules-audit
        uses: google-labs-code/jules-invoke@v1
        with:
          jules_api_key: ${{ secrets.JULES_API_KEY }}
          prompt: |
            You are auditing the Gemini CLI Prompt Library.

            Tasks:
              1. Detect duplicate or near‑duplicate prompt files (content similarity > 90%).
              2. Flag any markdown/YAML file missing the required front‑matter block:
                     ---
                     category: <string>
                     tags: [...]
                     version: "1.0"
                     ---
              3. Identify that reference deprecated CLI flags (consult docs/CLI_CHANGELOG.md for the list).
              4. Suggest a single PR that:
                     • merges exact duplicates,
                     • adds missing front‑matter,
                     • updates deprecated flag usage.

            Output a concise JSON array (max 2000 characters) with objects:
              { "type": "duplicate|missing_frontmatter|deprecated_flag",
                "path": "<relative/file>",
                "detail": "…" }

            Constraints:
              • Keep the total diff under 200 lines.
              • All existing tests (if any) must pass.
              • Follow the existing markdown/YAML formatting conventions.
          include_last_commit: false   # we want to scan the whole library each run
          include_commit_log: false
          starting_branch: main

      - name: Capture session ID (for later comment)
        id: capture
        run: |
          # The action outputs a line like: Session ID: <uuid>
          echo "session-id=$(echo "${{ steps.jules-audit.outputs.result }}" | grep -oP 'Session ID: \K[^\s]+')" >> $GITHUB_OUTPUT

      - name: Post Jules session comment on the most recent open PR
        if: always()   # still run even if the audit step failed (so we surface info)
        # Re‑use the jules-pr-comment step directly (avoid workflow_call complexity)
        uses: BeksOmega/jules-pr-comment@v1
        with:
          pr_number: ${{ github.event.pull_request.number }}
          jules_api_key: ${{ secrets.JULES_API_KEY }}
```

#### 2. PR‑Based Review (optional)
If you also want Jules to review PRs that modify the library (e.g., a new prompt file), you can reuse the **Advanced PR Reviewer** with a very short `extra_instructions` block:

Create `.github/workflows/jules-advanced-pr-review.yml` (same as in other repos) with:

```yaml
extra_instructions: |
  This repository holds Gemini CLI prompt templates (markdown/YAML).
  Focus on:
    • Every file must contain the required front‑matter block (category, tags, version).
    • No duplicate files (identical content) should exist.
    • Example commands must use relative paths (relative to repo root) and demonstrate correct CLI usage.
    • Follow the existing markdown/YAML formatting conventions.
    • Remove any deprecated CLI flag references (see docs/CLI_CHANGELOG.md).
```

#### Optional Rule File (`.github/jules-review-rules.md`)
A useful starter set:

```markdown
# Jules Review Rules – Gemini CLI Prompt Library

## Blocking
* New markdown file missing the required front‑matter block.
* Duplicate files (identical content) added in the same PR.

## Warn
* Files longer than 300 lines – consider splitting into sub‑categories.
* Use of absolute paths in example commands – prefer relative to the repo root.

## Info
* Missing example usage block (```bash …```) at the bottom of the file.
* Duplicate files (identical content) detected – keep only one copy.
```

### When to Use Other Jules Actions
| Action | When it makes sense | How to adapt (brief) |
|--------|--------------------|----------------------|
| **Jules Advanced PR Reviewer** | You want line‑level feedback on PRs that add/modify prompt files (e.g., missing front‑matter, duplicate files). | Use the workflow above `extra_instructions` block + optional rule file. |
| **Jules PR Comment** | Already shown in the scheduled audit workflow – posts a summary of what Jules found on the PR that triggered the audit (or on the most recent open PR if no PR triggered it). | As described. |
| **Send Feedback to Jules** | Allow maintainers to correct Jules’s audit findings (e.g., marking a false positive duplicate). | Add the `send-feedback-to-jules` workflow and list the maintainer usernames in `feedback_users`. |

---

## Reasoning & Context
* The **generic Invoke** action is ideal for a batch‑style audit because it lets Jules run arbitrary analysis (detect duplicates, check front‑matter, scan for deprecated flags) and return a structured JSON payload that we can easily turn into a PR or a comment.
* Setting `include_last_commit: false` and `include_commit_log: false` keeps the prompt focused on the whole library; the library is small (< 2 MB) so scanning it entirely each run is cheap in tokens.
* The `prompt` is deliberately concise (< 300 words) and asks Jules to output a limited‑size JSON array, keeping the response token‑efficient and easy to parse in the subsequent step.
* After the Invoke step we capture the returned **session ID** and feed it to the **Jules PR Comment** action, which pulls the session’s details (prompt, logs, any generated artifacts) and posts a readable comment on the PR. This gives contributors a transparent view of what Jules did without needing to open the Jules UI.
* If you also want line‑level feedback on PRs that modify the library, the **Advanced PR Reviewer** with a tight `extra_instructions` block (front‑matter, duplicates, relative paths, deprecated flags) works well; the rule file can encode the same heuristics as blocking/warn/info.
* The **Send Feedback to Jules** workflow closes the loop: maintainers can review Jules’s audit comments, approve or request changes, and their feedback is sent back to the Jules session so it can learn from false positives or adjust its future audits.
* All workflows reuse the existing `mise` environment and `~/.env` secret, ensuring Jules sees the same CLI tools and SDKs that local developers use.