# Jules Action Recommendations – Email Intelligence

> **Recommendation record:** Validate repository assumptions and use the canonical
> workflows in this repository; embedded examples are not distribution authorities.

## Project Overview
This repository contains Python utilities for parsing, enriching, and analysing email headers and bodies (SPF/DKIM/DMARC, threat intelligence, etc.). Key characteristics:
- Heavy reliance on regular expressions for header parsing.
- Use of pandas for bulk enrichment.
- Emphasis on security (avoid ReDoS, never log raw PII).
- Clear module layout under `email_parsers/` and a suite of unit tests.
- Documentation expects each public function to have a docstring and each module to have a short description.

Most contributions are small‑to‑medium PRs that modify regex patterns, add new parser functions, or update unit tests. Therefore the **Advanced Jules PR Reviewer** is again the best choice: it can pinpoint problematic regex lines, flag missing docstrings, and auto‑resolve its comments once you push a fix.

### Recommended Workflow (Advanced PR Reviewer)
Create `.github/workflows/jules-advanced-pr-review.yml`:

```yaml
name: Jules Advanced PR Review – Email Intelligence PR Review – Email Intelligence
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

concurrency:
  group: jules-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write   # post review comments & set status
      contents: read         # read repo & rule file
      statuses: write        # set jules/review check
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # full history needed for diff analysis

      - name: Load environment (mise + .env)
        run: |
          eval "$(mise activate bash)"
          source ~/.env

      - name: Run Jules Advanced PR Review
        uses: thalesraymond/jules-pr-reviewer@v1
        with:
          jules_api_key: ${{ secrets.JULES_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          # Optional rule file – create if you want to encode house rules
          rules_file: .github/jules-review-rules.md
          # Project‑specific extra instructions (keep < 200 words)
          extra_instructions: |
            This repository contains Python utilities for email header/body parsing and intelligence.
            Focus on:
              • Regex correctness and safety – avoid patterns that could lead to ReDoS (e.g., nested quantifiers without atomic groups).
              • Security – never log raw email subject/body or other PII at INFO level or higher.
              • Docstring completeness – every public function must have a docstring describing its purpose, parameters, and return value.
              • Consistency with the existing `email_parsers/` module layout and naming conventions.
              • Unit‑test coverage – any new public function should be accompanied by at least one test.
              • Follow the project’s linting/formatting config (see pyproject.toml, flake8, black).
          timeout_minutes: 40
```

#### Optional Rule File (`.github/jules-review-rules.md`)
A useful starter set:

```markdown
# Jules Review Rules – Email Intelligence

## Blocking
* Regex containing more than two nested quantifiers (`*`, `+`, `{m,n}`) without atomic groups – potential ReDoS.
* Functions that log raw email content (subject/body) at INFO level or higher.

## Warn
* Use of bare `except:` – catch specific exception types.
* Public functions missing a docstring.

## Info
* Lines longer than 100 characters – consider splitting for readability.
* Replacing `print()` debugging statements with the project logger (`logger.debug(...)`).
```

### When to Use Other Jules Actions
| Action | When it makes sense | How to adapt (brief) |
|--------|--------------------|----------------------|
| **Jules Invoke** (generic task) | Scheduled maintenance (dependency updates, linting, docs sweeps) that is not tied to a specific PR. | Use the generic Invoke template (see below) with a prompt such as “Run `pip list --outdated`, open a PR to update any package with known CVSS ≥ 7.0; ensure flake8/black pass; verify README reflects current structure; run the test suite and propose fixes for any failures.” |
| **Jules PR Comment** | You run a Jules task from a schedule or workflow_dispatch and want the session details (prompt, logs, artifacts) posted on the relevant PR(s). | After the Invoke step captures the returned session ID, call the `jules-pr-comment` workflow (or copy its step) with that session ID and the PR number you want to comment on. |
| **Send Feedback to Jules** | You want human reviewers (maintainers) to be able to feed their review comments back into Jules so it can learn from corrections. | Add the `send-feedback-to-jules` workflow (see below) and list the maintainer usernames in `feedback_users`. |

---

## Reasoning & Context
* The **Advanced PR Reviewer** sends only the *changed* diff to Jules on each `synchronize` event, which is essential for a Python‑heavy repo where a full‑repo scan would waste tokens on unchanged files.
* Line‑level comments map directly to the exact regex pattern or function definition that Jules flags, making it trivial for contributors to locate and fix the issue.
* Auto‑resolve reduces comment noise: once you push a fix, Jules automatically marks its own comment thread as resolved, keeping the PR tidy.
* The `extra_instructions` block injects project‑specific conventions (regex safety, PII handling, docstring completeness, module layout, unit‑test coverage, linting/formatting) without requiring Jules to relearn them from scratch, improving accuracy and lowering token cost.
* The rule file lets you encode “house rules” (blocking/warn/info) that Jules will treat with the appropriate severity, aligning its verdict with your project’s policy.
* All workflows reuse the existing environment setup (`mise activate bash; source ~/.env`) so Jules has access to the same CLI tools and SDKs that local developers use.
