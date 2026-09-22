#!/usr/bin/env python3
"""
SQLite store for cross-repo PR triage data.

Single file (~/.jules/pr_store.db), one schema, ``repo`` column — the
SQLite translation of the per-repo PostgreSQL design. Populated on
demand by Letta agents via tools/store/sync_prs.py; freshness is
tracked per repo in sync_meta (``last_pr_sync:<repo>``) so the same
sync-before-read gate pattern as the session store applies.

Schema (per the Sept 2026 PR-tracking design, SQLite subset):
    pull_request  — core PR row, generated churn/size/abandoned columns
    pr_label      — labels per PR
    sync_meta     — watermarks (last_pr_sync:<repo>)

Deferred (documented graduation path, not schema changes needed now):
    review/review_thread/pr_comment (needs comment classification),
    pr_conflict (needs hunk-level ingest), Linear linkage, merge train.
"""

import sqlite3
import time
from pathlib import Path
from typing import Any

PR_STORE_PATH = Path(
    __import__("os").environ.get(
        "JULES_PR_STORE", str(Path.home() / ".jules" / "pr_store.db")
    )
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS sync_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pull_request (
    repo            TEXT NOT NULL,
    pr_number       INTEGER NOT NULL,
    title           TEXT NOT NULL,
    html_url        TEXT,
    author_login    TEXT,
    state           TEXT NOT NULL CHECK (state IN ('open','closed','merged','draft')),
    is_draft        INTEGER NOT NULL DEFAULT 0,
    merged          INTEGER NOT NULL DEFAULT 0,
    merged_at       TEXT,
    mergeable       INTEGER,          -- NULL = GitHub still computing
    mergeable_state TEXT CHECK (mergeable_state IN
                        ('clean','dirty','blocked','behind','unstable',
                         'unknown','has_hooks')) DEFAULT 'unknown',
    head_ref        TEXT,
    head_sha        TEXT,
    base_ref        TEXT,
    additions       INTEGER DEFAULT 0,
    deletions       INTEGER DEFAULT 0,
    changed_files   INTEGER DEFAULT 0,
    churn           INTEGER GENERATED ALWAYS AS (additions + deletions) STORED,
    size_bucket     TEXT GENERATED ALWAYS AS (
        CASE WHEN additions + deletions <= 50   THEN 'XS'
             WHEN additions + deletions <= 200  THEN 'S'
             WHEN additions + deletions <= 600  THEN 'M'
             WHEN additions + deletions <= 2000 THEN 'L'
             ELSE 'XL' END) STORED,
    created_at      TEXT,
    updated_at      TEXT,
    closed_at       TEXT,
    abandoned       INTEGER GENERATED ALWAYS AS
                        (state = 'closed' AND merged = 0) STORED,
    -- md5() is registered by PRStore at connect time (SQLite has no
    -- built-in hash); maintained by upsert_prs, not generated, because
    -- Python-registered functions are non-deterministic to SQLite.
    title_fingerprint TEXT,
    review_decision TEXT,             -- APPROVED/CHANGES_REQUESTED/REVIEW_REQUIRED
    ci_conclusion   TEXT,             -- success/failure/pending/neutral/unknown
    ci_failing_checks INTEGER DEFAULT 0,
    last_synced_at  TEXT NOT NULL,
    PRIMARY KEY (repo, pr_number)
);

CREATE INDEX IF NOT EXISTS idx_pr_state_updated
    ON pull_request (state, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_pr_conflicts
    ON pull_request (repo) WHERE state = 'open' AND mergeable_state = 'dirty';
CREATE INDEX IF NOT EXISTS idx_pr_size
    ON pull_request (size_bucket, state);
CREATE INDEX IF NOT EXISTS idx_pr_fingerprint
    ON pull_request (title_fingerprint, state);

CREATE TABLE IF NOT EXISTS pr_label (
    repo      TEXT NOT NULL,
    pr_number INTEGER NOT NULL,
    label     TEXT NOT NULL,
    PRIMARY KEY (repo, pr_number, label),
    FOREIGN KEY (repo, pr_number) REFERENCES pull_request (repo, pr_number)
        ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_label ON pr_label (label);
"""


class PRStore:
    """SQLite-backed PR triage store."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = Path(db_path or PR_STORE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    @staticmethod
    def fingerprint(title: str) -> str:
        """Normalized-title hash for duplicate detection (dup-PR pattern)."""
        import hashlib
        import re

        norm = re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()
        return hashlib.md5(norm.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Watermarks
    # ------------------------------------------------------------------

    def get_watermark(self, key: str) -> str | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT value FROM sync_meta WHERE key=?", (key,)
            ).fetchone()
        return row["value"] if row else None

    def set_watermark(self, key: str, value: str | None = None) -> None:
        ts = value or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sync_meta (key, value) VALUES (?, ?)",
                (key, ts),
            )

    def is_repo_stale(self, repo: str, max_age_hours: float) -> bool:
        """True if repo's PR data is older than max_age (or never synced)."""
        last = self.get_watermark(f"last_pr_sync:{repo}")
        if last is None:
            return True
        from datetime import datetime

        try:
            age_s = time.time() - datetime.fromisoformat(last).timestamp()
        except ValueError:
            return True
        return age_s > max_age_hours * 3600

    # ------------------------------------------------------------------
    # Upserts
    # ------------------------------------------------------------------

    def upsert_prs(self, repo: str, prs: list[dict[str, Any]]) -> int:
        """Upsert PR rows (from gh pr list --json shape). Returns count."""
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._conn() as conn:
            for p in prs:
                author = (p.get("author") or {}).get("login", "")
                state = p.get("state", "").lower()  # OPEN/CLOSED/MERGED
                if state == "open" and p.get("isDraft"):
                    state = "draft"
                ms = (p.get("mergeStateStatus") or "UNKNOWN").lower()
                ms_map = {
                    "clean": "clean",
                    "dirty": "dirty",
                    "blocked": "blocked",
                    "behind": "behind",
                    "unstable": "unstable",
                    "has_hooks": "has_hooks",
                    "unknown": "unknown",
                }
                rollup = p.get("statusCheckRollup") or []
                failing = sum(1 for c in rollup if c.get("conclusion") == "FAILURE")
                if failing:
                    ci = "failure"
                elif any(c.get("status") == "IN_PROGRESS" for c in rollup):
                    ci = "pending"
                elif rollup:
                    ci = "success"
                else:
                    ci = "unknown"

                conn.execute(
                    """INSERT OR REPLACE INTO pull_request
                       (repo, pr_number, title, html_url, author_login, state,
                        is_draft, merged, merged_at, mergeable, mergeable_state,
                        head_ref, head_sha, base_ref, additions, deletions,
                        changed_files, created_at, updated_at, closed_at,
                        review_decision, ci_conclusion, ci_failing_checks,
                        title_fingerprint, last_synced_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        repo,
                        p["number"],
                        p.get("title", ""),
                        p.get("url", ""),
                        author,
                        state,
                        1 if p.get("isDraft") else 0,
                        1 if state == "merged" else 0,
                        p.get("mergedAt"),
                        p.get("mergeable"),
                        ms_map.get(ms, "unknown"),
                        p.get("headRefName", ""),
                        p.get("headRefOid", ""),
                        p.get("baseRefName", ""),
                        p.get("additions") or 0,
                        p.get("deletions") or 0,
                        p.get("changedFiles") or 0,
                        p.get("createdAt"),
                        p.get("updatedAt"),
                        p.get("closedAt"),
                        p.get("reviewDecision", ""),
                        ci,
                        failing,
                        self.fingerprint(p.get("title", "")),
                        now,
                    ),
                )
                # Labels: replace-set per PR
                conn.execute(
                    "DELETE FROM pr_label WHERE repo=? AND pr_number=?",
                    (repo, p["number"]),
                )
                for lbl in p.get("labels") or []:
                    conn.execute(
                        "INSERT OR IGNORE INTO pr_label (repo, pr_number, label)"
                        " VALUES (?,?,?)",
                        (repo, p["number"], lbl.get("name", "")),
                    )
        return len(prs)
