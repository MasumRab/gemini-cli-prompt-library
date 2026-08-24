#!/usr/bin/env python3
"""
Compare the existing Jules session store (~/.jules/store.db) with the API store (jules_sessions_store_api_via_store.db)
to find which session IDs are missing in the existing store.
"""

import sqlite3
from pathlib import Path

EXISTING_STORE = Path.home() / ".jules" / "store.db"
API_STORE = Path("./jules_sessions_store_api_via_store.db")

def get_session_ids(db_path: Path) -> set[str]:
    """Return a set of session_id from the sessions table."""
    if not db_path.exists():
        print(f"❌ Store not found: {db_path}")
        return set()
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT session_id FROM sessions;")
        return {row["session_id"] for row in cursor.fetchall()}

def main() -> None:
    print("🔍 Comparing session stores...")
    print(f"Existing store: {EXISTING_STORE}")
    print(f"API store:      {API_STORE}")
    
    existing_ids = get_session_ids(EXISTING_STORE)
    api_ids = get_session_ids(API_STORE)
    
    print(f"\n📦 Existing store contains {len(existing_ids)} sessions")
    print(f"📦 API store contains    {len(api_ids)} sessions")
    
    missing_in_existing = api_ids - existing_ids
    extra_in_existing = existing_ids - api_ids
    
    print(f"\n🆕 Sessions in API store but missing in existing: {len(missing_in_existing)}")
    if missing_in_existing:
        print("First 10 missing session IDs:")
        for sid in sorted(missing_in_existing)[:10]:
            print(f"  - {sid}")
    
    print(f"\n🗑️  Sessions in existing store but not in API store: {len(extra_in_existing)}")
    if extra_in_existing:
        print("First 10 extra session IDs:")
        for sid in sorted(extra_in_existing)[:10]:
            print(f"  - {sid}")
    
    # Optionally, write the missing IDs to a file for further inspection
    if missing_in_existing:
        missing_file = Path("./missing_session_ids.txt")
        missing_file.write_text("\n".join(sorted(missing_in_existing)))
        print(f"\n💾 All missing session IDs written to: {missing_file}")

if __name__ == "__main__":
    main()