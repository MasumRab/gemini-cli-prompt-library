# Forensics Workflow & Workspace Integration

**Status:** Design specification
**Created:** 2026-08-29
**Supersedes:** Ad-hoc forensics in `docs/forensics/`

---

## 1. Problem Statement

Forensics data is currently stored in two places:
1. `docs/forensics/` — Jules tooling (migrated data, schemas, scripts)
2. `workspaces/<repo>/analysis/forensics/` — Target repo workspace (analysis docs)

This creates ambiguity about:
- Where new forensics data should be written
- How forensics scripts should be invoked
- What belongs to Jules tooling vs target repo analysis

---

## 2. Design Principles

| Principle | Implication |
|-----------|-------------|
| **Tooling in tools/** | Forensics scripts belong in `tools/` or `scripts/`, not `docs/` |
| **Analysis in workspace** | Generated forensics reports belong in `workspaces/<repo>/analysis/forensics/` |
| **Schema-validated** | All forensics data should be validated against `forensics_data_schema.json` |
| **Repo-scoped** | Forensics queries must filter by repo (like all Jules operations) |
| **Migration path** | Legacy `docs/forensics/` data will eventually move to `workspaces/jules/` |

---

## 3. Architecture

```
jules repo (tooling)
├── tools/
│   └── forensics/
│       ├── generate_report.py      # Main forensics report generator
│       ├── validate_schema.py      # Schema validation
│       └── forensics_data_schema.json
├── scripts/
│   └── forensics/                 # Bash wrappers
└── docs/
    └── forensics/
        └── WORKSPACE_INTEGRATION.md  # This document

workspaces/<repo>/
└── analysis/
    └── forensics/                 # Generated reports live here
        ├── INDEX.yaml            # Manifest of all forensics for this repo
        ├── FORENSICS_SUMMARY.yaml
        └── <report>_<date>.md    # Individual reports with YAML frontmatter
```

---

## 4. Forensics Report Format

Every forensics report in a workspace MUST have YAML frontmatter:

```yaml
---
session:
  id: "<jules_session_id>"
  title: "<report title>"
  repository: "<repo-name>"
  created: "<ISO 8601>"
  updated: "<ISO 8601>"
  status: completed
  source: "forensics"
  
forensics:
  type: "<failure_analysis|intervention_outcome|pattern_analysis|audit>"
  confidence: "<exact|strong|probable|unresolved>"
  api_boundary: "<API endpoint used>"
  retrieval_timestamp: "<ISO 8601>"
---
```

---

## 5. Workflow Integration

### 5.1 Generate Forensics Report

```bash
# For a specific repo
python3 tools/forensics/generate_report.py \
  --repo EmailIntelligence \
  --type failure_analysis \
  --session-id 596003508416904399 \
  --output workspaces/EmailIntelligence/analysis/forensics/
```

### 5.2 Validate Forensics JSON

```bash
# Validate all forensics JSON data files in tools/forensics/
python3 tools/forensics/validate_schema.py
```

Note: `validate_schema.py` validates the JSON data files (sessions, pull_requests,
interventions) against `forensics_data_schema.json`. It does **not** accept a
`--workspace` argument and does not validate Markdown report frontmatter.

### 5.3 List Available Reports

```bash
# Show forensics available for a repo
cat workspaces/EmailIntelligence/analysis/forensics/INDEX.yaml
```

---

## 6. Naming Conventions

| File type | Pattern | Example |
|-----------|---------|---------|
| Individual report | `<type>_<YYYY-MM-DD>.md` | `failure_analysis_2026-08-06.md` |
| Manifest | `INDEX.yaml` | Per-workspace index |
| Summary | `FORENSICS_SUMMARY.yaml` | Aggregated summary |
| Schema | `forensics_data_schema.json` | Tooling in `tools/` |

---

## 7. Transition Plan

| Phase | Action | Status |
|-------|--------|--------|
| 1 | Move analysis docs to `workspaces/<repo>/analysis/forensics/` | ✅ Done |
| 2 | Add YAML frontmatter to all reports | ✅ Done |
| 3 | Move scripts to `tools/forensics/` | Pending |
| 4 | Update `tools/forensics/generate_report.py` | Pending |
| 5 | Deprecate `docs/forensics/*.md` (keep JSON data) | Pending |
| 6 | Move JSON data to `workspaces/jules/` | Future |

---

## 8. Open Questions

1. Should forensics scripts live in `tools/` or `scripts/`?
2. Should we keep a centralized `docs/forensics/` for cross-repo analysis?
3. How should real-time forensics (session monitoring) differ from post-hoc analysis?
4. Should forensics be generated automatically on session completion?

---

## 9. Related Documents

- `docs/runbooks/workspace_isolation.md` — Workspace layout rules
- `docs/guides/session_summary_standard.md` — Report format standard
- `docs/guides/workflow_session_traceability.md` — Cross-system correlation
- `tools/forensics/forensics_data_schema.json` — Schema definition
