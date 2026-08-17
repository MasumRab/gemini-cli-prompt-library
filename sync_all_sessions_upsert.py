#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools.store.jules_store import JulesSessionStore, _extract_session_row
from tools.api.jules_api_client import JulesAPIClient

def main() -> None:
    store = JulesSessionStore()
    client = JulesAPIClient()
    PAGE_SIZE = 200

    with store._conn() as conn:
        existing_count = conn.execute("SELECT COUNT(*) FROM sessions;").fetchone()[0]
    print(f"📦 Store currently contains {existing_count} sessions")

    print("🌐 Fetching all sessions from the Jules API …")
    all_sessions: Dict[str, dict] = {}
    pages = 0
    next_token: Optional[str] = None
    start_api = time.time()

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
        for s in sessions:
            sid = s.get("name", "").replace("sessions/", "")
            if sid:
                all_sessions[sid] = s

        print(
            f"📥 Page {pages}: fetched {len(sessions)} sessions "
            f"(req {req_time:.2f}s), cumulative unique {len(all_sessions)}"
        )
        next_token = resp.get("nextPageToken")
        if not next_token:
            print("✅ No more pages – reached the end of the API list.")
            break

        time.sleep(0.05)

    elapsed_api = time.time() - start_api
    print(f"🌐 API fetch finished after {pages} pages, "
          f"total {len(all_sessions)} unique session IDs in {elapsed_api:.2f}s")

    print("💾 Upserting all sessions from the API into the store …")
    upsert_start = time.time()
    inserted = 0
    updated = 0
    with store._conn() as conn:
        for sid, sess in all_sessions.items():
            row = _extract_session_row(sess)
            # Check if session exists to count inserts vs updates
            cur = conn.execute("SELECT 1 FROM sessions WHERE session_id = ?", (sid,))
            exists = cur.fetchone() is not None
            store.upsert_session(row)
            if exists:
                updated += 1
            else:
                inserted += 1
        conn.commit()
    upsert_elapsed = time.time() - upsert_start
    print(f"💾 Upserted {inserted} new and {updated} existing sessions in {upsert_elapsed:.2f}s")

    with store._conn() as conn:
        final_cnt = conn.execute("SELECT COUNT(*) FROM sessions;").fetchone()[0]
        oldest = conn.execute("SELECT MIN(create_time) FROM sessions;").fetchone()[0]
        newest = conn.execute("SELECT MAX(create_time) FROM sessions;").fetchone()[0]
    print(f"📊 Store now contains {final_cnt} sessions")
    print(f"🕒 Oldest create_time: {oldest}")
    print(f"🕒 Newest create_time: {newest}")
    print("🎉 Sync complete.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        sys.exit(0)