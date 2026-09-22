#!/usr/bin/env python3
"""
Async Python wrapper around the Jules SDK bridge (tools/sdk/dist/bridge.js).

Phase 1 of the streaming migration. The bridge is a Node CLI exposing
SDK-only features (stream/history/ask/waitFor/result/info/approve) that the
raw REST client cannot. This wrapper turns each bridge command into an
async-friendly Python API, with JSON-line parsing and typed results.

Feature flag: set JULES_STREAMING=1 to opt in. Callers should check
``streaming_enabled()`` and fall back to REST polling when disabled.

Usage:
    from tools.api.jules_stream_client import JulesStreamClient

    client = JulesStreamClient()
    async for activity in client.stream(SESSION_ID):
        handle(activity)            # dict per JSON line

    reply = await client.ask(SESSION_ID, "What is the status?")
    info = await client.info(SESSION_ID)
"""

import asyncio
import json
import os
import shlex
import subprocess
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = REPO_ROOT / "tools" / "sdk" / "dist" / "bridge.js"

# Bridge commands that print JSON lines (streamable) vs single JSON object.
_JSON_LINE_COMMANDS = {"stream", "history"}


def streaming_enabled() -> bool:
    """Whether streaming features are opted in (JULES_STREAMING=1)."""
    return os.environ.get("JULES_STREAMING", "") == "1"


class StreamClientError(RuntimeError):
    """Bridge invocation failed."""


class JulesStreamClient:
    """Async wrapper over the Node SDK bridge.

    Each command spawns ``node bridge.js <cmd> ...`` and parses its output.
    ``stream``/``history`` yield parsed JSON lines incrementally; other
    commands return a parsed JSON object once the process exits.
    """

    def __init__(
        self,
        bridge_path: Path | None = None,
        node_bin: str = "node",
        timeout: float = 600.0,
    ) -> None:
        self.bridge_path = Path(bridge_path or BRIDGE_PATH)
        if not self.bridge_path.exists():
            raise StreamClientError(f"bridge not found: {self.bridge_path}")
        self.node_bin = node_bin
        self.timeout = timeout

    def _argv(self, *args: str) -> list[str]:
        return [self.node_bin, str(self.bridge_path), *args]

    async def _run_command(
        self, *args: str, timeout: float | None = None
    ) -> dict[str, Any]:
        """Run a bridge command to completion; return parsed JSON output.

        Raises StreamClientError on non-zero exit or invalid JSON.
        """
        argv = self._argv(*args)
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout or self.timeout
            )
        except TimeoutError:
            proc.kill()
            await proc.wait()
            raise StreamClientError(
                f"bridge {shlex.join(args)} timed out after {timeout or self.timeout}s"
            ) from None
        if proc.returncode != 0:
            raise StreamClientError(
                f"bridge {shlex.join(args)} exited {proc.returncode}: "
                f"{stderr.decode(errors='replace').strip()[:500]}"
            )
        out = stdout.decode(errors="replace").strip()
        if not out:
            return {}
        try:
            return json.loads(out)
        except json.JSONDecodeError as e:
            raise StreamClientError(
                f"bridge {shlex.join(args)} produced invalid JSON: {e}"
            ) from e

    async def _iter_json_lines(self, *args: str) -> AsyncIterator[dict[str, Any]]:
        """Run a bridge command, yielding parsed JSON lines as they arrive.

        The loop ends when the bridge process exits (e.g. ``stream`` ends
        when the session reaches a terminal state).
        """
        argv = self._argv(*args)
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert proc.stdout is not None
        try:
            async for raw in proc.stdout:
                line = raw.decode(errors="replace").strip()
                if not line or line.startswith("[NodeFileStorage]"):
                    # SDK cache warnings go to stdout; skip them.
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    # Non-JSON line — ignore rather than kill the stream.
                    continue
        finally:
            if proc.returncode is None:
                proc.kill()
                await proc.wait()

    # ------------------------------------------------------------------
    # Streaming commands
    # ------------------------------------------------------------------

    async def stream(self, session_id: str) -> AsyncIterator[dict[str, Any]]:
        """Yield activities in real time: history first, then live updates.

        Ends when the session reaches a terminal state (bridge exits).
        """
        async for activity in self._iter_json_lines("stream", session_id):
            yield activity

    async def history(self, session_id: str) -> AsyncIterator[dict[str, Any]]:
        """Yield all past activities for a session."""
        async for activity in self._iter_json_lines("history", session_id):
            yield activity

    # ------------------------------------------------------------------
    # Command-style commands (single JSON result)
    # ------------------------------------------------------------------

    async def ask(
        self, session_id: str, prompt: str, timeout: float | None = None
    ) -> dict[str, Any]:
        """Send a message and wait for the agent's reply activity."""
        return await self._run_command("ask", session_id, prompt, timeout=timeout)

    async def wait_for(
        self, session_id: str, state: str, timeout: float | None = None
    ) -> dict[str, Any]:
        """Block until the session reaches ``state``; return session info."""
        return await self._run_command("waitFor", session_id, state, timeout=timeout)

    async def result(
        self, session_id: str, timeout: float | None = None
    ) -> dict[str, Any]:
        """Wait for session completion; return the outcome object."""
        return await self._run_command("result", session_id, timeout=timeout)

    async def info(self, session_id: str) -> dict[str, Any]:
        """Return session info as a dict."""
        return await self._run_command("info", session_id)

    async def approve(self, session_id: str) -> dict[str, Any]:
        """Approve a pending plan; returns session info."""
        return await self._run_command("approve", session_id)

    # ------------------------------------------------------------------
    # Sync fallback helpers
    # ------------------------------------------------------------------

    def stream_sync(self, session_id: str, timeout: float | None = None):
        """Blocking variant of stream() for non-async callers.

        Yields parsed activity dicts. Runs bridge via subprocess and reads
        stdout line by line.
        """
        argv = self._argv("stream", session_id)
        proc = subprocess.Popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        import signal
        from collections.abc import Iterator

        def _gen() -> Iterator[dict[str, Any]]:
            assert proc.stdout is not None
            try:
                for raw in proc.stdout:
                    line = raw.decode(errors="replace").strip()
                    if not line or line.startswith("[NodeFileStorage]"):
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()

        gen = _gen()
        if timeout is not None:
            # Arm a watchdog that kills the bridge when the caller abandons.
            def _watchdog() -> None:
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.kill()

            import threading

            t = threading.Thread(target=_watchdog, daemon=True)
            t.start()
        del signal  # reserved for future SIGINT handling
        return gen


def main() -> int:
    """CLI smoke test: stream a session (Ctrl+C to stop)."""
    import sys

    if len(sys.argv) < 3 or sys.argv[1] not in (
        "stream",
        "history",
        "info",
        "result",
    ):
        print("Usage: jules_stream_client.py <stream|history|info|result> <session-id>")
        return 1
    cmd, sid = sys.argv[1], sys.argv[2]

    async def _run() -> None:
        client = JulesStreamClient()
        if cmd in ("stream", "history"):
            async for activity in getattr(client, cmd)(sid):
                print(json.dumps(activity, ensure_ascii=False)[:200])
        else:
            print(json.dumps(await getattr(client, cmd)(sid), indent=2))

    if os.name == "nt":
        asyncio.run(_run())
    else:
        try:
            asyncio.run(_run())
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
