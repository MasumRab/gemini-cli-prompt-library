# Jules Session Store Migration Plan

## Context
The local SQLite store (`~/.jules/store.db`) is a **cache** continuously refreshed from the Jules API via `upsert_session()`. It supports forensics tasks (T-29, T-30, T-33) and operations queries.

**Current state:** Schema has basic session/activity tables but lacks columns for forensics/operations queries (T-29, T-30, T-33).

---

## Completed Work

| Task | Status |
|------|--------|
| Core schema review | ✅ Done |
| Null-safe migration design | ✅ Done |
| Sync-compatible migration script | ✅ Written |
| Plan document | ✅ This document |

---

## Migration Scope (Minimal Essential)

### 7 New Columns (sessions table)

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `session_type` | TEXT | ❌ | `'unknown'` | Classification: review/auto-fix/walkthrough/rebuild/resolve/address/triage/backlog |
| `outcome` | TEXT | ✅ | NULL | Terminal state: success/partial/failed/timeout |
| `retry_of_session_id` | TEXT | ✅ | NULL | Self-ref FK for retry chains (T-29, T-30) |
| `retry_count` | INTEGER | ❌ | 0 | Retry attempt counter |
| `send_message_count` | INTEGER | ❌ | 0 | Free sendMessage retries (T-30) |
| `verdict` | TEXT | ✅ | NULL | approve/comment/block (T-33) |
| `quality_score` | REAL | ✅ | NULL | 0-1 confidence (T-33) |

### 3 Indexes

| Index | Table | Columns | Purpose |
|-------|-------|---------|---------|
| `idx_sessions_type` | sessions | session_type | Filter by session_type |
| `idx_sessions_outcome` | sessions | outcome | Filter terminal states |
| `idx_sessions_retry` | sessions | retry_of_session_id | Retry chain queries |

### Backfill (Idempotent)

```sql
UPDATE sessions SET session_type = CASE
    WHEN tags LIKE '%auto-fix%' THEN 'auto-fix'
    WHEN tags LIKE '%force-review%' THEN 'force-review'
    WHEN tags LIKE '%walkthrough%' THEN 'walkthrough'
    WHEN tags LIKE '%rebuild%' THEN 'rebuild'
    WHEN tags LIKE '%resolve%' THEN 'resolve-conflicts'
    WHEN tags LIKE '%address%' THEN 'address-comments'
    WHEN tags LIKE '%backlog%' THEN 'backlog-review'
    WHEN tags LIKE '%triage%' THEN 'issue-triage'
    ELSE 'review'
END WHERE session_type = 'unknown';
```

---

## Sync Pattern Compatibility

The local store is a **cache** continuously refreshed from Jules API via `upsert_session()`. Migration must support:

| Operation | Trigger | Columns Updated |
|-----------|---------|-----------------|
| `upsert_session()` | Periodic API poll | All columns refreshed |
| `record_send_message()` | After sendMessage API | `send_message_count`, `last_send_message` |
| `record_retry_session()` | New retry created | `retry_of_session_id`, `retry_count` |
| `finalize_session()` | Terminal state reached | `outcome`, `verdict`, `quality_score` |

### New Helper Methods (Add to `JulesSessionStore`)

```python
def find_stale_sessions(self, hours: int = 2) -> List[Dict]:
    """Sessions needing state refresh from API."""
    
def find_retryable_failed_sessions(self, max_retries: int = 3) -> List[Dict]:
    """Failed/timeout sessions eligible for free sendMessage retry (T-30)."""
    
def record_send_message(self, session_id: str) -> None:
    """Increment send_message_count after successful sendMessage API."""
    
def record_retry_session(self, new_session_id: str, parent_session_id: str) -> None:
    """Link retry session to parent for chain tracking (T-29, T-30)."""
    
def finalize_session(self, session_id: str, verdict: str = None, quality_score: float = None) -> None:
    """Set outcome/verdict/quality_score on terminal state."""
```

---

## Derived at Query Time (NOT Stored)

| Data | Derivation |
|------|------------|
| `pr_number` | `pr_url LIKE '%/pull/123%'` |
| `head_sha` | From activities or API |
| `trigger_type` | From `session_type` mapping |
| `critical/high/security findings` | Count from activities at query time |

---

## Migration Safety

| Safety Mechanism | Implementation |
|------------------|----------------|
| Nullable columns | `outcome`, `verdict`, `retry_of_session_id` = NULL for historical rows |
| Safe defaults | `session_type` NOT NULL DEFAULT 'unknown', counters DEFAULT 0 |
| Idempotent backfill | `WHERE session_type = 'unknown'` |
| No query breaks | `SELECT *` still works; new columns nullable |
| No FK enforcement | `retry_of_session_id` nullable, no FK constraint |
| Continuous upsert | New columns populated on next API refresh |

---

## Open Questions / Decisions Needed

1. **Apply migration now?** Run the SQL migration against `~/.jules/store.db`?
2. **Add helper methods to `JulesSessionStore`?** Integrate the 5 sync-aware query methods?
3. **Update `upsert_session()`?** Populate new columns from API response (e.g., `session_type` from labels)?
4. **Add `last_send_message` timestamp?** For sendMessage scheduling?
5. **Add `quality_score` computation?** How to derive from API response?

---

## Next Steps (If Approved)

1. Run migration SQL against `~/.jules/store.db`
2. Add 5 helper methods to `JulesSessionStore` class
3. Update `upsert_session()` to populate `session_type` from API labels
5. Test with actual sync cycle
6. Verify forensics queries work (T-29, T-30, T-33)

---

## Rollback Plan

```sql
-- If needed, drop columns (SQLite 3.35+)
ALTER TABLE sessions DROP COLUMN session_type;
ALTER TABLE sessions DROP COLUMN outcome;
ALTER TABLE sessions DROP COLUMN retry_of_session_id;
ALTER TABLE sessions DROP COLUMN retry_count;
ALTER TABLE sessions DROP COLUMN send_message_count;
ALTER TABLE sessions DROP COLUMN verdict;
ALTER TABLE sessions DROP COLUMN quality_score;

DROP INDEX idx_sessions_type;
DROP INDEX idx_sessions_outcome;
DROP INDEX idx_sessions_retry;
```

---

## Approval

- [ ] Migration scope approved
- [ ] Helper methods approved
- [ ] Ready to apply migration
- [ ] Ready to integrate helper methods