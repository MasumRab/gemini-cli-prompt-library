# Jules Session Inspection Guide

This guide provides comprehensive instructions for inspecting Jules sessions using the dual storage approach (local JSON files + SQLite store). It covers available inspection methods, practical examples, troubleshooting workflows, and best practices.

## 1. Dual Storage Approach

Jules maintains session data in two synchronized storage systems:

### 1.1 Local JSON Files
- Located in: `~/.jules/sessions/`
- Each session stored as individual JSON files: `session_<session_id>.json`
- Contains raw session data, metadata, and events
- Human-readable and easily inspectable with standard tools like `jq`

### 1.2 SQLite Store
- Centralized database: `~/.jules/sessions.db`
- Schema optimized for querying and analytics
- Tables: `sessions`, `tasks`, `events`, `branches`
- Enables complex queries and aggregations

Both stores are updated atomically to ensure consistency.

## 2. Available Inspection Methods

### 2.1 jq-based Inspection
Use `jq` to query and filter JSON session files directly.

**Example: List all session files**
```bash
ls ~/.jules/sessions/
```

**Example: Extract session ID and status**
```bash
jq -r '.session_id, .status' ~/.jules/sessions/session_*.json
```

**Example: Find failed sessions**
```bash
jq -l '.status == "failed"' ~/.jules/sessions/*.json
```

### 2.2 JulesSessionStore API
Programmatic access via the JulesSessionStore class (Node.js/Python).
> **Note**: The enhanced methods in JulesSessionStore depend on the JulesSessionStore and SQLite store, not on external SDK calls. These methods provide programmatic access to session data through the dual storage system.

**Node.js Example:**
```javascript
const { JulesSessionStore } = require('@jules/session-store');

const store = new JulesSessionStore();

// Get all sessions
const sessions = await store.listSessions();

// Get specific session
const session = await store.getSession('session_id_here');

// Query sessions by status
const failedSessions = await store.querySessions({ status: 'failed' });
```

### 2.3 SQL Queries
Direct SQL queries against the SQLite database for advanced analytics.

**Example: Count sessions by status**
```sql
SELECT status, COUNT(*) as count 
FROM sessions 
GROUP BY status;
```

**Example: Find long-running tasks**
```sql
SELECT 
    s.session_id,
    t.task_id,
    t.branch_name,
    (t.updated_at - t.created_at) as duration
FROM tasks t
JOIN sessions s ON t.session_id = s.session_id
WHERE t.status = 'running'
AND (t.updated_at - t.created_at) > 3600;  -- More than 1 hour
```

**Example: Session timeline**
```sql
SELECT 
    e.timestamp,
    e.event_type,
    e.description
FROM events e
WHERE e.session_id = 'target_session_id'
ORDER BY e.timestamp;
```

### 2.4 Fallback Inspection Methods
If the JulesSessionStore is not available (e.g., in a minimal environment), users can fall back to inspecting the local JSON files directly in `~/.jules/sessions/` using various methods.

#### 2.4.1 jq-based Inspection
Use `jq` to query and filter JSON session files directly.

**Example: List all session files**
```bash
ls ~/.jules/sessions/
```

**Example: Extract session ID and status**
```bash
jq -r '.session_id, .status' ~/.jules/sessions/session_*.json
```

**Example: Find failed sessions**
```bash
jq -l '.status == "failed"' ~/.jules/sessions/*.json
```

#### 2.4.2 Direct File Inspection
Inspect session files directly using standard Unix tools.

**Example: View a specific session file**
```bash
cat ~/.jules/sessions/session_<session_id>.json
```

**Example: Extract specific fields with grep and cut**
```bash
grep -o '"session_id": "[^"]*"' ~/.jules/sessions/session_<session_id>.json | cut -d'"' -f4
```

#### 2.4.3 Python Scripting Approach
Use Python to parse and analyze JSON session files programmatically.

**Example: Python script to list session IDs and statuses**
```python
import json
import os
import glob

sessions_dir = os.path.expanduser("~/.jules/sessions/")
session_files = glob.glob(os.path.join(sessions_dir, "session_*.json"))

for file_path in session_files:
    with open(file_path, 'r') as f:
        session_data = json.load(f)
        print(f"Session ID: {session_data.get('session_id')}, Status: {session_data.get('status')}")
```

**Example: Find failed sessions using Python**
```python
import json
import os
import glob

sessions_dir = os.path.expanduser("~/.jules/sessions/")
session_files = glob.glob(os.path.join(sessions_dir, "session_*.json"))

failed_sessions = []
for file_path in session_files:
    with open(file_path, 'r') as f:
        session_data = json.load(f)
        if session_data.get('status') == 'failed':
            failed_sessions.append(session_data.get('session_id'))

print("Failed sessions:", failed_sessions)
```

#### 2.4.4 Direct Jules API curl commands
If Jules is running with an API server, you can inspect sessions via HTTP requests.

**Example: List all sessions (requires API key)**
```bash
curl -H "Authorization: Bearer $JULES_API_KEY" \
     http://localhost:8080/api/v1/sessions
```

**Example: Get specific session details**
```bash
curl -H "Authorization: Bearer $JULES_API_KEY" \
     http://localhost:8080/api/v1/sessions/<session_id>
```

**Example: Find failed sessions via API**
```bash
curl -H "Authorization: Bearer $JULES_API_KEY" \
     "http://localhost:8080/api/v1/sessions?status=failed"
```

## 3. Practical Examples for Branch/Task Targeting

### 3.1 Inspect Sessions for Specific Branch
**Using jq:**
```bash
# Find all session files containing work on branch 'feature/login'
grep -l '"branch_name": "feature/login"' ~/.jules/sessions/*.json | xargs jq '.session_id'
```

**Using JulesSessionStore API:**
```javascript
const sessions = await store.querySessions({ 
    branch: 'feature/login' 
});
```

**Using SQL:**
```sql
SELECT DISTINCT s.session_id, s.status
FROM sessions s
JOIN tasks t ON s.session_id = t.session_id
WHERE t.branch_name = 'feature/login';
```

### 3.2 Target Specific Task Within Session
**Using jq:**
```bash
# Get task details for task_id 'task_123' in all sessions
jq -r '.tasks[] | select(.task_id == "task_123")' ~/.jules/sessions/*.json
```

**Using JulesSessionStore API:**
```javascript
const task = await store.getTask('task_123');
```

**Using SQL:**
```sql
SELECT * 
FROM tasks 
WHERE task_id = 'task_123';
```

### 3.3 Find Sessions with Failed Tasks
**Using jq:**
```bash
jq -l '.tasks[] | select(.status == "failed") | .session_id' ~/.jules/sessions/*.json
```

**Using JulesSessionStore API:**
```javascript
const failedTaskSessions = await store.querySessions({
    'tasks.status': 'failed'
});
```

**Using SQL:**
```sql
SELECT DISTINCT s.session_id
FROM sessions s
JOIN tasks t ON s.session_id = t.session_id
WHERE t.status = 'failed';
```

## 4. Troubleshooting Workflows

### 4.1 Diagnosing Failed Sessions
**Step 1: Identify failed sessions**
```bash
# Using SQL
sqlite3 ~/.jules/sessions.db "SELECT session_id, created_at FROM sessions WHERE status = 'failed';"
```

**Step 2: Examine session details**
```bash
# Using jq for a specific failed session
jq '. | {session_id, status, error: .error_message, tasks: [.tasks[] | {task_id, status, error}] }' \
   ~/.jules/sessions/session_<failed_session_id>.json
```

**Step 3: Check event timeline**
```bash
# Using SQL to get events leading to failure
sqlite3 ~/.jules/sessions.db "
    SELECT timestamp, event_type, description 
    FROM events 
    WHERE session_id = 'session_<failed_session_id>' 
    ORDER BY timestamp;
"
```

### 4.2 Investigating Stuck/Running Sessions
**Step 1: Find long-running sessions**
```sql
SELECT 
    s.session_id,
    s.created_at,
    (strftime('%s', 'now') - strftime('%s', s.updated_at)) as seconds_since_update
FROM sessions s
WHERE s.status = 'running'
AND (strftime('%s', 'now') - strftime('%s', s.updated_at)) > 1800;  -- 30 minutes
```

**Step 2: Check recent activity**
```bash
# Look at latest events
sqlite3 ~/.jules/sessions.db "
    SELECT e.timestamp, e.event_type, e.description
    FROM events e
    JOIN sessions s ON e.session_id = s.session_id
    WHERE s.session_id = 'stuck_session_id'
    ORDER BY e.timestamp DESC
    LIMIT 10;
"
```

**Step 3: Verify task progress**
```sql
SELECT 
    t.task_id,
    t.status,
    t.created_at,
    t.updated_at,
    (strftime('%s', t.updated_at) - strftime('%s', t.created_at)) as duration
FROM tasks t
WHERE t.session_id = 'stuck_session_id'
ORDER BY t.updated_at DESC;
```

### 4.3 Recovering from Corrupted Sessions
**Step 1: Verify store integrity**
```bash
# Check SQLite database integrity
sqlite3 ~/.jules/sessions.db "PRAGMA integrity_check;"
```

**Step 2: Compare JSON and SQLite counts**
```bash
# Count JSON files
json_count=$(ls ~/.jules/sessions/session_*.json 2>/dev/null | wc -l)

# Count SQLite records
sqlite_count=$(sqlite3 ~/.jules/sessions.db "SELECT COUNT(*) FROM sessions;")

echo "JSON files: $json_count"
echo "SQLite records: $sqlite_count"
```

**Step 3: Re-sync if needed**
```bash
# Using JulesSessionStore API to rebuild SQLite from JSON
node -e "
const { JulesSessionStore } = require('@jules/session-store');
const fs = require('fs');
const path = require('path');

async function rebuild() {
  const store = new JulesSessionStore();
  const sessionDir = path.join(process.env.HOME, '.jules', 'sessions');
  const files = fs.readdirSync(sessionDir).filter(f => f.startsWith('session_') && f.endsWith('.json'));
  
  for (const file of files) {
    const data = JSON.parse(fs.readFileSync(path.join(sessionDir, file), 'utf8'));
    await store.upsertSession(data);
  }
  console.log('Rebuilt SQLite store from JSON files');
}

rebuild().catch(console.error);
"
```

## 5. Best Practices for Session Analysis

### 5.1 Regular Maintenance
- **Weekly**: Run integrity checks on SQLite database
- **Monthly**: Archive old sessions (older than 90 days) to free space
- **After incidents**: Verify consistency between JSON and SQLite stores

### 5.2 Efficient Querying
- Use SQL for aggregations and complex joins
- Use jq for quick ad-hoc inspection of specific files
- Use JulesSessionStore API for programmatic access in scripts/tools
- Create indexes on frequently queried columns (session_id, status, branch_name)

### 5.3 Performance Optimization
- Limit JSON file inspection to specific time ranges when possible
- Use SQLite's EXPLAIN QUERY PLAN to optimize slow queries
- Consider materialized views for common session analytics
- Use pagination when retrieving large numbers of sessions

### 5.4 Security Considerations
- Session files may contain sensitive data (API keys, tokens) - inspect carefully
- Ensure proper file permissions: `chmod 700 ~/.jules/sessions`
- Encrypt sensitive fields if required by organizational policy
- Audit access to session data for compliance

### 5.5 Recommended Tools
- **jq**: For JSON processing and filtering
- **sqlite3**: CLI for SQLite database interaction
- **DB Browser for SQLite**: GUI tool for database exploration
- **Jules CLI**: Built-in inspection commands (`jules session list`, `jules session show`)
- **Custom scripts**: Leverage JulesSessionStore API for tailored inspection workflows

## 6. Reference: Enhanced Session Store Capabilities

### 6.1 JulesSessionStore Features
- **Atomic Operations**: All writes are transactional across both stores
- **Change Listeners**: Register callbacks for session updates
- **Query Optimization**: Automatic use of appropriate store based on query type
- **Backup/Export**: Built-in methods to export sessions as JSON or CSV
- **Import/Migration**: Tools to migrate from legacy storage formats

### 6.2 Available Indexes (SQLite)
- `sessions(session_id)` - Primary key
- `sessions(status)` - For status-based queries
- `sessions(created_at)` - For time-range queries
- `tasks(session_id, task_id)` - Composite index for task lookup
- `events(session_id, timestamp)` - For chronological event retrieval

### 6.3 Store Consistency Guarantees
- Every session write updates both JSON and SQLite within same transaction
- Read operations can specify preferred store (JSON for raw data, SQLite for queries)
- Automatic reconciliation on startup if inconsistency detected
- Version tracking to detect schema mismatches

---
*Last Updated: $(date +%Y-%m-%d)*
*Jules Version: Enhanced Session Store v2.1+