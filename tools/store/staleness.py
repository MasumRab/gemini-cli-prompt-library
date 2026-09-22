#!/usr/bin/env python3
"""
Sync-before-read staleness gate for the Jules session store.

Every store consumer should call ``ensure_fresh()`` (or the CLI wrapper)
before reading. If the store is older than the freshness threshold, the
incremental sync runs first; otherwise the call is a no-op costing one
SQLite query. This replaces the daemon approach: no background process,
freshness happens exactly when someone reads the store.

The last-sync timestamp lives in the store's sync_meta table under
``last_incremental_sync``.

CLI:
    uv run python tools/store/staleness.py            # sync if stale
    uv run python tools/store/staleness.py --check    # report only
    uv run python tools/store/staleness.py --max-age 6
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.store.jules_store import JulesSessionStore

META_KEY = "last_incremental_sync"
DEFAULT_MAX_AGE_HOURS = 12.0


def _parse_iso(ts: str) -> float:
    """RFC3339 -> epoch seconds; 0.0 on malformed input."""
    from datetime import datetime

    try:
        return datetime.fromisoformat(ts).timestamp()
    except (ValueError, AttributeError):
        return 0.0


def get_last_sync(store: JulesSessionStore) -> str | None:
    """Last successful incremental sync timestamp, if any."""
    with store._conn() as conn:
        row = conn.execute(
            "SELECT value FROM sync_meta WHERE key=?", (META_KEY,)
        ).fetchone()
    return row["value"] if row else None


def record_sync(store: JulesSessionStore) -> None:
    """Stamp the current time as the last successful sync."""
    with store._conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO sync_meta (key, value) VALUES (?, ?)",
            (META_KEY, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
        )


def is_stale(
    store: JulesSessionStore, max_age_hours: float = DEFAULT_MAX_AGE_HOURS
) -> tuple[bool, str | None]:
    """Return (stale, last_sync_iso). Stale = older than max_age or never synced."""
    last = get_last_sync(store)
    if last is None:
        return True, None
    age_s = time.time() - _parse_iso(last)
    return age_s > max_age_hours * 3600, last


def ensure_fresh(
    store: JulesSessionStore | None = None,
    max_age_hours: float = DEFAULT_MAX_AGE_HOURS,
    quiet: bool = False,
) -> bool:
    """Run incremental sync if the store is stale. Returns True if a sync ran.

    On sync failure the store is left untouched (still readable, just
    stale) and False is returned — readers should proceed with stale data
    rather than fail.
    """
    from tools.store.sync_incremental import main as sync_main

    store = store or JulesSessionStore()
    stale, last = is_stale(store, max_age_hours)
    if not stale:
        return False

    if not quiet:
        print(
            f"🔄 Store stale (last sync {last or 'never'}), running incremental sync…",
            file=sys.stderr,
        )
    rc = sync_main(["--max-pages", "5"])
    if rc == 0:
        record_sync(store)
        return True
    if not quiet:
        print("⚠️  Sync failed; continuing with stale store", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Session store staleness gate")
    parser.add_argument(
        "--max-age",
        type=float,
        default=DEFAULT_MAX_AGE_HOURS,
        help=f"Freshness threshold in hours (default {DEFAULT_MAX_AGE_HOURS})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only report staleness, do not sync",
    )
    args = parser.parse_args()

    store = JulesSessionStore()
    stale, last = is_stale(store, args.max_age)
    print(f"last sync: {last or 'never'}")
    print(f"stale: {stale} (threshold {args.max_age}h)")

    if args.check:
        return 1 if stale else 0

    if stale:
        ran = ensure_fresh(store, args.max_age)
        print(f"sync ran: {ran}")
    else:
        print("store is fresh, no sync needed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
