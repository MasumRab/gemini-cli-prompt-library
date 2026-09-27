#!/usr/bin/env python3
"""Read-only freshness diagnostics and explicit refresh for the Jules session store.

Age is informational: reading freshness never triggers a Jules API request or
changes the store. Refresh is available only through the explicit ``--sync``
CLI option or an explicit call to :func:`sync_store`.

The last successful explicit incremental sync is recorded in ``sync_meta``
under ``last_incremental_sync``. The marker describes a successful invocation
of the bounded incremental sync, not a complete account-wide snapshot.

CLI examples::

    uv run python tools/store/staleness.py --check  # report metadata only
    uv run python tools/store/staleness.py --sync   # explicitly request sync
    uv run python tools/store/staleness.py --max-age 6 --check
"""

import argparse
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.store.jules_store import JulesSessionStore, STORE_DB

META_KEY = "last_incremental_sync"
DEFAULT_MAX_AGE_HOURS = 12.0


@dataclass(frozen=True)
class FreshnessStatus:
    """Observed store freshness; never an instruction to fetch or mutate."""

    last_sync: str | None
    age_seconds: float | None
    max_age_hours: float
    is_old: bool | None
    timestamp_problem: str | None = None


class _ReadOnlyStore:
    """Minimal existing-database connection that cannot initialize or write it."""

    def __init__(self, db_path: Path) -> None:
        uri = f"{db_path.resolve().as_uri()}?mode=ro"
        self._connection = sqlite3.connect(uri, uri=True)
        self._connection.row_factory = sqlite3.Row

    def _conn(self) -> sqlite3.Connection:
        return self._connection

    def close(self) -> None:
        self._connection.close()


def _parse_iso(ts: str) -> datetime | None:
    """Parse an ISO-8601 timestamp and normalize it to UTC, if possible."""
    try:
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    if parsed.tzinfo is None:
        # The marker is written in UTC. Treat legacy naive timestamps as UTC.
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def get_last_sync(store: JulesSessionStore) -> str | None:
    """Return the last successful explicit incremental-sync marker, if any."""
    with store._conn() as conn:
        row = conn.execute(
            "SELECT value FROM sync_meta WHERE key=?", (META_KEY,)
        ).fetchone()
    return row["value"] if row else None


def inspect_freshness(
    store: JulesSessionStore,
    max_age_hours: float = DEFAULT_MAX_AGE_HOURS,
    *,
    now: datetime | None = None,
) -> FreshnessStatus:
    """Read freshness metadata only; never sync, write, or schedule work.

    ``is_old`` is ``None`` when no valid successful-sync marker exists. The
    threshold is descriptive only and does not cause any action.
    """
    if max_age_hours < 0:
        raise ValueError("max_age_hours must be non-negative")

    last = get_last_sync(store)
    if last is None:
        return FreshnessStatus(
            last_sync=None,
            age_seconds=None,
            max_age_hours=max_age_hours,
            is_old=None,
            timestamp_problem="missing",
        )

    parsed = _parse_iso(last)
    if parsed is None:
        return FreshnessStatus(
            last_sync=last,
            age_seconds=None,
            max_age_hours=max_age_hours,
            is_old=None,
            timestamp_problem="malformed",
        )

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    age_s = (current.astimezone(timezone.utc) - parsed).total_seconds()
    if age_s < 0:
        return FreshnessStatus(
            last_sync=last,
            age_seconds=age_s,
            max_age_hours=max_age_hours,
            is_old=None,
            timestamp_problem="future_timestamp_or_clock_skew",
        )
    return FreshnessStatus(
        last_sync=last,
        age_seconds=age_s,
        max_age_hours=max_age_hours,
        is_old=age_s > max_age_hours * 3600,
    )


def record_sync(store: JulesSessionStore, *, synced_at: datetime | None = None) -> None:
    """Record a successful explicit sync invocation in UTC."""
    stamp = synced_at or datetime.now(timezone.utc)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    value = stamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with store._conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO sync_meta (key, value) VALUES (?, ?)",
            (META_KEY, value),
        )


def sync_store(store: JulesSessionStore | None = None) -> bool:
    """Explicitly run the bounded incremental sync; return success status.

    This function performs API and SQLite writes by design. Callers must invoke
    it only in response to explicit user intent, never as a consequence of age.
    A zero exit status records the marker. A non-zero status or exception does
    not update the marker; exceptions are returned as ``False`` after reporting.
    """
    from tools.store.sync_incremental import main as sync_main

    store = store or JulesSessionStore()
    try:
        rc = sync_main(["--max-pages", "5"])
    except SystemExit as exc:  # missing credentials use sys.exit() in the API client
        print(f"⚠️  Explicit sync failed (exit {exc.code}); freshness marker not updated", file=sys.stderr)
        return False
    except Exception as exc:  # authentication/init failures can happen pre-request
        print(f"⚠️  Explicit sync failed; freshness marker not updated: {exc}", file=sys.stderr)
        return False
    if rc != 0:
        print("⚠️  Explicit sync failed; freshness marker not updated", file=sys.stderr)
        return False
    record_sync(store)
    return True


def _format_age(age_seconds: float | None) -> str:
    if age_seconds is None:
        return "unknown"
    if age_seconds < 0:
        return f"clock skew/future timestamp ({age_seconds:.0f}s)"
    return f"{age_seconds / 3600:.2f}h"


def main() -> int:
    parser = argparse.ArgumentParser(description="Session store freshness diagnostics")
    parser.add_argument(
        "--max-age",
        type=float,
        default=DEFAULT_MAX_AGE_HOURS,
        help=f"Informational age threshold in hours (default {DEFAULT_MAX_AGE_HOURS})",
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--check", action="store_true", help="Report freshness only (default)"
    )
    action.add_argument(
        "--sync", action="store_true", help="Explicitly run incremental sync"
    )
    args = parser.parse_args()

    if args.max_age < 0:
        parser.error("--max-age must be non-negative")

    if args.sync:
        store = JulesSessionStore()
        if not sync_store(store):
            return 1
        status = inspect_freshness(store, args.max_age)
    elif not STORE_DB.exists():
        status = FreshnessStatus(
            last_sync=None,
            age_seconds=None,
            max_age_hours=args.max_age,
            is_old=None,
            timestamp_problem="store_not_created",
        )
    else:
        store = _ReadOnlyStore(STORE_DB)
        try:
            status = inspect_freshness(store, args.max_age)
        finally:
            store.close()
    print(f"last sync: {status.last_sync or 'never'}")
    print(f"age: {_format_age(status.age_seconds)}")
    print(f"informational threshold: {status.max_age_hours:g}h")
    print(f"older than threshold: {status.is_old if status.is_old is not None else 'unknown'}")
    if status.timestamp_problem:
        print(f"timestamp status: {status.timestamp_problem}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
