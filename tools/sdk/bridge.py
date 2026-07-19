"""Python wrapper for the @google/jules-sdk bridge.

Provides access to SDK-only features (streaming, ask, waitFor, run, result)
from Python tools via subprocess calls to the Node.js bridge.

Usage:
    from tools.sdk.bridge import JulesSDKBridge

    bridge = JulesSDKBridge()
    reply = bridge.ask("session-123", "What is the status?")
    bridge.wait_for("session-123", "awaitingPlanApproval")
    activities = bridge.history("session-123")
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

# Path to the compiled bridge.js — relative to this file
_BRIDGE_JS = Path(__file__).parent / "dist" / "bridge.js"


class JulesSDKBridge:
    """Call the @google/jules-sdk via the Node.js bridge.

    Requires:
        - Node.js >= 18
        - npm install (run from repo root to install @google/jules-sdk)
        - JULES_API_KEY environment variable

    The bridge is built with: npm run build:sdk
    """

    def __init__(self, bridge_path: Optional[Path] = None) -> None:
        self._bridge = bridge_path or _BRIDGE_JS
        if not self._bridge.exists():
            raise FileNotFoundError(
                f"Bridge not built. Run 'npm run build:sdk' first. "
                f"Expected at: {self._bridge}"
            )

    def _run(self, *args: str) -> Dict[str, Any]:
        """Run a bridge command and return parsed JSON output."""
        result = subprocess.run(
            ["node", str(self._bridge), *args],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            try:
                error = json.loads(error_msg)
                raise RuntimeError(f"SDK bridge error: {error.get('error', error_msg)}")
            except json.JSONDecodeError:
                raise RuntimeError(f"SDK bridge failed: {error_msg}")

        return json.loads(result.stdout)

    def _run_lines(self, *args: str) -> Generator[Dict[str, Any], None, None]:
        """Run a bridge command that outputs JSON lines (for streaming)."""
        proc = subprocess.Popen(
            ["node", str(self._bridge), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert proc.stdout is not None
        try:
            for line in proc.stdout:
                line = line.strip()
                if line:
                    yield json.loads(line)
        finally:
            proc.wait()
            if proc.returncode and proc.returncode != 0:
                stderr = proc.stderr.read() if proc.stderr else ""
                raise RuntimeError(f"SDK bridge error: {stderr.strip()}")

    # --- SDK-only features (not in JulesAPIClient) ---

    def ask(self, session_id: str, prompt: str) -> Dict[str, Any]:
        """Send a message and wait for the agent's reply.

        Args:
            session_id: The Jules session ID.
            prompt: The message to send.

        Returns:
            The agent's reply activity as a dict.
        """
        return self._run("ask", session_id, prompt)

    def wait_for(self, session_id: str, state: str) -> Dict[str, Any]:
        """Block until the session reaches a specific state.

        Args:
            session_id: The Jules session ID.
            state: Target state (e.g. "awaitingPlanApproval", "completed").

        Returns:
            Final session info as a dict.
        """
        return self._run("waitFor", session_id, state)

    def run(self, repo: str, branch: str, prompt: str) -> Dict[str, Any]:
        """Start an automated (fire-and-forget) task.

        Args:
            repo: GitHub repo in "owner/repo" format.
            branch: Base branch (e.g. "main").
            prompt: Task description.

        Returns:
            Dict with sessionId and state.
        """
        return self._run("run", repo, branch, prompt)

    def result(self, session_id: str) -> Dict[str, Any]:
        """Wait for session completion and return the outcome.

        Args:
            session_id: The Jules session ID.

        Returns:
            Session outcome as a dict.
        """
        return self._run("result", session_id)

    def stream(self, session_id: str) -> Generator[Dict[str, Any], None, None]:
        """Stream activities in real-time (generator).

        Yields activity dicts as they arrive. The generator blocks
        until the session reaches a terminal state.

        Args:
            session_id: The Jules session ID.

        Yields:
            Activity dicts.
        """
        yield from self._run_lines("stream", session_id)

    # --- Features also available in JulesAPIClient (SDK as alternative) ---

    def info(self, session_id: str) -> Dict[str, Any]:
        """Get session info as JSON."""
        return self._run("info", session_id)

    def approve(self, session_id: str) -> Dict[str, Any]:
        """Approve a pending plan."""
        return self._run("approve", session_id)

    def history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all past activities as a list of dicts."""
        return list(self._run_lines("history", session_id))
