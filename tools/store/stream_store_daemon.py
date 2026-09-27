#!/usr/bin/env python3
"""
Stream-to-store daemon: continuously polls and updates store.db while explicitly running.

Phase 2 of the streaming migration. Three mechanisms cooperate:

1. Subscription: every ACTIVE session (QUEUED / IN_PROGRESS /
   AWAITING_USER_FEEDBACK / PAUSED) discovered by a REST poll gets a
   live SDK stream (bridge.js ``stream``); each incoming activity is
   upserted into store.db immediately.
2. Session-state poll: on every cycle, the REST session list is
   upserted, so state transitions (including sessions we do not
   stream, e.g. ones that went terminal between cycles) land in the
   store.
3. Explicit historical refresh: this daemon does not run periodic account-wide
   sweeps. Use ``tools/store/sync_incremental.py`` when an operator explicitly
   wants that bounded historical refresh.

Requires JULES_STREAMING=1 for subscriptions; without it the daemon
degrades to polling only (no real-time activities).

Usage:
    uv run python tools/store/stream_store_daemon.py            # foreground
    uv run python tools/store/stream_store_daemon.py --once     # single cycle
    uv run python tools/store/stream_store_daemon.py --stop     # stop daemon
    uv run python tools/store/stream_store_daemon.py --status   # check state
"""

import argparse
import asyncio
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.api.jules_api_client import JulesAPIClient
from tools.api.jules_stream_client import JulesStreamClient, StreamClientError
from tools.store.jules_store import JulesSessionStore

# States where the session may still produce activities.
ACTIVE_STATES = {"QUEUED", "IN_PROGRESS", "AWAITING_USER_FEEDBACK", "PAUSED"}

POLL_INTERVAL = 60  # seconds between REST polls
SUBSCRIPTION_TIMEOUT = 8 * 3600  # max lifetime of one stream subprocess
DISCOVERY_PAGE_SIZE = 100
DISCOVERY_MAX = 300  # cap sessions examined per cycle

PID_FILE = Path.home() / ".jules" / "stream_store_daemon.pid"
LOG_FILE = Path.home() / ".jules" / "stream_store_daemon.log"

_stop = False


def _log(msg: str) -> None:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def _request_stop(signum: int, frame: Any) -> None:
    global _stop
    _stop = True


def _stop_requested() -> bool:
    return _stop


class StreamStoreDaemon:
    def __init__(self, store: JulesSessionStore, client: JulesAPIClient) -> None:
        self.store = store
        self.client = client
        self.stream_client: JulesStreamClient | None = None
        self.subscriptions: dict[str, asyncio.Task] = {}

    # ------------------------------------------------------------------
    # Discovery + session-row freshness
    # ------------------------------------------------------------------

    def poll_sessions(self) -> int:
        """Upsert recent sessions from the REST list; return active count."""
        upserted = 0
        active: list[str] = []
        seen = 0
        for sess in self.client.list_sessions(
            page_size=DISCOVERY_PAGE_SIZE, max_results=DISCOVERY_MAX
        ):
            seen += 1
            sid = sess.get("name", "").replace("sessions/", "")
            state = sess.get("state", "")
            try:
                self.store.upsert_session(sess)
                upserted += 1
            except Exception as e:
                _log(f"upsert failed for {sid}: {e}")
            if state in ACTIVE_STATES:
                active.append(sid)
        _log(
            f"poll: {seen} sessions scanned, {upserted} upserted, {len(active)} active"
        )
        return len(active)

    # ------------------------------------------------------------------
    # Streaming subscriptions
    # ------------------------------------------------------------------

    async def _subscribe(self, session_id: str) -> None:
        """Stream one session's activities into the store until it ends."""
        assert self.stream_client is not None
        count = 0
        try:
            async for activity in self.stream_client.stream(session_id):
                try:
                    self.store.upsert_activities(session_id, [activity])
                    count += 1
                except Exception as e:
                    _log(f"activity upsert failed ({session_id}): {e}")
        except StreamClientError as e:
            _log(f"stream error ({session_id}): {e}")
        finally:
            self.subscriptions.pop(session_id, None)
            # Refresh the session row with its final state.
            try:
                info = self.client.get_session(session_id)
                self.store.upsert_session(info)
            except Exception as e:
                _log(f"final state refresh failed ({session_id}): {e}")
            _log(f"subscription ended ({session_id}): {count} activities")

    async def reconcile_subscriptions(self) -> None:
        """Start streams for active sessions; abandon streams for dead tasks."""
        if self.stream_client is None:
            return

        # Determine currently active sessions from the store (fresh from poll).
        with self.store._conn() as conn:
            rows = conn.execute(
                "SELECT session_id FROM sessions WHERE state IN "
                f"({','.join('?' * len(ACTIVE_STATES))})",
                sorted(ACTIVE_STATES),
            ).fetchall()
        active = {r["session_id"] for r in rows}

        # Drop finished/crashed subscription tasks.
        for sid, task in list(self.subscriptions.items()):
            if task.done() or sid not in active:
                if not task.done():
                    task.cancel()
                self.subscriptions.pop(sid, None)

        # Start subscriptions for newly active sessions.
        for sid in sorted(active):
            if sid not in self.subscriptions:
                self.subscriptions[sid] = asyncio.create_task(self._subscribe(sid))
                _log(f"subscription started ({sid}), {len(self.subscriptions)} total")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    async def run_forever(self, once: bool = False) -> None:
        from tools.api.jules_stream_client import streaming_enabled

        if streaming_enabled():
            try:
                self.stream_client = JulesStreamClient()
            except StreamClientError as e:
                _log(f"stream client unavailable, poll-only mode: {e}")
        else:
            _log("JULES_STREAMING not set; poll-only mode (no live activities)")

        while not _stop_requested():
            cycle_start = time.time()
            try:
                self.poll_sessions()
                await self.reconcile_subscriptions()
            except Exception as e:
                _log(f"cycle error: {e}")

            if once:
                break
            elapsed = time.time() - cycle_start
            await asyncio.sleep(max(1.0, POLL_INTERVAL - elapsed))

        # Shutdown: cancel subscriptions
        for task in self.subscriptions.values():
            task.cancel()
        if self.subscriptions:
            await asyncio.gather(*self.subscriptions.values(), return_exceptions=True)
        _log("daemon stopped")


def is_running() -> bool:
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            return True
        except (ValueError, ProcessLookupError, PermissionError):
            return False
    return False


def stop_daemon() -> None:
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        try:
            os.kill(pid, signal.SIGTERM)
            _log(f"sent SIGTERM to {pid}")
        except ProcessLookupError:
            _log(f"process {pid} not found")
        PID_FILE.unlink(missing_ok=True)
    else:
        _log("no PID file found")


def main() -> int:
    parser = argparse.ArgumentParser(description="Jules stream-to-store daemon")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--stop", action="store_true", help="Stop the running daemon")
    parser.add_argument("--status", action="store_true", help="Show daemon status")
    args = parser.parse_args()

    if args.status:
        print(f"running: {is_running()}")
        if PID_FILE.exists():
            print(f"pid: {PID_FILE.read_text().strip()}")
        return 0
    if args.stop:
        stop_daemon()
        return 0
    if is_running() and not args.once:
        print("daemon already running")
        return 1

    if not args.once:
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PID_FILE.write_text(str(os.getpid()))
        signal.signal(signal.SIGTERM, _request_stop)
        signal.signal(signal.SIGINT, _request_stop)

    store = JulesSessionStore()
    client = JulesAPIClient()
    daemon = StreamStoreDaemon(store, client)
    try:
        asyncio.run(daemon.run_forever(once=args.once))
    finally:
        PID_FILE.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
