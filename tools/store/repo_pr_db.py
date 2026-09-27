#!/usr/bin/env python3
"""Per-repo PR tracking DB — Tier 0 of the governance-aware schema.

One SQLite database per target repository, living in its workspace:

    workspaces/<repo>/generated/pr_tracking.db        (gitignored by rule 62)

Design goals, in order:
  1. USABLE IMMEDIATELY — one command to create, one to populate, joins to the
     Jules session store out of the box.
  2. GOVERNANCE-CORRECT BY CONSTRUCTION — the closure vocabulary does not exist
     in any CHECK domain, so "close because it is old" is unrepresentable.
  3. COMPACT — 8 tables + 7 views instead of the 37-object full schema. The
     dropped objects are listed with their tier in SIMPLIFICATION_ROADMAP.md.

Non-goals at Tier 0: comment/review ingest, hunk-level conflicts, LLM execution.

Usage
-----
  python3 tools/store/repo_pr_db.py init           --repo kaggle-notebooks-analysis
  python3 tools/store/repo_pr_db.py import-jsonl   --repo <repo> [--dir ~/.jules/pr_history]
  python3 tools/store/repo_pr_db.py sync           --repo <repo> [--with-files]
  python3 tools/store/repo_pr_db.py link-sessions  --repo <repo> [--sessions ~/.jules/store.db]
  python3 tools/store/repo_pr_db.py refresh        --repo <repo>
  python3 tools/store/repo_pr_db.py verify         --repo <repo>      # parity vs the API
  python3 tools/store/repo_pr_db.py report         --repo <repo>
  python3 tools/store/repo_pr_db.py init-all                        # every registry repo
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

JULES_ROOT = Path(__file__).resolve().parents[2]
WORKSPACES = JULES_ROOT / "workspaces"
DEFAULT_CORPUS = Path.home() / ".jules" / "pr_history"
DEFAULT_SESSIONS = Path.home() / ".jules" / "store.db"
OWNER = "MasumRab"
PAGE = 50
MAX_ATTEMPTS = 5

# --------------------------------------------------------------------------- schema
SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- Governance travels with the data. Seeded below; read it before editing.
CREATE TABLE IF NOT EXISTS governance_rule (
    rule_id TEXT PRIMARY KEY,
    text    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pull_request (
    pr_number     INTEGER PRIMARY KEY,
    title         TEXT    NOT NULL,
    state         TEXT    NOT NULL CHECK (state IN ('open','closed','merged')),
    is_draft      INTEGER NOT NULL DEFAULT 0,
    merged        INTEGER NOT NULL DEFAULT 0,
    additions     INTEGER NOT NULL DEFAULT 0,
    deletions     INTEGER NOT NULL DEFAULT 0,
    changed_files INTEGER NOT NULL DEFAULT 0,
    churn         INTEGER GENERATED ALWAYS AS (additions + deletions) STORED,
    size_bucket   TEXT    GENERATED ALWAYS AS (
        CASE WHEN additions + deletions <= 50   THEN 'XS'
             WHEN additions + deletions <= 200  THEN 'S'
             WHEN additions + deletions <= 600  THEN 'M'
             WHEN additions + deletions <= 2000 THEN 'L'
             ELSE 'XL' END) STORED,
    head_ref      TEXT,
    base_ref      TEXT,
    head_sha      TEXT,
    author_login  TEXT,
    author_kind   TEXT CHECK (author_kind IS NULL OR author_kind IN
                      ('human','dependabot','jules','trunk','tembo','copilot','other_bot')),
    created_at    TEXT,
    updated_at    TEXT,
    closed_at     TEXT,
    merged_at     TEXT,
    -- governance-sensitive fields are PROJECTIONS of lineage + state
    restoration_status TEXT CHECK (restoration_status IS NULL OR restoration_status IN
                      ('active','merged','superseded','restored_elsewhere','merged_via_successor',
                       'split_into_successors','pending_restoration','pending_analysis',
                       'intentionally_abandoned')),
    historical_outcome TEXT CHECK (historical_outcome IS NULL OR historical_outcome IN
                      ('merged','superseded','restored_elsewhere','merged_via_successor',
                       'split_into_successors','pending_analysis','intentionally_abandoned')),
    historical_outcome_reason TEXT,
    final_reviewed_state TEXT,
    is_historical INTEGER NOT NULL DEFAULT 0,
    -- informational signals: never closure evidence (Rules 1-3)
    has_conflicts      INTEGER NOT NULL DEFAULT 0,
    ci_conclusion      TEXT,
    ci_failing_checks  INTEGER NOT NULL DEFAULT 0,
    review_decision    TEXT,
    approvals          INTEGER NOT NULL DEFAULT 0,
    changes_requested_count INTEGER NOT NULL DEFAULT 0,
    unresolved_thread_count INTEGER NOT NULL DEFAULT 0,
    actionable_comment_count INTEGER NOT NULL DEFAULT 0,
    behind_by          INTEGER,
    title_fingerprint  TEXT,          -- md5, computed in Python (no md5 in SQLite)
    lineage_version    INTEGER NOT NULL DEFAULT 0,
    last_synced_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_pr_state_updated ON pull_request (state, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_pr_fingerprint   ON pull_request (title_fingerprint);
CREATE INDEX IF NOT EXISTS idx_pr_outcome
    ON pull_request (historical_outcome) WHERE state = 'closed' AND merged = 0;
CREATE INDEX IF NOT EXISTS idx_pr_historical    ON pull_request (is_historical) WHERE is_historical = 1;
CREATE INDEX IF NOT EXISTS idx_pr_author        ON pull_request (author_kind, state);

CREATE TABLE IF NOT EXISTS pr_file (
    pr_number  INTEGER NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    path       TEXT    NOT NULL,
    status     TEXT,
    additions  INTEGER,
    deletions  INTEGER,
    changes    INTEGER,
    is_lockfile INTEGER GENERATED ALWAYS AS (
        CASE WHEN path LIKE '%.lock' OR path LIKE '%lock.json' OR path LIKE '%-lock.yaml'
               OR path LIKE '%.lockfile' THEN 1 ELSE 0 END) STORED,
    PRIMARY KEY (pr_number, path)
);
CREATE INDEX IF NOT EXISTS idx_file_path ON pr_file (path);

-- Rule 5: duplicates create lineage, never closures.
CREATE TABLE IF NOT EXISTS pr_lineage (
    ancestor_pr   INTEGER NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    descendant_pr INTEGER NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    relation_type TEXT    NOT NULL CHECK (relation_type IN
                      ('continued_by','superseded_by','merged_via','split_into',
                       'reimplemented_as','rebased_as','restored_as','replaced_by')),
    confidence    REAL    NOT NULL DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    evidence      TEXT,
    discovered_at TEXT    NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (ancestor_pr, descendant_pr, relation_type),
    CHECK (ancestor_pr <> descendant_pr)
);
CREATE INDEX IF NOT EXISTS idx_lineage_desc ON pr_lineage (descendant_pr, relation_type);
CREATE INDEX IF NOT EXISTS idx_lineage_anc  ON pr_lineage (ancestor_pr, relation_type);

CREATE TABLE IF NOT EXISTS pr_jules_session (
    pr_number   INTEGER NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    session_id  TEXT    NOT NULL,
    role        TEXT    NOT NULL DEFAULT 'unknown' CHECK (role IN
                    ('author','review','auto_fix','resolve_conflicts','unknown')),
    link_source TEXT    NOT NULL CHECK (link_source IN ('pr_url','branch_name','body','manual')),
    confidence  REAL    NOT NULL DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    linked_at   TEXT    NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (pr_number, session_id)
);
CREATE INDEX IF NOT EXISTS idx_pr_session ON pr_jules_session (session_id);

CREATE TABLE IF NOT EXISTS restoration_queue (
    pr_number        INTEGER PRIMARY KEY REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    priority_score   REAL,
    restore_reason   TEXT,
    status           TEXT CHECK (status IS NULL OR status IN
                        ('pending_analysis','pending_rebase','pending_restoration',
                         'pending_review','ready_for_merge','blocked','completed')),
    assigned_to      TEXT,
    discovered_at    TEXT DEFAULT (datetime('now')),
    last_reviewed_at TEXT
);

CREATE TABLE IF NOT EXISTS historical_validation (
    validation_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    pr_number       INTEGER NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    validation_type TEXT    NOT NULL CHECK (validation_type IN
                        ('lineage_exists','successor_exists','final_intent_recovered',
                         'implementation_verified','restoration_completed')),
    passed          INTEGER,
    details         TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_hist_val ON historical_validation (pr_number, validation_type);

-- Minimal auditable LLM store. Tier 1 fills it; the shape is fixed now so
-- historical judgments stay interpretable (task codes are immutable).
CREATE TABLE IF NOT EXISTS judgment (
    judgment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_type  TEXT NOT NULL,
    subject_key   TEXT NOT NULL,
    task_code     TEXT NOT NULL,
    output        TEXT NOT NULL,
    confidence    REAL,
    rationale     TEXT NOT NULL,
    model         TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    input_hash    TEXT NOT NULL,
    lineage_version TEXT,
    historical_candidate INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    superseded_by INTEGER REFERENCES judgment(judgment_id),
    UNIQUE (subject_type, subject_key, task_code, input_hash, prompt_version)
);

-- ---------------------------------------------------------------- views
DROP VIEW IF EXISTS v_pr;
CREATE VIEW v_pr AS
SELECT p.*,
       CAST(julianday('now') - julianday(p.created_at) AS INTEGER) AS age_days,
       CAST(julianday('now') - julianday(COALESCE(p.updated_at, p.created_at)) AS INTEGER) AS idle_days,
       (p.behind_by IS NULL) AS cost_is_estimated
FROM pull_request p;

-- Rule 4: closed-unmerged PRs are historical work, not failures.
DROP VIEW IF EXISTS v_historical;
CREATE VIEW v_historical AS
SELECT h.pr_number, h.title, h.state, h.merged, h.age_days, h.idle_days, h.is_historical,
       h.restoration_status, h.historical_outcome, h.historical_outcome_reason,
       h.final_reviewed_state,
       h.churn, h.changed_files, h.size_bucket, h.author_kind,
       h.created_at, h.closed_at, h.base_ref, h.head_ref,
       (SELECT count(*) FROM pr_lineage l WHERE l.ancestor_pr = h.pr_number) AS lineage_edges,
       (SELECT count(*) FROM pr_jules_session s WHERE s.pr_number = h.pr_number) AS jules_sessions,
       (SELECT status FROM restoration_queue q WHERE q.pr_number = h.pr_number) AS queue_status
FROM v_pr h
WHERE h.state = 'closed' AND h.merged = 0;

-- Rule 5: candidates for lineage adjudication. Not duplicates, not closures.
DROP VIEW IF EXISTS v_lineage_candidates;
CREATE VIEW v_lineage_candidates AS
SELECT title_fingerprint,
       group_concat(pr_number, ',') AS prs,
       count(*) AS candidate_count,
       sum(merged) AS merged_count
FROM pull_request
WHERE title_fingerprint IS NOT NULL
GROUP BY title_fingerprint
HAVING count(*) > 1;

-- NOTE: dependabot supersession needs parsed package/scope/manifest evidence.
-- Deliberately absent at Tier 0 rather than shipped as a broken stub — see
-- SIMPLIFICATION_ROADMAP.md Tier 1 (core.dependency_change).

DROP VIEW IF EXISTS v_jules_linked;
CREATE VIEW v_jules_linked AS
SELECT p.pr_number, p.title, p.state, p.merged, p.age_days, p.idle_days,
       p.historical_outcome, p.restoration_status, p.has_conflicts,
       p.ci_failing_checks, p.approvals, p.changes_requested_count,
       s.session_id, s.role, s.link_source, s.confidence
FROM v_pr p JOIN pr_jules_session s ON s.pr_number = p.pr_number;

DROP VIEW IF EXISTS v_restoration_efficiency;
CREATE VIEW v_restoration_efficiency AS
SELECT substr(COALESCE(merged_at, closed_at), 1, 7) AS month,
       sum(CASE WHEN historical_outcome = 'merged' THEN 1 ELSE 0 END)              AS merged,
       sum(CASE WHEN historical_outcome = 'restored_elsewhere' THEN 1 ELSE 0 END)  AS restored_elsewhere,
       sum(CASE WHEN historical_outcome = 'merged_via_successor' THEN 1 ELSE 0 END) AS merged_via_successor,
       sum(CASE WHEN historical_outcome = 'superseded' THEN 1 ELSE 0 END)          AS superseded,
       sum(CASE WHEN historical_outcome = 'pending_analysis' THEN 1 ELSE 0 END)    AS pending_analysis,
       sum(CASE WHEN historical_outcome IN ('merged','restored_elsewhere',
                'merged_via_successor','split_into_successors') THEN churn ELSE 0 END) AS recovered_churn,
       sum(CASE WHEN historical_outcome = 'pending_analysis' THEN churn ELSE 0 END)    AS churn_awaiting_evaluation
FROM pull_request WHERE closed_at IS NOT NULL GROUP BY 1;

-- Operational queue: live work only. Deliberately contains no closure action.
DROP VIEW IF EXISTS v_actionable;
CREATE VIEW v_actionable AS
SELECT pr_number, title, age_days, idle_days, has_conflicts, ci_failing_checks,
       approvals, changes_requested_count, actionable_comment_count, review_decision,
       CASE
         WHEN has_conflicts = 1                  THEN 'resolve_conflicts'
         WHEN ci_failing_checks > 0              THEN 'needs_ci_fix'
         WHEN changes_requested_count > 0
           OR actionable_comment_count > 0       THEN 'address_comments'
         WHEN approvals = 0                      THEN 'request_review'
         WHEN changed_files > 40 OR churn > 2000 THEN 'split_pr'
         ELSE 'merge_or_rebase'
       END AS suggested_action
FROM v_pr WHERE state = 'open';
"""

GOVERNANCE_RULES = [
    ("R1", "PR age is informational only."),
    ("R2", "No PR may be classified as abandoned automatically."),
    ("R3", "No process may recommend closure solely because a PR is old, inactive, CI has not run recently, reviews are outdated, GitHub marked it stale, or a newer PR exists."),
    ("R4", "Closed-unmerged PRs are historical work items requiring classification."),
    ("R5", "Duplicate detection creates lineage links, not closure actions."),
    ("R6", "Every historical PR must eventually be classified as superseded, restored_elsewhere, merged_via_successor, split_into_successors, intentionally_abandoned, or pending_analysis."),
    ("R7", "Reduction of PR count is never a system objective."),
    ("R8", "Historical implementation work is retained forever."),
    ("R9", "Governance actions are validated at three levels: parse, type, behavioural. Parse-clean does not imply governance-compliant."),
    ("R10", "Task codes are immutable: a code's meaning may never change once used in production."),
    ("R11", "Derived truth dominates cached truth: restoration_status / historical_outcome / effective_status are projections recomputable from lineage and state."),
    ("R12", "intentionally_abandoned requires failed lineage analysis (recorded in historical_validation) plus an auditable decision."),
]


# --------------------------------------------------------------------------- helpers
def db_path(repo: str) -> Path:
    return WORKSPACES / repo / "generated" / "pr_tracking.db"


def connect(repo: str) -> sqlite3.Connection:
    p = db_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def fingerprint(title: str) -> str:
    norm = re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()
    return hashlib.md5(norm.encode()).hexdigest()


def author_kind(login: str | None) -> str:
    a = (login or "").lower()
    if "dependabot" in a:
        return "dependabot"
    if "jules" in a:
        return "jules"
    if a.startswith("trunk") or "mergify" in a:
        return "trunk"
    if "tembo" in a:
        return "tembo"
    if "copilot" in a:
        return "copilot"
    if a.endswith("[bot]") or a.endswith("-bot"):
        return "other_bot"
    return "human"


# --------------------------------------------------------------------------- commands
def cmd_init(repo: str, quiet: bool = False) -> None:
    conn = connect(repo)
    conn.executescript(SCHEMA)
    conn.executemany("INSERT OR REPLACE INTO governance_rule (rule_id, text) VALUES (?,?)",
                     GOVERNANCE_RULES)
    conn.commit()
    if not quiet:
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY 1")]
        views = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view' ORDER BY 1")]
        print(f"init {repo}: {db_path(repo)}")
        print(f"  tables ({len(tables)}): {', '.join(tables)}")
        print(f"  views  ({len(views)}): {', '.join(views)}")


def upsert_rows(conn: sqlite3.Connection, rows: list[dict]) -> int:
    """Upsert harvested/synced PR rows. Idempotent on pr_number."""
    n = 0
    for r in rows:
        num = r.get("number") or r.get("pr_number")
        if num is None:
            continue
        state = (r.get("state") or "").lower()
        merged = 1 if (r.get("mergedAt") or r.get("merged_at")) else 0
        if merged and state != "open":
            state = "merged"
        if state not in ("open", "closed", "merged"):
            state = "closed"
        labels = r.get("labels")
        author = r.get("author") or {}
        login = author.get("login") if isinstance(author, dict) else r.get("author_login")
        conn.execute("""
            INSERT INTO pull_request (
                pr_number, title, state, is_draft, merged, additions, deletions, changed_files,
                head_ref, base_ref, head_sha, author_login, author_kind,
                created_at, updated_at, closed_at, merged_at,
                review_decision, title_fingerprint, last_synced_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
            ON CONFLICT (pr_number) DO UPDATE SET
                title=excluded.title, state=excluded.state, is_draft=excluded.is_draft,
                merged=excluded.merged, additions=excluded.additions,
                deletions=excluded.deletions, changed_files=excluded.changed_files,
                head_ref=excluded.head_ref, base_ref=excluded.base_ref, head_sha=excluded.head_sha,
                author_login=excluded.author_login, author_kind=excluded.author_kind,
                updated_at=excluded.updated_at, closed_at=excluded.closed_at,
                merged_at=excluded.merged_at, review_decision=excluded.review_decision,
                title_fingerprint=excluded.title_fingerprint, last_synced_at=datetime('now')
        """, (
            num, r.get("title") or "", state, 1 if r.get("isDraft") else 0, merged,
            r.get("additions") or 0, r.get("deletions") or 0, r.get("changedFiles") or 0,
            r.get("headRefName") or r.get("head_ref"), r.get("baseRefName") or r.get("base_ref"),
            r.get("headRefOid") or r.get("head_sha"), login, author_kind(login),
            r.get("createdAt") or r.get("created_at"), r.get("updatedAt") or r.get("updated_at"),
            r.get("closedAt") or r.get("closed_at"), r.get("mergedAt") or r.get("merged_at"),
            r.get("reviewDecision") or r.get("review_decision"), fingerprint(r.get("title") or ""),
        ))
        n += 1
        for f in (r.get("files") or []):
            conn.execute("""INSERT OR REPLACE INTO pr_file
                (pr_number, path, status, additions, deletions, changes)
                VALUES (?,?,?,?,?,?)""",
                (num, f.get("path"), f.get("status") or f.get("changeType"),
                 f.get("additions"), f.get("deletions"), f.get("changes")))
    conn.commit()
    return n


def cmd_import_jsonl(repo: str, corpus: Path) -> None:
    conn = connect(repo)
    total = 0
    for state_file in sorted(corpus.glob(f"{repo}.*.jsonl")):
        rows = [json.loads(ln) for ln in state_file.read_text().splitlines() if ln.strip()]
        n = upsert_rows(conn, rows)
        total += n
        print(f"  imported {n:5d} from {state_file.name}")
    conn.execute("INSERT OR REPLACE INTO sync_meta (key,value) VALUES (?,?)",
                 (f"import_jsonl:{repo}", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    conn.commit()
    print(f"import-jsonl {repo}: {total} rows upserted")


def cmd_sync(repo: str) -> None:
    """Live GraphQL sync, resumable via sync_meta cursors."""
    conn = connect(repo)
    query = """
    query($owner:String!,$name:String!,$states:[PullRequestState!],$cursor:String){
      repository(owner:$owner,name:$name){
        pullRequests(states:$states, first:%d, after:$cursor,
                     orderBy:{field:CREATED_AT,direction:DESC}){
          totalCount pageInfo{hasNextPage endCursor}
          nodes{ number title state isDraft additions deletions changedFiles createdAt updatedAt
                 closedAt mergedAt reviewDecision headRefName baseRefName headRefOid
                 author{ login } labels(first:20){nodes{name}} }
        } } }
    """ % PAGE
    for bucket in ("OPEN", "MERGED", "CLOSED"):
        key = f"cursor:{repo}:{bucket}"
        cur = conn.execute("SELECT value FROM sync_meta WHERE key=?", (key,)).fetchone()
        cursor = cur["value"] if cur else None
        seen = 0
        while True:
            page = gql(query, {"owner": OWNER, "name": repo, "states[]": bucket, "cursor": cursor})
            pr = page["repository"]["pullRequests"]
            upsert_rows(conn, pr["nodes"])
            seen += len(pr["nodes"])
            if not pr["pageInfo"]["hasNextPage"]:
                conn.execute("INSERT OR REPLACE INTO sync_meta (key,value) VALUES (?,?)",
                             (f"total:{repo}:{bucket}", str(pr["totalCount"])))
                conn.execute("DELETE FROM sync_meta WHERE key=?", (key,))
                conn.commit()
                break
            cursor = pr["pageInfo"]["endCursor"]
            conn.execute("INSERT OR REPLACE INTO sync_meta (key,value) VALUES (?,?)", (key, cursor))
            conn.commit()
        print(f"  synced {seen:5d} {bucket.lower()} PRs")
    conn.execute("INSERT OR REPLACE INTO sync_meta (key,value) VALUES (?,?)",
                 (f"last_sync:{repo}", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    conn.commit()
    # file ingest is a separate, resumable command: fetch-files


def gql(query: str, variables: dict) -> dict:
    """Run a GraphQL query via gh.

    gh's -f passes a raw STRING and -F passes a TYPED value. Using -f for an
    Int! variable fails with "Variable $number of type Int! was provided invalid
    value" — so the flag is chosen from the Python type, not hardcoded.
    """
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        if v is None:
            continue
        flag = "-F" if isinstance(v, (int, float, bool)) else "-f"
        cmd += [flag, f"{k}={v}"]
    last = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode == 0:
            try:
                payload = json.loads(p.stdout)
                if payload.get("data"):
                    return payload["data"]
                last = str(payload.get("errors"))[:200]
            except json.JSONDecodeError:
                last = "bad JSON"
        else:
            last = p.stderr.strip()[:200]
        time.sleep(5 * attempt)
    raise RuntimeError(f"graphql failed after {MAX_ATTEMPTS} attempts: {last}")



FILES_QUERY = """
query($owner:String!,$name:String!,$number:Int!,$cursor:String){
  repository(owner:$owner,name:$name){
    pullRequest(number:$number){
      files(first:100, after:$cursor){
        totalCount
        pageInfo{ hasNextPage endCursor }
        nodes{ path additions deletions changeType }
      } } } }
"""



# --------------------------------------------------------------------------- reopen
TRUNK_SQL = """(
    COALESCE(author_kind,'') = 'trunk'
    OR lower(COALESCE(author_login,'')) LIKE 'trunk%'
    OR lower(COALESCE(head_ref,''))     LIKE 'trunk%'
    OR lower(COALESCE(head_ref,''))     LIKE 'mergify%'
)"""


def reopen_candidates(conn: sqlite3.Connection, repo: str, scope: str,
                      exclude_trunk: bool = True, require_session: bool = False,
                      live_branches: set[str] | None = None,
                      allow_empty_diff: bool = False) -> list[sqlite3.Row]:
    """Closed-unmerged PRs eligible for reopening, with every exclusion applied.

    Eligibility is deliberately conservative: a PR is only a candidate when its
    head branch still exists (GitHub cannot reopen otherwise), it is not a
    whole-repo-diff artifact, and its change is small enough to be reviewable.
    """
    sql = f"""SELECT pr_number, title, head_ref, base_ref, changed_files, churn,
                     author_login, author_kind,
                     CAST(julianday('now')-julianday(created_at) AS INT) AS age_days,
                     (SELECT count(*) FROM pr_jules_session s
                       WHERE s.pr_number = pull_request.pr_number) AS jules_sessions
              FROM pull_request
              WHERE state='closed' AND merged=0
                AND changed_files <= 300
                AND churn <= 2000
                AND (changed_files > 0 OR churn > 0)
                {('AND NOT ' + TRUNK_SQL) if exclude_trunk else ''}
             ORDER BY age_days"""
    rows = conn.execute(sql).fetchall()
    if live_branches is not None:
        rows = [r for r in rows if r["head_ref"] in live_branches]
    if scope == "reopenable":
        wide = f"""SELECT pr_number, title, head_ref, base_ref, changed_files, churn,
                          author_login, author_kind,
                          CAST(julianday('now')-julianday(created_at) AS INT) AS age_days,
                          (SELECT count(*) FROM pr_jules_session s
                            WHERE s.pr_number = pull_request.pr_number) AS jules_sessions
                   FROM pull_request
                   WHERE state='closed' AND merged=0
                     {('AND NOT ' + TRUNK_SQL) if exclude_trunk else ''}
                   ORDER BY age_days"""
        rows = conn.execute(wide).fetchall()
        if live_branches is not None:
            rows = [r for r in rows if r["head_ref"] in live_branches]
    if require_session:
        rows = [r for r in rows if r["jules_sessions"] > 0]
    if not allow_empty_diff and scope == "reopenable":
        rows = [r for r in rows if (r["changed_files"] or 0) > 0 or (r["churn"] or 0) > 0]
    return rows


def live_branch_set(repo: str) -> set[str]:
    out = subprocess.run(["gh", "api", f"repos/{OWNER}/{repo}/branches?per_page=100",
                          "--paginate", "--jq", ".[].name"],
                         capture_output=True, text=True)
    return {ln.strip() for ln in out.stdout.splitlines() if ln.strip()}



# --------------------------------------------------------------------------- restore
def pr_head_sha(repo: str, pr: int, fallback: str | None = None) -> str | None:
    """Authoritative head SHA for a PR.

    `refs/pull/<n>/head` survives branch deletion, so it is preferred over the
    PR's recorded head_sha — it works even for PRs ingested before headRefOid
    was captured (fullstack and kaggle currently have none).
    """
    out = subprocess.run(["gh", "api", f"repos/{OWNER}/{repo}/git/ref/pull/{pr}/head",
                          "--jq", ".object.sha"], capture_output=True, text=True)
    sha = out.stdout.strip()
    return sha or fallback


def cmd_restore_branch(repo: str, confirm: bool, limit: int | None,
                       exclude_trunk: bool = True, then_reopen: bool = False,
                       include_dependabot: bool = False) -> None:
    """Recreate deleted head branches at their PR head commit.

    Reversible: this only creates refs; `gh api -X DELETE .../git/refs/heads/<name>`
    removes them again. Restoring a branch does NOT reopen the PR — that stays a
    separate, deliberate step.
    """
    conn = connect(repo)
    live = live_branch_set(repo)
    rows = conn.execute("""SELECT pr_number, head_ref, head_sha, changed_files, churn
                           FROM pull_request
                           WHERE state='closed' AND merged=0
                             AND head_ref IS NOT NULL
                           ORDER BY pr_number""").fetchall()
    missing = [r for r in rows if r["head_ref"] not in live]
    if exclude_trunk:
        missing = [r for r in missing
                   if not (r["head_ref"] or "").lower().startswith(("trunk", "mergify"))]
    # A closed dependabot branch is a superseded version bump, not historical
    # implementation work — the value is captured by the newer bump. Restoring
    # them adds branch clutter, and dependabot may delete them again on its next
    # run. Excluded by default; --include-dependabot restores them too.
    dep = [r for r in missing if (r["head_ref"] or "").lower().startswith(("dependabot", "renovate"))]
    if not include_dependabot:
        missing = [r for r in missing if r not in dep]
    empty = [r for r in missing if (r["changed_files"] or 0) == 0 and (r["churn"] or 0) == 0]
    missing = [r for r in missing if r not in empty]
    if limit:
        missing = missing[:limit]
    print(f"restore-branch {repo}: {len(missing)} branch(es) to recreate "
          f"(skipped: {len(empty)} empty-diff, {0 if include_dependabot else len(dep)} dependabot, "
          f"trunk excluded={exclude_trunk})")
    restored = failed = 0
    for r in missing:
        pr, ref = r["pr_number"], r["head_ref"]
        sha = pr_head_sha(repo, pr, r["head_sha"])
        if not sha:
            failed += 1
            print(f"  #{pr} {ref[:40]} NO SHA available")
            continue
        if not confirm:
            print(f"  #{pr} {ref[:44]:44s} <- {sha[:12]}  (dry run)")
            continue
        res = subprocess.run(["gh", "api", "-X", "POST", f"repos/{OWNER}/{repo}/git/refs",
                              "-f", f"ref=refs/heads/{ref}", "-f", f"sha={sha}"],
                             capture_output=True, text=True)
        if res.returncode == 0:
            restored += 1
            conn.execute("""INSERT INTO sync_meta (key,value) VALUES (?,?)
                            ON CONFLICT (key) DO UPDATE SET value=excluded.value""",
                         (f"branch_restored:{repo}:{pr}",
                          time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            conn.commit()
            print(f"  #{pr} restored {ref[:44]}")
            if then_reopen:
                subprocess.run(["gh", "pr", "reopen", str(pr), "--repo", f"{OWNER}/{repo}"],
                               capture_output=True, text=True)
        else:
            failed += 1
            print(f"  #{pr} FAILED: {res.stderr.strip()[:130]}")
        time.sleep(1)
    if confirm:
        print(f"  restored {restored}, failed {failed}")
    else:
        print("  DRY RUN — pass --confirm to create the refs")


def cmd_reopen(repo: str, scope: str, exclude_trunk: bool, require_session: bool,
               confirm: bool, limit: int | None) -> None:
    conn = connect(repo)
    live = live_branch_set(repo)
    rows = reopen_candidates(conn, repo, scope, exclude_trunk, require_session, live)
    if limit:
        rows = rows[:limit]
    print(f"reopen {repo}: scope={scope} exclude_trunk={exclude_trunk} "
          f"require_session={require_session} -> {len(rows)} PR(s)")
    for r in rows:
        print(f"  #{r['pr_number']:<5} age={r['age_days']:>4}d files={r['changed_files']:>4} "
              f"churn={r['churn']:>6} sessions={r['jules_sessions']} ref={r['head_ref']}")
    if not confirm:
        print("  DRY RUN — pass --confirm to actually reopen")
        return
    ok = failed = 0
    for r in rows:
        res = subprocess.run(["gh", "pr", "reopen", str(r["pr_number"]), "--repo", f"{OWNER}/{repo}"],
                             capture_output=True, text=True)
        if res.returncode == 0:
            ok += 1
            conn.execute("""INSERT INTO sync_meta (key,value) VALUES (?,?)
                            ON CONFLICT (key) DO UPDATE SET value=excluded.value""",
                         (f"reopened:{repo}:{r['pr_number']}",
                          time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            conn.commit()
        else:
            failed += 1
            print(f"    #{r['pr_number']} FAILED: {res.stderr.strip()[:120]}")
        time.sleep(1)
    print(f"  reopened {ok}, failed {failed}")


def cmd_fetch_files(repo: str, budget: int | None = None, force: bool = False) -> None:
    """Fetch changed files per PR into pr_file. Resumable: skips PRs that already
    have rows unless --force. `budget` caps API calls for a bounded run."""
    conn = connect(repo)
    # Artifact guard: PRs carrying a whole-repository diff (the contaminated-branch
    # class — 135 PRs across the portfolio hold ~97% of all churn, some with 7,997
    # files) cost hundreds of API calls each and yield nothing usable. Their size is
    # already recorded on pull_request.changed_files, so file detail is skipped and
    # counted, not silently dropped.
    ARTIFACT_FILE_THRESHOLD = 300
    skipped = conn.execute(
        "SELECT count(*) FROM pull_request WHERE changed_files > ?",
        (ARTIFACT_FILE_THRESHOLD,)).fetchone()[0]
    if force:
        todo = conn.execute("SELECT pr_number FROM pull_request ORDER BY pr_number").fetchall()
    else:
        todo = conn.execute("""SELECT p.pr_number FROM pull_request p
            WHERE p.changed_files <= ?
              AND NOT EXISTS (SELECT 1 FROM pr_file f WHERE f.pr_number = p.pr_number)
            ORDER BY (p.state='open') DESC, p.pr_number""",
            (ARTIFACT_FILE_THRESHOLD,)).fetchall()
    if budget:
        todo = todo[:budget]
    done = 0
    for row in todo:
        pr = row["pr_number"]
        cursor = None
        while True:
            data = gql(FILES_QUERY, {"owner": OWNER, "name": repo, "number": pr, "cursor": cursor})
            files = data["repository"]["pullRequest"]["files"]
            for f in files["nodes"]:
                conn.execute("""INSERT OR REPLACE INTO pr_file
                    (pr_number, path, status, additions, deletions, changes)
                    VALUES (?,?,?,?,?,?)""",
                    (pr, f["path"], f.get("changeType"), f.get("additions"),
                     f.get("deletions"), (f.get("additions") or 0) + (f.get("deletions") or 0)))
            if not files["pageInfo"]["hasNextPage"]:
                break
            cursor = files["pageInfo"]["endCursor"]
        conn.commit()
        done += 1
        if done % 25 == 0:
            print(f"    files: {done}/{len(todo)} PRs", flush=True)
    conn.execute("INSERT OR REPLACE INTO sync_meta (key,value) VALUES (?,?)",
                 (f"files_synced:{repo}", str(done)))
    conn.commit()
    total = conn.execute("SELECT count(*) FROM pr_file").fetchone()[0]
    print(f"fetch-files {repo}: {done} PRs processed, pr_file now {total} rows "
          f"({skipped} PRs skipped as >{ARTIFACT_FILE_THRESHOLD}-file artifacts)")


def cmd_link_sessions(repo: str, sessions_db: Path) -> None:
    """Link PRs to Jules sessions by parsing pr_url. Read-only on the session store."""
    conn = connect(repo)
    if not sessions_db.exists():
        print(f"link-sessions: session store not found at {sessions_db}")
        return
    src = sqlite3.connect(f"file:{sessions_db}?mode=ro", uri=True)
    src.row_factory = sqlite3.Row
    n = 0
    for s in src.execute(
            "SELECT session_id, repo, pr_url, state, session_type FROM sessions WHERE pr_url IS NOT NULL"):
        # AUTHORITATIVE: parse owner/repo out of the URL itself. Neither the
        # session store's `repo` column (NULL for 64 sessions) nor PR-number
        # existence is safe — PR numbers collide across repositories, so the
        # earlier version could false-link a cross-repo session.
        m = re.search(r"github\.com/[^/]+/([^/]+)/pull/(\d+)", s["pr_url"] or "")
        if not m:
            continue
        url_repo, pr = m.group(1), int(m.group(2))
        if url_repo != repo:
            continue
        if not conn.execute("SELECT 1 FROM pull_request WHERE pr_number=?", (pr,)).fetchone():
            continue  # session for a PR outside this DB's scope
        role = "author"
        st = (s["session_type"] or "").lower()
        if "review" in st:
            role = "review"
        elif "fix" in st:
            role = "auto_fix"
        elif "conflict" in st:
            role = "resolve_conflicts"
        conn.execute("""INSERT INTO pr_jules_session (pr_number, session_id, role, link_source, confidence)
                        VALUES (?,?,?,'pr_url',1.0)
                        ON CONFLICT (pr_number, session_id) DO UPDATE SET role=excluded.role""",
                     (pr, s["session_id"], role))
        n += 1
    conn.commit()
    src.close()
    linked = conn.execute("SELECT count(DISTINCT pr_number) FROM pr_jules_session").fetchone()[0]
    print(f"link-sessions {repo}: {n} session links, covering {linked} PRs")


def cmd_refresh(repo: str) -> None:
    """Recompute projections (Rule 11) and enqueue historical work (Rule 4)."""
    conn = connect(repo)
    # is_historical — Rule 1: informational only, never changes the outcome
    conn.execute("""UPDATE pull_request SET is_historical =
        CASE WHEN created_at IS NOT NULL
              AND (julianday('now') - julianday(created_at)) > 365 THEN 1 ELSE 0 END""")
    # restoration_status — lineage-derived; human abandonment is sticky
    conn.execute("""UPDATE pull_request SET restoration_status = CASE
        WHEN merged = 1 THEN 'merged'
        WHEN state = 'open' THEN 'active'
        WHEN restoration_status = 'intentionally_abandoned' THEN 'intentionally_abandoned'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l WHERE l.ancestor_pr = pr_number AND l.relation_type='restored_as') THEN 'restored_elsewhere'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l WHERE l.ancestor_pr = pr_number AND l.relation_type='split_into') THEN 'split_into_successors'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l WHERE l.ancestor_pr = pr_number AND l.relation_type IN ('superseded_by','replaced_by') AND l.confidence >= 0.95) THEN 'superseded'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l WHERE l.ancestor_pr = pr_number AND l.relation_type='merged_via') THEN 'merged_via_successor'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l WHERE l.ancestor_pr = pr_number AND l.relation_type='continued_by') THEN 'pending_restoration'
        ELSE 'pending_analysis' END""")
    # historical_outcome — Rule 4 + Rule 6 (7 values)
    conn.execute("""UPDATE pull_request SET historical_outcome = CASE
        WHEN merged = 1 THEN 'merged'
        WHEN state <> 'closed' THEN NULL
        WHEN restoration_status = 'superseded' THEN 'superseded'
        WHEN restoration_status = 'restored_elsewhere' THEN 'restored_elsewhere'
        WHEN restoration_status = 'merged_via_successor' THEN 'merged_via_successor'
        WHEN restoration_status = 'split_into_successors' THEN 'split_into_successors'
        WHEN restoration_status = 'intentionally_abandoned' THEN 'intentionally_abandoned'
        ELSE 'pending_analysis' END""")
    # enqueue historical work for evaluation — not a closure proposal
    conn.execute("""INSERT INTO restoration_queue (pr_number, status, restore_reason, priority_score)
        SELECT pr_number, 'pending_analysis',
               CASE WHEN is_historical = 1
                    THEN 'long-lived repository rule: historical work awaiting evaluation'
                    ELSE 'closed unmerged: restoration candidate' END,
               (COALESCE(churn,0) / 1000.0)
                 - (SELECT count(*) FROM pr_lineage l WHERE l.ancestor_pr = pull_request.pr_number) * 5
        FROM pull_request WHERE state = 'closed' AND merged = 0
        ON CONFLICT (pr_number) DO NOTHING""")
    conn.commit()
    row = conn.execute("""SELECT
        (SELECT count(*) FROM pull_request) AS prs,
        (SELECT count(*) FROM pull_request WHERE state='open') AS open,
        (SELECT count(*) FROM pull_request WHERE state='closed' AND merged=0) AS historical,
        (SELECT count(*) FROM pull_request WHERE is_historical=1) AS over_365,
        (SELECT count(*) FROM restoration_queue) AS queued,
        (SELECT count(*) FROM pr_jules_session) AS session_links""").fetchone()
    print(f"refresh {repo}: prs={row['prs']} open={row['open']} historical={row['historical']} "
          f"over_365d={row['over_365']} queued={row['queued']} session_links={row['session_links']}")


def cmd_verify(repo: str) -> None:
    """Parity: stored rows per state vs the API's declared totals (Rule: no truncation)."""
    conn = connect(repo)
    print(f"verify {repo}")
    ok = True
    for bucket, state_pred in (("OPEN", "state='open'"),
                               ("MERGED", "state='merged'"),
                               ("CLOSED", "state='closed' AND merged=0")):
        local = conn.execute(f"SELECT count(*) FROM pull_request WHERE {state_pred}").fetchone()[0]
        q = '{repository(owner:"%s",name:"%s"){pullRequests(states:[%s]){totalCount}}}' % (OWNER, repo, bucket)
        declared = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"],
                                  capture_output=True, text=True)
        try:
            api = json.loads(declared.stdout)["data"]["repository"]["pullRequests"]["totalCount"]
        except Exception:  # noqa: BLE001
            api = None
        flag = "OK" if api == local else "MISMATCH"
        if api != local:
            ok = False
        print(f"  {bucket:7s} local={local:5d} api={api} {flag}")
    print(f"  -> {'parity confirmed' if ok else 'PARITY FAILURE — data is incomplete'}")


def cmd_report(repo: str) -> None:
    conn = connect(repo)
    r = conn.execute("SELECT * FROM v_restoration_efficiency").fetchall()
    print(f"\n=== {repo} ===")
    totals = conn.execute("""SELECT count(*) prs,
        sum(CASE WHEN state='open' THEN 1 ELSE 0 END) open,
        sum(CASE WHEN state='closed' AND merged=0 THEN 1 ELSE 0 END) historical,
        sum(CASE WHEN historical_outcome='merged' THEN 1 ELSE 0 END) merged,
        sum(CASE WHEN historical_outcome='pending_analysis' THEN 1 ELSE 0 END) pending
        FROM pull_request""").fetchone()
    print(f"  PRs {totals['prs']} | open {totals['open']} | historical {totals['historical']} "
          f"| merged {totals['merged']} | pending_analysis {totals['pending']}")
    direct = 100.0 * (totals["merged"] or 0) / max(1, totals["prs"])
    print(f"  direct merge rate: {direct:.1f}%  (historical work may still resolve via "
          f"successor/restoration — see Part C interpretation rules)")
    linked = conn.execute("SELECT count(DISTINCT pr_number) FROM pr_jules_session").fetchone()[0]
    print(f"  PRs linked to Jules sessions: {linked}")
    print("  top lineage candidates:")
    for row in conn.execute("""SELECT title_fingerprint, prs, candidate_count FROM v_lineage_candidates
                               ORDER BY candidate_count DESC LIMIT 3"""):
        print(f"    {row['candidate_count']}x PRs {row['prs']}")
    if r:
        print("  restoration efficiency (recent months):")
        for row in r[-3:]:
            print(f"    {row['month']}: merged={row['merged']} pending={row['pending_analysis']} "
                  f"recovered_churn={row['recovered_churn']}")


def cmd_init_all() -> None:
    reg = JULES_ROOT / "workspaces" / "registry.yaml"
    repos = re.findall(r"^\s*-\s*name:\s*(\S+)", reg.read_text(), re.M) if reg.exists() else []
    for repo in repos:
        cmd_init(repo)
    print(f"init-all: {len(repos)} repos")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["init", "init-all", "import-jsonl", "sync",
                                        "fetch-files", "link-sessions", "refresh",
                                        "verify", "report", "reopen", "restore-branch"])
    ap.add_argument("--repo")
    ap.add_argument("--dir", default=str(DEFAULT_CORPUS))
    ap.add_argument("--sessions", default=str(DEFAULT_SESSIONS))
    ap.add_argument("--budget", type=int, help="cap API calls for a bounded run")
    ap.add_argument("--force", action="store_true", help="re-fetch even if rows exist")
    ap.add_argument("--scope", default="candidates", choices=["candidates", "reopenable"],
                    help="candidates = small/non-artifact; reopenable = any with a live branch")
    ap.add_argument("--require-session", action="store_true",
                    help="only PRs with a Jules session behind them")
    ap.add_argument("--include-trunk", action="store_true",
                    help="INCLUDES trunk-merge branches; excluded by default")
    ap.add_argument("--confirm", action="store_true", help="actually reopen (default is dry run)")
    ap.add_argument("--allow-empty-diff", action="store_true",
                    help="include PRs whose diff is empty (excluded by default: an empty diff is "
                         "evidence the work already landed, not a restoration target)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--then-reopen", action="store_true",
                    help="reopen the PR after its branch is restored")
    ap.add_argument("--include-dependabot", action="store_true",
                    help="also restore dependabot/renovate branches (excluded by default)")
    a = ap.parse_args()

    if a.command == "init-all":
        cmd_init_all()
        return 0
    if not a.repo:
        ap.error(f"--repo is required for {a.command}")
    if a.command == "init":
        cmd_init(a.repo)
    elif a.command == "import-jsonl":
        cmd_import_jsonl(a.repo, Path(a.dir))
    elif a.command == "sync":
        cmd_sync(a.repo)
    elif a.command == "fetch-files":
        cmd_fetch_files(a.repo, a.budget, a.force)
    elif a.command == "link-sessions":
        cmd_link_sessions(a.repo, Path(a.sessions))
    elif a.command == "refresh":
        cmd_refresh(a.repo)
    elif a.command == "verify":
        cmd_verify(a.repo)
    elif a.command == "report":
        cmd_report(a.repo)
    elif a.command == "restore-branch":
        cmd_restore_branch(a.repo, a.confirm, a.limit,
                           exclude_trunk=not a.include_trunk, then_reopen=a.then_reopen,
                           include_dependabot=a.include_dependabot)
    elif a.command == "reopen":
        cmd_reopen(a.repo, a.scope, exclude_trunk=not a.include_trunk,
                   require_session=a.require_session, confirm=a.confirm, limit=a.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
