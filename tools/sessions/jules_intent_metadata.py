#!/usr/bin/env python3
"""Extract generalized intent metadata for Jules sessions.

For ANY set of sessions (filtered by state / repo / date window / explicit id
list / pending), emit minimal intent metadata as JSON, JSONL, or a table.

Usage:
    uv run python3 -m tools.sessions.jules_intent_metadata --limit 5
    uv run python3 -m tools.sessions.jules_intent_metadata --state AWAITING_USER_FEEDBACK --limit 5
    uv run python3 -m tools.sessions.jules_intent_metadata --repo EmailIntelligence --pending --limit 5
    uv run python3 -m tools.sessions.jules_intent_metadata --sessions 1122791329330329850 --jsonl
    uv run python3 -m tools.sessions.jules_intent_metadata --all --jsonl

By default (``--limit 20`` without ``--all``) the scan is capped at 500
sessions so casual queries stay fast. ``--all`` removes the scan cap AND the
row limit, enabling full-account intent dumps.
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional

from tools.api.jules_api_client import JulesAPIClient

# Known non-action states — every other state (including unknown/future API
# states) is surfaced as "pending" so edge cases stay visible.
NO_ACTION_STATES = {"COMPLETED", "QUEUED", "PLANNING", "STATE_UNSPECIFIED"}

PR_URL_RE = re.compile(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)")

# Boilerplate/persona line patterns stripped when distilling intent.
BOILERPLATE_LINE_RES = [
    re.compile(r'^You are "[^"]+"', re.IGNORECASE),
    re.compile(r"^##\s+code review request\b", re.IGNORECASE),
    re.compile(r"^(?:name|description|schedule|prompt)\s*[=:]", re.IGNORECASE),
    re.compile(r"^repository\s*:", re.IGNORECASE),
    re.compile(r"^title\s*:", re.IGNORECASE),
]

SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")


def _all_pr_urls(session: Dict[str, Any]) -> List[str]:
    """Collect PR urls from both ``outputs[].pullRequest.url`` and flattened ``pr_urls``."""
    urls: List[str] = []
    for output in session.get("outputs") or []:
        url = (output.get("pullRequest") or {}).get("url")
        if url:
            urls.append(url)
    urls.extend(session.get("pr_urls") or [])
    return urls


def extract_repo(session: Dict[str, Any]) -> Optional[str]:
    """Return the owner/repo for a session, or None.

    Priority: ``sourceContext.source`` (``sources/github/...``) → any PR url in
    outputs/pr_urls → ``sourceContext.githubRepoContext.repoName``.
    """
    sc = session.get("sourceContext") or {}
    source = sc.get("source") or ""
    if source.startswith("sources/github/"):
        repo = source[len("sources/github/"):].strip()
        return repo or None
    for url in _all_pr_urls(session):
        m = PR_URL_RE.search(url)
        if m:
            return f"{m.group(1)}/{m.group(2)}"
    repo_name = (sc.get("githubRepoContext") or {}).get("repoName")
    if repo_name:
        return repo_name
    return None


def extract_pr_refs(session: Dict[str, Any]) -> List[str]:
    """Return deduplicated short PR refs like ``"EmailIntelligence#792"``.

    Gathers urls from ``outputs[].pullRequest.url`` AND flattened ``pr_urls``,
    normalizes each to ``<repo-basename>#<number>``, preserving first-seen order.
    """
    refs: List[str] = []
    seen = set()
    for url in _all_pr_urls(session):
        m = PR_URL_RE.search(url)
        if not m:
            continue
        ref = f"{m.group(2)}#{m.group(3)}"
        if ref not in seen:
            seen.add(ref)
            refs.append(ref)
    return refs


def _strip_boilerplate(text: str) -> str:
    """Remove persona/boilerplate lines, returning remaining text joined by spaces."""
    kept: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if any(pattern.match(line) for pattern in BOILERPLATE_LINE_RES):
            continue
        kept.append(line)
    return " ".join(kept).strip()


def _first_sentences(text: str, max_sentences: int = 2) -> str:
    """Return the first 1-2 sentences of text as a single string."""
    parts = [p.strip() for p in SENTENCE_BOUNDARY_RE.split(text) if p.strip()]
    return " ".join(parts[:max_sentences])


def distill_intent(session: Dict[str, Any], max_chars: int = 200) -> str:
    """Distill a session's intent from its prompt (or title fallback).

    Strips persona/boilerplate lines, keeps the first 1-2 meaningful sentences,
    and truncates to ``max_chars``. Falls back to the title if nothing remains.
    """
    prompt = (session.get("prompt") or "").strip()
    title = (session.get("title") or "").strip()
    source = prompt or title
    if not source:
        return ""
    stripped = _strip_boilerplate(source)
    if not stripped:
        return title
    kept = _first_sentences(stripped)
    kept = kept.rstrip()
    if len(kept) > max_chars:
        kept = kept[: max_chars - 1].rstrip() + "…"
    if not kept:
        return title
    return kept


def build_intent_metadata(session: Dict[str, Any]) -> Dict[str, Any]:
    """Build the canonical intent-metadata dict for a session."""
    session_id = (session.get("id") or session.get("name") or "").replace("sessions/", "")
    sc = session.get("sourceContext") or {}
    prompt = session.get("prompt") or ""
    return {
        "id": session_id,
        "state": session.get("state", "UNKNOWN"),
        "title": session.get("title") or "",
        "createTime": session.get("createTime") or "",
        "updateTime": session.get("updateTime") or "",
        "repo": extract_repo(session),
        "startingBranch": (sc.get("githubRepoContext") or {}).get("startingBranch"),
        "pr_refs": extract_pr_refs(session),
        "intent": distill_intent(session),
        "prompt_tail": prompt[:400],
    }


def _in_date_window(
    ts: Optional[str], after: Optional[str], before: Optional[str]
) -> bool:
    """Check an ISO timestamp against inclusive YYYY-MM-DD bounds.

    Uses the date prefix of the timestamp (``ts[:10]``) for a string comparison,
    so ``on/before`` and ``on/after`` boundaries are exact. Missing timestamps
    are excluded when any bound is set.
    """
    if after is None and before is None:
        return True
    if not ts:
        return False
    day = ts[:10]
    if after and day < after:
        return False
    if before and day > before:
        return False
    return True


def filter_sessions(sessions: List[Dict[str, Any]], args) -> List[Dict[str, Any]]:
    """Apply all client-side filters (state/exclude/pending/active/repo/dates)."""
    include = [s.upper() for s in (args.state or [])]
    exclude = [s.upper() for s in (args.exclude_state or [])]
    repo_sub = (args.repo or "").lower()
    result = []
    for session in sessions:
        state = (session.get("state") or "UNKNOWN").upper()
        if include and state not in include:
            continue
        if exclude and state in exclude:
            continue
        if args.pending and state in NO_ACTION_STATES:
            continue
        if args.active_only and state == "COMPLETED":
            continue
        if repo_sub:
            repo = extract_repo(session) or ""
            if repo_sub not in repo.lower():
                continue
        if not _in_date_window(session.get("createTime"), args.created_after, args.created_before):
            continue
        if not _in_date_window(session.get("updateTime"), args.updated_after, args.updated_before):
            continue
        result.append(session)
    return result


def _create_time_sort_key(session: Dict[str, Any]) -> tuple:
    ts = session.get("createTime") or ""
    return (ts == "", ts)


def main():
    parser = argparse.ArgumentParser(description="Extract intent metadata for Jules sessions")
    parser.add_argument(
        "--state", nargs="+", metavar="STATE",
        help="Only include these states (case-insensitive, e.g. --state FAILED AWAITING_USER_FEEDBACK)"
    )
    parser.add_argument(
        "--exclude-state", nargs="+", metavar="STATE",
        help="Exclude these states (case-insensitive, e.g. --exclude-state COMPLETED QUEUED)"
    )
    parser.add_argument(
        "--pending", action="store_true",
        help="Only sessions likely needing attention (state not in {COMPLETED, QUEUED, PLANNING, STATE_UNSPECIFIED}; "
             "unknown/future states are surfaced)"
    )
    parser.add_argument("--active-only", action="store_true", help="Exclude COMPLETED sessions")
    parser.add_argument(
        "--repo", metavar="REPO",
        help="Only sessions whose repo matches this substring (case-insensitive; matches 'emailintelligence' "
             "or 'MasumRab/EmailIntelligence')"
    )
    parser.add_argument(
        "--created-after", metavar="YYYY-MM-DD",
        help="Include sessions created on/after this date"
    )
    parser.add_argument(
        "--created-before", metavar="YYYY-MM-DD",
        help="Include sessions created on/before this date"
    )
    parser.add_argument(
        "--updated-after", metavar="YYYY-MM-DD",
        help="Include sessions updated on/after this date"
    )
    parser.add_argument(
        "--updated-before", metavar="YYYY-MM-DD",
        help="Include sessions updated on/before this date"
    )
    parser.add_argument(
        "--sessions", nargs="*", metavar="ID",
        help="Explicit session ids (resolved individually via get_session; skips the full scan; --limit is ignored)"
    )
    parser.add_argument(
        "--limit", type=int, default=20,
        help="Max rows to output (default 20; ignored when --sessions given; use --all for a full scan)"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Scan the ENTIRE account (max_results=None) and output every matching session — required for "
             "full-account intent dumps. Without --all the scan is capped at 500 sessions (fast) and rows "
             "are capped at --limit."
    )
    parser.add_argument("--json", action="store_true", help="Output as a pretty JSON array")
    parser.add_argument("--jsonl", action="store_true", help="Output as JSON Lines (one object per line)")
    args = parser.parse_args()

    client = JulesAPIClient()

    if args.sessions:
        sessions = [client.get_session(sid) for sid in args.sessions]
    else:
        scan_limit = None if args.all else 500
        sessions = list(client.list_sessions(page_size=50, max_results=scan_limit))

    filtered = filter_sessions(sessions, args)
    filtered.sort(key=_create_time_sort_key)

    rows = [build_intent_metadata(s) for s in filtered]

    if not args.sessions and not args.all and args.limit:
        rows = rows[: args.limit]

    if args.json:
        try:
            print(json.dumps(rows, indent=2))
        except BrokenPipeError:
            pass
        return

    if args.jsonl:
        try:
            for row in rows:
                print(json.dumps(row))
        except BrokenPipeError:
            pass
        return

    if not rows:
        print("No matching sessions found.")
        return

    intent_width = 90
    header = f"{'ID':<22} | {'State':<25} | {'Repo':<32} | Intent"
    print(header)
    print("-" * len(header))
    for row in rows:
        intent = row["intent"] or ""
        shown = intent if len(intent) <= intent_width else intent[: intent_width - 1].rstrip() + "…"
        repo = row["repo"] or ""
        print(
            f"{row['id']:<22} | {row['state']:<25} | {repo[:32]:<32} | {shown}"
        )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
