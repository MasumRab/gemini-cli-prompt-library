# Transitioning Jules Session Monitoring from Polling to Streaming: Complete Migration Guide

## Executive Summary

This document consolidates research on migrating Jules session monitoring from REST polling to SDK streaming, incorporating actual codebase implementations, runbook workflows, and existing streaming infrastructure. The Jules SDK provides three streaming modes (`history()`, `updates()`, `stream()`) returning `AsyncIterator<Activity>` objects, enabling real-time monitoring with sub-second latency. However, the current repository already contains a working TypeScript SDK bridge (`tools/sdk/src/bridge.ts`) that exposes streaming to Python/shell tools via subprocess calls. The migration strategy should enhance Python tools to consume this bridge's streaming output natively via async subprocess wrappers, rather than replacing one-time sync scripts. Critical runbook workflows—daily triage daemon, recovery manager, prompt logging, and transport fallback chains—must be preserved throughout the transition.

## Current Polling Mechanisms in the Codebase

### Continuous Polling Daemons (Primary Migration Targets)

| Component | Type | Interval | Purpose | Streaming Candidate |
|-----------|------|----------|---------|---------------------|
| `tools/sessions/jules_monitor.py` | Continuous daemon | 60s (configurable via `MONITOR_INTERVAL` / `--interval`) | Session health monitoring + auto-recovery via `JulesRecoveryManager` | **YES** — replace `time.sleep()` loop with SDK bridge `stream` |
| `tools/api/jules_api_client.py::wait_for_state()` | Sync polling helper | 2s default (configurable) | Block until session reaches target state (e.g., `AWAITING_PLAN_APPROVAL`) | **YES** — replace with SDK `waitFor` bridge command |
| `tools/api/jules_api_client.py::ask()` | Sync polling helper | 2s hardcoded | Send message + await `agentMessaged` activity reply | **YES** — replace with SDK `ask` bridge command |

### One-Time Batch Scripts (NOT Streaming Candidates)

| Component | Type | Interval | Purpose | Streaming Candidate |
|-----------|------|----------|---------|---------------------|
| `tools/shell/retrieve_sessions.sh` | One-time batch | 1s between calls (API politeness) | Fetch problematic session details from list | **NO** — batch fetch, not continuous monitoring |
| `tools/shell/jules_sync_all.sh` | One-time batch | None (sequential) | Sync local JSON files with remote API state | **NO** — metadata sync, not activity streaming |

### SDK Internal Polling (Backing for Streaming Methods)

| Component | Type | Interval | Purpose |
|-----------|------|----------|---------|
| `NetworkAdapter.rawStream()` (SDK) | Internal polling | 5000ms default | Backs `updates()` stream; paginates then sleeps |

### Pagination Generators (Not Polling)

- `JulesAPIClient.list_sessions()` — Generator handling pagination automatically via `nextPageToken`
- `JulesAPIClient.list_activities()` — Generator with `max_results` early-stop optimization

---

## Jules SDK Streaming Capabilities

### Three Streaming Modes (via `Session` methods)

| Method | Description | Implementation |
|--------|-------------|----------------|
| `history()` | Cold stream: yields past activities from local storage, then hydrates from network (with 404 retry) | `packages/core/src/activities/client.ts` |
| `updates()` | Hot stream: yields only future activities from network, polling when no more pages | `NetworkAdapter.rawStream()` with deduplication |
| `stream()` | Hybrid: delegates to `_activities.stream()` yielding `history()` then `updates()`, optional originator filter | `packages/core/src/session.ts` |

All return `AsyncIterator<Activity>`.

### Activity Object Structure

Types include: `planGenerated`, `agentMessaged`, `progressUpdated`, `sessionCompleted`. Each carries `artifacts` (code diffs, shell output, media).

### Built-In Resilience (Handled by SDK)

- Pagination via `nextPageToken`
- Deduplication using high-water mark (`createTime`) and last-seen ID
- Initial 404 retry with exponential backoff (10 retries, 1s initial, 30s cap) via `withFirstRequestRetry`
- After first successful network call, retries disabled for subsequent errors

### No External Streaming Protocol

No WebSocket, SSE, or gRPC — streaming abstraction built atop HTTP polling.

---

## Existing Streaming Infrastructure: SDK Bridge

The repository **already has a working streaming bridge** at `tools/sdk/src/bridge.ts` (compiled to `tools/sdk/dist/bridge.js`):

```bash
# Commands exposed:
node tools/sdk/dist/bridge.js stream <sessionId>      # history() then updates() — JSON lines
node tools/sdk/dist/bridge.js history <sessionId>     # history() only — JSON lines
node tools/sdk/dist/bridge.js ask <sessionId> <prompt> # sendMessage + await reply
node tools/sdk/dist/bridge.js waitFor <sessionId> <state> # waitFor(targetState)
node tools/sdk/dist/bridge.js result <sessionId>      # await completion
node tools/sdk/dist/bridge.js info <sessionId>        # session info
node tools/sdk/dist/bridge.js approve <sessionId>     # approve plan
```

**Runbooks explicitly reference this as fallback** (`docs/runbooks/session_recovery.md`):
> "If REST polling times out (>30s, or >300s in a monitor loop), fall back to SDK bridge or CLI — see Transport fallbacks below."

---

## Runbook-Defined Operational Workflows (Must Preserve)

### Daily Triage Workflow (`docs/runbooks/session_runbook.md`)

1. **List sessions with grading**: `commands/jules-list`
2. **Run monitor daemon**: `python3 -m tools.sessions.jules_monitor --daemon`
3. **Check stuck sessions**: `python3 -m tools.sessions.jules_recovery_manager <SESSION_ID>`
4. **Address unanswered questions**: `python3 -m tools.sessions.analyze_unanswered <SESSION_ID>`
5. **Enhanced inspection queries**:
   - `find_stale_sessions --hours 2`
   - `find_retryable_failed_sessions`
   - `list_sessions --label "bug" --label "urgent"`

### Recovery Playbook (`docs/runbooks/session_recovery.md`)

| State | Action | Command |
|-------|--------|---------|
| `FAILED` | Retry | `jules_recovery_manager` → `retry` strategy |
| `PAUSED` / `AWAITING_USER_FEEDBACK` / `AWAITING_PLAN_APPROVAL` | Approve / Send guidance | `jules_approve_plan` / `jules_send_message` |
| `IN_PROGRESS` | Monitor; if REST times out → SDK bridge | `node tools/sdk/dist/bridge.js history/stream <sid>` |
| `COMPLETED` | Audit PR | `jules_audit_session_pr.py` (auto-triggered) |

### Transport Fallback Chain (Critical)

1. **REST API** (primary) — `jules_api_client.py` polling
2. **SDK Bridge** (fallback) — `history` (one-shot) or `stream` (real-time)
3. **Jules CLI** (last resort) — `jules remote pull --session <id>`

All fallbacks write to same per-repo workspace (`workspaces/<owner>/<repo>/`).

### Prompt Logging Requirement

Every message sent to a Jules session must be logged to:
- `skills/jules-sessions/references/sent_responses.md` (global)
- `workspaces/<owner>/<repo>/prompts/sent_responses.md` (workspace)

Format:
```yaml
session_id: "<id>"
prompt_type: "nudge|rectification|approve|follow-up"
prompt_sent: "Verbatim text"
outcome: "QUEUED|COMPLETED|FAILED"
```

### Workspace Isolation

Per-repo workspace structure documented in `docs/runbooks/workspace_isolation.md`.

---

## Skills & Integration Points (Must Remain Compatible)

| Skill / Tool | Purpose | Streaming Impact |
|--------------|---------|------------------|
| `skills/jules-api/` | API reference & quickstart | Update examples to show streaming |
| `skills/jules-session-manager/` | Session lifecycle, PR triage | Uses `jules_recovery_manager`, `session_pr_triage.py` |
| `tools/sessions/jules_recovery_manager.py` | State analysis → action pipeline | Consumes activities; must work with streamed input |
| `tools/sessions/analyze_unanswered.py` | Categorize awaiting sessions | Uses activity polling; migrate to stream |
| `tools/sessions/find_stale_sessions.py` | Triage query | Uses `list_sessions` + activity timestamps |
| `tools/sessions/find_retryable_failed_sessions.py` | Triage query | Same |
| `tools/pr/jules_audit_session_pr.py` | Post-completion safety audit | Triggered by recovery manager on `COMPLETED` |
| `skills/jules-sessions/references/sent_responses.md` | Prompt log | Must continue receiving entries |

---

## Latency & Interval Reality Check

| Metric | Current (Codebase) | Streaming Target |
|--------|-------------------|------------------|
| Monitor daemon interval | 60s (`MONITOR_INTERVAL`) | Event-driven (sub-second) |
| `wait_for_state()` poll | 2s default | SDK `waitFor` (bridge) |
| `ask()` activity poll | 2s hardcoded | SDK `ask` (bridge) |
| SDK `rawStream()` poll | 5s default | N/A (backs `updates()`) |
| REST timeout threshold | >30s (single), >300s (monitor) | Bridge `stream` avoids entirely |
| Third-party uptime | 100% (mostly), 99.86% (Nov 2025) | Maintain or improve |
| Avg. response time | 142–211ms | ≤211ms |

---

## Implementation Plan: Streaming Migration

### Phase 1: Build Async Bridge Wrapper (Foundation)

Create `tools/api/jules_stream_client.py` — async Python wrapper around SDK bridge:

```python
# tools/api/jules_stream_client.py
import asyncio
import json
from typing import AsyncIterator, Dict, Any, Optional

async def stream_activities(session_id: str, mode: str = "stream") -> AsyncIterator[Dict[str, Any]]:
    """
    Consume SDK bridge streaming output as async iterator.
    mode: "stream" (history + updates) | "history" | "updates"
    """
    cmd = ["node", "tools/sdk/dist/bridge.js", mode, session_id]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        async for line in proc.stdout:
            line = line.decode().strip()
            if line:
                yield json.loads(line)
    finally:
        proc.terminate()
        await proc.wait()

async def ask_session(session_id: str, prompt: str) -> Dict[str, Any]:
    cmd = ["node", "tools/sdk/dist/bridge.js", "ask", session_id, prompt]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    return json.loads(stdout.decode().strip())

async def wait_for_state(session_id: str, target_state: str) -> Dict[str, Any]:
    cmd = ["node", "tools/sdk/dist/bridge.js", "waitFor", session_id, target_state]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    return json.loads(stdout.decode().strip())
```

**Prerequisites**: Ensure `tools/sdk/dist/bridge.js` is built (`npm run build` in `tools/sdk/`). Add build step to CI / setup.

### Phase 2: Migrate `jules_monitor.py` (Highest Impact)

Replace polling loop with async stream consumer:

```python
# tools/sessions/jules_monitor.py (updated monitor_loop)
from tools.api.jules_stream_client import stream_activities

async def monitor_loop_async(once=False):
    client = JulesAPIClient()
    manager = JulesRecoveryManager(client)

    print(f"Jules Monitor started (streaming mode)")

    while True:
        try:
            print(f"[{time.ctime()}] Checking sessions...")
            for session in client.list_sessions(page_size=10, max_results=10):
                session_id = session["name"]
                
                # Stream activities for this session
                async for activity in stream_activities(session_id, mode="stream"):
                    # Process activity in real-time
                    if activity.get("type") in ["planGenerated", "agentMessaged", "progressUpdated"]:
                        report = manager.analyze_session_state(session_id)
                        if report["action"] in ["retry", "approve", "AUDIT"]:
                            manager.trigger_recovery(session_id, report["action"])
                    # Terminal state detection
                    if activity.get("type") in ["sessionCompleted", "sessionFailed"]:
                        break

            if once:
                break
            await asyncio.sleep(MONITOR_INTERVAL)  # Inter-session check interval
        except KeyboardInterrupt:
            print("Monitor stopping...")
            break
        except Exception as e:
            print(f"Error in monitor loop: {e}")
            await asyncio.sleep(10)
```

**Daemon compatibility**: Keep `--daemon`, `--stop`, `--once`, `--interval` CLI interface. Use `asyncio.run(monitor_loop_async())` in `main()`.

### Phase 3: Migrate `JulesAPIClient` Polling Helpers

Replace `wait_for_state()` and `ask()` with bridge-backed async versions:

```python
# In JulesAPIClient class (tools/api/jules_api_client.py)

async def wait_for_state_async(
    self,
    session_id: str,
    target_state: str,
    timeout: float = 300,
) -> Dict[str, Any]:
    """Async version using SDK bridge waitFor."""
    from tools.api.jules_stream_client import wait_for_state
    return await wait_for_state(session_id, target_state)

async def ask_async(self, session_id: str, question: str, timeout: float = 120) -> Dict[str, Any]:
    """Async version using SDK bridge ask."""
    from tools.api.jules_stream_client import ask_session
    return await ask_session(session_id, question)

# Keep synchronous versions for backward compatibility
def wait_for_state(self, ...):  # existing implementation
    ...

def ask(self, ...):  # existing implementation
    ...
```

Update `JulesRecoveryManager` and CLI tools to use async versions where beneficial.

### Phase 4: Migrate Recovery Manager Activity Fetching

Replace `list_activities()` polling with `stream_activities(mode="history")` for one-shot fetches:

```python
# tools/sessions/jules_recovery_manager.py
from tools.api.jules_stream_client import stream_activities

async def get_recent_activities(session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    activities = []
    async for activity in stream_activities(session_id, mode="history"):
        activities.append(activity)
        if len(activities) >= limit:
            break
    return activities
```

### Phase 5: Shell Script Enhancements (Optional)

For `retrieve_sessions.sh` and `jules_sync_all.sh` — these are batch sync tools. Streaming not applicable. Instead:
- Add `--stream` flag to fetch activities via bridge `history` for richer detail
- Keep existing `curl` + `sleep 1` for session metadata (API politeness)

### Phase 6: Validation & Rollout

| Step | Validation |
|------|------------|
| 1. Bridge build | `npm run build` in `tools/sdk/` produces `dist/bridge.js` |
| 2. Unit tests | `stream_activities` yields expected Activity objects; error handling on bridge failure |
| 3. Monitor parity | Run old + new monitor in parallel; compare `analyze_session_state` hypotheses |
| 4. Recovery parity | Trigger recovery on `FAILED`/`PAUSED` sessions; verify same actions executed |
| 5. Runbook compliance | Execute daily triage workflow; verify all commands work |
| 6. Prompt logging | Confirm `sent_responses.md` entries still created |
| 7. Fallback chain | Simulate REST timeout; verify bridge `history`/`stream` invoked |
| 8. Workspace isolation | Verify per-repo workspace writes unchanged |

**Rollout Strategy**:
- Week 1: Deploy async bridge wrapper + feature flag (`JULES_STREAMING=1`)
- Week 2: Enable for `jules_monitor.py` only; compare latency/request metrics
- Week 3: Migrate `wait_for_state`/`ask` in recovery manager
- Week 4: Full regression suite; deprecate polling helpers (keep for fallback)

---

## Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SDK pre-1.0 instability (0.x versions) | High (bi-weekly releases) | Breaking changes to streaming API | Pin `@google/jules-sdk` version in `tools/sdk/package.json`; CI check for method signatures |
| Bridge subprocess crashes / stdout corruption | Medium | Monitor loses event stream | Supervise subprocess; auto-restart on non-zero exit; stderr logging |
| Increased memory from long-lived async iterators | Low | OOM in long-running monitor | Bounded buffers; periodic stream recreation |
| Skills relying on synchronous `wait_for_state`/`ask` | Low | Blocking calls stall event loop | Provide async variants; keep sync versions via thread pool fallback |
| Prompt logging race conditions | Low | Missing log entries | Ensure logging is synchronous/atomic before async continuation |

---

## Version & Compatibility Reality

- SDK: `@google/jules-sdk` (npm), version pinned in `tools/sdk/package.json`
- Bridge compiles to `tools/sdk/dist/bridge.js` — **must be built before use**
- Python tools assume bridge exists; add `npm run build` to setup scripts / CI
- No native Python SDK exists; bridge subprocess is the integration path
- Polling helpers (`wait_for_state`, `ask`) retained for backward compatibility and fallback

---

## Conclusion

Injecting streaming into Jules session monitoring is achieved by **consuming the existing SDK bridge's streaming output** via an async Python wrapper, replacing the polling loops in `jules_monitor.py`, `jules_api_client.py`, and `jules_recovery_manager.py`. The shell sync scripts (`retrieve_sessions.sh`, `jules_sync_all.sh`) serve a different purpose (batch metadata sync) and should not be converted to streaming. All runbook workflows, transport fallback chains, prompt logging, and workspace isolation conventions are preserved. With the bridge already implemented, the migration is a matter of wiring Python asyncio to the TypeScript streaming backend — a focused, low-risk enhancement that delivers sub-second activity visibility while maintaining operational continuity.

---

## Sources

[1] `/home/masum/github/remote/jules/tools/shell/retrieve_sessions.sh`  
[2] `/home/masum/github/remote/jules/tools/shell/jules_sync_all.sh`  
[3] `/home/masum/github/remote/jules/tools/sessions/jules_monitor.py`  
[4] `/home/masum/github/remote/jules/tools/api/jules_api_client.py`  
[5] `/home/masum/github/remote/jules/tools/sdk/src/bridge.ts`  
[6] `/home/masum/github/remote/jules/docs/runbooks/session_runbook.md`  
[7] `/home/masum/github/remote/jules/docs/runbooks/session_recovery.md`  
[8] `/home/masum/github/remote/jules/tools/sessions/jules_recovery_manager.py`  
[9] `/home/masum/github/remote/jules/docs/planning/STREAMING_RESEARCH.md`  
[10] `https://raw.githubusercontent.com/google-labs-code/jules-sdk/main/README.md`  
[11] `https://raw.githubusercontent.com/google-labs-code/jules-sdk/main/packages/core/src/network/adapter.ts`  
[12] `https://raw.githubusercontent.com/google-labs-code/jules-sdk/main/packages/core/src/streaming.ts`  
[13] `https://deepwiki.com/google-labs-code/jules-sdk/2.3-activity-streaming`  
[14] `https://blog.axway.com/product-insights/amplify-platform/streams/benchmark-server-sent-events-versus-polling`  
[15] `https://coinpaprika.com/education/polling-vs-streaming-for-price-updates-when-each-makes-sense/`  
[16] `https://registry.npmjs.org/@google/jules-sdk`  
[17] `https://raw.githubusercontent.com/google-labs-code/jules-sdk/main/packages/core/src/polling.ts`  
[18] `https://raw.githubusercontent.com/google-labs-code/jules-sdk/main/packages/core/package.json`  
[19] `https://eliteai.tools/tool/jules/uptime-status`  
[20] `https://github.com/Helloguys3324/jules-control-center/blob/main/jules_benchmark_results.md`