#!/usr/bin/env python3
"""
Fetch all missing Jules sessions from the API and insert them into the local store.
Assumes the store already contains the newest sessions (from previous incremental syncs).
Retrieves the full list from the API using pagination (nextPageToken), identifies missing
session IDs, and upserts the missing sessions.
This version fetches each session only once by storing the session objects during the first pass.
"""

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
    PAGE_SIZE = 500  # Increased page size to reduce number of requests
    # ------------------------------------------------------------------
    # 1. Load existing session IDs from store
    # ------------------------------------------------------------------
    with store._conn() as conn:
        rows = conn.execute("SELECT session_id FROM sessions;").fetchall()
    existing_ids = {row[0] for row in rows}
    print(f"📦 Store currently contains {len(existing_ids)} sessions")
    # ------------------------------------------------------------------
    # 2. Fetch all sessions from the API using pagination and store objects
    # ------------------------------------------------------------------
    print("🌐 Fetching all sessions from the Jules API ...")
    all_sessions_by_id = {}  # session_id -> session object
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
        # Store session objects by ID
        for s in sessions:
            sid = s.get("name", "").replace("sessions/", "")
            if sid:
                all_sessions_by_id[sid] = s
        print(
            f"📥 Page {pages}: fetched {fetched} sessions (req {req_time:.2f}s), cumulative {total_fetched}"
        )
        next_token = resp.get("nextPageToken")
        if not next_token:
            print("✅ No more pages – reached the end of the API list.")
            break
        # Be gentle with the API
        time.sleep(0.01)
    elapsed_api = time.time() - start_time
    print(
        f"🌐 API fetch finished after {pages} pages, total {len(all_sessions_by_id)} unique session objects in {elapsed_api:.2f}s"
    )
    # ------------------------------------------------------------------
    # 3. Determine missing IDs
    # ------------------------------------------------------------------
    missing_ids = set(all_sessions_by_id.keys()) - existing_ids
    print(f"🆕 {len(missing_ids)} session(s) are missing from the store")
    if not missing_ids:
        print("🎉 Nothing to do – the store is already up‑to‑date.")
        return
    # ------------------------------------------------------------------
    # 4. Upsert missing sessions
    # ------------------------------------------------------------------
    print("💾 Upserting missing sessions into the store ...")
    upsert_start = time.time()
    inserted = 0
    for sid in missing_ids:
        sess = all_sessions_by_id[sid]
        store.upsert_session(sess)
        inserted += 1
    upsert_elapsed = time.time() - upsert_start
    print(f"💾 Upserted {inserted} sessions in {upsert_elapsed:.2f}s")
    # ------------------------------------------------------------------
    # 5. Final verification
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