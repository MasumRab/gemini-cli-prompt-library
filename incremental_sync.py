#!/usr/bin/env python3
import os
import sys
import time
import argparse
from pathlib import Path

# Ensure we can import local modules (run from repo root or jules/ dir)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools.store.jules_store import JulesSessionStore
from tools.api.jules_api_client import JulesAPIClient

MAX_ITERATIONS = 1000  # safety bound so the loop cannot run unbounded forever


def main():
    parser = argparse.ArgumentParser(description="Incremental Jules session sync loop.")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=MAX_ITERATIONS,
        help="Maximum number of sync pages to process before exiting (default: %(default)s).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single sync page then exit instead of looping.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=200,
        help="Number of sessions to fetch per sync page (default: %(default)s).",
    )
    parser.add_argument(
        "--sleep-between",
        type=float,
        default=1.0,
        help="Seconds to wait between sync iterations (default: %(default)s).",
    )
    args = parser.parse_args()

    store = JulesSessionStore()
    client = JulesAPIClient()
    PAGE_SIZE = args.page_size
    SLEEP_BETWEEN = args.sleep_between
    max_iterations = 1 if args.once else args.max_iterations
    print("Starting incremental sync loop...")
    iterations = 0
    while iterations < max_iterations:
        iterations += 1
        start = time.time()
        try:
            result = store.sync_page(client, page_size=PAGE_SIZE)
        except Exception as e:
            print(f"Sync page failed: {e}")
            if args.once:
                break
            time.sleep(SLEEP_BETWEEN)
            continue
        fetched = result.get("new_synced", 0)
        elapsed = time.time() - start
        if fetched == 0:
            print(
                f"No new sessions fetched (took {elapsed:.2f}s). Waiting {SLEEP_BETWEEN}s before next check..."
            )
            if args.once:
                break
            time.sleep(SLEEP_BETWEEN)
            continue
        print(f"Fetched {fetched} new sessions in {elapsed:.2f}s")
        if args.once:
            break
        # Sleep briefly before next iteration
        time.sleep(SLEEP_BETWEEN)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        sys.exit(0)
