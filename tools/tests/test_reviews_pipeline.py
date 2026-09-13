"""Tests for the review-session pipeline library and templates."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.reviews.pipeline import (
    ReviewSession,
    completeness_issues,
    count_findings,
    count_suggestions,
    extract_verdict,
    has_verdict,
    is_review_content,
    latest_session_per_branch,
)
from tools.reviews.templates import (
    build_comment_delivery,
    build_fix_authorization,
    build_review_refresh,
    with_protocols,
)

# ---------------------------------------------------------------------------
# Content signals
# ---------------------------------------------------------------------------

def test_has_verdict() -> None:
    assert has_verdict("[VERDICT]: approve")
    assert has_verdict("review...\n[VERDICT]: block\n")
    assert not has_verdict("no verdict here")
    assert not has_verdict("")


def test_count_findings_and_suggestions() -> None:
    msg = "<!-- FINDING 1 -->x<!-- FINDING 2 -->```suggestion\nfix\n```"
    assert count_findings(msg) == 2
    assert count_suggestions(msg) == 1


def test_completeness_issues_full_review() -> None:
    full = "## Summary\n[VERDICT]: approve\nPrompt for AI: ...\n<!-- FINDING 1 -->\n```suggestion\nx\n```"
    assert completeness_issues(full) == []


def test_completeness_issues_missing_signals() -> None:
    thin = "looks fine to me"
    issues = completeness_issues(thin)
    assert "no-verdict" in issues
    assert "no-summary" in issues
    assert "no-ai-prompt-block" in issues


def test_completeness_suggestion_ratio() -> None:
    msg = "## Summary\n[VERDICT]: block\nPrompt for AI: x\n<!-- FINDING 1 --><!-- FINDING 2 -->\n```suggestion\na\n```"
    issues = completeness_issues(msg)
    assert any("suggestions-missing" in i for i in issues)


def test_is_review_content() -> None:
    assert is_review_content("### Finding: broken import")
    assert is_review_content("[VERDICT]: approve")
    assert not is_review_content("ok, will do")
    assert not is_review_content("")


def test_extract_verdict() -> None:
    assert extract_verdict("a\n[VERDICT]: block\nb") == "[VERDICT]: block"
    assert extract_verdict("none") == ""


# ---------------------------------------------------------------------------
# Routing: one-per-PR
# ---------------------------------------------------------------------------

def test_latest_session_per_branch() -> None:
    sessions = [
        ReviewSession("old", "2026-07-01T00:00", "feat/branch"),
        ReviewSession("new", "2026-08-01T00:00", "feat/branch"),
        ReviewSession("other", "2026-09-01T00:00", "other/branch"),
    ]
    latest = latest_session_per_branch(sessions)
    assert latest["feat_branch"].session_id == "new"
    assert latest["other_branch"].session_id == "other"


def test_best_review_prefers_complete_over_recent() -> None:
    s = ReviewSession("s", "2026-01-01", "b")
    s.review_messages = [
        ("2026-01-02", "ack, done"),  # recent but thin
        ("2026-01-01", "## Summary\n[VERDICT]: block\nPrompt for AI: x"),  # older but complete
    ]
    t, body = s.best_review()
    assert "[VERDICT]" in body
    assert t == "2026-01-01"


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def test_with_protocols_includes_all_blocks() -> None:
    msg = with_protocols("do the thing")
    assert "do the thing" in msg
    assert "CODEBASE DRIFT PROTOCOL" in msg
    assert "STALE-PASTE GUARD" in msg
    assert "DISABLED WORKFLOW RULES" in msg
    assert "duplicate definitions" in msg


def test_comment_delivery_bridge_pattern() -> None:
    msg = build_comment_delivery("review body", 570)
    assert "PR COMMENT DELIVERY" in msg
    assert "PR #570" in msg
    assert "---BEGIN FORWARDED REVIEW (posted to PR #570)---" in msg
    assert "review body" in msg
    assert "DRIFT PROTOCOL" in msg


def test_fix_authorization_includes_guard() -> None:
    msg = build_fix_authorization(791, "fix/ci", "1. CRITICAL - broken yaml")
    assert "IMPLEMENTATION AUTHORIZED" in msg
    assert "PR #791" in msg
    assert "1. CRITICAL - broken yaml" in msg
    assert "STALE-PASTE GUARD" in msg
    assert "DISABLED WORKFLOW RULES" in msg


def test_refresh_never_instructs_github_posting() -> None:
    """Regression: refresh template once told sessions to post PR comments,
    which sessions cannot do — it hallucinated into rogue PR creation."""
    msg = build_review_refresh("EmailIntelligence#775", "abc", "def")
    low = msg.lower()
    assert "do not create prs" in low or "do not push to github" in low
    assert "post your review as pr comments" not in low
