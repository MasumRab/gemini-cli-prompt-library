# Jules Action Recommendations – Kaggle Notebooks Analysis

> **Legacy reference:** This file documents the external `kaggle-notebooks-analysis` repo. Current Jules tools are in `tools/` within this repo.

## Project Overview
This repository holds Kaggle‑style notebooks, data‑processing scripts, and helper utilities. The primary goals are:
- Reproducible notebook execution (all cells runnable top‑to‑bottom without hidden state)
- Memory‑efficient data pipelines (avoid loading whole datasets when streaming/chunking is possible)
- Consistency with existing helper scripts in `scripts/` and the utility modules in `.agents/commands/`
- Clear documentation: each notebook should start with a markdown cell describing the data and objective and end with a “Next Steps” / “Conclusion” cell.

Because most work arrives as pull requests that touch notebooks or Python helpers, the **best‑fit Jules capability** is the **Advanced Jules PR Reviewer** (line‑level, incremental diff, auto‑resolve).  It lets Jules comment directly on problematic cells or imports, automatically resolves its comments when you push a fix, and only analyses the changed diff on each `synchronize` event – critical for keeping token usage low on large notebooks.

### Recommended Workflow (Advanced PR Reviewer)
Create `.github/workflows/jules-advanced-pr-review.yml` in the repo root:

```yaml
name: Jules Advanced PR Review – Kaggle Notebooks
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
            This repository contains Kaggle‑style notebooks and helper scripts.
            Focus on:
              • Notebook reproducibility – every cell must run top‑to‑bottom without hidden state.
              • Data‑leakage checks – raw test data must never appear in training pipelines.
              • Memory usage – avoid loading full datasets into RAM when chunking or streaming is possible.
              • Follow the existing notebook template (see notebook_template.ipynb).
              • Consistency with helper scripts in scripts/ and utilities in .agents/commands/.
          timeout_minutes: 50   # give Jules a bit more time for large notebooks
```

#### Optional Rule File (`.github/jules-review-rules.md`)
You can start with an empty file and add heuristics over time.  A useful starter set:

```markdown
# Jules Review Rules – Kaggle Notebooks Analysis

## Blocking
* Any notebook cell that uses `!pip install` without an explicit version pin.
* Direct file paths that point outside the `data/` or `notebooks/` directories (possible leakage).

## Warn
* Notebooks longer than 150 cells – consider splitting into modules or functions.
* Use of `pandas.iterrows()` – prefer vectorised operations.
* Hard‑coded random seeds that are not sourced from a config file.

## Info
* Missing a top‑level markdown cell that describes the dataset and objective.
* Notebooks that lack a concluding “Next Steps” or “Conclusion” cell.
```

### When to Use Other Jules Actions
| Action | When it makes sense | How to adapt (brief) |
|--------|--------------------|----------------------|
| **Jules Invoke** (generic task) | Scheduled maintenance (dependency updates, linting, docs sweeps) that is not tied to a specific PR. | Use `pull request.  Create a workflow similar to the generic Invoke template (see below) and point the `prompt` at tasks such as “run `npm outdated` and `pip list --outdated`, open a PR to update any package with CVSS ≥ 7.0”. |
| **Jules PR Comment** | You run a Jules task from a schedule or workflow_dispatch and want the session details (prompt, logs, artifacts) posted on the relevant PR(s). | After the Invoke step captures the returned session ID, call the `jules-pr-comment` workflow (or copy its step) with that session ID and the PR number you want to comment on. |
| **Send Feedback to Jules** | You want human reviewers (maintainers) to be able to feed their review comments back into Jules so it can learn from corrections. | Add the `send-feedback-to-jules` workflow (see below) and list the maintainer usernames in `feedback_users`. |

---

## Current PR Status & Workflow Guidance

> Last updated: 2026-07-20. Run `gh pr list --repo MasumRab/kaggle-notebooks-analysis --state open --json number,title,headRefName,mergeable,createdAt` to refresh.

### MERGEABLE — no conflicts, ready for review

| PR | Title | Label to apply |
|----|-------|---------------|
| [#119](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/119) | Fix dtype conformity check (tembo) | `jules-walkthrough` (has architectural changes) or `jules-force-review` |
| [#107](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/107) | PR Merge Order Assessment | `jules-walkthrough` |
| [#89](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/89) | Add tests for RegressionGuard methods | `jules-force-review` (has stale Gemini reviews) |

### CONFLICTING — needs conflict resolution

| PR | Title | Branch | Label to apply |
|----|-------|--------|---------------|
| [#120](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/120) | Restore Jules API client | `cto/restore-jules-api...` | `jules-resolve` |
| [#118](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/118) | Original prompt retrieval v3 | `fix/jules-prompt-retrieval-v3` | `jules-resolve` |
| [#116](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/116) | Fix unclosed file descriptor | `jules-14844...` | `jules-resolve` + `jules-force-review` |
| [#115](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/115) | Network request timeouts | `fix-network-timeout...` | `jules-resolve` + `jules-force-review` |
| [#113](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/113) | Validate notebook tests | `testing-improvement...` | `jules-resolve` |
| [#111](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/111) | Rebase orchestrator refactor | `cto/implement-rebase...` | `jules-resolve` |
| [#109](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/109) | Original prompt retrieval v1 | `fix/jules-api-prompts` | `jules-resolve` |
| [#108](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/108) | Sort metrics by ROI | `fix-roi-sorting...` | `jules-resolve` |
| [#106](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/106) | Diagnostic pipeline fix | `cto/diagnostic-fix...` | `jules-resolve` |
| [#105](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/105) | Original prompt retrieval | `feature/jules-prompt...` | `jules-resolve` |
| [#104](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/104) | Original prompt retrieval v2 | `fix-jules-api-prompts-v2` | `jules-resolve` |
| [#102](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/102) | RegressionGuard range error | `testing-improvement...` | `jules-resolve` |
| [#95](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/95) | Original prompt retrieval | `cto/fix-jules-api...` | `jules-resolve` |
| [#91](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/91) | Engine task changes | `cto/implement-jules-tools...` | `jules-resolve` |
| [#90](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/90) | Jules API key fix | `cto/implement-jules-tools...` | `jules-resolve` |
| [#88](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/88) | Task b0133363 update | `jules-sessions-status-6146b` | `jules-resolve` |
| [#87](https://github.com/MasumRab/kaggle-notebooks-analysis/pull/87) | Hardened Infrastructure | `cto/implement-hardened...` | `jules-resolve` |

### Workflow labels and their effect

| Label | Workflow | Session consumption | When to apply |
|-------|----------|-------------------|---------------|
| *(none — auto)* | `jules-pr-review.yml` | 1 session per PR sync | Every non-Jules PR open/sync (auto) |
| `jules-force-review` | `jules-pr-force-review.yml` | 1 session | Force review of any PR (including jules-* branches) |
| `jules-walkthrough` | `jules-pr-walkthrough.yml` | 1 session | Want architectural narrative + Mermaid diagrams |
| `jules-auto-fix` | `jules-pr-auto-fix.yml` | 1 session | PR describes a specific fix needed |
| `jules-resolve` | `jules-pr-resolve-conflicts.yml` | 1 session | PR has merge conflicts |

---

## Reasoning & Context
* The **Advanced PR Reviewer** sends only the *changed* diff to Jules on each `synchronize` event, which is essential for notebooks where a full‑repo scan would be prohibitively expensive in tokens and time.
* Line‑level comments map directly to notebook cells or import statements, making it easy for contributors to see exactly what Jules flagged.
* Auto‑resolve reduces comment noise: once you push a fix, Jules automatically marks its own comment thread as resolved, keeping the PR tidy.
* The `extra_instructions` block injects project‑specific conventions (reproducibility, memory usage, notebook template) without requiring Jules to relearn them from scratch, improving accuracy and lowering token cost.
* The rule file lets you encode “house rules” (blocking/warn/info) that Jules will treat with the appropriate severity, aligning its verdict with your project’s policy.
* All workflows reuse the existing environment setup (`mise activate bash; source ~/.env`) so Jules has access to the same CLI tools and SDKs that local developers use.