# SDK Integration Plan

**Status:** Planned (not implemented)  
**Created:** 2026-08-29  
**Priority:** High

---

## 1. Background

Two client implementations exist:

| Client | Language | Capabilities |
|--------|----------|---------------|
| `JulesAPIClient` | Python | REST API — list, get, send, create |
| `JulesSDKBridge` | TS→Python | Streaming, async ask, waitFor, result |

**Current gaps:**
- Session tools → JulesAPIClient ✅
- Forensics tools → Dead import ❌ (never uses SDK)
- Polling workarounds instead of streaming ⚠️

---

## 2. Gap Analysis

### 2.1 Forensics — Dead Import

```python
# tools/forensics/generate_report.py line 22
from api.jules_api_client import JulesAPIClient  # ← NEVER USED
```

Forensics reports are manual templates, not data-driven.

### 2.2 Session Tools — Polling

```python
# Current jules_monitor.py pattern
while True:
    activities = list(client.list_activities(session_id))
    time.sleep(2)  # Inefficient polling
```

---

## 3. SDK Commands Reference

### JulesSDKBridge API (SDK-unique)

```python
from tools.sdk.bridge import JulesSDKBridge
bridge = JulesSDKBridge()

bridge.ask(session_id, prompt)        # Send + await reply
bridge.wait_for(session_id, state)   # Block until state
bridge.stream(session_id)            # Real-time stream
bridge.result(session_id)            # Wait for completion
bridge.run(repo, branch, prompt)     # Fire-and-forget
bridge.info(session_id)              # Shared with REST
bridge.approve(session_id)          # Shared with REST
bridge.history(session_id)           # Shared with REST
```

### JulesAPIClient API (REST)

```python
from tools.api.jules_api_client import JulesAPIClient
client = JulesAPIClient()

client.list_sessions(repo=..., state=...)
client.get_session(session_id)
client.list_activities(session_id)
client.send_message(session_id, prompt)
client.create_session(repo, branch, prompt)
client.list_sources()
```

### When to Use Which

| Use Case | Client |
|----------|--------|
| List/filter sessions | JulesAPIClient |
| Await agent reply | JulesSDKBridge |
| Block for state | JulesSDKBridge |
| Real-time stream | JulesSDKBridge |
| Get completion | JulesSDKBridge |
| Create session | JulesAPIClient |
| Fetch activities (batch) | JulesAPIClient |

---

## 4. Implementation Tasks

### Task 1: Wire Forensics to SDK (HIGH)

**File:** `tools/forensics/generate_report.py`

Target state:
```python
from tools.sdk.bridge import JulesSDKBridge
from tools.api.jules_api_client import JulesAPIClient

def generate_failure_analysis(session_id: str, repo: str, output_dir: str):
    client = JulesAPIClient()
    session = client.get_session(session_id)
    activities = list(client.list_activities(session_id, page_size=100))
    errors = [a for a in activities if 'error' in a]
    
    report = {
        'session_id': session_id,
        'state': session.get('state'),
        'failure_count': len(errors),
        'activities': activities,
    }
    write_report(output_dir, report)
```

### Task 2: Create analyze_failures.py (HIGH)

**File:** `tools/forensics/analyze_failures.py`

```python
#!/usr/bin/env python3
"""Analyze failed sessions for forensics report."""

from tools.api.jules_api_client import JulesAPIClient

def analyze_session_failure(session_id: str, client: JulesAPIClient = None) -> dict:
    client = client or JulesAPIClient()
    session = client.get_session(session_id)
    activities = list(client.list_activities(session_id))
    errors = [a for a in activities if 'error' in a]
    return {
        'session_id': session_id,
        'state': session.get('state'),
        'errors': errors,
        'total_activities': len(activities),
    }
```

### Task 3: Create analyze_patterns.py (HIGH)

**File:** `tools/forensics/analyze_patterns.py`

```python
#!/usr/bin/env python3
"""Analyze session patterns (reuse, redundancy, batch outcomes)."""

from tools.api.jules_api_client import JulesAPIClient

def analyze_session_reuse(repo: str, client: JulesAPIClient = None) -> dict:
    client = client or JulesAPIClient()
    sessions = list(client.list_sessions(repo=repo))
    
    by_key = {}
    for s in sessions:
        pr = s.get('sourceContext', {}).get('pr', 'unknown')
        sha = s.get('sourceContext', {}).get('headSha', 'unknown')
        by_key.setdefault(f"{pr}::{sha}", []).append(s)
    
    return {'duplicates': {k:v for k,v in by_key.items() if len(v) > 1}}
```

### Task 4: Replace Polling in monitor (MEDIUM)

**File:** `tools/sessions/jules_monitor.py`

Replace polling loop:
```python
# BEFORE (polling)
while True:
    activities = list(client.list_activities(session_id))
    time.sleep(2)

# AFTER (streaming)
from tools.sdk.bridge import JulesSDKBridge
bridge = JulesSDKBridge()
for activity in bridge.stream(session_id):
    if "agentMessaged" in activity:
        return activity
```

### Task 5: Add SDK to send_message (MEDIUM)

**File:** `tools/sessions/jules_send_message.py`

```python
def send_with_reply(session_id: str, prompt: str, await_reply: bool = False):
    from tools.sdk.bridge import JulesSDKBridge
    bridge = JulesSDKBridge()
    
    if await_reply:
        return bridge.ask(session_id, prompt)  # SDK handles send + await
    
    client = JulesAPIClient()
    return client.send_message(session_id, prompt)
```

### Task 6: Unified SDK Facade (LOW)

**File:** `tools/sdk/unified.py`

```python
from tools.api.jules_api_client import JulesAPIClient
from tools.sdk.bridge import JulesSDKBridge

class JulesClient:
    def __init__(self):
        self._rest = JulesAPIClient()
        self._sdk = JulesSDKBridge()
    
    # REST methods
    def list_sessions(self, repo=None, state=None):
        return self._rest.list_sessions(repo=repo, state=state)
    
    # SDK methods
    def stream(self, session_id):
        return self._sdk.stream(session_id)
    
    def ask(self, session_id, prompt):
        return self._sdk.ask(session_id, prompt)
    
    def wait_for(self, session_id, state):
        return self._sdk.wait_for(session_id, state)
```

---

## 5. Implementation Order

| Order | Task | Priority | Time |
|-------|------|----------|------|
| 1 | Wire forensics to REST | High | 30 min |
| 2 | Create analyze_failures.py | High | 1 hour |
| 3 | Create analyze_patterns.py | High | 1 hour |
| 4 | Replace polling in monitor | Medium | 30 min |
| 5 | Add SDK to send_message | Medium | 30 min |
| 6 | Create unified facade | Low | 1 hour |

---

## 6. Testing

```bash
# Test bridge
node tools/sdk/dist/bridge.js info 596003508416904399

# Test Python wrapper
python3 -c "from tools.sdk.bridge import JulesSDKBridge; print(JulesSDKBridge().info('596003508416904399'))"

# Build SDK if needed
npm run build:sdk
```

---

## 7. Open Questions

1. SDK raises on timeout — need retry logic?
2. Should REST remain fallback for SDK failures?
3. Prefer unified client or explicit REST/SDK choice?

---

## 8. Related Documents

- `tools/sdk/bridge.py` — Python SDK wrapper
- `tools/sdk/src/bridge.ts` — TypeScript SDK source
- `tools/api/jules_api_client.py` — REST API client
- `docs/forensics/WORKSPACE_INTEGRATION.md` — Forensics workspace design
- `docs/OUTSTANDING_TASKS.md` — Open tasks list
