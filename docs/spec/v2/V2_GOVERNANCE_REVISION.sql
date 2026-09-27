-- ============================================================================
-- V2 GOVERNANCE REVISION — historical work preservation, lineage, restoration
--
-- Applies the author's governance model (2026-09-26) to the V2 schema:
--   * age/inactivity/staleness are NEVER closure evidence
--   * closed-unmerged PRs remain restoration candidates
--   * duplicates create lineage, not closures
--   * every closed-unmerged PR receives a restoration classification
--
-- This file is a DELTA over V1 + V2 Part 2 + V2_PART1_GENERATED.sql.
-- It SUPERSEDES specific delivered objects; each supersession is named.
--
-- VALIDATION: every statement parsed with pglast (PostgreSQL grammar).
-- Logic of the two new state functions and the corrected suggest_action() is
-- executed in SQLite. See GOVERNANCE_NOTES.md.
--
-- Transmissions artefacts corrected here (flagged for the author):
--   (a) count() -> count(*)  [count() is invalid SQL; 4 occurrences]
--   (b) 'conflicts_with  -> 'conflicts_with'  [unterminated literal]
-- ============================================================================

-- ========== G0. GOVERNANCE RULES (as schema documentation) ==========
-- Stored as comments so the rules travel with the database itself.

COMMENT ON SCHEMA core IS
$doc$
PR GOVERNANCE RULES (authoritative — 2026-09-26)

 1. PR age is informational only.
 2. No automated process may recommend closure solely because a PR is old,
    inactive, marked stale by GitHub, has outdated reviews, or has not run CI
    recently.
 3. Closed unmerged PRs remain restoration candidates.
 4. Every closed unmerged PR must eventually be classified as exactly one of:
    superseded | restored_elsewhere | split_into_successors |
    intentionally_abandoned | pending_analysis.
 5. Duplicate detection creates lineage links, not closure actions.
 6. Merge ordering must respect historical dependencies.
 7. Supersession must preserve traceable ancestry.
 8. Historical work must remain queryable permanently.
 9. Reduction of open PR count is never a system objective.
10. The primary objective is recovery and integration of reviewed historical work.

LONG-LIVED REPOSITORY RULE
 A PR older than 365 days is HISTORICAL WORK IN NEED OF EVALUATION, not stale.
 Historical PRs receive a default restoration_status of 'pending_analysis'
 until lineage and final intent are determined.

REVIEW-OUTDATED SEMANTICS
 Review staleness indicates only that additional review may be required.
 It never implies closure, supersession, or abandonment.
$doc$;


-- ========== G1. ENUM REPLACEMENT (safe form) ==========
-- HAZARD: the requested `DROP TYPE core.triage_action CASCADE` would cascade-
-- drop every dependent column and view (pr_triage.recommended_action,
-- triage_event.action, and any view selecting them). Implemented instead as:
-- create successor type -> migrate columns -> rename legacy aside -> promote.
-- Effect is identical, without destroying dependents.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace
                   WHERE n.nspname = 'core' AND t.typname = 'triage_action_v2') THEN
        CREATE TYPE core.triage_action_v2 AS ENUM (
            'merge_now',
            'rebase_then_merge',
            'resolve_conflicts',
            'address_comments',
            'request_review',
            'reconstruct_final_state',
            'restore_historical_work',
            'merge_via_successor',
            'record_lineage',
            'verify_supersession',
            'split_pr',
            'wait_on_dependency',
            'needs_ci_fix',
            'needs_historical_analysis',
            'escalate_human'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace
                   WHERE n.nspname = 'core' AND t.typname = 'relation_kind_v2') THEN
        CREATE TYPE core.relation_kind_v2 AS ENUM (
            'depends_on',
            'blocks',
            'duplicate_candidate',
            'continued_by',
            'superseded_by',
            'shares_lineage_with',
            'stacked_on',
            'related',
            'conflicts_with'
        );
    END IF;
END $$;

-- Migrate dependent columns. The mapping retires the closure verbs: any
-- historical close_* value becomes a restoration verb, never a closure.
--
-- ⚠ REQUIRED PRE-STEP (PostgreSQL will refuse otherwise): a column's type cannot
-- be altered while a VIEW selects it — the server raises
-- "cannot alter type of a column used by a view or rule". These delivered views
-- select pr_triage.recommended_action / triage_event.action and must be dropped
-- before G1 and recreated verbatim from V2 Part 2 afterwards:
--
--     DROP VIEW IF EXISTS v_triage_queue;
--     DROP VIEW IF EXISTS v_pr_dossier;
--     -- ... then re-run their CREATE VIEW statements from V2 Part 2 A3/A4.
--
-- They are NOT re-typed here on purpose: a hand-copied 60-line view definition
-- is exactly the transcription risk this project has been avoiding. Recreate
-- from the delivered text, then diff against any saved copy.
--
-- (Reasoned, not executed — no Postgres server was available. Verify with
--  \d+ v_triage_queue after the ALTERs.)

ALTER TABLE pr_triage ALTER COLUMN recommended_action TYPE core.triage_action_v2
    USING (CASE recommended_action::text
               WHEN 'close_stale'       THEN 'needs_historical_analysis'
               WHEN 'close_duplicate'   THEN 'record_lineage'
               WHEN 'close_superseded'  THEN 'verify_supersession'
               ELSE recommended_action::text
           END::core.triage_action_v2);

ALTER TABLE triage_event ALTER COLUMN action TYPE core.triage_action_v2
    USING (CASE action::text
               WHEN 'close_stale'       THEN 'needs_historical_analysis'
               WHEN 'close_duplicate'   THEN 'record_lineage'
               WHEN 'close_superseded'  THEN 'verify_supersession'
               ELSE action::text
           END::core.triage_action_v2);

-- pr_relation.kind uses core.relation_kind; migrate the same way.
ALTER TABLE pr_relation ALTER COLUMN kind TYPE core.relation_kind_v2
    USING (CASE kind::text
               WHEN 'duplicate_of'      THEN 'duplicate_candidate'
               ELSE kind::text
           END::core.relation_kind_v2);

-- Promote: legacy aside, successor into the canonical name. Guarded so a
-- re-run is a no-op rather than an error.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace
               WHERE n.nspname = 'core' AND t.typname = 'triage_action') THEN
        ALTER TYPE core.triage_action RENAME TO triage_action_legacy;
    END IF;
    ALTER TYPE core.triage_action_v2 RENAME TO triage_action;

    IF EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace
               WHERE n.nspname = 'core' AND t.typname = 'relation_kind') THEN
        ALTER TYPE core.relation_kind RENAME TO relation_kind_legacy;
    END IF;
    ALTER TYPE core.relation_kind_v2 RENAME TO relation_kind;
END $$;
-- The *_legacy types are deliberately retained: dropping them would break any
-- view or CHECK still referencing them, and they cost nothing. Drop manually
-- after verifying no dependents remain.


-- ========== G2. PULL_REQUEST: closure columns out, restoration state in ==========

-- Rule 9: `abandoned` encodes "closed and not merged" as a terminal judgement.
-- It is replaced by a classification that can be reasoned about and revised.
ALTER TABLE pull_request DROP COLUMN IF EXISTS abandoned;

ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS restoration_status TEXT;
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS effective_status   TEXT;
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS restoration_reason TEXT;
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS is_historical      BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS final_reviewed_state TEXT;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pr_restoration_status_known') THEN
        ALTER TABLE pull_request ADD CONSTRAINT pr_restoration_status_known CHECK (
            restoration_status IS NULL OR restoration_status IN (
                'active','merged','superseded','restored_elsewhere',
                'split_into_successors','pending_restoration','pending_analysis',
                'intentionally_abandoned'));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pr_effective_status_known') THEN
        ALTER TABLE pull_request ADD CONSTRAINT pr_effective_status_known CHECK (
            effective_status IS NULL OR effective_status IN (
                'active','merged','ready_for_merge','needs_rebase','needs_restoration',
                'restored_elsewhere','superseded','historical_reference',
                'intentionally_abandoned'));
    END IF;
END $$;

-- `abandoned` had a generated expression over (state, merged); anything that
-- selected it must now use restoration_status. Known dependents: v_wasted_churn,
-- v_zombies (indirectly via v_pr), core.v_all_prs, core.v_portfolio_efficiency.
CREATE INDEX IF NOT EXISTS idx_pr_restoration_status
    ON pull_request (restoration_status) WHERE state = 'closed' AND merged = FALSE;
CREATE INDEX IF NOT EXISTS idx_pr_historical
    ON pull_request (is_historical) WHERE is_historical;

COMMENT ON COLUMN pull_request.restoration_status IS
    'Rule 4 classification. Closed-unmerged defaults to pending_analysis; only a human decision may set intentionally_abandoned.';
COMMENT ON COLUMN pull_request.effective_status IS
    'Operator-facing state. Distinct from restoration_status: a PR can be active+needs_rebase.';
COMMENT ON COLUMN pull_request.is_historical IS
    'Long-lived repository rule: age > 365 days. Informational — never a closure signal.';
COMMENT ON COLUMN pull_request.final_reviewed_state IS
    'Reconstructed reviewed state for historical work (branch, tree, review set) once determined.';


-- ========== G3. PR LINEAGE ==========

CREATE TABLE IF NOT EXISTS pr_lineage (
    ancestor_pr   INTEGER     NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    descendant_pr INTEGER     NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    relation_type TEXT        NOT NULL,
    confidence    NUMERIC(3,2) NOT NULL DEFAULT 1.00,
    evidence      TEXT,
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (ancestor_pr, descendant_pr, relation_type),
    CONSTRAINT pr_lineage_not_self CHECK (ancestor_pr <> descendant_pr),
    CONSTRAINT pr_lineage_confidence_range CHECK (confidence >= 0 AND confidence <= 1),
    -- CHOICE: the eight documented relation values are enforced as a CHECK.
    -- The author specified the values in prose; enforcing them prevents the
    -- free-text drift that would otherwise break rule 7 (traceable ancestry).
    CONSTRAINT pr_lineage_relation_known CHECK (relation_type IN (
        'continued_by','superseded_by','split_into','merged_via',
        'rebased_as','reimplemented_as','replaced_by','restored_as'))
);

CREATE INDEX IF NOT EXISTS idx_lineage_descendant
    ON pr_lineage (descendant_pr, relation_type);
CREATE INDEX IF NOT EXISTS idx_lineage_ancestor
    ON pr_lineage (ancestor_pr, relation_type);
CREATE INDEX IF NOT EXISTS idx_lineage_confident
    ON pr_lineage (relation_type, confidence DESC);

COMMENT ON TABLE pr_lineage IS
    'Rule 5/7: directed ancestry between PRs. Duplicate detection writes here; it never closes anything.';
COMMENT ON COLUMN pr_lineage.confidence IS
    'Adjudicated confidence. 1.00 = human-confirmed; >= 0.95 is the supersession threshold used by v_dependabot_superseded.';

-- CHOICE: lineage vs the delivered pr_relation. They are kept separate:
-- pr_relation is the undirected-ish general graph (conflicts, blocks) keyed on
-- core.relation_kind; pr_lineage is strictly directed ancestry. Flagged in
-- GOVERNANCE_NOTES §4 for the author — merging them is defensible if the
-- duplicate vocabularies are not wanted.


-- ========== G4. RESTORATION QUEUE ==========

CREATE TABLE IF NOT EXISTS restoration_queue (
    pr_number        INTEGER PRIMARY KEY REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    priority_score   NUMERIC(10,2),
    restore_reason   TEXT,
    status           TEXT,
    assigned_to      TEXT,
    discovered_at    TIMESTAMPTZ DEFAULT now(),
    last_reviewed_at TIMESTAMPTZ,
    -- CHOICE: the seven documented statuses are enforced (author gave them in
    -- prose without a constraint).
    CONSTRAINT restoration_queue_status_known CHECK (status IS NULL OR status IN (
        'pending_analysis','pending_rebase','pending_restoration','pending_review',
        'ready_for_merge','blocked','completed'))
);

CREATE INDEX IF NOT EXISTS idx_restoration_open
    ON restoration_queue (status, priority_score DESC) WHERE status <> 'completed';

COMMENT ON TABLE restoration_queue IS
    'Work queue for historical PRs. Entry is not a closure proposal — it is an evaluation assignment.';


-- ========== G5. REVIEW STALENESS RENAME ==========
-- Renamed so the column cannot be read as a closure signal. Rule 2 + the
-- review-outdated note.

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema = current_schema() AND table_name = 'review'
                 AND column_name = 'is_stale') THEN
        ALTER TABLE review RENAME COLUMN is_stale TO is_outdated_by_new_commits;
    END IF;
END $$;

COMMENT ON COLUMN review.is_outdated_by_new_commits IS
    'Additional review may be required. Never implies closure, supersession, or abandonment.';

-- DEPENDENTS THAT MUST BE UPDATED WITH THIS RENAME (delivered objects — the
-- revisions are provided below for the two the revision owns; the other two
-- are delivered bodies the author must rename at source):
--   1. pr_detect_events() trigger          -> corrected in G6
--   2. compute_review_decision()           -> corrected in G7
--   3. refresh_pr_rollups() rv CTE         -> `NOT r.is_stale` becomes
--                                             `NOT r.is_outdated_by_new_commits`
--   4. v_reviewer_status                   -> selects `r.is_stale`
-- Missing any of these leaves the schema broken at runtime, not at creation.


-- ========== G6. CORRECTED TRIGGER (writes the renamed column) ==========

CREATE OR REPLACE FUNCTION pr_detect_events() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.head_sha IS DISTINCT FROM OLD.head_sha AND OLD.head_sha IS NOT NULL THEN
        INSERT INTO pr_timeline_event (pr_number,event_type,occurred_at,from_sha,to_sha,derived)
          VALUES (NEW.pr_number,'head_changed',now(),OLD.head_sha,NEW.head_sha,TRUE)
          ON CONFLICT DO NOTHING;
        -- renamed column; semantic change is documentation-only
        UPDATE review SET is_outdated_by_new_commits = TRUE
          WHERE pr_number = NEW.pr_number
            AND commit_sha IS DISTINCT FROM NEW.head_sha;
    END IF;
    IF OLD.state = 'closed' AND NEW.state IN ('open','draft') THEN
        INSERT INTO pr_timeline_event (pr_number,event_type,occurred_at,derived)
          VALUES (NEW.pr_number,'reopened',now(),TRUE) ON CONFLICT DO NOTHING;
    END IF;
    IF OLD.is_draft AND NOT NEW.is_draft THEN
        INSERT INTO pr_timeline_event (pr_number,event_type,occurred_at,derived)
          VALUES (NEW.pr_number,'ready_for_review',now(),TRUE) ON CONFLICT DO NOTHING;
    END IF;
    IF OLD.base_ref IS DISTINCT FROM NEW.base_ref THEN
        INSERT INTO pr_timeline_event (pr_number,event_type,occurred_at,detail,derived)
          VALUES (NEW.pr_number,'base_changed',now(),
                  jsonb_build_object('from',OLD.base_ref,'to',NEW.base_ref),TRUE)
          ON CONFLICT DO NOTHING;
    END IF;
    RETURN NEW;
END $$;


-- ========== G7. RESTORATION & EFFECTIVE STATUS ==========

-- --- compute_restoration_status ------------------------------------------
-- Rule 4. Only a human decision may produce 'intentionally_abandoned', so this
-- function never returns it; it preserves an existing human-set value instead.
CREATE OR REPLACE FUNCTION compute_restoration_status(p INT)
RETURNS TEXT
LANGUAGE sql STABLE AS $$
    SELECT CASE
        WHEN pr.merged THEN 'merged'
        WHEN pr.state = 'open' OR pr.state = 'draft' THEN 'active'
        -- a human decision is sticky and outranks automated inference
        WHEN pr.restoration_status = 'intentionally_abandoned' THEN 'intentionally_abandoned'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l
                     WHERE l.ancestor_pr = p AND l.relation_type = 'restored_as') THEN 'restored_elsewhere'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l
                     WHERE l.ancestor_pr = p AND l.relation_type = 'split_into') THEN 'split_into_successors'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l
                     WHERE l.ancestor_pr = p AND l.relation_type IN ('superseded_by','replaced_by')
                       AND l.confidence >= 0.95) THEN 'superseded'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l
                     WHERE l.ancestor_pr = p AND l.relation_type IN ('continued_by','merged_via')) THEN 'pending_restoration'
        -- Rule 3 + long-lived rule: closed-unmerged is a restoration candidate,
        -- never an abandonment. This is the default that replaces `abandoned`.
        ELSE 'pending_analysis'
    END
    FROM pull_request pr WHERE pr.pr_number = p;
$$;

-- --- compute_effective_status --------------------------------------------
-- Rule 1/2: no branch of this function returns a closure state derived from
-- age or inactivity.
--
-- FIXED 2026-09-26: the closed branch previously read the PERSISTED
-- restoration_status with COALESCE(...,'pending_analysis'). That created a
-- hidden ordering dependency — evaluated before refresh_restoration_state()
-- had run, every closed PR silently degraded to 'historical_reference' even
-- when lineage proved it superseded. It now derives the outcome inline, so the
-- function is correct regardless of refresh order.
CREATE OR REPLACE FUNCTION compute_effective_status(p INT)
RETURNS TEXT
LANGUAGE sql STABLE AS $$
    SELECT CASE
        WHEN pr.merged THEN 'merged'
        WHEN pr.state = 'closed' THEN
            CASE compute_restoration_status(pr.pr_number)
                WHEN 'superseded'              THEN 'superseded'
                WHEN 'restored_elsewhere'      THEN 'restored_elsewhere'
                WHEN 'merged_via_successor'    THEN 'merged'
                WHEN 'intentionally_abandoned' THEN 'intentionally_abandoned'
                WHEN 'split_into_successors'   THEN 'historical_reference'
                ELSE 'historical_reference'
            END
        -- open / draft
        WHEN pr.has_conflicts THEN 'needs_rebase'
        WHEN pr.restoration_status = 'pending_restoration' THEN 'needs_restoration'
        WHEN pr.state = 'draft' THEN 'active'
        WHEN pr.approvals > 0 AND pr.changes_requested_count = 0 THEN 'ready_for_merge'
        ELSE 'active'
    END
    FROM pull_request pr WHERE pr.pr_number = p;
$$;

-- NOTE: effective_status deliberately carries NO CI state. The author's domain
-- (active, merged, ready_for_merge, needs_rebase, needs_restoration,
-- restored_elsewhere, superseded, historical_reference,
-- intentionally_abandoned) has no CI member, and widening an author-enumerated
-- domain silently is worse than omitting a branch: CI state is already carried
-- by ci_conclusion / ci_failing_checks on the same row. Flagged in
-- GOVERNANCE_NOTES §5 — if a CI state IS wanted, add it to the CHECK and
-- reinstate the branch here.


-- ========== G8. CORRECTED TRIAGE ENGINE ==========
-- Rule 2/9: this function can no longer emit any closure verb. close_stale,
-- close_duplicate and close_superseded do not exist in the new enum, so their
-- emission is impossible by construction — the safety is in the type, not in
-- the CASE ladder.
CREATE OR REPLACE FUNCTION suggest_action(p INT)
RETURNS core.triage_action
LANGUAGE sql STABLE AS $$
    SELECT CASE
        -- duplicate/lineage families: record ancestry, never close
        WHEN EXISTS (SELECT 1 FROM v_pr_fanout f WHERE p = ANY(f.prs) AND f.suggested_survivor <> p)
                                                                     THEN 'record_lineage'
        WHEN EXISTS (SELECT 1 FROM v_dep_supersession d WHERE p = ANY(d.close_these))
                                                                     THEN 'verify_supersession'
        WHEN EXISTS (SELECT 1 FROM v_tooling_artifacts t WHERE t.pr_number = p)
                                                                     THEN 'record_lineage'
        -- historical work: reconstruct, then analyse, then restore — never discard.
        -- FIXED 2026-09-26 (reachability): the previous order was
        --   no-lineage -> needs_historical_analysis; closed -> restore_historical_work;
        --   final_reviewed_state IS NULL -> reconstruct_final_state
        -- so the third branch could never fire (branch 2 caught every closed PR).
        -- reconstruct_final_state is an allowed L-7 verb and must be reachable, so
        -- reconstruction now comes FIRST for closed-unmerged work that has neither
        -- lineage nor a reconstructed reviewed state.
        WHEN pr.state = 'closed' AND NOT pr.merged
             AND NOT EXISTS (SELECT 1 FROM pr_lineage l WHERE l.ancestor_pr = p)
             AND pr.final_reviewed_state IS NULL                    THEN 'reconstruct_final_state'
        WHEN pr.state = 'closed' AND NOT pr.merged
             AND NOT EXISTS (SELECT 1 FROM pr_lineage l WHERE l.ancestor_pr = p)
                                                                     THEN 'needs_historical_analysis'
        -- ADDED 2026-09-26 (reachability invariant): 'merge_via_successor' is in
        -- the L-7 allowed set and in the enum, but no branch could emit it, so it
        -- was DECORATIVE. Fires when the ancestor's implementation demonstrably
        -- landed through a successor that itself merged.
        WHEN pr.state = 'closed' AND NOT pr.merged
             AND EXISTS (SELECT 1 FROM pr_lineage l
                         JOIN pull_request d ON d.pr_number = l.descendant_pr AND d.merged
                         WHERE l.ancestor_pr = p AND l.relation_type = 'merged_via')
                                                                     THEN 'merge_via_successor'
        WHEN pr.state = 'closed' AND NOT pr.merged                  THEN 'restore_historical_work'
        -- ordinary live-work handling, unchanged
        -- (an old-but-approved OPEN PR reaches merge_now below: age is not a signal)
        WHEN pr.has_conflicts                                        THEN 'resolve_conflicts'
        WHEN pr.ci_failing_checks > 0                                THEN 'needs_ci_fix'
        WHEN pr.actionable_comment_count > 0
          OR pr.changes_requested_count > 0                          THEN 'address_comments'
        WHEN EXISTS (SELECT 1 FROM merge_prerequisite m
                     JOIN pull_request q ON q.pr_number = m.prerequisite_pr
                     WHERE m.pr_number = p AND m.hard AND q.state = 'open') THEN 'wait_on_dependency'
        WHEN pr.changed_files > 40 OR pr.churn > 2000                THEN 'split_pr'
        WHEN pr.approvals = 0                                        THEN 'request_review'
        WHEN pr.mergeable_state = 'behind'                           THEN 'rebase_then_merge'
        ELSE 'merge_now'
    END
    FROM pull_request pr WHERE pr.pr_number = p;
$$;
-- NOTE (deliberate omission): the delivered ladder's `close_stale` branch keyed
-- off `updated_at < now() - 90 days`. It is gone, not merely unreachable,
-- because leaving the branch in place would let a future edit re-enable it.


-- ========== G9. CORRECTED VIEWS ==========

-- --- v_restoration_efficiency (replaces v_closure_efficiency) -------------
-- count() is not valid SQL; corrected to count(*). Author's version also closed
-- the FILTER clauses with a stray `) AS …` on line 1 of each — normalised here.
DROP VIEW IF EXISTS v_closure_efficiency;

CREATE OR REPLACE VIEW v_restoration_efficiency AS
SELECT date_trunc('month', COALESCE(merged_at, closed_at))                AS month,
       count(*) FILTER (WHERE restoration_status = 'merged')              AS merged,
       count(*) FILTER (WHERE restoration_status = 'restored_elsewhere')  AS restored_elsewhere,
       count(*) FILTER (WHERE restoration_status = 'superseded')          AS superseded,
       count(*) FILTER (WHERE restoration_status = 'pending_restoration') AS pending_restoration,
       count(*) FILTER (WHERE restoration_status = 'pending_analysis')    AS pending_analysis,
       sum(churn) FILTER (WHERE restoration_status IN ('merged','restored_elsewhere'))
                                                                          AS recovered_churn,
       sum(churn) FILTER (WHERE restoration_status = 'pending_analysis')  AS churn_awaiting_evaluation
FROM pull_request
GROUP BY 1;

COMMENT ON VIEW v_restoration_efficiency IS
    'Rule 10 reporting: recovered vs pending churn. Deliberately does not report "wasted" churn — unevaluated work is not waste.';

-- --- v_lineage_candidates (replaces the duplicate-closure query) ----------
-- Rule 5: results are lineage candidates, not duplicates.
CREATE OR REPLACE VIEW v_lineage_candidates AS
SELECT title_fingerprint,
       array_agg(pr_number ORDER BY pr_number) AS prs,
       count(*)                                AS candidate_count,
       -- suggested ordering target for human adjudication, not a closure set
       (array_agg(pr_number ORDER BY
              (state = 'merged') DESC,
              churn DESC NULLS LAST,
              updated_at DESC NULLS LAST))[1]  AS most_complete_candidate
FROM pull_request
GROUP BY title_fingerprint
HAVING count(*) > 1;

COMMENT ON VIEW v_lineage_candidates IS
    'Rule 5: lineage candidates. Does not imply duplication, closure, or abandonment.';

-- --- v_dependabot_superseded (replaces the auto-close query) --------------
CREATE OR REPLACE VIEW v_dependabot_superseded AS
SELECT p.pr_number,
       p.title,
       l.descendant_pr AS superseded_by_pr,
       l.confidence
FROM pull_request p
JOIN core.actor a ON a.actor_id = p.author_id AND a.kind = 'dependabot'
JOIN pr_lineage l ON l.ancestor_pr = p.pr_number
                 AND l.relation_type = 'superseded_by'
                 AND l.confidence >= 0.95;

COMMENT ON VIEW v_dependabot_superseded IS
    'Dependabot PRs VERIFIED as superseded by adjudicated lineage. Emits no closure recommendation.';

-- --- v_historical_evaluation (long-lived repository rule) -----------------
CREATE OR REPLACE VIEW v_historical_evaluation AS
SELECT p.pr_number, p.title, p.state, p.merged,
       (EXTRACT(EPOCH FROM (now() - p.created_at)) / 86400)::int AS age_days,
       p.restoration_status, p.effective_status, p.is_historical,
       p.final_reviewed_state,
       (SELECT count(*) FROM pr_comment c WHERE c.pr_number = p.pr_number)      AS comments,
       (SELECT count(*) FROM review r WHERE r.pr_number = p.pr_number)          AS reviews,
       (SELECT count(*) FROM pr_lineage l WHERE l.ancestor_pr = p.pr_number)    AS lineage_edges
FROM pull_request p
WHERE p.is_historical
   OR (p.state = 'closed' AND NOT p.merged);

COMMENT ON VIEW v_historical_evaluation IS
    'LONG-LIVED REPOSITORY RULE: age > 365d is historical work needing evaluation, NOT stale. This view is an evaluation queue; it never proposes closure.';

-- --- v_outdated_reviews (renamed semantics of the old stale-approval view) -
CREATE OR REPLACE VIEW v_outdated_reviews AS
SELECT r.pr_number, a.login AS reviewer, r.state, r.submitted_at,
       r.commit_sha, p.head_sha, r.is_outdated_by_new_commits
FROM review r
JOIN pull_request p USING (pr_number)
JOIN core.actor a ON a.actor_id = r.reviewer_id
WHERE p.state = 'open'
  AND r.is_outdated_by_new_commits;

COMMENT ON VIEW v_outdated_reviews IS
    'Additional review may be required. Never implies closure, supersession, or abandonment.';


-- ========== G10. RESTORATION STATE REFRESH ==========
-- The delivered design populated derived columns from refresh_pr_rollups(). The
-- governance columns need the same treatment: without a population step,
-- restoration_status / effective_status / is_historical stay NULL and every
-- downstream view reads empty. Idempotent, so it satisfies acceptance A7.

CREATE OR REPLACE FUNCTION refresh_restoration_state(p_only INT DEFAULT NULL)
RETURNS INT
LANGUAGE plpgsql AS $$
DECLARE n INT;
BEGIN
    -- 1. LONG-LIVED REPOSITORY RULE: age > 365 days marks historical work.
    --    Informational only — it never changes restoration_status on its own.
    --    NOTE: cannot be a generated column; `now()` is not immutable (B2).
    UPDATE pull_request p
       SET is_historical = (
             p.created_at IS NOT NULL
             AND (EXTRACT(EPOCH FROM (now() - p.created_at)) / 86400) > 365)
     WHERE (p_only IS NULL OR p.pr_number = p_only)
       AND p.is_historical IS DISTINCT FROM (
             p.created_at IS NOT NULL
             AND (EXTRACT(EPOCH FROM (now() - p.created_at)) / 86400) > 365);

    -- 2. restoration_status. A human-set 'intentionally_abandoned' is preserved;
    --    compute_restoration_status() already returns it unchanged.
    UPDATE pull_request p
       SET restoration_status = compute_restoration_status(p.pr_number)
     WHERE (p_only IS NULL OR p.pr_number = p_only)
       AND p.restoration_status IS DISTINCT FROM compute_restoration_status(p.pr_number);

    -- 3. effective_status.
    UPDATE pull_request p
       SET effective_status = compute_effective_status(p.pr_number)
     WHERE (p_only IS NULL OR p.pr_number = p_only)
       AND p.effective_status IS DISTINCT FROM compute_effective_status(p.pr_number);

    -- 3b. historical_outcome (Rule 6 + Phase 5's 7-value model). ADDED
    -- 2026-09-26: the column existed but nothing populated it, so every
    -- downstream metric (v_historical_resolution_rate, v_recovered_churn,
    -- v_pending_analysis_count) read empty. Populated only for resolved
    -- historical work; open PRs keep NULL because they are not yet history.
    UPDATE pull_request p
       SET historical_outcome = CASE
             WHEN p.merged THEN 'merged'
             WHEN p.state <> 'closed' THEN NULL
             WHEN p.restoration_status = 'superseded'              THEN 'superseded'
             WHEN p.restoration_status = 'restored_elsewhere'      THEN 'restored_elsewhere'
             WHEN p.restoration_status = 'merged_via_successor'    THEN 'merged_via_successor'
             WHEN p.restoration_status = 'split_into_successors'   THEN 'split_into_successors'
             WHEN p.restoration_status = 'intentionally_abandoned' THEN 'intentionally_abandoned'
             -- Rule 4: unclassified historical work is pending analysis, never
             -- abandoned, and never left NULL for a closed-unmerged PR.
             ELSE 'pending_analysis'
           END
     WHERE (p_only IS NULL OR p.pr_number = p_only)
       AND p.historical_outcome IS DISTINCT FROM (
             CASE
               WHEN p.merged THEN 'merged'
               WHEN p.state <> 'closed' THEN NULL
               WHEN p.restoration_status = 'superseded'              THEN 'superseded'
               WHEN p.restoration_status = 'restored_elsewhere'      THEN 'restored_elsewhere'
               WHEN p.restoration_status = 'merged_via_successor'    THEN 'merged_via_successor'
               WHEN p.restoration_status = 'split_into_successors'   THEN 'split_into_successors'
               WHEN p.restoration_status = 'intentionally_abandoned' THEN 'intentionally_abandoned'
               ELSE 'pending_analysis'
             END);

    -- 4. Enqueue close-unmerged work for evaluation. Rule 3: these remain
    --    restoration candidates. Enqueue is not a closure proposal.
    INSERT INTO restoration_queue (pr_number, status, restore_reason, priority_score)
    SELECT p.pr_number,
           'pending_analysis',
           CASE WHEN p.is_historical
                THEN 'long-lived repository rule: historical work awaiting evaluation'
                ELSE 'closed unmerged: restoration candidate' END,
           -- CHOICE: priority rewards recoverable work (churn) and penalises
           -- evaluation cost (lineage already present lowers it further).
           COALESCE(p.churn, 0) / 1000.0
             - COALESCE((SELECT count(*) FROM pr_lineage l
                         WHERE l.ancestor_pr = p.pr_number), 0) * 5
    FROM pull_request p
    WHERE p.state = 'closed' AND NOT p.merged
      AND (p_only IS NULL OR p.pr_number = p_only)
    ON CONFLICT (pr_number) DO NOTHING;

    GET DIAGNOSTICS n = ROW_COUNT;
    RETURN n;
END $$;

COMMENT ON FUNCTION refresh_restoration_state(INT) IS
    'Populates is_historical, restoration_status, effective_status and enqueues restoration candidates. Idempotent. Run after each ingest batch, alongside refresh_pr_rollups().';

-- CHOICE: effective_status has no CI member in the author's domain, so a
-- CI-failing open PR still reads 'active' here while ci_failing_checks carries
-- the signal. See GOVERNANCE_NOTES §5 Q3.
CREATE INDEX IF NOT EXISTS idx_pr_effective_status
    ON pull_request (effective_status) WHERE state IN ('open','draft');


-- ============================================================================
-- PART 2 of the governance revision — HISTORICAL INTENT PRESERVATION MODEL
-- (author, 2026-09-26, second revision). Governs the schema AND the analysis
-- pipeline: no deterministic step, heuristic, LLM judgment, triage action,
-- report, scorecard or recommendation may treat old/inactive/closed/stale-CI
-- work as abandoned.
-- ============================================================================

-- ========== G11. GLOBAL RULE + CLASSIFICATION DOMAIN RECONCILIATION ==========

-- FIXED 2026-09-26: `COMMENT ON DATABASE CURRENT_DATABASE() IS …` is invalid —
-- COMMENT takes a literal object name, not an expression (caught by pglast, not
-- by review). Applied dynamically instead.
DO $$
BEGIN
    EXECUTE format(
        'COMMENT ON DATABASE %I IS %L',
        current_database(),
        $doc$HISTORICAL PRESERVATION RULE (global — governs schema and analysis pipeline)

No deterministic process, heuristic, LLM judgment, triage action, report,
scorecard, or recommendation may classify a PR as abandoned solely because:
  - it is old
  - it has no recent activity
  - it is closed
  - it has stale reviews
  - CI has not run recently
  - a newer PR exists

A PR may only be classified intentionally_abandoned after lineage analysis has
failed to establish restoration potential, successor implementation,
reimplementation elsewhere, or merge viability, AND a human or explicitly
auditable decision records the abandonment.

OBJECTIVE (not closure): reconstruct final reviewed state, preserve
implementation history, recover useful work, determine lineage, determine
mergeability, identify successor PRs, restore abandoned functionality.
Reduction of open PR count is never an objective.$doc$);
END $$;

-- RECONCILIATION (flagged): two overlapping valuesets appeared across the
-- author's revisions. The later, canonical one (Rule 6 + A3 Historical Outcome
-- Classification) is used here:
--   superseded, restored_elsewhere, merged_via_successor,
--   split_into_successors, pending_analysis, intentionally_abandoned
-- The earlier revision's 'historical_unclassified' is DEPRECATED in favour of
-- 'pending_analysis' — same concept, and Rule 6 names it pending_analysis.
--
-- CHOICE: kept as a separate field from restoration_status (workflow state vs
-- analysis outcome) — a PR can be workflow 'pending_restoration' while its
-- outcome is still 'pending_analysis'. Flagged in HISTORICAL_PRESERVATION §6 Q1:
-- the two domains now overlap heavily and could be collapsed if the author
-- prefers a single field.
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS historical_outcome TEXT;
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS historical_outcome_reason TEXT;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pr_historical_outcome_known') THEN
        -- CLARIFIED 2026-09-26 by the 9-phase implementation plan, Phase 5
        -- ("Historical Outcome Model — allowed outcomes"): SEVEN values, i.e. the
        -- Rule 6 list plus 'merged'. That resolves an inconsistency this file had
        -- carried: compute_restoration_status() already returns 'merged' for
        -- directly-merged PRs, which the previous 6-value CHECK would have
        -- REJECTED on write. Direct merges are outcomes too.
        ALTER TABLE pull_request ADD CONSTRAINT pr_historical_outcome_known CHECK (
            historical_outcome IS NULL OR historical_outcome IN (
                'merged','superseded','restored_elsewhere','merged_via_successor',
                'split_into_successors','pending_analysis','intentionally_abandoned'));
    END IF;
    -- widen restoration_status to carry merged_via_successor
    ALTER TABLE pull_request DROP CONSTRAINT IF EXISTS pr_restoration_status_known;
    ALTER TABLE pull_request ADD CONSTRAINT pr_restoration_status_known CHECK (
        restoration_status IS NULL OR restoration_status IN (
            'active','merged','superseded','restored_elsewhere','merged_via_successor',
            'split_into_successors','pending_restoration','pending_analysis',
            'intentionally_abandoned'));
END $$;

CREATE INDEX IF NOT EXISTS idx_pr_historical_outcome
    ON pull_request (historical_outcome) WHERE state = 'closed' AND merged = FALSE;

COMMENT ON COLUMN pull_request.historical_outcome IS
    'Rule 6 analysis outcome for historical work. Defaults to pending_analysis; only an auditable human decision may set intentionally_abandoned.';

-- Refinement to compute_restoration_status under the new model: lineage of
-- 'merged_via' now resolves the ancestor's work (its implementation landed via
-- a successor), whereas 'continued_by' merely continues it.
CREATE OR REPLACE FUNCTION compute_restoration_status(p INT)
RETURNS TEXT
LANGUAGE sql STABLE AS $$
    SELECT CASE
        WHEN pr.merged THEN 'merged'
        WHEN pr.state IN ('open','draft') THEN 'active'
        WHEN pr.restoration_status = 'intentionally_abandoned' THEN 'intentionally_abandoned'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l
                     WHERE l.ancestor_pr = p AND l.relation_type = 'restored_as') THEN 'restored_elsewhere'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l
                     WHERE l.ancestor_pr = p AND l.relation_type = 'split_into') THEN 'split_into_successors'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l
                     WHERE l.ancestor_pr = p AND l.relation_type IN ('superseded_by','replaced_by')
                       AND l.confidence >= 0.95) THEN 'superseded'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l
                     WHERE l.ancestor_pr = p AND l.relation_type = 'merged_via') THEN 'merged_via_successor'
        WHEN EXISTS (SELECT 1 FROM pr_lineage l
                     WHERE l.ancestor_pr = p AND l.relation_type = 'continued_by') THEN 'pending_restoration'
        ELSE 'pending_analysis'
    END
    FROM pull_request pr WHERE pr.pr_number = p;
$$;


-- ========== G12. HISTORICAL VALIDATION LEDGER ==========

CREATE TABLE IF NOT EXISTS historical_validation (
    validation_id   BIGSERIAL PRIMARY KEY,
    pr_number       INTEGER NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    validation_type TEXT    NOT NULL,
    passed          BOOLEAN,
    details         JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- CHOICE: author listed five example types in prose; enforced so the ledger
    -- stays queryable rather than accumulating free-text labels.
    CONSTRAINT historical_validation_type_known CHECK (validation_type IN (
        'lineage_exists','successor_exists','final_intent_recovered',
        'implementation_verified','restoration_completed'))
);
CREATE INDEX IF NOT EXISTS idx_hist_validation_pr
    ON historical_validation (pr_number, validation_type, created_at DESC);

COMMENT ON TABLE historical_validation IS
    'Mandatory deterministic checks backing a restoration/abandonment claim. An intentional_abandoned classification is only auditable when the lineage_exists / successor_exists checks are recorded here as failed.';


-- ========== G13. LLM JUDGMENT ADDITIONS ==========
-- Allows judgments to be REPLAYED against an evolving lineage graph: a stored
-- verdict is only valid for the lineage_version it was formed against.
ALTER TABLE core.llm_judgment ADD COLUMN IF NOT EXISTS lineage_version     TEXT;
ALTER TABLE core.llm_judgment ADD COLUMN IF NOT EXISTS restoration_context JSONB;
ALTER TABLE core.llm_judgment ADD COLUMN IF NOT EXISTS historical_candidate BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_judgment_historical
    ON core.llm_judgment (task_code, historical_candidate) WHERE historical_candidate;

COMMENT ON COLUMN core.llm_judgment.lineage_version IS
    'Lineage graph revision the judgment was formed against. A lineage change invalidates dependent judgments — re-run rather than reusing.';
COMMENT ON COLUMN core.llm_judgment.restoration_context IS
    'Snapshot of lineage/successor evidence shown to the model, for auditability.';


-- ========== G14. DETERMINISTIC HISTORICAL METRICS ==========
-- Replaces merge rate. A closed-unmerged PR whose work was preserved elsewhere
-- is a SUCCESS, not a failure; merge rate cannot express that.

CREATE OR REPLACE VIEW v_historical_resolution AS
SELECT count(*) FILTER (WHERE state = 'closed' AND merged = FALSE)               AS historical_prs,
       count(*) FILTER (WHERE restoration_status = 'merged')
     + count(*) FILTER (WHERE restoration_status = 'superseded')
     + count(*) FILTER (WHERE restoration_status = 'restored_elsewhere')
     + count(*) FILTER (WHERE restoration_status = 'merged_via_successor')
     + count(*) FILTER (WHERE restoration_status = 'split_into_successors')       AS resolved,
       count(*) FILTER (WHERE historical_outcome = 'pending_analysis')      AS unclassified,
       count(*) FILTER (WHERE restoration_status = 'intentionally_abandoned')      AS human_abandoned
FROM pull_request;

CREATE OR REPLACE VIEW v_historical_resolution_rate AS
SELECT historical_prs, resolved, unclassified, human_abandoned,
       round(100.0 * resolved / NULLIF(resolved + unclassified, 0), 1) AS historical_resolution_rate_pct
FROM v_historical_resolution;
-- NOTE: the denominator is resolved + unclassified, i.e. the rate measures
-- RESOLUTION PROGRESS over historical work, not a success ratio. Stated
-- explicitly because the author's formula lists the resolved states in the
-- denominator, which reads as a mixed numerator/denominator.

-- lineage_coverage_pct — how much historical work has ANY adjudicated ancestry
CREATE OR REPLACE VIEW v_lineage_coverage AS
SELECT count(*) FILTER (WHERE p.state = 'closed' AND NOT p.merged) AS historical_prs,
       count(*) FILTER (WHERE p.state = 'closed' AND NOT p.merged
                          AND EXISTS (SELECT 1 FROM pr_lineage l
                                      WHERE l.ancestor_pr = p.pr_number)) AS with_lineage,
       round(100.0 * count(*) FILTER (WHERE p.state = 'closed' AND NOT p.merged
                          AND EXISTS (SELECT 1 FROM pr_lineage l
                                      WHERE l.ancestor_pr = p.pr_number))
             / NULLIF(count(*) FILTER (WHERE p.state = 'closed' AND NOT p.merged), 0), 1)
           AS lineage_coverage_pct
FROM pull_request p;

-- successor_link_rate — resolved-with-successor share of resolved work
CREATE OR REPLACE VIEW v_successor_link_rate AS
SELECT count(*) FILTER (WHERE restoration_status IN
             ('superseded','restored_elsewhere','merged_via_successor','split_into_successors')) AS resolved,
       count(*) FILTER (WHERE restoration_status IN
             ('merged_via_successor','restored_elsewhere','split_into_successors'))            AS via_successor,
       round(100.0 * count(*) FILTER (WHERE restoration_status IN
             ('merged_via_successor','restored_elsewhere','split_into_successors'))
             / NULLIF(count(*) FILTER (WHERE restoration_status IN
             ('superseded','restored_elsewhere','merged_via_successor','split_into_successors')), 0), 1)
           AS successor_link_rate_pct
FROM pull_request;

-- recovered_churn / unrecovered_churn — the replacement for "wasted churn"
CREATE OR REPLACE VIEW v_recovered_churn AS
SELECT sum(churn) FILTER (WHERE restoration_status IN
             ('merged','restored_elsewhere','merged_via_successor','split_into_successors')) AS recovered_churn,
       sum(churn) FILTER (WHERE historical_outcome = 'pending_analysis')              AS churn_awaiting_evaluation,
       sum(churn) FILTER (WHERE restoration_status = 'intentionally_abandoned')              AS human_abandoned_churn
FROM pull_request;
-- CHOICE: no "wasted_churn" column. Unevaluated work is not waste, and naming a
-- column that way would reintroduce the concept the governance model removes.

CREATE OR REPLACE VIEW v_pending_analysis_count AS
SELECT count(*) AS pending_analysis_prs,
       min(created_at) AS oldest
FROM pull_request
WHERE state = 'closed' AND NOT merged
  AND COALESCE(historical_outcome, 'pending_analysis') = 'pending_analysis';


-- ========== G15. DEPENDABOT SUPERSESSION — STRICTER CRITERIA ==========
-- The delivered rule ("same package, newer PR exists") was too aggressive.
-- Tightened twice: first to same-or-newer target version (2026-09-26 revision),
-- then to require SAME SCOPE and SAME MANIFEST (author decision, this revision),
-- using core.dependency_change as the evidence source. Supersession is proven
-- deterministically here; the LLM is only involved in adjudicating ambiguity.
CREATE OR REPLACE VIEW v_dependabot_supersession_candidates AS
WITH bumps AS (
    -- one row per (PR, dependency) with the manifest and scope it touched
    SELECT p.pr_number, p.created_at, p.state, p.merged,
           dc.package_name, dc.dependency_scope, dc.manifest_path,
           dc.old_version, dc.new_version
    FROM pull_request p
    JOIN core.actor a ON a.actor_id = p.author_id AND a.kind = 'dependabot'
    JOIN dependency_change dc ON dc.pr_number = p.pr_number
)
SELECT b.pr_number, b.package_name, b.dependency_scope, b.manifest_path,
       b.new_version AS target_version,
       newer.pr_number AS newer_pr, newer.new_version AS newer_target_version
FROM bumps b
JOIN bumps newer
  ON newer.package_name       = b.package_name        -- same package
 AND newer.dependency_scope   = b.dependency_scope     -- same scope (deps vs devDeps)
 AND newer.manifest_path      = b.manifest_path        -- same manifest
 AND newer.pr_number          <> b.pr_number
 AND newer.created_at         > b.created_at
 AND string_to_array(newer.new_version, '.') >= string_to_array(b.new_version, '.')
WHERE b.state = 'open' AND NOT b.merged
  AND b.new_version IS NOT NULL;

COMMENT ON VIEW v_dependabot_supersession_candidates IS
    'Deterministic CANDIDATE stage: same package AND same scope AND same manifest AND same-or-newer target version. NOT a closure set — candidates must be promoted to verified_superseded via confirmed lineage.';

CREATE OR REPLACE VIEW v_dependabot_verified_superseded AS
SELECT c.pr_number, c.package, c.target_version, c.newer_pr,
       l.confidence, l.evidence
FROM v_dependabot_supersession_candidates c
JOIN pr_lineage l ON l.ancestor_pr = c.pr_number
                 AND l.descendant_pr = c.newer_pr
                 AND l.relation_type = 'superseded_by'
                 AND l.confidence >= 0.95;

COMMENT ON VIEW v_dependabot_verified_superseded IS
    'verified_superseded: candidate + confirmed lineage. Still no closure recommendation — the action is verify_supersession/record_lineage.';

-- GAP FLAGGED: the author's stricter rule also requires "same dependency scope"
-- (dependencies vs devDependencies/peer/optional). Scope is not present in any
-- delivered table or derivable from title/package alone — it needs a new
-- column populated from the manifest diff. See G16.1.


-- ============================================================================
-- G16. AUTHOR DECISIONS APPLIED (2026-09-26, third response)
--      L-14 task code · dependency scope defect · Rule 9 · enum consistency
-- ============================================================================

-- ========== G16.1 CORE.DEPENDENCY_CHANGE (closes the scope defect) ==========
-- Author-supplied design. Manifest-scoped dependency evidence, so supersession
-- can be proven deterministically instead of inferred from PR titles.
CREATE TABLE IF NOT EXISTS core.dependency_change (
    pr_number        INTEGER NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    ecosystem        TEXT    NOT NULL,        -- npm | pypi | cargo | go | …
    package_name     TEXT    NOT NULL,
    old_version      TEXT,
    new_version      TEXT,
    dependency_scope TEXT    NOT NULL,        -- dependencies | devDependencies | …
    manifest_path    TEXT    NOT NULL,        -- package.json | requirements.txt | uv.lock | …
    detected_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- NOTE: the author's PRIMARY KEY includes manifest_path, which implicitly
    -- makes it NOT NULL. Stated explicitly above so the constraint is visible
    -- rather than accidental. If a manifest path can ever be unknown, drop
    -- manifest_path from the PK and add a unique index with NULLS NOT DISTINCT.
    PRIMARY KEY (pr_number, ecosystem, package_name, dependency_scope, manifest_path),
    CONSTRAINT dependency_scope_known CHECK (dependency_scope IN (
        'dependencies','devDependencies','peerDependencies','optionalDependencies',
        'bundledDependencies','build','system','runtime','dev','test'))
);
CREATE INDEX IF NOT EXISTS idx_dep_change_supersession
    ON core.dependency_change (package_name, dependency_scope, manifest_path);

COMMENT ON TABLE core.dependency_change IS
    'Manifest-scoped dependency bumps. Same package in a different scope (dependencies vs devDependencies) is NOT an equivalent change — this table is what makes that distinction provable.';

-- ========== G16.2 TASK-CODE IMMUTABILITY + L-14 (author decision) ==========
COMMENT ON COLUMN core.llm_judgment.task_code IS
$doc$Task codes are IMMUTABLE. Once a task code has been used in production its
meaning may never change. New semantic tasks receive new codes.

  L-11 = Linear Linking            (existing deployed meaning — unchanged)
  L-12 = Jules session detection   (existing deployed meaning — unchanged)
  L-13 = cross-source reconciliation (existing deployed meaning — unchanged)
  L-14 = Historical Intent Reconstruction  (NEW — see HISTORICAL_PRESERVATION.md)

Rationale: changing a code retroactively changes the meaning of historical
judgments already stored, violating auditability. model / prompt_version /
input_hash / task_code exist precisely so historical records stay interpretable.
If L-14 ever replaces L-11's function, that is a new task with a new code and a
new prompt_version — never a renumbering exercise.$doc$;

-- ========== G16.3 RULE 9 — THREE-LEVEL VALIDATION ==========
COMMENT ON SCHEMA ingest IS
$doc$RULE 9 — GOVERNANCE VALIDATION AT THREE LEVELS

  1. Parse correctness      — the SQL is well-formed.
  2. Type correctness       — values fall inside declared domains.
  3. Behavioural correctness — the object does what governance intends.

Passing SQL parsing and schema validation does NOT imply governance compliance.
Two defects in this design proved that: mv_merge_order could never flag a cycle,
and suggest_action() returned a value absent from its own return type. Both were
parse-clean and type-plausible until executed.

REQUIRED INVARIANTS
  * Every triage action must have at least one positive test, at least one
    negative test, and explicit reachability coverage — otherwise actions
    silently become decorative.
  * For governance-sensitive status fields (effective_status, restoration_status,
    historical_outcome), DERIVED TRUTH DOMINATES CACHED TRUTH. The authoritative
    source is the lineage graph plus current state; persisted classifications are
    PROJECTIONS and must be recomputable from truth alone.$doc$;

COMMENT ON COLUMN pull_request.restoration_status IS
    'PROJECTION of compute_restoration_status() — the lineage graph is authoritative. Never read this as ground truth in a governance decision.';
COMMENT ON COLUMN pull_request.effective_status IS
    'PROJECTION of compute_effective_status() — derived from lineage + current state. Recomputable; never authoritative.';
COMMENT ON COLUMN pull_request.historical_outcome IS
    'PROJECTION of the Rule 6 outcome model (7 values incl. merged). Lineage is authoritative; only intentionally_abandoned may be human-set and is then sticky.';

-- ========== G16.4 ENUM/RETURN CONSISTENCY ENFORCEMENT ==========
-- The author proposed `CREATE ASSERTION`. That will not run: CREATE ASSERTION is
-- standard SQL, but PostgreSQL has NEVER implemented it (no such statement in
-- the grammar). Two mechanisms that DO work are provided instead.

-- (a) STRONG MECHANISM — a catalog table whose column IS the enum type, so an
--     illegal action cannot be inserted at all. Type correctness by construction.
CREATE TABLE IF NOT EXISTS core.triage_action_catalog (
    action      core.triage_action PRIMARY KEY,   -- illegal values are unrepresentable
    is_allowed_llm BOOLEAN NOT NULL DEFAULT FALSE,
    is_deterministic BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT
);

COMMENT ON TABLE core.triage_action_catalog IS
    'Enum-typed catalog: an action outside core.triage_action cannot be inserted, which is stronger than a checked assertion. Keep in sync with the L-7 allowed/prohibited lists.';

-- (b) CI/DIAGNOSTIC MECHANISM — extract every string literal returned by
--     functions whose declared return type is an enum, and report any literal
--     that is not a member. This is the check that would have caught the
--     delivered close_artifact defect. Run it in CI; expect zero invalid rows.
CREATE OR REPLACE FUNCTION core.validate_enum_returns(
    p_enum regtype DEFAULT 'core.triage_action'::regtype
) RETURNS TABLE (function_name TEXT, literal TEXT, is_valid BOOLEAN)
LANGUAGE sql STABLE AS $$
    SELECT p.proname::text,
           m.literal,
           EXISTS (SELECT 1 FROM pg_enum e
                   WHERE e.enumtypid = p_enum AND e.enumlabel = m.literal)
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    CROSS JOIN LATERAL regexp_matches(pg_get_functiondef(p.oid),
                                      '''([a-z][a-z_]{2,40})''', 'g') AS m(literal)
    WHERE p.prorettype = p_enum
      AND n.nspname NOT IN ('pg_catalog','information_schema');
$$;

COMMENT ON FUNCTION core.validate_enum_returns(regtype) IS
    'CI check: every literal returned by an enum-returning function must be a member of that enum. Expect zero rows with is_valid = false. NOTE: regex-based over function source, so it can over-report literals used in comparisons; treat is_valid=false rows as requiring review, and prefer the enum-typed core.triage_action_catalog for write-path safety.';
