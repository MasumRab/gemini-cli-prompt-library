#!/usr/bin/env python3
"""
Sync PR data from GitHub into the PR store, per repo, incrementally.

Designed to be invoked by Letta agents on request. For each repo:
  1. Skip if fresh (last_pr_sync:<repo> watermark within threshold)
     unless --force.
  2. gh pr list --json … (one call per state bucket: open + merged/closed
     recent) → upsert.

Usage:
    uv run python tools/store/sync_prs.py                    # all repos, if stale
    uv run python tools/store/sync_prs.py --repo EmailIntelligence
    uv run python tools/store/sync_prs.py --force            # ignore freshness
    uv run python tools/store/sync_prs.py --status           # report only
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.store.pr_store import PRStore

REPOS = [
    "EmailIntelligence",
    "kaggle-notebooks-analysis",
    "gemini-fullstack-langgraph-quickstart",
    "gemini-cli-prompt-library",
]
OWNER = "MasumRab"
DEFAULT_MAX_AGE_HOURS = 12.0

# Fields we need from gh pr list. statusCheckRollup is fetched separately
# (it makes gh pr list 504 on repos with many PRs × many checks).
PR_FIELDS = (
    "number,title,url,author,state,isDraft,mergedAt,mergeable,"
    "mergeStateStatus,headRefName,headRefOid,baseRefName,additions,"
    "deletions,changedFiles,createdAt,updatedAt,closedAt,reviewDecision,"
    "labels"
)
ROLLUP_FIELDS = "number,statusCheckRollup"
ROLLUP_CHUNK = 25  # PRs per rollup fetch; larger chunks 504 on big repos
ROLLUP_RETRIES = 3
ROLLUP_BACKOFF_S = 10


def gh_pr_list(
    repo: str, state: str, limit: int, fields: str = PR_FIELDS
) -> list[dict[str, Any]]:
    """Run gh pr list for one state bucket; return parsed JSON list."""
    argv = [
        "gh",
        "pr",
        "list",
        "--repo",
        f"{OWNER}/{repo}",
        "--state",
        state,
        "--limit",
        str(limit),
        "--json",
        fields,
    ]
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(
            f"gh pr list failed for {repo} ({state}): {proc.stderr.strip()[:300]}"
        )
    return json.loads(proc.stdout or "[]")


def fetch_rollups(repo: str, prs: list[dict[str, Any]]) -> None:
    """Attach statusCheckRollup to each open-PR dict, in small chunks.

    Mutates in place: p['statusCheckRollup']. Only open PRs have live
    checks; merged/closed rows keep their last-known CI state.
    """
    open_prs = [p for p in prs if p.get("state", "").upper() == "OPEN"]
    for i in range(0, len(open_prs), ROLLUP_CHUNK):
        chunk = open_prs[i : i + ROLLUP_CHUNK]
        rows: list[dict[str, Any]] = []
        for attempt in range(ROLLUP_RETRIES):
            try:
                rows = gh_pr_list(repo, "open", ROLLUP_CHUNK, ROLLUP_FIELDS)
                break
            except RuntimeError:
                if attempt == ROLLUP_RETRIES - 1:
                    raise
                time.sleep(ROLLUP_BACKOFF_S)
        by_num = {r["number"]: r for r in rows}
        for p in chunk:
            p["statusCheckRollup"] = by_num.get(p["number"], {}).get(
                "statusCheckRollup", []
            )


def sync_repo(
    store: PRStore,
    repo: str,
    force: bool = False,
    max_age: float = DEFAULT_MAX_AGE_HOURS,
) -> str:
    """Sync one repo. Returns status string."""
    if not force and not store.is_repo_stale(repo, max_age):
        return "fresh (skipped)"

    t0 = time.time()
    prs = gh_pr_list(repo, "open", 200)
    # Recent non-open PRs power closure-efficiency metrics; cap at 100.
    prs += gh_pr_list(repo, "merged", 100)
    prs += gh_pr_list(repo, "closed", 100)
    # CI rollups fetched separately (chunked — see fetch_rollups).
    fetch_rollups(repo, prs)
    n = store.upsert_prs(repo, prs)
    store.set_watermark(f"last_pr_sync:{repo}")
    return f"synced {n} PRs in {time.time() - t0:.1f}s"


def main() -> int:
    parser = argparse.ArgumentParser(description="PR store sync")
    parser.add_argument("--repo", choices=REPOS, help="Sync a single repo")
    parser.add_argument(
        "--force", action="store_true", help="Sync even if watermark is fresh"
    )
    parser.add_argument(
        "--max-age",
        type=float,
        default=DEFAULT_MAX_AGE_HOURS,
        help=f"Freshness threshold hours (default {DEFAULT_MAX_AGE_HOURS})",
    )
    parser.add_argument(
        "--status", action="store_true", help="Report watermark status only"
    )
    args = parser.parse_args()

    store = PRStore()
    repos = [args.repo] if args.repo else REPOS

    if args.status:
        for r in repos:
            last = store.get_watermark(f"last_pr_sync:{r}")
            with store._conn() as conn:
                cnt = conn.execute(
                    "SELECT COUNT(*) FROM pull_request WHERE repo=?", (r,)
                ).fetchone()[0]
                open_cnt = conn.execute(
                    "SELECT COUNT(*) FROM pull_request WHERE repo=? AND state IN ('open','draft')",
                    (r,),
                ).fetchone()[0]
            stale = store.is_repo_stale(r, args.max_age)
            print(
                f"{r:<40} last={last or 'never':<21} rows={cnt:<5} open={open_cnt:<4} stale={stale}"
            )
        return 0

    failed = 0
    for r in repos:
        try:
            print(f"{r}: {sync_repo(store, r, force=args.force, max_age=args.max_age)}")
        except Exception as e:
            print(f"{r}: FAILED — {e}")
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
