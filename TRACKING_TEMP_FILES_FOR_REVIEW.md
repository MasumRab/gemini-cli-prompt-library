# TEMPORARY FILES TRACKING - FOR LATER REVIEW

## Purpose
This document tracks files that were committed to support the current autoresearch/task but may not belong permanently in the Jules repository. These files should be reviewed periodically to determine if they should be:
1. Retained permanently (if they provide ongoing value)
2. Moved to a more appropriate location
3. Archived or removed (if temporary)

## Files Under Review

### 1. WATCHDOG.yml
- **Location**: Root of repository
- **Purpose**: Advisor configuration for automated processes
- **Review Question**: Is this a standard Jules configuration file or task-specific?
- **Suggested Review**: Check if similar configs exist elsewhere in repo
- **Retention Criteria**: Keep if it's a standard Jules configuration pattern

### 2. scratch_branch_alignment_scaffold/ Directory
- **Location**: Root of repository
- **Contents**: 
  - DESIGN.md
  - REQUIREMENTS.md
  - TASKS.md
  - CROSSWALK_EXISTING_TASKS.md
  - PHASE_2_INVESTIGATION_PLAN.md
  - CLUSTERING_PROCESS.md
  - PRD_BRANCH_ALIGNMENT.md
  - WORKTREE_CONFIG.md
  - README_SCAFFOLD.md
- **Purpose**: Branch alignment investigation files from a temporary scaffold
- **Review Question**: Are these investigation artifacts that should be retained as documentation?
- **Suggested Review**: Evaluate if content duplicates existing docs or provides unique value
- **Retention Criteria**: Keep only if contains unique, valuable information not found elsewhere

### 3. session_tracking/2026/07/596003508416904399_status_report_recovered.md
- **Location**: session_tracking/2026/07/
- **Purpose**: Evidence-based status report from Jules session 596003508416904399
- **Review Question**: Is this a standard session tracking artifact or task-specific?
- **Suggested Review**: Compare with other session tracking files in same directory
- **Retention Criteria**: Keep if it follows standard Jules session reporting patterns

## Review Schedule
- **Initial Review**: 1 week from commit (2026-09-02)
- **Follow-up Review**: 2 weeks from commit (2026-09-09)  
- **Final Decision**: 1 month from commit (2026-09-26)

## Decision Criteria
When reviewing each file/directory, consider:
1. **Uniqueness**: Does this contain information not available elsewhere in the repo?
2. **Standardization**: Does it follow established Jules patterns and conventions?
3. **Ongoing Value**: Will this be useful for future Jules operations beyond the current task?
4. **Location**: Is this in the appropriate directory for its type/content?
5. **Size/Complexity**: Is the maintenance overhead justified by the value?

## Action Options for Each Item
- **RETAIN**: Keep file in current location if it provides ongoing value
- **RELOCATE**: Move to more appropriate directory (docs/, tools/, etc.)
- **ARCHIVE**: Move to archive/ or historical/ directory
- **REMOVE**: Delete if temporary/no longer needed
- **SUMMARIZE**: Extract key information to existing docs then remove

## Review Process
1. Assign reviewer(s) for each file/directory
2. Check against decision criteria above
3. Document decision and rationale in this file
4. Take appropriate action (retain, relocate, archive, remove, summarize)
5. Update tracking file with decision and date

---
*This tracking file created: 2026-08-26*
*Associated with commit: a179b04 (Add branch alignment investigation files and session status report)*
*Related to Jules session: 596003508416904399*
