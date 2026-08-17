#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools.store.jules_store import JulesSessionStore
from tools.api.jules_api_client import JulesAPIClient

def main() -> None:
    store = JulesSessionStore()
    client = JulesAPIClient()
    print("📦 Store initialized")

    # Sync all sessions from the API, storing only session metadata (no activities)
    # We set activity_limit=0 to skip fetching activities (as per the plan, we only need session data for now)
    sessions_synced, activities_synced = store.sync_all_sessions(
        client,
        page_size=200,
        activity_limit=0,  # We don't need activities for this sync
        activity_max=0,
        max_pages=None,    # Fetch all pages until exhausted
    )
    print(f"🎉 Sync complete: {sessions_synced} sessions synced, {activities_synced} activities synced")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        sys.exit(0)
