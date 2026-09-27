#!/usr/bin/env python3
"""Bounded, resumable backfill of Jules session activities into store.db.

The store's activity table is populated only by explicit opt-in: sync
entry points upsert session rows but never fetch activities, so coverage
decays to whatever an operator last requested. This tool closes that gap
on demand. It never runs on a timer; invoking it IS the explicit intent.

Scope is bounded by flags (state, recency, session IDs, limit) and the
run is resumable: a cursor of completed session IDs is kept in
sync_meta (``activity_backfill_cursor``), so an interrupted run resumes
where it stopped. Ingest is idempotent (INSERT OR IGNORE), so re-running
any range is safe. A before/after count assertion is printed at the end.

Usage:
    uv run python tools/store/backfill_activities.py --state FAILED --limit 50
    uv run python tools/store/backfill_activities.py --non-terminal
    uv run python tools/store/backfill_activities.py --sessions 123,456
    uv run python tools/store/backfill_activities.py --since 2026-07-01
    uv run python tools/store/backfill_activities.py --resume --limit 200
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.api.jules_api_client import JulesAPIClient
from tools.store.jules_store import JulesSessionStore

CURSOR_KEY = "activity_backfill_cursor"
MAX_ACTIVITIES_PER_SESSION = 500  # matches store_activities() cap
NON_TERMINAL_STATES = ("QUEUED", "IN_PROGRESS", "AWAITING_USER_FEEDBACK", "PAUSED", "PLANNING")


def load_cursor(store: JulesSessionStore) -> set:
    """Session IDs already attempted by a previous run."""
    with store._conn() as conn:
        row = conn.execute(
            "SELECT value FROM sync_meta WHERE key=?", (CURSOR_KEY,)
        ).fetchone()
    if not row:
        return set()
    try:
        return set(json.loads(row[0]))
    except (ValueError, TypeError):
        return set()


def save_cursor(store: JulesSessionStore, done: set) -> None:
    with store._conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO sync_meta (key, value) VALUES (?, ?)",
            (CURSOR_KEY, json.dumps(sorted(done))),
        )


def select_sessions(
    store: JulesSessionStore,
    states: Optional[tuple],
    since: Optional[str],
    session_ids: Optional[set],
    limit: Optional[int],
    skip_covered: bool,
) -> list:
    """Pick gap sessions from the local store (no API calls)."""
    q = "SELECT session_id, state FROM sessions WHERE 1=1"
    params: list = []
    if states:
        q += f" AND state IN ({','.join('?' * len(states))})"
        params.extend(states)
    if session_ids:
        q += f" AND session_id IN ({','.join('?' * len(session_ids))})"
        params.extend(session_ids)
    if since:
        q += " AND update_time >= ?"
        params.append(since)
    if skip_covered:
        q += " AND activity_count = 0"
    q += " ORDER BY update_time DESC"
    if limit:
        q += " LIMIT ?"
        params.append(limit)
    with store._conn() as conn:
        return [
            (r["session_id"], r["state"])
            for r in conn.execute(q, params).fetchall()
        ]


def backfill(
    client: JulesAPIClient,
    store: JulesSessionStore,
    targets: list,
    resume_done: set,
) -> dict:
    """Fetch activities for each target session and upsert them."""
    stats = {"attempted": 0, "sessions_with_new": 0, "new_rows": 0, "errors": 0}
    done = set(resume_done)
    for i, (sid, state) in enumerate(targets, 1):
        if sid in done:
            continue
        try:
            activities = list(
                client.list_activities(sid, page_size=100,
                                       max_results=MAX_ACTIVITIES_PER_SESSION)
            )
            new = store.upsert_activities(sid, activities)
        except Exception as e:  # noqa: BLE001 — one bad session must not stop the run
            stats["errors"] += 1
            print(f"  [{i}/{len(targets)}] {sid} ({state}): ERROR {e}", flush=True)
            time.sleep(2)
            done.add(sid)
            continue
        stats["attempted"] += 1
        done.add(sid)
        if new:
            stats["sessions_with_new"] += 1
            stats["new_rows"] += new
        print(
            f"  [{i}/{len(targets)}] {sid} ({state}): +{new} rows "
            f"(api {len(activities)})",
            flush=True,
        )
        if i % 25 == 0:
            save_cursor(store, done)
    save_cursor(store, done)
    return stats


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--state", help="Comma-separated states (COMPLETED,FAILED,...)")
    scope.add_argument("--non-terminal", action="store_true",
                        help="QUEUED/IN_PROGRESS/AWAITING/PAUSED/PLANNING")
    scope.add_argument("--sessions", help="Comma-separated explicit session IDs")
    parser.add_argument("--since", help="Only sessions with update_time >= this (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, help="Max sessions this run")
    parser.add_argument("--include-covered", action="store_true",
                        help="Do not skip sessions that already have activities")
    parser.add_argument("--resume", action="store_true",
                        help="Skip session IDs recorded by a previous run's cursor")
    parser.add_argument("--dry-run", action="store_true",
                        help="List targets without fetching")
    args = parser.parse_args(argv)

    store = JulesSessionStore()
    if args.state:
        states = tuple(s.strip().upper() for s in args.state.split(","))
    elif args.non_terminal:
        states = NON_TERMINAL_STATES
    else:
        states = None
    session_ids = (
        {s.strip() for s in args.sessions.split(",")} if args.sessions else None
    )

    targets = select_sessions(
        store, states, args.since, session_ids, args.limit,
        skip_covered=not args.include_covered,
    )
    print(f"Targets: {len(targets)} sessions "
          f"(states={states or 'ALL'}, since={args.since or 'any'}, "
          f"limit={args.limit or 'none'})")
    if not targets:
        return 0
    if args.dry_run:
        for sid, state in targets:
            print(f"  {sid} ({state})")
        return 0

    resume_done = load_cursor(store) if args.resume else set()
    if resume_done:
        print(f"Resuming: {len(resume_done)} session IDs already attempted")

    with store._conn() as conn:
        before_rows = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]

    client = JulesAPIClient()
    stats = backfill(client, store, targets, resume_done)

    with store._conn() as conn:
        after_rows = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
    print(
        f"\nDone: attempted {stats['attempted']}, sessions with new rows "
        f"{stats['sessions_with_new']}, new activity rows {stats['new_rows']}, "
        f"errors {stats['errors']}"
    )
    print(f"Assertion: activities {before_rows} -> {after_rows} "
          f"(delta {after_rows - before_rows}, expected {stats['new_rows']})")
    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
