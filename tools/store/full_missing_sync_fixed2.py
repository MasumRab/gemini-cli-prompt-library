#!/usr/bin/env python3
"""
Full back‑fill of missing Jules sessions from the API.
Uses the store's upsert_session() method to avoid column‑count mismatches.
"""
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Make sure we can import the local modules
# Assume this script lives in <repo>/jules/tools/store/
# We need to add the directory that contains the 'tools' package (i.e., <repo>/jules)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.store.jules_store import JulesSessionStore
from tools.api.jules_api_client import JulesAPIClient

def main() -> None:
    store = JulesSessionStore()
    client = JulesAPIClient()
    PAGE_SIZE = 200                     # safe page size for the Jules API

    # ------------------------------------------------------------------
    # 1. Load the set of session IDs we already have
    # ------------------------------------------------------------------
    with store._conn() as conn:
        existing = {row[0] for row in conn.execute(
            "SELECT session_id FROM sessions;"
        ).fetchall()}
    print(f"📦 Store currently contains {len(existing)} sessions")

    # ------------------------------------------------------------------
    # 2. Page through the API to collect *all* session IDs that exist
    # ------------------------------------------------------------------
    print("🌐 Fetching all sessions from the Jules API …")
    all_ids: set[str] = set()
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
                all_ids.add(sid)

        print(
            f"📥 Page {pages}: fetched {len(sessions)} sessions "
            f"(req {req_time:.2f}s), cumulative unique {len(all_ids)}"
        )
        next_token = resp.get("nextPageToken")
        if not next_token:
            print("✅ No more pages – reached the end of the API list.")
            break

        # Be gentle with the API
        time.sleep(0.05)

    elapsed_api = time.time() - start_api
    print(f"🌐 API fetch finished after {pages} pages, "
          f"total {len(all_ids)} unique session IDs in {elapsed_api:.2f}s")

    # ------------------------------------------------------------------
    # 3. Determine which IDs are missing from the store
    # ------------------------------------------------------------------
    missing = all_ids - existing
    print(f"🆕 {len(missing)} session(s) are missing from the store")
    if not missing:
        print("🎉 Nothing to do – the store is already up‑to‑date.")
        return

    # ------------------------------------------------------------------
    # 4. Re‑fetch the full session objects for the missing IDs
    # ------------------------------------------------------------------
    print("📥 Re‑fetching full session objects for missing IDs …")
    missing_sessions: list[dict] = []
    pages = 0
    next_token = None
    start_miss = time.time()

    while missing:
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
            if sid in missing:
                missing_sessions.append(sess)
                missing.remove(sid)

        print(
            f"📥 Page {pages}: scanned {len(resp.get('sessions', []))} sessions, "
            f"collected {len(missing_sessions)} missing so far (req {req_time:.2f}s)"
        )

        if not missing:
            print("✅ All missing sessions collected.")
            break

        next_token = resp.get("nextPageToken")
        if not next_token:
            print("⚠️  Ran out of pages before finding all missing sessions – "
                  "something is inconsistent.")
            break

        time.sleep(0.05)

    elapsed_miss = time.time() - start_miss
    print(f"📥 Finished scanning after {pages} pages, "
          f"collected {len(missing_sessions)} missing session objects in "
          f"{elapsed_miss:.2f}s")

    # ------------------------------------------------------------------
    # 5. Upsert the missing sessions using the store's proven method
    # ------------------------------------------------------------------
    print("💾 Upserting missing sessions into the store …")
    upsert_start = time.time()
    inserted = 0
    with store._conn() as conn:
        for sess in missing_sessions:
            # The store's internal extractor returns a dict with *all* columns
            row = store._extract_session_row(sess)
            store.upsert_session(row)   # <-- relies on the correct INSERT … ON CONFLICT DO UPDATE
            inserted += 1
        conn.commit()
    upsert_elapsed = time.time() - upsert_start
    print(f"💾 Upserted {inserted} sessions in {upsert_elapsed:.2f}s")

    # ------------------------------------------------------------------
    # 6. Final verification
    # ------------------------------------------------------------------
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
