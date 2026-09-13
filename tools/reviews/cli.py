"""CLI entry points for the review-session pipeline.

Each command maps to a former /tmp script, now parameterized:

    python -m tools.reviews.cli discover     --repo EmailIntelligence
    python -m tools.reviews.cli download     --repo EmailIntelligence --output-dir /tmp/reviews
    python -m tools.reviews.cli audit        --repo EmailIntelligence
    python -m tools.reviews.cli aggregate     --repo EmailIntelligence --reviews-dir /tmp/reviews
    python -m tools.reviews.cli check-responses --repo EmailIntelligence
    python -m tools.reviews.cli deliver      --pr 570 --session <id> --review-file /tmp/reviews/PR570.md
    python -m tools.reviews.cli authorize-fix --pr 570 --session <id> --findings "..."
    python -m tools.reviews.cli refresh       --pr 775 --session <id> --current-head abc123 --reviewed-head def456

All commands support --json for machine-readable output and --dry-run to
preview without side effects.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.api.jules_api_client import JulesAPIClient
from tools.reviews.pipeline import (
    completeness_issues,
    discover_review_sessions,
    extract_verdict,
    fetch_review_messages,
    group_by_branch,
    latest_session_per_branch,
    send_with_backoff,
)
from tools.reviews.templates import (
    build_comment_delivery,
    build_fix_authorization,
    build_review_refresh,
)


def _api() -> JulesAPIClient:
    if not os.environ.get("JULES_API_KEY"):
        print("ERROR: JULES_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return JulesAPIClient()


def _print_json(data) -> None:
    print(json.dumps(data, indent=2, default=str))


# ---------------------------------------------------------------------------
# discover
# ---------------------------------------------------------------------------


def cmd_discover(args: argparse.Namespace) -> None:
    """List all review sessions from the local store."""
    sessions = discover_review_sessions(repo=args.repo)
    if args.json:
        _print_json(
            [
                {
                    "session_id": s.session_id,
                    "create_time": s.create_time,
                    "branch": s.branch,
                    "pr_url": s.pr_url,
                    "repo": s.repo,
                }
                for s in sessions
            ]
        )
    else:
        print(f"total review sessions: {len(sessions)}")
        grouped = group_by_branch(sessions)
        for key, group in sorted(grouped.items()):
            latest = max(group, key=lambda s: s.create_time)
            print(f"  {key[:55]:55} {len(group)} sessions  latest={latest.session_id}")


# ---------------------------------------------------------------------------
# download
# ---------------------------------------------------------------------------


def cmd_download(args: argparse.Namespace) -> None:
    """Download full review content from all sessions into per-branch files."""
    api = _api()
    sessions = discover_review_sessions(repo=args.repo)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_lines: list[str] = []

    for key, group in sorted(group_by_branch(sessions).items()):
        combined = out_dir / f"{key}-all-reviews.md"
        with open(combined, "w") as f:
            for s in group:
                fetch_review_messages(api, s, sleep=args.sleep)
                latest = max(group, key=lambda x: x.create_time)
                s._is_latest = s is latest
                if s.review_messages:
                    f.write(
                        f"\n\n{'=' * 80}\n"
                        f"SESSION {s.session_id} @ {s.create_time}\n"
                        f"pr_url: {s.pr_url}\n"
                        f"{'=' * 80}\n"
                    )
                    f.writelines(
                        f"\n--- {t} ---\n{msg}\n" for t, msg in s.review_messages
                    )
                    n = len(s.review_messages)
                    print(f"  {s.session_id}: {n} review chunks")
                    summary_lines.append(
                        f"{s.branch}: {n} chunks, latest={s.session_id}"
                    )
                else:
                    print(f"  {s.session_id}: no review content")
                    summary_lines.append(f"{s.branch}: no content")

        # Mark latest in the group
    (out_dir / "download-summary.txt").write_text("\n".join(summary_lines))
    print(f"\nDONE — {len(sessions)} sessions, files in {out_dir}/")


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------


def cmd_audit(args: argparse.Namespace) -> None:
    """Audit review completeness: find sessions with malformed/incomplete reviews."""
    api = _api()
    sessions = discover_review_sessions(repo=args.repo)
    issues: list[dict] = []

    for s in sessions:
        fetch_review_messages(api, s, sleep=args.sleep)
        if not s.review_messages:
            issues.append(
                {
                    "session_id": s.session_id,
                    "branch": s.branch,
                    "create_time": s.create_time,
                    "issues": ["NO-REVIEW-IN-CHAT"],
                    "artifact_count": s.artifact_count,
                }
            )
            continue

        best_t, best_msg = s.best_review()
        probs = completeness_issues(best_msg)
        if probs:
            issues.append(
                {
                    "session_id": s.session_id,
                    "branch": s.branch,
                    "create_time": s.create_time,
                    "issues": probs,
                    "artifact_count": s.artifact_count,
                    "best_review_time": best_t,
                    "best_review_len": len(best_msg),
                }
            )

    if args.json:
        _print_json(
            {
                "total_sessions": len(sessions),
                "incomplete_count": len(issues),
                "incomplete": issues,
            }
        )
    else:
        print(f"total review sessions: {len(sessions)}")
        print(f"sessions with incomplete/malformed review content: {len(issues)}")
        for i in issues:
            print(
                f"  {i['create_time']} {i['branch'][:50]:50} "
                f"{','.join(i['issues'])} (artifacts: {i['artifact_count']})"
            )


# ---------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------


def cmd_aggregate(args: argparse.Namespace) -> None:
    """Aggregate findings per PR and show the one session to message."""
    reviews_dir = Path(args.reviews_dir)
    sessions = discover_review_sessions(repo=args.repo)
    latest_map = latest_session_per_branch(sessions)

    targets: list[dict] = []
    for key, latest in sorted(latest_map.items()):
        safe = key.replace("/", "_")
        review_file = reviews_dir / f"{safe}-all-reviews.md"
        has_file = review_file.exists()
        targets.append(
            {
                "branch": latest.branch,
                "safe_branch": key,
                "pr_url": latest.pr_url,
                "latest_session": latest.session_id,
                "create_time": latest.create_time,
                "review_file": str(review_file) if has_file else None,
            }
        )

    if args.json:
        _print_json(targets)
    else:
        print(f"PRs to message (one per branch): {len(targets)}")
        for t in targets:
            print(
                f"  {t['branch'][:55]:55} -> {t['latest_session']} "
                f"({'file ready' if t['review_file'] else 'NO FILE'})"
            )


# ---------------------------------------------------------------------------
# check-responses
# ---------------------------------------------------------------------------


def cmd_check_responses(args: argparse.Namespace) -> None:
    """Poll messaged sessions for state + last agent message + verdict."""
    api = _api()
    session_ids = args.session_ids or []
    if not session_ids:
        sessions = discover_review_sessions(repo=args.repo)
        session_ids = [s.session_id for s in sessions]

    results: list[dict] = []
    for sid in session_ids:
        try:
            s = api.get_session(sid)
            if isinstance(s, str):
                s = json.loads(s)
            state = s.get("state", "?")
            updated = (s.get("updateTime", "") or "")[:19]

            acts = list(api.list_activities(sid))
            last_agent = None
            for a in acts:
                if isinstance(a, dict) and a.get("agentMessaged"):
                    last_agent = (
                        (a.get("createTime", "") or "")[:19],
                        a.get("agentMessaged", {}).get("agentMessage", ""),
                    )
            if last_agent:
                t, msg = last_agent
                verdict = extract_verdict(msg)
                results.append(
                    {
                        "session_id": sid,
                        "state": state,
                        "updated": updated,
                        "last_agent_time": t,
                        "verdict": verdict,
                        "preview": msg[:150],
                    }
                )
            else:
                results.append({"session_id": sid, "state": state, "updated": updated})
        except Exception as e:  # noqa: BLE001 — API errors reported per-session
            results.append({"session_id": sid, "error": str(e)[:80]})
        time.sleep(args.sleep)

    if args.json:
        _print_json(results)
    else:
        for r in results:
            sid = r["session_id"]
            if "error" in r:
                print(f"  {sid[-6:]}: ERR {r['error']}")
            elif "verdict" in r:
                print(
                    f"  {sid[-6:]}: state={r['state']:12} "
                    f"upd={r['updated']} verdict={r['verdict'][:40]}"
                )
            else:
                print(
                    f"  {sid[-6:]}: state={r['state']:12} "
                    f"upd={r['updated']} NO agent messages"
                )


# ---------------------------------------------------------------------------
# deliver
# ---------------------------------------------------------------------------


def cmd_deliver(args: argparse.Namespace) -> None:
    """Deliver a posted review to a session via the bridge pattern."""
    review_body = Path(args.review_file).read_text()
    # Strip a leading "# ..." header line (written by download/extract steps)
    lines = review_body.split("\n")
    if lines and lines[0].startswith("#"):
        lines = lines[1:]
    body = "\n".join(lines).lstrip("\n")

    msg = build_comment_delivery(body, args.pr)

    if args.dry_run:
        print(f"[DRY RUN] Would send {len(msg)} chars to {args.session}")
        print(msg[:500] + "...")
        return

    api = _api()
    send_with_backoff(api, args.session, msg)
    print(f"OK — delivered review for PR#{args.pr} to {args.session}")


# ---------------------------------------------------------------------------
# authorize-fix
# ---------------------------------------------------------------------------


def cmd_authorize_fix(args: argparse.Namespace) -> None:
    """Authorize a blocking session to implement fixes."""
    msg = build_fix_authorization(
        args.pr, args.branch or "", args.findings, args.note or ""
    )

    if args.dry_run:
        print(f"[DRY RUN] Would send {len(msg)} chars to {args.session}")
        print(msg[:500] + "...")
        return

    api = _api()
    send_with_backoff(api, args.session, msg)
    print(f"OK — fix authorization sent for PR#{args.pr} to {args.session}")


# ---------------------------------------------------------------------------
# refresh
# ---------------------------------------------------------------------------


def cmd_refresh(args: argparse.Namespace) -> None:
    """Ask a review session to refresh a stale review."""
    msg = build_review_refresh(args.pr_ref, args.current_head, args.reviewed_head)

    if args.dry_run:
        print(f"[DRY RUN] Would send {len(msg)} chars to {args.session}")
        print(msg[:500] + "...")
        return

    api = _api()
    send_with_backoff(api, args.session, msg)
    print(f"OK — refresh request sent to {args.session}")


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tools.reviews.cli",
        description="Jules review-session pipeline CLI",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # discover
    sp = sub.add_parser("discover", help="List review sessions from the store")
    sp.add_argument("--repo", default=None, help="Filter by repo name")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_discover)

    # download
    sp = sub.add_parser("download", help="Download all review content")
    sp.add_argument("--repo", default=None)
    sp.add_argument("--output-dir", default="/tmp/jules-reviews")
    sp.add_argument("--sleep", type=float, default=1.0)
    sp.set_defaults(func=cmd_download)

    # audit
    sp = sub.add_parser("audit", help="Audit review completeness")
    sp.add_argument("--repo", default=None)
    sp.add_argument("--sleep", type=float, default=1.0)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_audit)

    # aggregate
    sp = sub.add_parser("aggregate", help="Aggregate findings per PR")
    sp.add_argument("--repo", default=None)
    sp.add_argument("--reviews-dir", default="/tmp/jules-reviews")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_aggregate)

    # check-responses
    sp = sub.add_parser("check-responses", help="Poll messaged sessions")
    sp.add_argument("--repo", default=None)
    sp.add_argument("--session-ids", nargs="*", default=[])
    sp.add_argument("--sleep", type=float, default=1.0)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_check_responses)

    # deliver
    sp = sub.add_parser("deliver", help="Deliver a review to a session")
    sp.add_argument("--pr", type=int, required=True)
    sp.add_argument("--session", required=True)
    sp.add_argument("--review-file", required=True)
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=cmd_deliver)

    # authorize-fix
    sp = sub.add_parser("authorize-fix", help="Authorize a session to fix")
    sp.add_argument("--pr", type=int, required=True)
    sp.add_argument("--session", required=True)
    sp.add_argument("--branch", default="")
    sp.add_argument("--findings", required=True)
    sp.add_argument("--note", default="")
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=cmd_authorize_fix)

    # refresh
    sp = sub.add_parser("refresh", help="Refresh a stale review")
    sp.add_argument("--pr-ref", required=True, help="e.g. EmailIntelligence#775")
    sp.add_argument("--session", required=True)
    sp.add_argument("--current-head", required=True)
    sp.add_argument("--reviewed-head", required=True)
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=cmd_refresh)

    return p


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
