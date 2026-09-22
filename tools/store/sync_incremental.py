#!/usr/bin/env python3
"""
Incremental sync of Jules sessions from API to local store.

The API list endpoint returns sessions newest-first by createTime and
supports NO filter or orderBy parameter (verified: updatedSince/filter/
orderBy all 400). A session created long ago can still change state
later (e.g. a sendMessage wakes a COMPLETED session), so a pure
updateTime high-water mark would miss late state changes on old
sessions.

Strategy: page from the top (newest first), upsert every session whose
(state, update_time) differs from the store, and stop when a full page
contains no changes AND all its sessions are older than the store's
newest createTime. This keeps store.db fresh in a handful of API calls
instead of the full 15-page sync (sync_all_sessions.py).

Usage:
    uv run python tools/store/sync_incremental.py           # sync
    uv run python tools/store/sync_incremental.py --dry-run # report only
    uv run python tools/store/sync_incremental.py --max-pages 5
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

# Ensure we can import the local modules
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.api.jules_api_client import JulesAPIClient
from tools.store.jules_store import JulesSessionStore

PAGE_SIZE = 100
DEFAULT_MAX_PAGES = 10


def _parse_ts(ts: str) -> float:
    """RFC3339 -> epoch seconds; 0.0 on malformed input."""
    import calendar
    from datetime import datetime

    try:
        # Python >=3.11 parses trailing "Z" natively.
        dt = datetime.fromisoformat(ts)
        return calendar.timegm(dt.utctimetuple())
    except (ValueError, AttributeError):
        return 0.0


def get_store_high_water(store: JulesSessionStore) -> tuple[str | None, float]:
    """Latest create_time recorded in the store (string and epoch)."""
    with store._conn() as conn:
        row = conn.execute("SELECT MAX(create_time) FROM sessions").fetchone()
    latest = row[0] if row else None
    return latest, _parse_ts(latest or "")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f"Hard cap on pages fetched (default {DEFAULT_MAX_PAGES})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be synced without writing",
    )
    args = parser.parse_args(argv)

    store = JulesSessionStore()
    client = JulesAPIClient()

    hwm_str, hwm_epoch = get_store_high_water(store)
    print(
        f"📍 Store high-water mark (newest create_time): {hwm_str or '(empty store)'}"
    )

    start = time.time()
    upserted = 0
    scanned = 0
    pages = 0
    next_token: str | None = None
    stopped_reason = "page cap"

    while pages < args.max_pages:
        params = f"pageSize={PAGE_SIZE}"
        if next_token:
            params += f"&pageToken={next_token}"
        try:
            resp = client._request(f"sessions?{params}")
        except Exception as e:
            print(f"❌ API request failed on page {pages + 1}: {e}")
            return 1

        pages += 1
        sessions = resp.get("sessions", [])

        # Look up current store state for this page's sessions in one query.
        with store._conn() as conn:
            ids = [s.get("name", "").replace("sessions/", "") for s in sessions]
            placeholders = ",".join("?" * len(ids)) if ids else "NULL"
            rows = conn.execute(
                f"SELECT session_id, state, update_time FROM sessions "
                f"WHERE session_id IN ({placeholders})",
                ids,
            ).fetchall()
        known = {r["session_id"]: (r["state"], r["update_time"]) for r in rows}

        page_changes = 0
        page_below_hwm = True  # stays True only if every session is older
        for sess in sessions:
            scanned += 1
            sid = sess.get("name", "unknown").replace("sessions/", "")
            upd = sess.get("updateTime", "")
            crt_epoch = _parse_ts(sess.get("createTime", ""))

            if hwm_epoch and crt_epoch and crt_epoch > hwm_epoch:
                page_below_hwm = False  # something newer than store exists

            existing = known.get(sid)
            if existing and existing[0] == sess.get("state") and existing[1] == upd:
                continue  # unchanged — already fresh in store

            if not args.dry_run:
                try:
                    store.upsert_session(sess)
                except Exception as e:
                    print(f"⚠️  Failed to upsert session {sid}: {e}")
                    continue
            upserted += 1
            page_changes += 1

        print(
            f"📥 Page {pages}: {len(sessions)} sessions, "
            f"{page_changes} changed ({upserted} upserted so far)"
        )

        # Stop when this page had no changes AND nothing on it is newer
        # than the store's newest create_time — we are caught up.
        if page_changes == 0 and page_below_hwm:
            stopped_reason = "caught up (no changes, all older than store)"
            break

        next_token = resp.get("nextPageToken")
        if not next_token:
            stopped_reason = "end of API list"
            break
        time.sleep(0.05)

    elapsed = time.time() - start
    print(
        f"✅ Stopped: {stopped_reason} — {pages} pages, {scanned} scanned in {elapsed:.2f}s"
    )
    print(f"💾 Upserted: {upserted}{' (dry-run)' if args.dry_run else ''}")

    if not args.dry_run:
        with store._conn() as conn:
            cnt = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            latest = conn.execute("SELECT MAX(update_time) FROM sessions").fetchone()[0]
        print(f"📊 Store: {cnt} sessions, newest update_time {latest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
