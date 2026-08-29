# Migrating legacy Jules workflow worktrees to `.github`

Use this guide when a branch or worktree still edits the pre-`b706754` Jules template
layout. The migration moved executable workflow assets from documentation directories
into GitHub's runtime directory. A worktree that continues editing the old paths can
produce valid-looking changes that GitHub never executes.

This guide covers path migration only. It does not make a legacy implementation current,
resolve the open findings in `HANDOFF.md`, or authorize target-repository distribution.

## Canonical ownership

| Legacy path                                         | Canonical path                                 | Treatment                                                                   |
| --------------------------------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------- |
| `docs/actions/workflows/*.yml`                      | `.github/workflows/*.yml`                      | Port semantic changes to the matching runtime workflow                      |
| `docs/actions/scripts/jules-comment-classifier.cjs` | `.github/scripts/jules-comment-classifier.cjs` | Port classifier changes and update consumers together                       |
| `docs/actions/workflows/EDGE_CASES.md`              | `docs/actions/EDGE_CASES.md`                   | Update only if the catalog still reflects verified behavior                 |
| `docs/actions/workflows/HANDOFF_PATTERNS.md`        | `docs/actions/HANDOFF_PATTERNS.md`             | Port reusable patterns after checking current runtime code                  |
| `docs/actions/workflows/SMOKE_TEST_PLAN.md`         | `docs/actions/SMOKE_TEST_PLAN.md`              | Port scenarios and expected results                                         |
| `docs/actions/workflows/CHANGELOG.md`               | `docs/actions/artifacts/CHANGELOG.md`          | Historical only; put new status in `HANDOFF.md`, not the archived changelog |

The original path-only move is commit `b706754`. Current runtime behavior is always the
tip of `.github/workflows/` and `.github/scripts/` on the branch being reviewed—not the
contents of that migration commit or an old worktree.

## Before migration

1. Read the repository and branch guidance that applies to the worktree. Do not rebase,
   merge, or cherry-pick across protected product branches merely to perform this path
   migration.
2. Record the worktree branch, base commit, and dirty state:

   ```bash
   git status --short
   git branch --show-current
   git merge-base HEAD origin/main
   ```

3. Commit the legacy work on its existing branch, or save a reviewable binary diff
   outside the repository. Do not use an unlabelled stash as the only copy.
4. Inventory every legacy-path change, including deletions and classifier consumers:

   ```bash
   git diff --name-status <base>...HEAD -- \
     docs/actions/workflows docs/actions/scripts
   rg -n 'docs/actions/(workflows|scripts)' . \
     --glob '!docs/actions/artifacts/**'
   ```

5. Separate semantic changes from path-only moves, formatting, and generated output.
   Migrate behavior; do not restore the old directory structure.

## Preferred migration: replay onto current canonical code

Use a new branch or worktree based on the current canonical branch. This avoids rewriting
the legacy branch and makes the migration reviewable:

```bash
git fetch origin
git worktree add ../jules-migrate-<topic> -b migrate/<topic> origin/main
```

In the new worktree, replay each legacy commit in order:

```bash
git cherry-pick <legacy-commit>
```

Git may follow the `b706754` renames automatically. When it does not, resolve the
conflict by applying the intent to the canonical path, then remove the obsolete path:

```bash
git add .github/workflows/<workflow>.yml
git rm --ignore-unmatch docs/actions/workflows/<workflow>.yml
git cherry-pick --continue
```

For classifier changes, migrate the classifier and all affected workflows in the same
reviewable unit. Current consumers load the classifier from a trusted base-branch
checkout under `_helpers/.github/scripts/`; do not restore imports from
`docs/actions/scripts/` or from the PR-head checkout.

Do not resolve conflicts by choosing all of the legacy file or all of the canonical
file. Start from the current canonical implementation and port the smallest semantic
change. This preserves hardening added after the old worktree diverged.

## Alternative: rebase an unpublished worktree branch

An unpublished branch may be rebased onto the current canonical branch if repository
guidance allows history rewriting:

```bash
git fetch origin
git rebase origin/main
```

Resolve rename conflicts using the mapping above. Do not use this method for a shared or
published branch without explicit approval. A successful rebase is not proof that Git
mapped every change to the correct runtime file; inspect the resulting diff.

## Target-repository overlays

Path migration must not erase repository-specific behavior. Before copying canonical
files into EmailIntelligence, Kaggle, or another target, complete T-24:

1. Read authoritative instruction, branch-governance, and review-policy files from the
   exact target base revision.
2. Classify each requirement as trusted-base prompt context, a deterministic workflow
   check, or operator-only guidance.
3. Preserve intentional differences through documented inputs or a narrow overlay.
4. Test prompt loading separately from enforceable branch and safety checks.

Never overwrite a target workflow merely because its filename matches the canonical
manifest. Compare behavior and policy first.

## Required validation

### No executable assets remain in legacy paths

```bash
test -z "$(git ls-files 'docs/actions/workflows/*.yml')"
test -z "$(git ls-files 'docs/actions/scripts/*.cjs')"
```

Historical artifacts and this migration guide necessarily mention old paths. Runtime
code, skills, commands, and top-level entry points must not depend on them:

```bash
if rg -n 'docs/actions/(workflows|scripts)' \
  .github scripts skills commands README.md ARCHITECTURE.md \
  --glob '!.github/README.md'; then
  echo "legacy workflow path still referenced by active code or an entry point" >&2
  exit 1
fi
```

### Canonical assets and references are complete

```bash
test "$(git ls-files '.github/workflows/jules-*.yml' | wc -l)" -eq 11
test -f .github/scripts/jules-comment-classifier.cjs
node -e "require('./.github/scripts/jules-comment-classifier.cjs')"
```

Run `actionlint` and the applicable scenarios in `SMOKE_TEST_PLAN.md`. For a target
repository, also produce the manifest/content-hash report required by
`REVIEW_RECOMMENDATION.md` and run the target-policy tests required by T-24.

### Review the migrated diff

Confirm that:

- Each legacy semantic change appears once in its canonical destination.
- No post-migration hardening was lost.
- No duplicate workflow can drift outside `.github/workflows/`.
- Classifier changes remain symmetric across intended consumers.
- Workflow permissions, trusted-base loading, fork guards, state handling, and markers
  still match the current review invariants.
- The commit message records the legacy branch/commit range and canonical base commit.

Only delete the legacy worktree after its commits are preserved, the migrated branch is
reviewed, and all validation passes.
