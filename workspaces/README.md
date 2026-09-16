# Jules Workspaces

This directory contains local, repository-scoped projections used by Jules
session operations. It is not a collection of target-repository checkouts, and
it is not automatically part of the Jules application source or CodeRabbit
review scope.

## Layout

```text
jules/workspaces/
├── README.md                         # this shared policy
└── <repo>/
    ├── sessions/<session-id>/        # fully ignored raw session projections
    ├── analysis/                     # tracked findings, summaries, and reports
    ├── prompts/                      # tracked message proposals/logs
    ├── state/INDEX.yaml              # tracked session/worktree coordination state
    └── state/<session-id>/           # ignored registered editable worktree
```

Current repository projections:

- `EmailIntelligence`
- `gemini-cli-prompt-library`
- `gemini-fullstack-langgraph-quickstart`
- `kaggle-notebooks-analysis`

Each `<repo>` directory is only a local Jules operations namespace. Its
`sessions/` is fully ignored: raw pulls, patches, REST/SDK exports, summaries,
and generated session state are local-only projections. Move durable findings to
`analysis/`. `state/INDEX.yaml` is tracked coordination metadata; the
materialized `state/<session-id>/` worktrees remain ignored. Only explicitly
curated analysis, prompt logs, indexes, and workspace documentation outside
those disposable directories may be tracked. Raw patches, generated files, caches,
temporary files, and target-source copies must remain ignored.

## Repository and review boundary

The Jules repository is the default scope:

```text
/home/masum/github/remote/jules
```

Do not explore, edit, test, or stage an unpushed sibling checkout such as
`/home/masum/github/remote/EmailIntelligence` by default. It may contain
unrelated user changes. Use the Jules CLI and a localized state worktree for
session work instead. Remote GitHub refs and PR metadata may be queried only
for an explicitly named repository, PR, session, or branch.

Running `coderabbit review` from `/home/masum/github/remote/jules`—including
from any `workspaces/` subdirectory—reviews Jules repository changes. It does
not review the target repository represented by a workspace folder. A target
review requires a verified localized `state/<session-id>/` worktree:

```bash
jules remote list --session <SESSION_ID>
jules remote pull --session <SESSION_ID>
git -C workspaces/<repo>/state/<SESSION_ID> rev-parse --show-toplevel
git -C workspaces/<repo>/state/<SESSION_ID> status --short --ignored
```

Verify the worktree's branch, PR, base ref, and task before editing. A session
artifact directory is not a worktree and must never be used as a review or
repair target. Review findings are hypotheses: confirm every path and symbol
against the localized current tree.

## Session and worktree isolation

- Scope every Jules query by repository and session; the global session store is
  not repository-scoped by default.
- Keep one state worktree per repository, session, and branch. Never reuse a
  state directory for another branch or session.
- Pull without applying first. Inspect the patch and history in the localized
  state worktree; use real three-way conflict resolution for repairs.
- Push only to the existing named PR branch after focused checks. Do not create
  a new PR or message duplicate sessions merely because an artifact is old.
- Log every outbound session message under the corresponding `prompts/`
  directory before or immediately after sending.
- Use specific Git paths when staging. Never use broad staging that could make
  ignored projections visible.

## Commands

From `/home/masum/github/remote/jules`:

```bash
jules auth status
jules remote list --repo <OWNER/REPO>
jules remote list --session <SESSION_ID>
jules remote pull --session <SESSION_ID>
jules teleport <SESSION_ID>
jules teleport --help

git worktree list --porcelain
git check-ignore -v \
  workspaces/<repo>/sessions/<SESSION_ID>/patch.diff \
  workspaces/<repo>/state/<SESSION_ID>/README.md
```

`jules teleport` and explicit `git worktree` creation must still leave the
editable checkout under the matching `workspaces/<repo>/state/<session-id>/`
namespace. Confirm registration with `git worktree list --porcelain`.

## Tracking policy

Track in the Jules repository only:

- this shared README and durable workspace indexes;
- curated session summaries and analysis;
- prompt logs required for operational traceability;
- Jules tooling needed to manage these projections.

Do not track raw session payloads, detached worktree files, target-repository
source copies, credentials, local databases, caches, generated output, or
temporary exports. The root `.gitignore` is the enforcement layer; verify it
with `git check-ignore` before creating or staging new workspace material.

Per-repository notes, when genuinely necessary, belong in that repository's
`analysis/` or curated session summary—not in a duplicate workspace README.
