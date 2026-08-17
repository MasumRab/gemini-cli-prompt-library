#!/usr/bin/env python3
"""
Sync all sessions from the Jules API to a new SQLite store for inspection.
This script creates a new store (jules_sessions_store_api.db) containing
only the sessions data fetched from the API, allowing comparison with
the existing store (~/.jules/store.db).
"""

import sys
import time
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any

# Add the current directory to sys.path to import local modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools.store.jules_store import _extract_session_row, SCHEMA_SQL
from tools.api.jules_api_client import JulesAPIClient


def create_new_store(db_path: Path) -> sqlite3.Connection:
    """Create a new SQLite store with the Jules schema."""
    # Ensure the directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing file if any
    if db_path.exists():
        db_path.unlink()
    
    # Create connection and apply schema
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Execute the schema from jules_store.py
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    
    return conn


def fetch_all_sessions_from_api() -> Dict[str, Dict[str, Any]]:
    """Fetch all sessions from the Jules API."""
    client = JulesAPIClient()
    PAGE_SIZE = 200
    
    all_sessions: Dict[str, Dict[str, Any]] = {}
    pages = 0
    next_token: Optional[str] = None
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
    
    return all_sessions


def upsert_sessions(conn: sqlite3.Connection, sessions: Dict[str, Dict[str, Any]]) -> int:
    """Upsert session data into the sessions table using UPSERT."""
    inserted = 0
    cursor = conn.cursor()
    
    upsert_sql = """
        INSERT INTO sessions (
            session_id, state, title, prompt_snippet, create_time,
            update_time, pr_url, repo, activity_count, notes, tags,
            session_type, outcome, retry_of_session_id, retry_count,
            send_message_count, verdict, quality_score, last_seen, fetch_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            state=excluded.state,
            title=excluded.title,
            prompt_snippet=excluded.prompt_snippet,
            create_time=excluded.create_time,
            update_time=excluded.update_time,
            pr_url=excluded.pr_url,
            repo=excluded.repo,
            activity_count=excluded.activity_count,
            notes=excluded.notes,
            tags=excluded.tags,
            session_type=excluded.session_type,
            outcome=excluded.outcome,
            retry_of_session_id=excluded.retry_of_session_id,
            retry_count=excluded.retry_count,
            send_message_count=excluded.send_message_count,
            verdict=excluded.verdict,
            quality_score=excluded.quality_score,
            last_seen=strftime('%Y-%m-%dT%H:%M:%SZ','now'),
            fetch_count=sessions.fetch_count + 1
    """
    
    for sid, sess in sessions.items():
        # Determine activity_count, notes, tags from existing row or defaults
        cursor.execute(
            "SELECT activity_count, notes, tags FROM sessions WHERE session_id = ?",
            (sid,)
        )
        existing = cursor.fetchone()
        
        if existing:
            activity_count = existing["activity_count"]
            notes = existing["notes"]
            tags = existing["tags"]
        else:
            activity_count = 0
            notes = None
            tags = "[]"
        
        # Extract the base row (without activity_count, notes, tags)
        row = _extract_session_row(sess)
        
        # Prepare the 19 values for the INSERT (in the order of the columns)
        values = (
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
            row["session_type"],
            row["outcome"],
            row["retry_of_session_id"],
            row["retry_count"],
            row["send_message_count"],
            row["verdict"],
            row["quality_score"]
        )
        
        cursor.execute(upsert_sql, values)
        # Note: We cannot know if it was an insert or update from this execution.
        # We'll count inserts by checking if the row existed before.
        if existing is None:
            inserted += 1
    
    conn.commit()
    return inserted


def main() -> None:
    """Main sync function."""
    # Define path for the new API store
    api_store_path = Path("./jules_sessions_store_api.db")
    print(f"📦 Creating new API store at: {api_store_path}")
    
    # Create new store
    conn = create_new_store(api_store_path)
    
    try:
        # Fetch all sessions from API
        all_sessions = fetch_all_sessions_from_api()
        
        if not all_sessions:
            print("🎉 No sessions fetched from API.")
            return
        
        # Upsert into new store
        print("💾 Upserting sessions into the new store …")
        upsert_start = time.time()
        inserted = upsert_sessions(conn, all_sessions)
        upsert_elapsed = time.time() - upsert_start
        
        print(f"💾 Upserted {inserted} new sessions in {upsert_elapsed:.2f}s")
        
        # Final count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions;")
        final_count = cursor.fetchone()[0]
        print(f"📊 New store now contains {final_count} sessions")
        
        # Show oldest and newest create_time
        cursor.execute("SELECT MIN(create_time), MAX(create_time) FROM sessions;")
        oldest, newest = cursor.fetchone()
        print(f"🕒 Oldest create_time: {oldest}")
        print(f"🕒 Newest create_time: {newest}")
        
        print("🎉 API store sync complete.")
        
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)