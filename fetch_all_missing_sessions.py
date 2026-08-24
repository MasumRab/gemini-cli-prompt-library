#!/usr/bin/env python3
"""
Fetch all missing Jules sessions from the API and insert them into the local store.

Assumes the store already contains the newest sessions (from previous incremental syncs).
Retrieves the full list from the API using pagination (nextPageToken), identifies missing
session IDs, and upserts the missing sessions.

Usage:
    python fetch_all_missing_sessions.py
"""

import os
import sys
import time
from pathlib import Path

# Ensure local modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools.store.jules_store import JulesSessionStore
from tools.api.jules_api_client import JulesAPIClient


def main():
    store = JulesSessionStore()
    client = JulesAPIClient()
    PAGE_SIZE = 200  # Jules API accepts up to 500 (or 1000); 200 is safe
    # ------------------------------------------------------------------
    # 1. Load existing session IDs from store
    # ------------------------------------------------------------------
    with store._conn() as conn:
        rows = conn.execute("SELECT session_id FROM sessions;").fetchall()
    existing_ids = {row[0] for row in rows}
    print(f"📦 Store currently contains {len(existing_ids)} sessions")
    # ------------------------------------------------------------------
    # 2. Fetch all sessions from the API using pagination
    # ------------------------------------------------------------------
    print("🌐 Fetching all sessions from the Jules API ...")
    all_api_ids = set()
    pages = 0
    total_fetched = 0
    next_token = None
    start_time = time.time()
    while True:
        pages += 1
        params = f"pageSize={PAGE_SIZE}"
        if next_token:
            params += f"&pageToken={next_token}"
        url = f"sessions?{params}"
        t0 = time.time()
        try:
            resp = client._request(url)
        except Exception as e:
            print(f"❌ API request failed on page {pages}: {e}")
            break
        req_time = time.time() - t0
        sessions = resp.get("sessions", [])
        fetched = len(sessions)
        total_fetched += fetched
        # Extract session IDs (strip 'sessions/' prefix)
        for s in sessions:
            sid = s.get("name", "").replace("sessions/", "")
            if sid:
                all_api_ids.add(sid)
        print(
            f"📥 Page {pages}: fetched {fetched} sessions (req {req_time:.2f}s), cumulative {total_fetched}"
        )
        next_token = resp.get("nextPageToken")
        if not next_token:
            print("✅ No more pages – reached the end of the API list.")
            break
        # Be gentle with the API
        time.sleep(0.05)
    elapsed_api = time.time() - start_time
    print(
        f"🌐 API fetch finished after {pages} pages, total {len(all_api_ids)} unique session IDs in {elapsed_api:.2f}s"
    )
    # ------------------------------------------------------------------
    # 3. Determine missing IDs
    # ------------------------------------------------------------------
    missing_ids = all_api_ids - existing_ids
    print(f"🆕 {len(missing_ids)} session(s) are missing from the store")
    if not missing_ids:
        print("🎉 Nothing to do – the store is already up‑to‑date.")
        return
    # ------------------------------------------------------------------
    # 4. Re-fetch full session objects for missing IDs
    # ------------------------------------------------------------------
    print("📥 Re‑fetching full session objects for missing IDs ...")
    missing_sessions = []
    pages = 0
    next_token = None
    start_time = time.time()
    while True:
        pages += 1
        params = f"pageSize={PAGE_SIZE}"
        if next_token:
            params += f"&pageToken={next_token}"
        url = f"sessions?{params}"
        t0 = time.time()
        try:
            resp = client._request(url)
        except Exception as e:
            print(f"❌ API request failed on page {pages}: {e}")
            break
        req_time = time.time() - t0
        for sess in resp.get("sessions", []):
            sid = sess.get("name", "").replace("sessions/", "")
            if sid in missing_ids:
                missing_sessions.append(sess)
                missing_ids.remove(sid)
        print(
            f"📥 Page {pages}: scanned {len(resp.get('sessions', []))} sessions, collected {len(missing_sessions)} missing so far (req {req_time:.2f}s)"
        )
        if not missing_ids:
            print("✅ All missing sessions collected.")
            break
        next_token = resp.get("nextPageToken")
        if not next_token:
            print(
                "⚠️ Ran out of pages before finding all missing sessions – something is inconsistent."
            )
            break
        time.sleep(0.05)
    elapsed_miss = time.time() - start_time
    print(
        f"📥 Finished scanning after {pages} pages, collected {len(missing_sessions)} missing session objects in {elapsed_miss:.2f}s"
    )
    # ------------------------------------------------------------------
    # 5. Upsert missing sessions
    # ------------------------------------------------------------------
    print("💾 Upserting missing sessions into the store ...")
    upsert_start = time.time()
    inserted = 0
    with store._conn() as conn:
        for sess in missing_sessions:
            # Use the store's internal extractor to get the dict for upsert
            row = store._extract_session_row(sess)
            # Preserve activity_count, notes, tags on UPDATE
            existing = conn.execute(
                "SELECT activity_count, notes, tags FROM sessions WHERE session_id=?",
                (row["session_id"],),
            ).fetchone()
            if existing:
                activity_count = existing["activity_count"]
                notes = existing["notes"]
                tags = existing["tags"]
            else:
                activity_count = 0
                notes = None
                tags = "[]"
            conn.execute(
                """INSERT INTO sessions
                   (session_id, state, title, prompt_snippet, create_time,
                    update_time, pr_url, repo, activity_count, notes, tags,
                    session_type, outcome, retry_of_session_id, retry_count,
                    send_message_count, verdict, quality_score,
                    last_seen, fetch_count)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,
                           strftime('%Y-%m-%dT%H:%M:%SZ','now'),
                           COALESCE((SELECT fetch_count+1 FROM sessions WHERE session_id=?), 1))
                   ON CONFLICT(session_id) DO UPDATE SET
                       state=excluded.state,
                       title=excluded.title,
                       prompt_snippet=excluded.prompt_snippet,
                       update_time=excluded.update_time,
                       pr_url=excluded.pr_url,
                       repo=excluded.repo,
                       activity_count=excluded.activity_count,
                       session_type=excluded.session_type,
                       outcome=excluded.outcome,
                       retry_of_session_id=excluded.retry_of_session_id,
                       retry_count=excluded.retry_count,
                       send_message_count=excluded.send_message_count,
                       verdict=excluded.verdict,
                       quality_score=excluded.quality_score,
                       last_seen=strftime('%Y-%m-%dT%H:%M:%SZ','now'),
                       fetch_count=excluded.fetch_count""",
                (
                    row["session_id"],
                    row["state"],
                    row["title"],
                    row["prompt_snippet"],
                    row["create_time"],
                    row["update_time"],
                    row["pr_url"],
                    row["repo"],
                    activity_count,
                    notes,
                    tags,
                    row.get("session_type"),
                    row.get("outcome"),
                    row.get("retry_of_session_id"),
                    row.get("retry_count"),
                    row.get("send_message_count"),
                    row.get("verdict"),
                    row.get("quality_score"),
                    row["session_id"],  # for COALESCE subquery
                ),
            )
            inserted += 1
        conn.commit()
    upsert_elapsed = time.time() - upsert_start
    print(f"💾 Upserted {inserted} sessions in {upsert_elapsed:.2f}s")
    # ------------------------------------------------------------------
    # 6. Final verification
    # ------------------------------------------------------------------
    with store._conn() as conn:
        final_count = conn.execute("SELECT COUNT(*) FROM sessions;").fetchone()[0]
        oldest = conn.execute("SELECT MIN(create_time) FROM sessions;").fetchone()[0]
        newest = conn.execute("SELECT MAX(create_time) FROM sessions;").fetchone()[0]
    print(f"📊 Store now contains {final_count} sessions")
    print(f"🕒 Oldest create_time: {oldest}")
    print(f"🕒 Newest create_time: {newest}")
    print(
        "🎉 All missing sessions have been added – the store is now fully synchronized."
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        sys.exit(0)
