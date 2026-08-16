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
    uv run python3 -m tools.sessions.jules_intent_metadata --classify --state COMPLETED --limit 5
    uv run python3 -m tools.sessions.jules_intent_metadata --stale-days 2 --jsonl
    uv run python3 -m tools.sessions.jules_intent_metadata --anomalies --jsonl
    uv run python3 -m tools.sessions.jules_intent_metadata --all --snapshot /tmp/snapshot.json

By default (``--limit 20`` without ``--all``) the scan is capped at 500
sessions so casual queries stay fast. ``--all`` removes the scan cap AND the
row limit, enabling full-account intent dumps. ``--snapshot`` always performs a
full scan regardless of ``--all``.
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from tools.api.jules_api_client import JulesAPIClient
from tools.sessions.config import NO_ACTION_STATES

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

# --- Rich distillation patterns (adapted from /tmp/opencode/build_intent_metadata.py) ---

FENCE_RE = re.compile(r"```.*?```", re.S)
URL_RE = re.compile(r"https?://[^\s)\]]+")

CODE_REVIEW_REQUEST_RE = re.compile(r"^##\s+Code Review Request\b", re.IGNORECASE)
PRIORITY_PR_TASK_RE = re.compile(r"priority pr (?:task|repair)", re.IGNORECASE)
DESCRIPTION_BLOCK_RE = re.compile(r"description:\s*>\s*\n(.*?)(?=\n\s*</|\Z)", re.S)
GOAL_LINE_RE = re.compile(r"(?im)^\s*(?:goal|objective|purpose)\s*:\s*(.+)$")
PR_REPAIR_TITLE_RE = re.compile(r"(?im)^\s*title\s*:\s*(.+)$")
PR_REPAIR_NUM_RE = re.compile(r"(?:PR REPAIR|PR)\s*:?\s*#?(\d+)", re.I)
BRANCH_TARGET_RE = re.compile(
    r"^You are working on Pull Requests in repository ([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\.\s*$"
)
STRUCT_FIELD_RE = re.compile(r"^\*\*[A-Za-z][A-Za-z ]+:\*\*")

PERSONA_NAME_RE = re.compile(
    r'^You are\s+["“”⚡🟡🐨🎨]*(?:Bolt|Sentinel|Palette|Turbo|Jules|'
    r"developer|agent|engineer|a performance-obsessed|a security-focused|"
    r"an? (?:autonomous|active|performance|security|maintenance))"
)

GENERIC_TEMPLATE_RE = re.compile(
    r"(Select exactly one open pull request targeting|Read the issue description completely|"
    r"Install dependencies first|working on Pull Requests in repository|"
    r"Based on the conversation history|^Working in the repo root)"
)

GENERIC_TITLE_RE = re.compile(
    r"(Agent|Optimizer|Auditor|Cleanup Agent|Maintenance Agent|Performance Optimization|"
    r"^Bolt: Autonomous|^Sentinel: Codebase|^Sentinel: Autonomous|^Bolt: Codebase|"
    r"^Palette:|^Turbo:|^Repository Maintenance|^Autonomous)"
)

GENERIC_TITLE_PREFIX_RE = re.compile(
    r"^(You are|You're|Select exactly one|## Code Review|PRIORITY|Use linear mcp)", re.I
)
GENERIC_TITLE_PREFIX_CLEAN_RE = re.compile(
    r"^(Security Fix|Performance Optimization Task|Code Review)\s*:\s*", re.I
)

# --- Classification patterns (adapted from /tmp/opencode/jules_analyze.py) ---

CODE_REVIEW_RE = re.compile(
    r"code.?review|you are working on pull requests|fix.?failing.?ci|fix.?ci|"
    r"priority pr|^pr #?\d|^PR \d| audit|review (feedback|comment|changes)|"
    r"pull request review|rebase.*pr|pr.*rebase|resolve.*pr|merge conflict",
    re.IGNORECASE,
)

STALE_STATES = ("IN_PROGRESS", "QUEUED")

EMOJI_RE = re.compile(r"[\U0001f300-\U0001faff\u2600-\u27bf\U0001f600-\U0001f64f\ufe0f]")

PAGE_SIZE = 50


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


def _clean_structural(s: str) -> str:
    """Strip markdown/emoji/URL noise from a line or phrase."""
    s = s.strip()
    s = re.sub(r"^#{1,6}\s*", "", s)
    s = re.sub(r"^[-*+]\s+", "", s)
    s = re.sub(r"^\d+[.)]\s+", "", s)
    s = re.sub(r"^[\[\(]+", "", s)
    s = s.strip("`*_ >|").strip()
    s = URL_RE.sub("", s).strip()
    s = re.sub(r"[`\"]", "", s)
    s = EMOJI_RE.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _truncate(s: str, max_chars: int) -> str:
    """Collapse whitespace and truncate to ``max_chars`` with an ellipsis."""
    s = re.sub(r"\s+", " ", s or "").strip()
    if len(s) > max_chars:
        s = s[:max_chars].rsplit(" ", 1)[0] + "…"
    return s


def _is_persona(s: str) -> bool:
    """Return True if a cleaned line is a persona/role definition."""
    return bool(PERSONA_NAME_RE.match(s))


def _specific_title(title: str) -> Optional[str]:
    """Return a cleaned title only if it is specific (not a generic template)."""
    if not title:
        return None
    t = title.strip()
    if GENERIC_TITLE_RE.search(t):
        return None
    if GENERIC_TITLE_PREFIX_RE.match(t):
        return None
    t = EMOJI_RE.sub("", t).strip()
    t = re.sub(r"^[:\- ]+", "", t)
    t = GENERIC_TITLE_PREFIX_CLEAN_RE.sub("", t)
    t = _clean_structural(t)
    if len(t) < 12:
        return None
    return t


def distill_intent_simple(session: Dict[str, Any], max_chars: int = 200) -> str:
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


def distill_intent_rich(session: Dict[str, Any], max_chars: int = 200) -> str:
    """Distill intent using rich heuristics, falling back to the title.

    Ported and adapted from /tmp/opencode/build_intent_metadata.py:

    - ``## Code Review Request`` block → ``review PR: <Title: line>``
    - ``PRIORITY PR TASK``/``priority pr repair`` → goal/title/PR-number intent
    - ``description: >`` block capture
    - ``goal:`` / ``objective:`` / ``purpose:`` line capture
    - ``You are working on Pull Requests in repository X`` → branch-targeted intent
    - ``mission is`` / ``responsible for`` tail extraction
    - persona / structural markdown / emoji / URL / generic-template rejection
    """
    prompt = (session.get("prompt") or "").strip()
    title = (session.get("title") or "").strip()

    if CODE_REVIEW_REQUEST_RE.match(prompt):
        m = re.search(r"(?m)^Title:\s*(.+)$", prompt)
        if m and _clean_structural(m.group(1)):
            return _truncate("review PR: " + _clean_structural(m.group(1)), max_chars)

    text = FENCE_RE.sub(" ", prompt)

    if PRIORITY_PR_TASK_RE.search(text):
        g = re.search(r"(?im)^\s*(?:goal|purpose)\s*:\s*(.+)$", text)
        goal = _clean_structural(g.group(1)) if g else "fix CI failures"
        ttl = PR_REPAIR_TITLE_RE.search(text)
        prnum = PR_REPAIR_NUM_RE.search(text)
        suffix = f" ({_clean_structural(ttl.group(1))})" if ttl else ""
        pr = f" (PR #{prnum.group(1)})" if prnum else ""
        return _truncate(goal + pr + suffix, max_chars)

    d = DESCRIPTION_BLOCK_RE.search(text)
    if d:
        desc = _clean_structural(d.group(1))
        if desc and len(desc) > 15:
            return _truncate(desc, max_chars)

    g = GOAL_LINE_RE.search(text)
    if g:
        val = _clean_structural(g.group(1))
        if val and len(val) > 8:
            return _truncate(val, max_chars)

    lines = [URL_RE.sub(" ", l).strip() for l in text.split("\n")]
    lines = [l for l in lines if l]

    if lines:
        m = BRANCH_TARGET_RE.match(lines[0])
        if m:
            sel = lines[1] if len(lines) > 1 else ""
            bm = re.search(r"targeting\s+[`']?(\S+)", sel)
            branch = bm.group(1).strip("`'.,") if bm else "?"
            return _truncate(
                f"fix failing required CI checks on an open `{branch}` PR in {m.group(1)}",
                max_chars,
            )

    for line in lines:
        low = line.lower()
        if "mission is" in low:
            i = low.find("mission is")
            tail = line[i + len("mission is"):].strip()
            tail = re.sub(r"^[:\-]+\s*", "", tail)
            tail = re.sub(r"^(to|of)\s+", "", tail, flags=re.I)
            if tail:
                return _truncate(_specific_title(title) or tail, max_chars)
        if re.match(r"^you\s+are", low) and "responsible" in low:
            i = low.find("responsible for")
            tail = line[i + len("responsible for"):].strip()
            if tail:
                return _truncate(_specific_title(title) or tail, max_chars)

    for line in lines:
        s = _clean_structural(line)
        if not s or len(s) < 6:
            continue
        if STRUCT_FIELD_RE.match(line):
            continue
        if _is_persona(s):
            continue
        if any(pattern.match(line) for pattern in BOILERPLATE_LINE_RES):
            continue
        s = re.sub(r"^you\s+are\s+", "", s, flags=re.I)
        s = re.sub(r"^you're\s+", "", s, flags=re.I)
        s = re.sub(
            r"^a[n]?\s+\w+\s+(?:agent|engineer|fixer|auditor|tester)[.\-]?\s+goal\s*:\s*",
            "",
            s,
            flags=re.I,
        )
        s = re.sub(r"^a test engineer\s*\.\s*", "", s, flags=re.I)
        s = re.sub(r"^a test fixer\s*\.\s*", "", s, flags=re.I)
        s = _clean_structural(s)
        if s and not GENERIC_TEMPLATE_RE.search(s):
            return _truncate(s, max_chars)

    if _specific_title(title):
        return _truncate(_specific_title(title), max_chars)
    cleaned = _clean_structural(title)
    return _truncate(cleaned, max_chars) if cleaned else None


def distill_intent(session: Dict[str, Any], max_chars: int = 200) -> str:
    """Distill a session's intent: rich heuristics, then simple, then title."""
    rich = distill_intent_rich(session, max_chars)
    if rich:
        return rich
    return distill_intent_simple(session, max_chars)


def classify_session(session: Dict[str, Any], pr_refs: Optional[List[str]] = None) -> Dict[str, str]:
    """Classify a session into has_pr / code_review_type / execution_type / other.

    Adapted from /tmp/opencode/jules_analyze.py:
    - has_pr: session has PR refs (or a PR url in outputs)
    - code_review_type: title matches the code-review regex
    - execution_type: COMPLETED with no PR and not code-review-type (missed candidates)
    - other: everything else
    """
    refs = list(pr_refs) if pr_refs is not None else extract_pr_refs(session)
    if refs or _all_pr_urls(session):
        return {"bucket": "has_pr", "reason": f"PR refs: {', '.join(refs) or 'present'}"}
    title = session.get("title") or ""
    if CODE_REVIEW_RE.search(title):
        return {"bucket": "code_review_type", "reason": "title matches code-review pattern"}
    state = (session.get("state") or "UNKNOWN").upper()
    if state == "COMPLETED":
        return {
            "bucket": "execution_type",
            "reason": "COMPLETED with no PR and not code-review type",
        }
    return {"bucket": "other", "reason": "no PR, not code-review type, non-terminal state"}


def is_stale(session: Dict[str, Any], before: str) -> bool:
    """Return True if a session's updateTime is before ``before`` (YYYY-MM-DD)."""
    ts = session.get("updateTime") or ""
    return bool(ts and ts[:10] < before)


def db_anomalies(sessions: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """Return ``(session_id, reason)`` pairs for database-integrity anomalies.

    Missing updateTime, updateTime < createTime, and non-terminal sessions
    created in 2025 (adapted from /tmp/opencode/jules_analyze.py).
    """
    out: List[Tuple[str, str]] = []
    for s in sessions:
        sid = (s.get("id") or s.get("name") or "").replace("sessions/", "")
        up = s.get("updateTime") or ""
        cr = s.get("createTime") or ""
        if not up:
            out.append((sid, "missing updateTime"))
        elif up < cr:
            out.append((sid, f"updateTime < createTime ({cr})"))
        if cr.startswith("2025") and (s.get("state") or "").upper() not in ("COMPLETED", "FAILED"):
            out.append((sid, "non-terminal with createTime in 2025"))
    return out


def build_intent_metadata(
    session: Dict[str, Any],
    classify: bool = False,
    stale: bool = False,
    anomaly: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the canonical intent-metadata dict for a session."""
    session_id = (session.get("id") or session.get("name") or "").replace("sessions/", "")
    sc = session.get("sourceContext") or {}
    prompt = session.get("prompt") or ""
    row = {
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
    if classify:
        row.update(classify_session(session, row["pr_refs"]))
    if stale:
        row["stale"] = True
    if anomaly:
        row["anomaly"] = anomaly
    return row


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
    """Apply all client-side filters (state/exclude/pending/active/repo/title/dates)."""
    include = [s.upper() for s in (args.state or [])]
    exclude = [s.upper() for s in (args.exclude_state or [])]
    repo_sub = (args.repo or "").lower()
    title_keywords = [k.lower() for k in (args.title_match or [])]
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
        if title_keywords:
            title = (session.get("title") or "").lower()
            if not any(k in title for k in title_keywords):
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


def _session_id(session: Dict[str, Any]) -> str:
    return (session.get("id") or session.get("name") or "").replace("sessions/", "")


def _stale_before_from_args(args) -> Optional[str]:
    """Resolve ``--stale-before`` / ``--stale-days`` to a YYYY-MM-DD threshold."""
    if args.stale_before:
        return args.stale_before
    if args.stale_days is not None:
        before = datetime.now(timezone.utc) - timedelta(days=args.stale_days)
        return before.date().isoformat()
    return None


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
        "--title-match", nargs="*", metavar="KEYWORD",
        help="Only sessions whose title contains ANY of these keywords (case-insensitive substring; "
             "e.g. --title-match taskmaster cli linear)"
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
    parser.add_argument(
        "--classify", action="store_true",
        help="Add a classification to each row: bucket (has_pr | code_review_type | execution_type | other) "
             "and a short reason. Shown as extra columns in table output."
    )
    stale_group = parser.add_mutually_exclusive_group()
    stale_group.add_argument(
        "--stale-before", metavar="YYYY-MM-DD",
        help="Only IN_PROGRESS/QUEUED sessions whose updateTime is before this date"
    )
    stale_group.add_argument(
        "--stale-days", type=int, metavar="N",
        help="Only IN_PROGRESS/QUEUED sessions not updated in the last N days"
    )
    parser.add_argument(
        "--anomalies", action="store_true",
        help="List only sessions with database-integrity anomalies (missing updateTime, "
             "updateTime < createTime, non-terminal created in 2025)"
    )
    parser.add_argument(
        "--snapshot", metavar="OUT.json",
        help="Write a full snapshot {'meta': {...}, 'sessions': [...]} to OUT.json (always full scan)"
    )
    parser.add_argument("--json", action="store_true", help="Output as a pretty JSON array")
    parser.add_argument("--jsonl", action="store_true", help="Output as JSON Lines (one object per line)")
    args = parser.parse_args()

    client = JulesAPIClient()

    if args.sessions:
        sessions = [client.get_session(sid) for sid in args.sessions]
        scanned_count = len(sessions)
    else:
        scan_limit = None if (args.all or args.snapshot) else 500
        sessions = list(client.list_sessions(page_size=PAGE_SIZE, max_results=scan_limit))
        scanned_count = len(sessions)

    filtered = filter_sessions(sessions, args)

    stale_before = _stale_before_from_args(args)
    if stale_before:
        filtered = [
            s for s in filtered
            if (s.get("state") or "UNKNOWN").upper() in STALE_STATES and is_stale(s, stale_before)
        ]

    anomaly_map: Dict[str, str] = {}
    if args.anomalies:
        anomaly_map = dict(db_anomalies(filtered))
        filtered = [s for s in filtered if _session_id(s) in anomaly_map]

    filtered.sort(key=_create_time_sort_key)

    rows = [
        build_intent_metadata(
            s,
            classify=args.classify,
            stale=stale_before is not None,
            anomaly=anomaly_map.get(_session_id(s)),
        )
        for s in filtered
    ]

    if args.snapshot:
        snapshot = {
            "meta": {
                "fetched_utc": datetime.now(timezone.utc).isoformat(),
                "total": len(rows),
                "pages": math.ceil(scanned_count / PAGE_SIZE),
            },
            "sessions": rows,
        }
        try:
            with open(args.snapshot, "w") as f:
                json.dump(snapshot, f, indent=1)
        except OSError as e:
            print(f"Error: could not write snapshot: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"Wrote snapshot of {len(rows)} sessions to {args.snapshot}")
        return

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
    classify_cols = ""
    if args.classify:
        classify_cols = f"{'Bucket':<18} | {'Reason':<34} | "
    header = f"{'ID':<22} | {'State':<25} | {'Repo':<32} | {classify_cols}Intent"
    print(header)
    print("-" * len(header))
    for row in rows:
        intent = row["intent"] or ""
        shown = intent if len(intent) <= intent_width else intent[: intent_width - 1].rstrip() + "…"
        repo = row["repo"] or ""
        if args.classify:
            bucket = row.get("bucket") or "other"
            reason = row.get("reason") or ""
            reason_shown = reason if len(reason) <= 34 else reason[:33] + "…"
            print(
                f"{row['id']:<22} | {row['state']:<25} | {repo[:32]:<32} | "
                f"{bucket:<18} | {reason_shown:<34} | {shown}"
            )
        else:
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
