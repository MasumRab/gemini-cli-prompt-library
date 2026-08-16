import json

with open("docs/forensics/session_priority_batch_plan_2026-08-14.json") as f:
    plan = json.load(f)

md = []
md.append("# Session Follow-up Message Drafts — 2026-08-14")
md.append("")
md.append(
    "**Analysis thread:** [T-019fd887-be34-7014-9cb1-e24012ad3aad](https://ampcode.com/threads/T-019fd887-be34-7014-9cb1-e24012ad3aad)"
)
md.append("")
md.append(
    "These are **drafts only**. Do not send without review. Each draft is reconstructed"
)
md.append("from the session's full conversation history, plan, and current PR state.")
md.append("")
md.append("## P0: AWAITING_USER_FEEDBACK Sessions (7 drafts)")
md.append("")

drafts = {
    "7404018986702295062": {
        "title": "GitHub and GH CLI Sandbox Access Issue",
        "repo": "MasumRab/kaggle-notebooks-analysis",
        "pr": "102",
        "draft": """Your plan was approved to fix the broken merge state on PR #102 by resetting the branch and re-applying the 3 specific files (tools/kaggle_forensics/setup.py, tools/kaggle_forensics/tests/conftest.py, and tools/kaggle_forensics/tests/validators/test_guards.py). You confirmed you have git and gh access in this sandbox.

PR #102 is still open and needs this fix. Please proceed with executing your approved plan now:
1. Check out the PR #102 branch
2. Reset to a clean state against main
3. Re-apply only the 3 specific files
4. Force-push to fix the broken merge state

Do not create a new PR. Update the existing PR #102.""",
    },
    "14844012706076784544": {
        "title": "Fix Unclosed File Descriptor in scripts/inject_data_loader.py",
        "repo": "MasumRab/kaggle-notebooks-analysis",
        "pr": None,
        "draft": """Your plan was approved and you applied patches to fix the unclosed file descriptor in scripts/inject_data_loader.py (changing json.load(open(nb_path)) to use a context manager). Pre-commit checks were run. However, no pull request was created.

Please push your changes as a PR now:
1. Verify your changes are still on your branch
2. Push the branch to the remote
3. Create a PR with a clear title and description
4. Reply with the PR URL

If you encounter any issues pushing, explain specifically what blocked you.""",
    },
    "5824169116591251349": {
        "title": "Fix failing CI checks in MasumRab/EmailIntelligence",
        "repo": "MasumRab/EmailIntelligence",
        "pr": "647",
        "draft": """You were fixing CI test failures for PR #647, specifically in SmartFilterManager and _EmailContext. You restored setup/launch.py and setup/services.py from origin/main to remove merge conflict markers. You then encountered a sqlite3.OperationalError when testing filter API because test_filter_api.py does not pass :memory: as db_path.

Important update: PR #647 has been CLOSED (not merged). The CI fix work may still be needed, but it will require a new PR.

Please assess:
1. Is the CI fix still relevant? Check if the same tests are still failing on main.
2. If yes, create a new branch from main, apply your fix (including the db_path fix for tests), and create a new PR.
3. If the fix is no longer needed, explain why.

Do not attempt to reopen PR #647. Create a fresh PR if the fix is still needed.""",
    },
    "11760979078520753675": {
        "title": "Fix failing CI checks for Pull Requests in MasumRab/EmailIntelligence",
        "repo": "MasumRab/EmailIntelligence",
        "pr": "610",
        "draft": """You were fixing syntax errors in setup/launch.py caused by merge conflict markers. When you restored the file from origin/main, it contained <<<<<<< HEAD markers causing SyntaxError. Removing markers with a script left improperly merged logic.

Important update: PR #610 has been CLOSED (not merged). The merge conflict markers you found in origin/main suggest the base branch itself had issues at the time.

Please assess:
1. Check if setup/launch.py on the current main branch still has merge conflict markers.
2. If the base branch is now clean, the original CI fix may no longer be needed.
3. If CI is still failing, create a new branch from the current main and apply only the necessary fixes.

Do not attempt to reopen PR #610.""",
    },
    "5852715954766644480": {
        "title": "Fix failing CI checks in EmailIntelligence",
        "repo": "MasumRab/EmailIntelligence",
        "pr": "610",
        "draft": """You were fixing CI test failures for PR #610, including an AttributeError in PathValidator (renamed validate_database_path to validate_and_resolve_db_path) and persistent Git merge conflict markers in setup files.

Important update: PR #610 has been CLOSED (not merged). Another session (11760979078520753675) was also working on this PR and found that origin/main itself had merge conflict markers.

Please assess:
1. Check if the current main branch is now clean (no merge conflict markers).
2. If the PathValidator rename is still needed, create a new branch from current main and apply just that fix.
3. If the CI is now passing on main, no further action is needed — explain what you find.

Do not attempt to reopen PR #610.""",
    },
    "6052746651524889133": {
        "title": "Sentinel: Autonomous Security Hardening Agent",
        "repo": "MasumRab/EmailIntelligence",
        "pr": None,
        "draft": """Your plan was approved and you made security hardening changes: replacing datetime.utcnow() with datetime.now(timezone.utc) in src/context_control/models.py, src/main.py health check endpoint, and other locations. Ruff checks passed successfully. However, test_basic_validation.py failed due to a missing pyproject.toml — this is a configuration/environment issue, not a code issue.

Please push your changes as a PR now:
1. The test failure is due to missing pyproject.toml configuration, not your code changes.
2. Verify your changes are on your branch
3. Push the branch and create a PR
4. Include in the PR description: "Security hardening: replaced deprecated datetime.utcnow() with timezone-aware datetime.now(timezone.utc). Ruff checks pass. test_basic_validation.py failure is a pre-existing config issue (missing pyproject.toml)."
5. Reply with the PR URL

Do not block on the test failure — it is an environment config issue, not a code issue.""",
    },
    "647582418723672708": {
        "title": "Fix CI failures for PR 589",
        "repo": "MasumRab/EmailIntelligence",
        "pr": "589",
        "draft": """You were fixing CI failures for PR #589. You successfully removed merge conflict markers from src/ and setup/ files. However, you identified that src/core/auth.py has a NameError: name 'logging' is not defined because the import logging statement was removed during conflict resolution.

PR #589 is still OPEN and needs this fix. Please:
1. Add `import logging` at the top of src/core/auth.py (it was accidentally removed during conflict resolution)
2. Run `python -c "import src.core.auth"` to verify the import works
3. Run pytest on the affected tests
4. Push the fix to the PR #589 branch
5. Confirm the CI checks pass

This is a simple one-line fix. Do not create a new PR — push to the existing PR #589.""",
    },
}

# P0 drafts
for sid, d in drafts.items():
    cls = plan["nonterminal_classification"][sid]
    md.append(f"### Draft for {sid}")
    md.append(f"")
    md.append(f"**Title:** {d['title']}")
    md.append(f"**Repo:** {d['repo']}")
    md.append(f"**PR:** {'#'+d['pr'] if d['pr'] else 'none'}")
    md.append(f"**Action type:** `{cls['recommended_action']}`")
    md.append(f"")
    md.append("```")
    md.append(d["draft"].strip())
    md.append("```")
    md.append("")

# P1 drafts
md.append("## P1: IN_PROGRESS Sessions (2 drafts — monitor first, send if stalled)")
md.append("")

p1_drafts = {
    "18254541687978082373": {
        "title": "Pre-compile Regex Patterns in ANCHOR_PATTERNS",
        "draft": """Your task was to pre-compile regex patterns in ANCHOR_PATTERNS. You confirmed that this work was already merged via PR #22 (⚡ Optimize regex patterns by pre-compilation).

PR #22 has been verified as MERGED. The task is complete. No further action is needed from this session. You do not need to create a new PR — the work is already in main.""",
    },
    "17065719860896443446": {
        "title": "PRIORITY PR REPAIR: #300",
        "draft": """You were working on PR #300 (⚡ Bolt: Optimize ContextIsolator regex matching) and made changes to fix ContextIsolator regex compilation in src/context_control/isolation.py. Your last activity was on 2026-04-13.

PR #300 is still OPEN. Please:
1. Check if your changes are still on the branch
2. Verify the regex compilation fix is correct
3. Run relevant tests
4. Push any remaining changes to the PR #300 branch
5. Reply with the current status

If you encounter merge conflicts with main, resolve them carefully. Do not create a new PR — update the existing PR #300.""",
    },
}

for sid, d in p1_drafts.items():
    cls = plan["nonterminal_classification"][sid]
    md.append(f"### Draft for {sid} (send only if no state change in 24h)")
    md.append(f"")
    md.append(f"**Title:** {d['title']}")
    md.append(f"**Repo:** {cls['repo']}")
    md.append(f"**PR:** {'#'+cls['pr'] if cls['pr'] else 'none'} ({cls['pr_state']})")
    md.append(f"**Action type:** `{cls['recommended_action']}`")
    md.append(f"")
    md.append("```")
    md.append(d["draft"].strip())
    md.append("```")
    md.append("")

# Batch template for failed sessions
md.append("## Failed Session Batch Message Template")
md.append("")
md.append("For each failed session, use this template with session-specific details:")
md.append("")
md.append("```")
md.append(
    """Your session was previously marked as FAILED. Before retrying, please check:

1. Are your previous changes still on your branch? Run: git log -1 --format='%H %s'
2. Is there an existing PR for this work? Check: gh pr list --head $(git branch --show-current)
3. If you have uncommitted or unpushed work, push it now and create/update a PR.
4. If you need to start fresh, create a new branch from main and reapply your changes.

Context from your previous work:
- Original task: [INSERT SESSION TITLE/PROMPT SUMMARY]
- PR target: [INSERT PR NUMBER OR "no PR created"]
- Last activity: [INSERT LAST AGENT ACTION SUMMARY]

Important:
- Do NOT create a new PR if one already exists for this task. Update the existing PR.
- Do NOT close or abandon any existing PRs. Migrate and update them.
- If the task is no longer relevant (PR was merged or closed), explain why and what you recommend.

Please take action and reply with the result."""
)
md.append("```")
md.append("")

md.append("## Notes on Message Construction")
md.append("")
md.append("Each message is constructed with:")
md.append("")
md.append("1. **Current PR state** — verified via GitHub API before messaging")
md.append("2. **Last agent action** — extracted from activity history")
md.append(
    "3. **Evolved task intent** — reconstructed from full conversation, not just the original prompt"
)
md.append("4. **Specific next action** — one concrete step, not a vague 'retry'")
md.append(
    "5. **PR preservation** — explicit instruction not to close/abandon existing PRs"
)
md.append("6. **Scope boundaries** — clear limits on what to touch")
md.append("")
md.append("## Delivery Tracking")
md.append("")
md.append("After sending each message, record in the intervention ledger:")
md.append("")
md.append("| Field | Description |")
md.append("|-------|-------------|")
md.append("| session_id | Jules session ID |")
md.append("| message_sent_at | Timestamp |")
md.append("| pre_state | Session state before message |")
md.append("| message_type | reply_to_proceed / reply_to_push_pr / etc. |")
md.append("| pr_state_at_send | open / closed / merged / none |")
md.append("| post_state_24h | State 24 hours after message |")
md.append("| agent_responded | true/false |")
md.append(
    "| response_type | completed / pr_created / pr_updated / no_response / error |"
)
md.append("| notes | Any relevant context |")
md.append("")

with open("docs/forensics/SESSION_FOLLOWUP_MESSAGE_DRAFTS_2026-08-14.md", "w") as f:
    f.write("\n".join(md))

print(
    f"Drafts saved: {len(md)} lines, {len(drafts)} P0 drafts, {len(p1_drafts)} P1 drafts"
)
