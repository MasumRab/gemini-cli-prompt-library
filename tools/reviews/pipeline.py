"""Shared library for the Jules review-session pipeline.

Consolidates the patterns proven during the 2026-09 108-session audit:

- Session discovery from the local store (title/prompt matching, branch
  extraction from the review-request prompt format)
- Review-content extraction from session chat (agentMessage entries)
- Completeness signals (verdict / summary / AI-prompt block / suggestion
  ratio) used to find reviews that never posted or are malformed
- One-per-PR routing: many sessions may exist per PR; always aggregate
  content from all of them and message ONLY the most recent session
- Quota-aware sending: 429s are real; space sends and back off

All functions are repository-agnostic: pass --repo to filter, or run
across everything in the store.
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_STORE = Path.home() / ".jules" / "store.db"

# Review-request prompts embed the head branch after this marker.
BRANCH_MARKER = "PR head branch:"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ReviewSession:
    session_id: str
    create_time: str
    branch: str
    pr_url: str = ""
    repo: str = ""
    review_messages: list[tuple[str, str]] = field(default_factory=list)
    artifact_count: int = 0

    @property
    def latest_session(self) -> bool:
        return getattr(self, "_is_latest", False)

    def best_review(self) -> tuple[str, str] | None:
        """Most complete review message: (timestamp, body).

        Completeness outranks recency: a short ack after a full review
        must not hide the full review.
        """
        if not self.review_messages:
            return None
        return max(
            self.review_messages,
            key=lambda m: (has_verdict(m[1]), count_findings(m[1]), len(m[1])),
        )


@dataclass
class CompletenessReport:
    session_id: str
    branch: str
    create_time: str
    issues: list[str] = field(default_factory=list)
    artifact_count: int = 0
    posted_to_github: bool | None = None  # filled by caller with gh

    @property
    def ok(self) -> bool:
        return not self.issues


# ---------------------------------------------------------------------------
# Content signals
# ---------------------------------------------------------------------------


def has_verdict(msg: str) -> bool:
    return "[VERDICT]" in msg


def has_summary(msg: str) -> bool:
    return "## Summary" in msg or "## " in msg


def has_ai_prompt(msg: str) -> bool:
    return "Prompt for AI" in msg or "AI prompt" in msg.lower()


def count_findings(msg: str) -> int:
    return msg.count("<!-- FINDING")


def count_suggestions(msg: str) -> int:
    return msg.count("```suggestion")


REVIEW_FILTER = re.compile(
    r"FINDING|Findings|VERDICT|Strengths|Concerns|### |## Summary",
    re.IGNORECASE,
)


def is_review_content(msg: str) -> bool:
    """Heuristic: does this agentMessage contain review content?"""
    return bool(msg) and bool(REVIEW_FILTER.search(msg))


def completeness_issues(msg: str) -> list[str]:
    """Return missing-signal descriptions for a review message."""
    issues: list[str] = []
    if not has_verdict(msg):
        issues.append("no-verdict")
    if not has_summary(msg):
        issues.append("no-summary")
    if not has_ai_prompt(msg):
        issues.append("no-ai-prompt-block")
    findings = count_findings(msg)
    suggestions = count_suggestions(msg)
    if findings > 0 and suggestions < findings:
        issues.append(f"suggestions-missing ({suggestions}/{findings})")
    return issues


# ---------------------------------------------------------------------------
# Store queries
# ---------------------------------------------------------------------------


def _store_conn(store_path: Path = DEFAULT_STORE) -> sqlite3.Connection:
    conn = sqlite3.connect(str(store_path))
    conn.row_factory = sqlite3.Row
    return conn


def discover_review_sessions(
    repo: str | None = None,
    store_path: Path = DEFAULT_STORE,
) -> list[ReviewSession]:
    """Find all code-review sessions in the local store.

    Matches the review-request session title/prompt patterns. Optionally
    filter by repo (store `repo` column or sourceContext embedded in the
    prompt snippet).
    """
    conn = _store_conn(store_path)
    try:
        rows = conn.execute(
            """
            SELECT session_id, create_time, pr_url, prompt_snippet,
                   COALESCE(repo, '') AS repo
            FROM sessions
            WHERE title LIKE '%Code Review%'
               OR prompt_snippet LIKE '%Code Review Request%'
            ORDER BY create_time DESC
            """
        ).fetchall()
    finally:
        conn.close()

    sessions: list[ReviewSession] = []
    for r in rows:
        if (
            repo
            and repo.lower() not in (r["repo"] or "").lower()
            and repo.lower() not in (r["prompt_snippet"] or "").lower()
        ):
            continue
        prompt = r["prompt_snippet"] or ""
        m = re.search(re.escape(BRANCH_MARKER) + r"\s*(\S+)", prompt)
        branch = m.group(1).strip(",") if m else "NO-BRANCH"
        sessions.append(
            ReviewSession(
                session_id=r["session_id"],
                create_time=(r["create_time"] or "")[:19],
                branch=branch,
                pr_url=r["pr_url"] or "",
                repo=r["repo"] or "",
            )
        )
    return sessions


def group_by_branch(sessions: list[ReviewSession]) -> dict[str, list[ReviewSession]]:
    """Group sessions by PR head branch (safe-branch keys preserved)."""
    grouped: dict[str, list[ReviewSession]] = {}
    for s in sessions:
        key = s.branch.replace("/", "_").replace("\\", "_")
        grouped.setdefault(key, []).append(s)
    return grouped


def latest_session_per_branch(
    sessions: list[ReviewSession],
) -> dict[str, ReviewSession]:
    """Map safe-branch key -> most recent session (the one to message)."""
    latest: dict[str, ReviewSession] = {}
    for key, group in group_by_branch(sessions).items():
        latest[key] = max(group, key=lambda s: s.create_time)
    return latest


# ---------------------------------------------------------------------------
# Chat extraction
# ---------------------------------------------------------------------------


def fetch_review_messages(
    api: Any, session: ReviewSession, sleep: float = 1.0
) -> ReviewSession:
    """Populate session.review_messages and artifact_count from the API.

    `api` is a JulesAPIClient (tools.api.jules_api_client).
    """
    review_chunks: list[tuple[str, str]] = []
    artifact_count = 0
    for act in api.list_activities(session.session_id):
        if isinstance(act, str):
            act = json.loads(act)
        am = act.get("agentMessaged", {}).get("agentMessage", "")
        if am and is_review_content(am):
            review_chunks.append((act.get("createTime", ""), am))
        if "artifacts" in act:
            artifact_count += 1
    session.review_messages = review_chunks
    session.artifact_count = artifact_count
    if sleep:
        time.sleep(sleep)
    return session


def extract_verdict(msg: str) -> str:
    """Return the [VERDICT] line from a message, or empty string."""
    for line in msg.split("\n"):
        if "[VERDICT]" in line:
            return line.strip()
    return ""


# ---------------------------------------------------------------------------
# Quota-aware sending
# ---------------------------------------------------------------------------


def send_with_backoff(
    api: Any,
    session_id: str,
    text: str,
    max_retries: int = 3,
    base_wait: float = 30.0,
    inter_send_gap: float = 5.0,
) -> dict[str, Any]:
    """Send a message, retrying on 429 with exponential backoff.

    Jules API 429s are common on batch sends; 30s waits have historically
    been insufficient — use 60s+ on retries. Keeps an inter-send gap so
    consecutive calls do not trip the limiter.
    """
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            result = api.send_message(session_id, text)
            time.sleep(inter_send_gap)
            return result
        except Exception as e:
            last_err = e
            if "429" in str(e) or "rate" in str(e).lower():
                time.sleep(base_wait * (2**attempt))
                continue
            raise
    raise RuntimeError(f"send_message failed after {max_retries} retries: {last_err}")


# ---------------------------------------------------------------------------
# GitHub cross-check
# ---------------------------------------------------------------------------


def jules_comments_on_pr(gh_json: dict[str, Any]) -> list[dict[str, Any]]:
    """Filter PR view JSON for comments authored by google-labs-jules."""
    return [
        c
        for c in gh_json.get("comments", [])
        if (c.get("author") or {}).get("login") == "google-labs-jules"
    ]


def jules_reviews_on_pr(gh_json: dict[str, Any]) -> list[dict[str, Any]]:
    """Filter PR view JSON for reviews authored by google-labs-jules."""
    return [
        r
        for r in gh_json.get("reviews", [])
        if (r.get("author") or {}).get("login") == "google-labs-jules"
    ]
