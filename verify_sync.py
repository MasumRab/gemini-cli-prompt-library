#!/usr/bin/env python3
"""
Verify that all session IDs from missing_session_ids.txt are now in the store.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools.store.jules_store import JulesSessionStore

def main():
    store = JulesSessionStore()
    # Read missing session IDs
    with open("missing_session_ids.txt", "r") as f:
        missing_ids = [line.strip() for line in f if line.strip()]
    print(f"Read {len(missing_ids)} session IDs from missing_session_ids.txt")
    
    # Check which are in store
    with store._conn() as conn:
        placeholders = ','.join(['?'] * len(missing_ids))
        query = f"SELECT session_id FROM sessions WHERE session_id IN ({placeholders})"
        rows = conn.execute(query, missing_ids).fetchall()
        found_ids = {row[0] for row in rows}
    
    missing = set(missing_ids) - found_ids
    print(f"Found {len(found_ids)} of {len(missing_ids)} missing IDs in store")
    if missing:
        print(f"Still missing {len(missing)} sessions:")
        for sid in list(missing)[:10]:  # Show first 10
            print(f"  {sid}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
    else:
        print("🎉 All previously missing sessions are now in the store!")

if __name__ == "__main__":
    main()