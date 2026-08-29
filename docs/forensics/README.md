# Forensics Directory — Legacy Jules-Tooling Copies

**Status:** The authoritative forensics reports now live in `workspaces/EmailIntelligence/analysis/forensics/` (YAML-frontmatter versions). The copies below are the legacy Jules-tooling originals and are slated for deprecation (see `WORKSPACE_INTEGRATION.md`, Phase 5).

## Migration Summary (2026-08-29)

The forensics reports were **copied** to the EmailIntelligence workspace and updated
with YAML frontmatter following the session summary standard. These original copies
remain here as legacy until deprecated; they are not the canonical location.

### New Location

```
workspaces/EmailIntelligence/analysis/forensics/
├── INDEX.yaml                    # Master index
├── FORENSICS_SUMMARY.yaml        # Summary manifest
├── FAILURE_ROOT_CAUSE_ANALYSIS_2026-08-06.md
├── HIGH_LINECOUNT_PR_ALIGNMENT_AUDIT_2026-08-14.md
├── INTERVENTION_E2E_OUTCOME_ANALYSIS_2026-08-07.md
├── PR_CONVERSATION_EVOLUTION_2026-08-06.md
├── SESSION_FOLLOWUP_TRACKER_2026-08-06.md
├── SESSION_INVESTIGATION_2026-08-06.md
├── SESSION_PRIORITY_BATCH_PLAN_2026-08-14.md
└── SESSION_REUSE_EVIDENCE_2026-08-06.md
```

### Why This Change

Per `docs/runbooks/workspace_isolation.md`:
- This jules repo is for Jules tooling only
- Target repo work belongs in `workspaces/<repo-name>/`
- EmailIntelligence forensics are now in the EmailIntelligence workspace

### Data Files

The JSON data files (`migrated_forensics_data.json`, etc.) remain here as they are
generic tooling and not specific to EmailIntelligence. They may be moved to a
`workspaces/jules/` directory in a future cleanup.

### Session Context

| Session ID | Repository | Status |
|-----------|------------|--------|
| 596003508416904399 | EmailIntelligence | COMPLETED |
