# Jules Response Templates

Pre-written message templates for different session states, incorporating session context and intent.

---

## Template Categories

### 1. AWAITING_PLAN_APPROVAL

**When:** Jules has generated a plan and is waiting for your approval.

**Context-aware template:**
```
Session: {title}
Original intent: {prompt_summary}

Approve response:
"Proceed with the plan. Focus on {key_objective_from_prompt}."
```

**Example:**
```
Session: Optimize Database Queries
Original intent: Improve query performance for the email search feature...

Approve response:
"Proceed with the plan. Focus on the core search queries first, then caching layer."
```

---

### 2. IN_PROGRESS_STUCK (Nudge)

**When:** Session has been in IN_PROGRESS state for longer than threshold.

**Context-aware template:**
```
Session: {title}
Running since: {update_time}
Original task: {prompt_summary}

Nudge response:
"Status update? If you're encountering blockers, describe them. Otherwise, continue with {current_phase_hint}."
```

**Example:**
```
Session: Add WebSocket Support
Running since: 2025-01-15T10:00:00Z
Original task: Implement real-time notifications via WebSocket...

Nudge response:
"Status update? If you're encountering blockers with the auth integration, describe them. Otherwise, continue with the notification dispatch logic."
```

---

### 3. COMPLETED_NO_CHANGES

**When:** Session completed but made no code changes.

**Why:** We work on EXISTING PRs - if nothing changed, the session didn't accomplish its goal.

**Context-aware template:**
```
Session: {title}
Branch: {branch}
Original intent: {prompt_summary}

Follow-up response:
"I see the session completed without changes. What happened?

RULE: We ALWAYS work on existing PRs, not create new ones.
If no changes were made, the work wasn't completed.

Questions:
- Were the requirements unclear?
- Was the codebase different than expected?
- Did you try to create a new PR (not allowed)?

Please:
1. Check if you pushed to the existing branch
2. If there's work to do, continue on the existing PR
3. Describe what specifically prevented progress
```

**Example:**
```
Session: Refactor API Handlers
Branch: scientific
Original intent: Consolidate duplicate API handlers...

Follow-up response:
"I see the session completed without changes. What happened?

RULE: We ALWAYS work on existing PRs, not create new ones.
If no changes were made, the work wasn't completed.

Questions:
- Were the requirements unclear?
- Was the codebase different than expected?
- Did you try to create a new PR (not allowed)?

Please:
1. Check if you pushed to the existing branch
2. If there's work to do, continue on the existing PR
3. Describe what specifically prevented progress
```

---

### 4. COMPLETED_NO_PR

**When:** Session completed but didn't push changes to an existing PR.

**Why:** We work on EXISTING PRs, not create new ones.

**Context-aware template:**
```
Session: {title}
Branch: {branch}
Changes made: {files_changed_count} files

⚠️ IMPORTANT: Do NOT create a new PR. Push changes to the EXISTING PR branch.

Follow-up response:
"I see the session completed but no PR was created/updated. 

RULE: We NEVER create new PRs - we always push to existing ones.

Please:
1. Find the existing PR for branch '{branch}' OR use an existing open PR
2. Push your changes to that PR's branch
3. Update the PR title if needed

If there's no existing PR for this work, describe what you want to accomplish and I'll find or create an existing PR for you to work on.
NEVER: git push -u origin (creates new branch/PR)
ALWAYS: git push to existing branch
```

**Example:**
```
Session: Add Rate Limiting
Branch: main
Changes made: 5 files

Follow-up response:
"I see the session completed but no PR was created/updated. 

RULE: We NEVER create new PRs - we always push to existing ones.

Please:
1. Find the existing PR for branch 'main' OR use an existing open PR
2. Push your changes to that PR's branch
3. Update the PR title if needed

If there's no existing PR for this work, describe what you want to accomplish and I'll find or create an existing PR for you to work on.
NEVER: git push -u origin (creates new branch/PR)
ALWAYS: git push to existing branch
```

---

### 5. COMPLETED_PR_STALE

**When:** PR created but not yet merged/reviewed.

**Context-aware template:**
```
Session: {title}
PR: {pr_url}
PR Title: {pr_title}

Merge reminder response:
"The PR is ready. I'll review these changes:
- {key_file_1}
- {key_file_2}

Any concerns before I merge?"
```

**Example:**
```
Session: Fix Auth Token Refresh
PR: https://github.com/.../pull/437
PR Title: fix: Auth token refresh race condition

Merge reminder response:
"The PR is ready. I'll review these changes:
- src/auth/token_refresh.py
- tests/test_auth.py

Any concerns before I merge?"
```

---

### 6. FAILED / TIMEOUT

**When:** Session failed or timed out.

**Why:** CRITICAL: Guide Jules to build on existing work, not start fresh. NEVER close PRs.

**Context-aware template:**
```
Session: {title}
State: {state}
Original intent: {prompt_summary}

⚠️ IMPORTANT RULES:
- Do NOT start fresh or dump previous changes
- Do NOT close existing PRs - work on them until merged
- ALWAYS push to existing PR branch
- This branch already has {commit_count} commits of work. Build on top of it.

Instead of rewriting:
- Identify what specifically failed
- Make surgical fixes to the existing code
- Preserve working functionality even if imperfect
- Incrementally improve, don't replace

Use these git commands to continue:
1. git fetch origin
2. git checkout {existing_branch}
3. git log --oneline -5  # Review recent commits
4. Make surgical fix to the specific file
5. git add fixed_file.py
6. git commit -m "fix: {specific fix}"
7. Run verification: pytest --ignore=tasks --ignore=workspace
8. git push origin {existing_branch}

Remember: 
- Incremental improvement > wholesale rewrite
- NEVER close PRs - work on them until merged
```

**Refinement strategies:**

| Original Issue | Refined Approach |
|----------------|------------------|
| Task too broad | Break into subtasks - focus on ONE specific fix |
| Missing context | Add specific file paths where the issue is |
| Scope creep | Limit to single file, single function |
| Dependency issue | Fix dependency first, then continue |
| "Start fresh" urge | NO - build on existing commits |

**Example:**
```
Session: Refactor Database Layer
State: TIMEOUT
Original intent: Refactor entire database layer for better modularity...

⚠️ IMPORTANT RULES:
- Do NOT start fresh or dump previous changes
- Do NOT close existing PRs - work on them until merged
- ALWAYS push to existing PR branch
- This branch already has 47 commits of work. Build on top of it.

Instead of rewriting:
- Identify what specifically failed
- Make surgical fixes to the existing code
- Preserve working functionality even if imperfect
- Incrementally improve, don't replace

Use these git commands to continue:
1. git fetch origin
2. git checkout bolt/refactor-db-layer
3. git log --oneline -5  # Review recent commits
4. Make surgical fix to the specific file
5. git add fixed_file.py
6. git commit -m "fix: {specific fix}"
7. Run verification: pytest --ignore=tasks --ignore=workspace
8. git push origin bolt/refactor-db-layer

Remember: 
- Incremental improvement > wholesale rewrite
- NEVER close PRs - work on them until merged
```

---

## Response Generation Guidelines

### Include in Every Response

1. **Context reminder** - What was the original intent?
2. **Current state** - What happened so far?
3. **Clear ask** - What do you want Jules to do?
4. **Constraints** - Any limitations or focus areas?

### Avoid

- Vague instructions ("fix bugs" → "fix auth timeout bug in login.py")
- Missing context ("continue" → "continue with rate limiting in api.py")
- Scope creep ("and also add tests" → separate session)

### Token Economy

- Keep responses under 500 tokens
- Reference existing code by path, not description
- Use bullet points for multi-step requests

---

## Quick Reference

| State | Action | Key Template |
|-------|--------|--------------|
| AWAITING_PLAN_APPROVAL | Approve | "Proceed with the plan. Focus on X." |
| IN_PROGRESS_STUCK | Nudge | "Status update? Blockers?" |
| COMPLETED_NO_CHANGES | Ask why | "What happened? Unclear requirements?" |
| COMPLETED_NO_PR | Request PR | "Push changes and create PR titled X" |
| COMPLETED_PR_STALE | Merge | "PR ready. Reviewing X, Y files." |
| FAILED/TIMEOUT | Restart | "New session with refined scope: X" |

---

### 7. HIGH_DELETION_RATIO

**When:** Session completed but PR has >40% deletions (even if changes seem legitimate).

**Why:** Even legitimate optimizations often delete functionality users depend on. High deletion ratios indicate the approach may be too aggressive. CRITICAL: Do NOT encourage Jules to "start over" - guide incremental restoration. NEVER create new PRs.

**Context-aware template:**
```
Session: {title}
PR: {pr_url}
Deletion ratio: {deletions_pct}% ({del_count} deletions / {add_count} additions)

⚠️ IMPORTANT: 
- Do NOT rewrite from scratch. If you need to make changes, do surgical improvements
- Do NOT close existing PRs - work on them until merged
- Restore removed functionality incrementally, NOT wholesale rewrite
- Push changes to existing PR, don't create new ones

Even if the optimization seems justified, aggressive deletion often:
- Removes functionality users depend on
- Creates merge conflicts that are hard to resolve
- Makes thorough review difficult

Before merging, can you:
1. Document exactly what functionality was removed?
2. Confirm equivalent functionality exists elsewhere in the codebase?
3. If functionality was lost, restore incrementally using git:
   - git checkout {branch}
   - git log --oneline -20  # Find what was removed
   - Restore specific functionality: git checkout {commit} -- {file}
4. Consider if this could be split into smaller, more reviewable chunks?

Use surgical git commands to restore/fix:
1. git fetch origin
2. git checkout {existing_branch}
3. git diff HEAD~{n} --stat  # See what changed recently
4. git restore --source=HEAD~{n} {file_with_lost_functionality}
5. git add {restored_file}
6. git commit -m "restore: {functionality}"
7. pytest --ignore=tasks --ignore=workspace
8. git push origin {existing_branch}

Focus on incremental improvement, NOT replacement.
NEVER close or abandon a PR.
```

**Example:**
```
Session: Optimize Database Search
PR: https://github.com/.../pull/428
Deletion ratio: 63% (308 deletions / 178 additions)

⚠️ IMPORTANT: 
- Do NOT rewrite from scratch. If you need to make changes, do surgical improvements
- Do NOT close existing PRs - work on them until merged
- Restore removed functionality incrementally, NOT wholesale rewrite
- Push changes to existing PR, don't create new ones

Use git to restore lost functionality:
1. git fetch origin
2. git checkout bolt-optimize-search
3. git diff HEAD~10 --stat  # See what was removed
4. git restore --source=HEAD~10 src/core/search.py  # Restore lost file
5. git add src/core/search.py
6. git commit -m "restore: search functionality"
7. pytest --ignore=tasks --ignore=workspace
8. git push origin bolt-optimize-search

Focus on incremental improvement, NOT replacement.
NEVER close or abandon a PR.
```

---

### 8. EXCESSIVE_FILE_CHANGES

**When:** Changes span >30 files in a single PR - indicates scope creep.

**Why:** Large PRs are harder to review thoroughly, have higher regression risk, and often get delayed or rejected.

**Context-aware template:**
```
Session: {title}
Files changed: {file_count}

Follow-up response:
"This PR touches {file_count} files - that's a large change surface.
Large PRs:
- Are harder to review thoroughly
- Have higher chance of introducing regressions
- Often get delayed or rejected by reviewers

Consider:
1. Can this be split into focused PRs (e.g., optimization only, no refactoring)?
2. Can changes be limited to the specific area mentioned in the prompt?
3. Can refactoring or style changes be deferred to a separate PR?

Push a minimal version first to unblock the core request, then follow up with improvements."
```

**Example:**
```
Session: Refactor Database Layer
Files changed: 47

Follow-up response:
"This PR touches 47 files - that's a large change surface.
Large PRs:
- Are harder to review thoroughly
- Have higher chance of introducing regressions
- Often get delayed or rejected by reviewers

Consider:
1. Can this be split into focused PRs (e.g., optimization only, no refactoring)?
2. Can changes be limited to the specific area mentioned in the prompt?
3. Can refactoring or style changes be deferred to a separate PR?

Push a minimal version first to unblock the core request, then follow up with improvements."
```

---

### 9. UNRESOLVED_CONFLICTS

**When:** Session shows COMPLETED but PR has merge conflicts.

**Why:** COMPLETED should mean "ready to merge", not just "done with my todo list". A session isn't complete until the PR is mergeable. CRITICAL: Don't encourage Jules to "reset" - resolve conflicts on existing work. NEVER close PRs.

**Context-aware template:**
```
Session: {title}
Session state: COMPLETED
PR status: {merge_state} (mergeable: {is_mergeable})

⚠️ IMPORTANT RULES:
- Do NOT reset or restart. Resolve conflicts on the EXISTING branch.
- Do NOT close existing PRs - work on them until merged
- This branch has {commit_count} commits of work - preserve them

COMPLETED should mean 'ready to merge', not just 'done with my todo list'.

Please resolve using these git commands:
1. git fetch origin
2. git checkout {branch}
3. git merge origin/{base_branch}
4. Resolve conflicts manually - prefer keeping BOTH sets of changes where possible
   - Do NOT use git checkout --theirs or git checkout --ours wholesale - that loses work
   - Edit conflicted files to keep both changes
5. git add resolved_files
6. git commit
7. Run verification: pytest --ignore=tasks --ignore=workspace
8. git push origin {branch}

A session isn't complete until the PR is mergeable. Resolve the conflicts, don't restart.
NEVER close or abandon a PR - work on it until merged.
```

**Example:**
```
Session: Fix CI Failures
Session state: COMPLETED
PR status: DIRTY (mergeable: CONFLICTING)

⚠️ IMPORTANT RULES:
- Do NOT reset or restart. Resolve conflicts on the EXISTING branch.
- Do NOT close existing PRs - work on them until merged
- This branch has 23 commits of work - preserve them

Please resolve using these git commands:
1. git fetch origin
2. git checkout bolt/fix-ci-failures
3. git merge origin/main
4. Resolve conflicts manually - keep both changes
   - Do NOT use git checkout --theirs or --ours
5. git add resolved_files
6. git commit
7. Run verification: pytest --ignore=tasks --ignore=workspace
8. git push origin bolt/fix-ci-failures

NEVER close or abandon a PR - work on it until merged.
```

---

### 10. NEW_SESSION_CONSTRAINTS

**When:** Creating a new session - inject constraints into the prompt.

**Why:** Prevent problems before they start by setting clear boundaries on change scope. CRITICAL: Prevent "start from scratch" behavior and ensure existing PRs are used. NEVER create or close PRs.

**Prompt injection template:**
```
MANDATORY CONSTRAINTS for this session:

1. **INCREMENTAL IMPROVEMENT**: You are improving existing code, NOT replacing it.
   - NEVER dump all previous changes and start fresh
   - ALWAYS build on top of existing work on this branch
   - If asked to "refactor", do surgical changes, NOT wholesale rewrites
   - Preserve working functionality even if it's not elegant
   - Use: git checkout {existing_branch} && git pull origin {existing_branch}

2. **EXISTING PR ONLY**: 
   - NEVER create new PRs - push to existing PR branch
   - NEVER close existing PRs - work on them until merged
   - NEVER use: git push -u origin (creates new branch/PR)
   - ALWAYS use: git push origin {existing_branch}
   - If no existing PR matches, ask for clarification

3. **Change Limit**: Maximum 10 files changed per commit
4. **Deletion Guard**: If deletions > 30% of total changes:
   - Document WHY each line is being removed in commit message
   - Confirm equivalent functionality exists elsewhere
   - Consider if the change is worth the churn
5. **Atomic Focus**: Never refactor AND optimize in the same PR
6. **Verification**: Run pytest --ignore=tasks --ignore=workspace after each change
7. **Merge Check**: Verify PR is mergeable before marking session complete

GIT WORKFLOW - ALWAYS USE THESE COMMANDS:
1. git fetch origin
2. git checkout {existing_branch_with_open_PR}
3. git pull origin {existing_branch_with_open_PR}
4. # Make surgical changes
5. git add {specific_file.py}
6. git commit -m "fix: {specific fix description}"
7. pytest --ignore=tasks --ignore=workspace
8. git push origin {existing_branch_with_open_PR}

IF YOU FIND YOURSELF WANTING TO DELETE AND REWRITE:
- STOP
- Instead of rewriting, make surgical improvements
- If code works but isn't pretty, leave it unless there's a specific bug to fix
- Incrementally improve, don't replace wholesale

Remember: 
- Small, focused PRs are more likely to be reviewed and merged quickly
- Your goal is incremental improvement, not perfection
- If it works, don't break it just to make it "cleaner"
- ALWAYS work on existing PRs - don't create new ones
- NEVER close or abandon a PR
```

---

### 11. POST_MERGE_AUDIT

**When:** After a PR is merged - verify no regressions.

**Why:** Catch issues before they affect production.

**Audit response:**
```
PR #{pr_number} merged successfully.

Post-merge audit:
- [ ] Check CI passes on {base_branch}
- [ ] Verify no new broken tests
- [ ] Confirm expected functionality still works

If issues found, create a follow-up task rather than trying to fix in this PR.
```

---

## Extended Quick Reference

| State | Action | Key Template |
|-------|--------|--------------|
| AWAITING_PLAN_APPROVAL | Approve | "Proceed with the plan. Focus on X." |
| IN_PROGRESS_STUCK | Nudge | "Status update? Blockers?" |
| COMPLETED_NO_CHANGES | Ask why | "What happened? Unclear requirements?" |
| COMPLETED_NO_PR | Request push | "Push to existing PR, don't create new" |
| COMPLETED_PR_STALE | Merge | "PR ready. Reviewing X, Y files." |
| FAILED/TIMEOUT | Restart | "Surgical fix on existing branch, don't restart" |
| HIGH_DELETION_RATIO | Question | "63% del - restore incrementally, don't rewrite" |
| EXCESSIVE_FILE_CHANGES | Split | "47 files - consider splitting?" |
| UNRESOLVED_CONFLICTS | Resolve | "Complete means mergeable - resolve on existing branch" |
| NEW_SESSION_CONSTRAINTS | Inject | "Existing PR only, surgical changes, git workflow" |

---

## Core Rules (ALWAYS REMEMBER)

1. **INCREMENTAL IMPROVEMENT** - Build on existing work, don't replace
2. **EXISTING PR ONLY** - Never create new PRs, always push to existing
3. **NEVER CLOSE PRs** - Work on them until merged
4. **SURGICAL CHANGES** - Max 10 files per commit
5. **DELETION THRESHOLD** - Question if deletions > 30%
6. **VERIFY BEFORE PUSH** - Run pytest --ignore=tasks --ignore=workspace

---

## Git Commands (USE THESE)

```bash
# Start working on existing branch
git fetch origin
git checkout {existing_branch_with_open_PR}
git pull origin {existing_branch}

# Make changes
git add {specific_file.py}
git commit -m "fix: {specific fix}"

# Verify
pytest --ignore=tasks --ignore=workspace

# Push (to existing branch only!)
git push origin {existing_branch_with_open_PR}

# If conflicts
git fetch origin
git merge origin/{base_branch}
# Resolve manually, keeping both changes
git add .
git commit
git push origin {existing_branch}
```
