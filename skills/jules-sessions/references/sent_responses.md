# Jules Sent Responses Log

Track follow-up, nudge, and rectification prompts sent to Jules sessions.

---

## Log Format

Each entry includes:
- **Session ID**: Which session received the prompt
- **Timestamp**: When sent
- **Prompt Type**: initial/follow-up/nudge/approve/rectification
- **Prompt Sent**: The actual message
- **Outcome**: What happened after (optional)

---

## Prompt Improvements Log

Document cases where a follow-up required to fix a situation could have been prevented by improving the original prompt.

### Pattern 1: Timeout from Too-Broad Scope

**Problem:** Session timed out on monolithic task.

```yaml
session_id: "wip-refactor-backend"
original_prompt: |
  Refactor backend for better modularity
outcome: "TIMEOUT - scope too broad"
follow_up_required: |
  Refactor ONLY the auth module:
  1. Move auth routes to src/auth/routes.py
  2. Extract token logic to src/auth/tokens.py
prompt_improvement: |
  INSTEAD OF: "Refactor backend for better modularity"
  
  SAY: "Refactor ONLY the auth module. Move auth routes to 
        src/auth/routes.py, extract token logic to 
        src/auth/tokens.py. Keep backward compatibility."
lesson: |
  Break monolithic tasks into subtasks. Specify exact files
  and target locations. Limit scope to single feature.
```

### Pattern 2: Over-Deletion (Aggressive Refactor)

**Problem:** Jules deleted too much code during "cleanup".

```yaml
session_id: "cleanup-session"
original_prompt: |
  Clean up unused code and imports
outcome: "DELETED useful code, broke tests"
follow_up_required: |
  Restore deleted files, only remove truly unused imports
prompt_improvement: |
  INSTEAD OF: "Clean up unused code and imports"
  
  SAY: "Remove ONLY imports that are provably unused across
        the entire codebase. Do NOT delete any functions or
        classes. Run tests after each change."
lesson: |
  Explicitly forbid deletion. Require test verification.
  "Unused" is ambiguous - be specific about scope.
```

### Pattern 3: Documentation Merger Lost Content

**From WIP Analysis:**

```yaml
session_id: "wip-deployment-docs"
original_prompt: |
  Streamline and centralize deployment documentation.
outcome: "Content merged but minor omissions"
issues:
  - "Explicit listing of run_tests.py missing"
  - "Requires final review for completeness"
prompt_improvement: |
  INSTEAD OF: "Streamline deployment documentation"
  
  SAY: "Merge EXISTING_DEPLOYMENT_FRAMEWORKS.md into 
        docs/deployment_guide.md. Preserve ALL content 
        from source file. After merge, verify these 
        sections exist: [list sections]. Include explicit
        mention of run_tests.py in auxiliary scripts."
lesson: |
  List required sections explicitly. Require verification
  of specific content preservation.
```

### Pattern 4: Test Framework Refactor Broke Test Paths

**From WIP Analysis:**

```yaml
session_id: "wip-test-framework"
original_prompt: |
  Refactor testing framework and standardize logging
outcome: "Test paths incorrect after refactoring"
follow_up_required: |
  Correct test directory paths for integration and API tests
prompt_improvement: |
  INSTEAD OF: "Refactor testing framework"
  
  SAY: "Refactor testing framework. Ensure test paths 
        remain valid: tests/unit/, tests/integration/, 
        tests/api/. Run full test suite after changes 
        to verify no path regressions."
lesson: |
  Specify paths that must remain valid. Require test 
  suite execution as verification step.
```

### Pattern 5: Smart Refactoring Caused Circular Dependency

**From WIP Analysis:**

```yaml
session_id: "wip-ai-engine"
original_prompt: |
  Refactor AI engine for better architecture
outcome: "CIRCULAR DEPENDENCY introduced"
follow_up_required: |
  Resolve circular dependency between DatabaseManager and AdvancedAIEngine
prompt_improvement: |
  INSTEAD OF: "Refactor AI engine"
  
  SAY: "Refactor AI engine for better architecture. 
        AVOID circular imports - if DatabaseManager 
        imports AdvancedAIEngine, AdvancedAIEngine 
        must NOT import DatabaseManager. Use dependency
        injection or create shared interface module."
lesson: |
  Explicitly forbid circular dependencies. Suggest
  architectural pattern (dependency injection, shared module).
```

---

## Improvement Patterns Summary

| Problem Type | Warning to Include |
|--------------|-------------------|
| Large scope | "Focus on X only, not Y" |
| Deletion | "Do NOT delete, only modify" |
| Paths | "Verify these paths remain valid: [...]" |
| Dependencies | "Avoid circular imports between X and Y" |
| Tests | "Run test suite after each change" |
| Documentation | "Preserve ALL content from source" |
| Refactoring | "Keep backward compatibility with existing imports" |

---

## Suggested Prompt Prefixes

For risk-prone task types:

**Refactoring:**
```
Refactor X. Requirements:
- Keep backward compatibility
- Run tests after changes
- Do NOT delete existing functions
```

**Cleanup:**
```
Clean up X. Requirements:
- Only remove imports provably unused
- Do NOT delete any functions/classes
- Run tests after each file
```

**Documentation:**
```
Merge X into Y. Requirements:
- Preserve ALL content from source
- Verify these sections exist: [list]
- Keep existing structure unless told otherwise
```

---

## Entries

### Entry 2025-01-15-001

```yaml
session_id: "15863163327149061241"
session_title: "Optimize Database Search"
branch: "scientific"
timestamp: "2025-01-15T14:30:00Z"
prompt_type: "initial"
prompt_sent: |
  Execute Task 1: Recover Lost Backend Modules.
  Begin by creating a comprehensive list...
outcome: "COMPLETED, PR #437"
```

### Entry 2025-01-16-001

```yaml
session_id: "14550388554331055113"
session_title: "Fix Auth Token Refresh"
branch: "main"
timestamp: "2025-01-16T09:15:00Z"
prompt_type: "nudge"
prompt_sent: |
  Status update? If encountering blockers with auth integration,
  describe them. Otherwise continue with token refresh logic.
outcome: "COMPLETED with refinements"
notes: "Session was stuck for 45min, nudge prompted completion"
```

### Entry 2025-01-17-001

```yaml
session_id: "abc123def456"
session_title: "Refactor Backend Handlers"
branch: "scientific"
timestamp: "2025-01-17T11:00:00Z"
prompt_type: "rectification"
prompt_sent: |
  The session timed out. Creating new session with refined scope:
  
  Refactor ONLY the auth module:
  1. Move auth routes to src/auth/routes.py
  2. Extract token logic to src/auth/tokens.py
  3. Keep backward compatibility with existing imports
outcome: "PENDING"
notes: "Broken down from monolithic refactor task"
```

---

## Statistics

| Type | Count |
|------|-------|
| initial | 1 |
| follow-up | 0 |
| nudge | 1 |
| approve | 0 |
| rectification | 1 |

**Success Rate:** 2/3 sessions completed (66%)

---

## Adding New Entries

Use the skill's reminder or manually append:

```markdown
### Entry YYYY-MM-DD-XXX

\`\`\`yaml
session_id: "<session_id>"
session_title: "<title>"
branch: "<branch>"
timestamp: "<ISO timestamp>"
prompt_type: "<initial|follow-up|nudge|approve|rectification>"
prompt_sent: |
  <the actual prompt text>
outcome: "<result or PENDING>"
notes: "<optional context>"
\`\`\`
```

---

## Query Examples

```bash
# Find all nudges sent
grep -A10 "prompt_type: nudge" references/sent_responses.md

# Find prompts for specific session
grep -B2 -A10 "session_id: 15863163327149061241" references/sent_responses.md

# Count by type
grep "prompt_type:" references/sent_responses.md | sort | uniq -c
```

---

## 2026-08-13 Batch: Refresh Stalled/Failed Sessions

### Failed Code Review Sessions (EmailIntelligence, live API)
- **Session**: 15008828426973856885 | **Type**: retry | **Prompt**: Status check, retry if relevant
- **Session**: 5938780760607407206 | **Type**: retry | **Prompt**: Status check, retry if relevant
- **Session**: 8294985337104762975 | **Type**: retry | **Prompt**: Status check, retry if relevant

### Failed Session Tracking Sessions (EmailIntelligence)
- **Session**: 10865630989900669675 | **Type**: close | **Prompt**: PR #660 closed, no action needed
- **Session**: 13005011563799472129 | **Type**: retry | **Prompt**: Retry CI fix with focused scope
- **Session**: 16320746218997740002 | **Type**: guidance | **Prompt**: PR #663 still open, check if fix needed post-#596
- **Session**: 9164742845732374282 | **Type**: retry | **Prompt**: Retry scientific CI fix, diagnose environment

### Awaiting Feedback Sessions (EmailIntelligence)
- **Session**: 14823980629961743161 | **Type**: guidance | **Prompt**: Create PR or confirm if resolved by #719/#713
- **Session**: 3620294950430015682 | **Type**: guidance | **Prompt**: Create PR or confirm if resolved by #719/#713
- **Session**: 6003660157445494667 | **Type**: close | **Prompt**: Superseded by PR #735 (verify_model_safety)
- **Session**: 14862791250094253007 | **Type**: close | **Prompt**: Security issues fixed by PRs #735/#696/#659/#600/#596
- **Session**: 11122169390008224115 | **Type**: guidance | **Prompt**: PR #730 still open, push changes or confirm
- **Session**: 2281891166145596786 | **Type**: guidance | **Prompt**: Security fixes applied, create PR for remaining or confirm
- **Session**: 3921006696662628935 | **Type**: close | **Prompt**: PR #727 closed, no action needed

### Kaggle Notebooks Sessions
- **Session**: 3030477830221326431 | **Type**: approve | **Prompt**: Proceed with PR for regex pre-compile
- **Session**: 13172420826211369022 | **Type**: guidance | **Prompt**: Proceed with PR for pipeline stubs
- **Session**: 16638769467548151530 | **Type**: nudge | **Prompt**: Status update, describe blockers or continue
- **Session**: 16994837303056291039 | **Type**: nudge | **Prompt**: Status update on test failures
- **Session**: 3927471279591052912 | **Type**: nudge | **Prompt**: Proceed with static analysis handoff
- **Session**: 7979893028704332984 | **Type**: guidance | **Prompt**: Proceed with absolute path replacement
- **Session**: 8371048452105557519 | **Type**: retry | **Prompt**: Retry kaggle kernel execution

### Other Sessions
- **Session**: 7956689661359593335 | **Type**: nudge | **Prompt**: Status update on gemini-fullstack maintenance
- **Session**: 14586978430582998057 | **Type**: close | **Prompt**: Confirm and close completed session

### Scientific Branch PR Sessions (jules_sessions/)
- **Session**: 15863163327149061241 (PR #437) | **Type**: guidance | **Prompt**: Rebase or confirm close
- **Session**: 125717287297355188 (PR #464) | **Type**: guidance | **Prompt**: Rebase or confirm close
- **Session**: 17857204272766840681 (PR #487) | **Type**: guidance | **Prompt**: Rebase or confirm close
- **Session**: 4710008747613819117 (PR #489) | **Type**: guidance | **Prompt**: Rebase or confirm close
- **Session**: 9033653426873037468 (PR #494) | **Type**: guidance | **Prompt**: Rebase or confirm close
- **Session**: 8364650927851285109 (PR #521) | **Type**: guidance | **Prompt**: Rebase or confirm close
- **Session**: 654824856418808212 (PR #523) | **Type**: guidance | **Prompt**: Rebase or confirm close
- **Session**: 7592875515078415283 (PR #535) | **Type**: guidance | **Prompt**: Rebase or confirm close
- **Session**: 16314414237181869537 (PR #571) | **Type**: guidance | **Prompt**: Rebase or confirm close

**Total: 28 messages sent across 3 repos (EmailIntelligence, kaggle-notebooks, gemini-fullstack)**
