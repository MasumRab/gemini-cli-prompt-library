#!/usr/bin/env python3
"""
Sync all sessions from the Jules API to a new SQLite store using the JulesSessionStore class.
This ensures the new store has the same schema and upsert logic as the existing store.
"""

import sys
import time
from pathlib import Path

# Add the current directory to sys.path to import local modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools.store.jules_store import JulesSessionStore
from tools.api.jules_api_client import JulesAPIClient


def fetch_all_sessions_from_api() -> list[dict]:
    """Fetch all sessions from the Jules API."""
    client = JulesAPIClient()
    PAGE_SIZE = 200
    
    all_sessions: list[dict] = []
    pages = 0
    next_token: str | None = None
    start_api = time.time()
    
    print("🌐 Fetching all sessions from the Jules API …")
    
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
            # In a real script, we might want to retry or break
            break
        
        req_time = time.time() - t0
        sessions = resp.get("sessions", [])
        all_sessions.extend(sessions)
        
        print(
            f"📥 Page {pages}: fetched {len(sessions)} sessions "
            f"(req {req_time:.2f}s), cumulative {len(all_sessions)}"
        )
        
        next_token = resp.get("nextPageToken")
        if not next_token:
            print("✅ No more pages – reached the end of the API list.")
            break
        
        time.sleep(0.05)
    
    elapsed_api = time.time() - start_api
    print(f"🌐 API fetch finished after {pages} pages, "
          f"total {len(all_sessions)} sessions in {elapsed_api:.2f}s")
    
    return all_sessions


def main() -> None:
    """Main sync function."""
    # Define path for the new API store
    api_store_path = Path("./jules_sessions_store_api_via_store.db")
    print(f"📦 Creating new API store at: {api_store_path}")
    
    # Create JulesSessionStore instance (this will ensure the schema is created on first use)
    store = JulesSessionStore(db_path=api_store_path)
    
    try:
        # Fetch all sessions from API
        all_sessions = fetch_all_sessions_from_api()
        
        if not all_sessions:
            print("🎉 No sessions fetched from API.")
            return
        
        # Upsert into new store using the store's method
        print("💾 Upserting sessions into the new store …")
        upsert_start = time.time()
        inserted = 0
        
        # We'll use the store's upsert_session method which returns None.
        # To count inserts, we could check before each upsert, but for simplicity,
        # we'll just count the total sessions we process and note that upsert_session
        # does an INSERT OR REPLACE, so it will update existing or insert new.
        # Since we are starting with an empty store, every session will be inserted.
        for sess in all_sessions:
            store.upsert_session(sess)
            inserted += 1
            if inserted % 100 == 0:
                print(f"  🔄 Processed {inserted} sessions…")
        
        upsert_elapsed = time.time() - upsert_start
        print(f"💾 Upserted {inserted} sessions in {upsert_elapsed:.2f}s")
        
        # Final count from the store
        with store._conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions;")
            final_count = cursor.fetchone()[0]
            print(f"📊 New store now contains {final_count} sessions")
            
            # Show oldest and newest create_time
            cursor.execute("SELECT MIN(create_time), MAX(create_time) FROM sessions;")
            oldest, newest = cursor.fetchone()
            print(f"🕒 Oldest create_time: {oldest}")
            print(f"🕒 Newest create_time: {newest}")
        
        print("🎉 API store sync complete.")
        
    finally:
        store.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)