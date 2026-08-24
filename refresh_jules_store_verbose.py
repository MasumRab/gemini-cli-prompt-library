#!/usr/bin/env python3
"""
Verbose full-refresh of the Jules session store.

- Clears the high-water-mark -> forces a complete pull from the Jules cloud.
- Pages through the Jules API, upserts each session, and prints progress.
- Leaves the store ready for normal incremental syncs afterwards.

Usage:
    python refresh_jules_store_verbose.py   # (make sure JULES_API_KEY is set)
"""

import os
import sys
import time
from pathlib import Path

# ----------------------------------------------------------------------
# Make sure the local `tools` package can be imported when running from the repo root
# ----------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from tools.store.jules_store import JulesSessionStore
from tools.api.jules_api_client import JulesAPIClient

# ----------------------------------------------------------------------
# Configuration – tweak if you want a different page size or more/less verbosity
# ----------------------------------------------------------------------
PAGE_SIZE = 500          # Jules API accepts up to 500 (or 1000) per page; larger = fewer HTTP calls
VERBOSE   = True        # set False to silence per-page output (only summary will be shown)

# ----------------------------------------------------------------------
# Helper: simple pretty-print with timestamp
# ----------------------------------------------------------------------
def log(msg: str):
    if VERBOSE:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

# ----------------------------------------------------------------------
# Main routine
# ----------------------------------------------------------------------
def main():
    # ---- 1. sanity check – API key must be present --------------------
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        sys.exit("❌  ERROR: JULES_API_KEY environment variable not set.")
    log(f"🔑 Jules API key detected (length={len(api_key)})")

    # ---- 2. Initialise store and client --------------------------------
    store = JulesSessionStore()                     # uses ~/.jules/store.db by default
    client = JulesAPIClient()                       # pulls the key from os.environ
    log("🛠️  JulesSessionStore and JulesAPIClient initialised")

    # ---- 3. Reset the high-water-mark (force full fetch) ----------------
    with store._conn() as conn:
        # Setting value to empty string signals "no high water mark"
        conn.execute(
            "INSERT OR REPLACE INTO sync_meta (key, value) VALUES ('high_water_mark', '')"
        )
        conn.commit()
    log("🔄 High-water-mark cleared – next sync will request *all* sessions")

    # ---- 4. Page-by-page fetch & upsert ---------------------------------
    total_fetched = 0
    page_num = 0
    start_time = time.time()

    while True:
        page_num += 1
        log(f"⏳ Fetching page {page_num} (page_size={PAGE_SIZE}) …")
        page_start = time.time()

        # The JulesAPIClient yields sessions via its `list_sessions` generator.
        # We pull a page at a time by calling the low-level `_request` directly
        # so we can count how many items we actually got.
        params = f"pageSize={PAGE_SIZE}"
        # If we had a stored HWM we would add &startTime=…, but we cleared it,
        # so we ask from the very beginning.
        url = f"sessions?{params}"
        try:
            resp = client._request(url)          # returns dict with 'sessions' and maybe 'nextPageToken'
        except Exception as e:
            log(f"❌  API request failed on page {page_num}: {e}")
            break

        sessions = resp.get("sessions", [])
        fetched   = len(sessions)
        total_fetched += fetched
        page_elapsed = time.time() - page_start

        log(f"   📥 Page {page_num}: {fetched} session{'s' if fetched!=1 else ''} "
            f"(cumulative {total_fetched}) – took {page_elapsed:.2f}s")

        # Upsert each session – this updates all derived columns, FTS, etc.
        for sess in sessions:
            try:
                store.upsert_session(sess)
            except Exception as e:
                log(f"⚠️  Failed to upsert session {sess.get('name','?')}: {e}")

        # Stop when we got fewer than PAGE_SIZE items (means last page)
        if fetched < PAGE_SIZE:
            log(f"✅  Received a partial page ({fetched}<{PAGE_SIZE}) – assuming end of list.")
            break

        # Optional safety stop: break after a hard limit if you only want a test.
        # if page_num >= 5: break

    # ---- 5. Final summary ------------------------------------------------
    elapsed_total = time.time() - start_time
    log("=" * 60)
    log(f"🎉 Refresh finished after {page_num} page{'s' if page_num!=1 else ''}.")
    log(f"📊 Total sessions upserted: {total_fetched}")
    log(f"⏱️  Elapsed wall time: {elapsed_total:.2f} seconds")
    if elapsed_total > 60:
        log(f"   ({elapsed_total/60:.1f} minutes)")

    # ---- 6. Quick sanity check (optional) --------------------------------
    with store._conn() as conn:
        db_cnt = conn.execute("SELECT COUNT(*) FROM sessions;").fetchone()[0]
        oldest = conn.execute("SELECT MIN(create_time) FROM sessions;").fetchone()[0]
        newest = conn.execute("SELECT MAX(create_time) FROM sessions;").fetchone()[0]
    log(f"🗄️  Store now contains {db_cnt} sessions")
    log(f"🕒 Oldest create_time: {oldest}")
    log(f"🕒 Newest create_time: {newest}")

    # Hint for the user: you can now run normal incremental syncs quickly.
    log("💡  Future incremental syncs will be fast because the HWM now points to the newest session.")

if __name__ == "__main__":
    main()