"""Message templates for the review-session pipeline.

Single source of truth for the protocol boilerplate that was previously
duplicated (with drift!) across ad-hoc /tmp scripts. Every outbound
message to a stale session MUST include the drift protocol, the
stale-paste guard, and the disabled-workflow rules.

Rules encoded here (learned from regressions, see EDGE_CASES.md):
- Sessions CANNOT see PR comments without @jules mentions — use the
  forwarded-comment bridge pattern for delivery.
- Sessions CANNOT post to GitHub — chat reply with [VERDICT] is the
  review channel.
- Old sessions operate on stale snapshots — always send drift protocol.
- NEVER instruct a session to "post your review as PR comments" (no
  GitHub write access from the VM — such instructions get hallucinated
  into rogue PR creation).
- NEVER enable or edit .github/workflows/*.DISABLED files.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Protocol blocks (append to outbound messages)
# ---------------------------------------------------------------------------

DRIFT_PROTOCOL = """CODEBASE DRIFT PROTOCOL (mandatory before editing — your snapshot may be weeks old):
1. git fetch origin main FIRST — never work from remembered file state
2. For EVERY file you touch: git diff $(git merge-base HEAD origin/main)..origin/main -- <file>
3. Re-read current file versions from disk before editing
4. Resolve conflicts 3-way per hunk (merge-base, ours, theirs); NEVER checkout --ours/--theirs wholesale
5. PROTECT NEWER FILES: files added on main stay intact; if your branch deletes a file main modified, keep it and flag
6. After resolving: git diff origin/main...HEAD must show ONLY intended changes
7. Run lint/tests locally before pushing
8. Push directly to the PR branch — do NOT create a new PR
9. Reply in chat with what you did + [VERDICT] marker"""

STALE_PASTE_GUARD = """STALE-PASTE GUARD: if your fix would change >200 lines in a file not in this PR's original scope, STOP — re-read the current file from disk and apply only the minimal edit."""

DISABLED_WORKFLOW_RULES = """DISABLED WORKFLOW RULES (NON-NEGOTIABLE): never re-enable, rename, delete, or edit .github/workflows/*.DISABLED files. Treat them as frozen — they must match main. If your diff touches any .DISABLED path, that is a regression: revert it immediately."""

DUPLICATE_CHECK = """After resolving: check duplicate definitions (grep -c "^def |^class " <file> > 1 needs investigation) — Python's last-definition-wins silently disables earlier ones."""

ALL_PROTOCOLS = "\n\n".join(  # noqa: FLY002 — join is intentional for block list
    [DRIFT_PROTOCOL, STALE_PASTE_GUARD, DISABLED_WORKFLOW_RULES, DUPLICATE_CHECK]
)


def with_protocols(body: str) -> str:
    """Append all protocol blocks to a message body."""
    return f"{body}\n\n{ALL_PROTOCOLS}"


# ---------------------------------------------------------------------------
# Message builders
# ---------------------------------------------------------------------------


def build_comment_delivery(review_body: str, pr_number: int) -> str:
    """Bridge pattern: forward a PR comment a session cannot see.

    Sessions only receive comments that carry an @jules mention AND were
    posted on a Jules-created PR. Plain comments (human, CodeRabbit,
    Sourcery, recovered-review reposts) are invisible — deliver them via
    sendMessage with the body inline.
    """
    return (
        "PR COMMENT DELIVERY — you cannot see PR comments directly "
        "(comments without @jules mentions are not routed to sessions). "
        f"This message forwards the review comment posted on PR #{pr_number}. "
        "Your snapshot may be STALE — apply the drift protocol below before acting.\n\n"
        f"---BEGIN FORWARDED REVIEW (posted to PR #{pr_number})---\n"
        f"{review_body}\n"
        "---END FORWARDED REVIEW---\n\n"
        "If a finding was already fixed on main or the PR branch, verify and "
        'reply "[VERDICT]: approve" instead of re-fixing.\n\n'
        f"{ALL_PROTOCOLS}"
    )


def build_aggregated_rereview(
    pr_number: int,
    branch: str,
    findings_summary: str,
    current_state: str,
) -> str:
    """Ask the most recent session to re-verify aggregated findings.

    One message per PR — NEVER message N duplicate sessions; aggregate
    content from all of them and send once to the newest.
    """
    return with_protocols(
        f"RE-REVIEW REQUEST — PR #{pr_number} (branch {branch}).\n\n"
        f"Current PR state: {current_state}\n\n"
        f"Aggregated findings from all review sessions for this PR:\n\n"
        f"{findings_summary}\n\n"
        "Please: (1) re-read the current PR head (git fetch origin first — "
        "your snapshot may be stale; NEVER work from remembered file state), "
        "(2) verify each finding's current state against the CURRENT code, "
        "(3) if the PR is CONFLICTING with main, resolve using the drift "
        "protocol, (4) reply in chat with your refreshed [VERDICT] + any new "
        "concerns. You cannot post to GitHub — your chat reply is the review "
        "channel."
    )


def build_fix_authorization(
    pr_number: int,
    branch: str,
    findings: str,
    extra_note: str = "",
) -> str:
    """Authorize a blocking session to implement fixes."""
    note = f"\n{extra_note}\n" if extra_note else "\n"
    return (
        f"IMPLEMENTATION AUTHORIZED — PR #{pr_number} (branch {branch}). "
        "Your block verdict stands; fix these findings now:\n\n"
        f"{findings}\n"
        f"{note}"
        f"{ALL_PROTOCOLS}"
    )


def build_status_check(task: str, next_step: str) -> str:
    """Nudge an awaiting/stalled session with a specific next step."""
    return with_protocols(
        f"Status check: you were mid-work on {task}. "
        f"Please continue: {next_step}, then report the outcome."
    )


def build_conflict_resolution(pr_number: int, failing_checks: str = "") -> str:
    """Conflict + failing-checks message with the full drift protocol."""
    checks = (
        f" Then fix the failing checks: {failing_checks}." if failing_checks else ""
    )
    return with_protocols(
        f"Your PR #{pr_number} is CONFLICTING with current main. "
        "Rebase/merge current main into your branch, resolve conflicts per "
        f"the drift protocol below.{checks} Re-run CI and report when green."
    )


def build_wake_up(
    pr_number: int,
    drift_summary: str,
    task: str,
) -> str:
    """Wake a COMPLETED session whose PR needs adjustment after drift.

    COMPLETED is NOT shutdown — sendMessage works on any state. Old
    sessions have stale snapshots, so spell out what drifted.
    """
    return with_protocols(
        f"Wake-up: your PR #{pr_number} needs adjustment. The base branch "
        "has drifted significantly since your session completed. "
        f"Changes since your work: {drift_summary}\n\n"
        f"Please: {task}\n\n"
        "Apply the drift protocol below to reconcile with the current base."
    )


def build_review_refresh(pr_ref: str, current_head: str, reviewed_head: str) -> str:
    """Ask a review session to refresh a stale review.

    IMPORTANT: never instruct the session to post anything to GitHub —
    sessions have no GitHub write access. The chat reply with [VERDICT]
    is the review channel; the workflow (or orchestrator) posts it.
    """
    return with_protocols(
        f"REVIEW REFRESH REQUEST — {pr_ref}. The PR head has moved: you "
        f"reviewed {reviewed_head}, current head is {current_head}. "
        "Re-review the current head (git fetch first — your snapshot is "
        "stale), verify each prior finding against the CURRENT code, and "
        "reply in chat with your refreshed [VERDICT] + findings. Do NOT "
        "create PRs, do NOT push to GitHub — your chat reply is the review "
        "channel."
    )
