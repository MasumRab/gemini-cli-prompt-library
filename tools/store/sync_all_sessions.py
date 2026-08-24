#!/usr/bin/env python3
"""
Sync all Jules sessions from API to local store using upsert_session.
Simple single-pass: page through API, upsert each session.
"""
import os
import sys
import time
from pathlib import Path

# Ensure we can import the local modules
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.store.jules_store import JulesSessionStore
from tools.api.jules_api_client import JulesAPIClient

def main() -> None:
    store = JulesSessionStore()
    client = JulesAPIClient()
    PAGE_SIZE = 200

    print("🌐 Starting full sync of Jules sessions via API …")
    start = time.time()
    pages = 0
    upserted = 0
    next_token: Optional[str] = None

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
        for sess in sessions:
            try:
                row = store._extract_session_row(sess)
                store.upsert_session(row)
                upserted += 1
            except Exception as e:
                sid = sess.get("name", "unknown").replace("sessions/", "")
                print(f"⚠️  Failed to upsert session {sid}: {e}")

        print(
            f"📥 Page {pages}: processed {len(sessions)} sessions "
            f"(req {req_time:.2f}s), total upserted {upserted}"
        )

        next_token = resp.get("nextPageToken")
        if not next_token:
            print("✅ No more pages – reached the end of the API list.")
            break

        # Be gentle with the API
        time.sleep(0.05)

    elapsed = time.time() - start
    print(f"🌐 Sync finished after {pages} pages in {elapsed:.2f}s")
    print(f"💾 Total upsert operations: {upserted}")

    # Final verification
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