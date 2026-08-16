# Workflow Dependency Graph

## 2.1 Event Trigger Hierarchy (text diagram showing PR lifecycle events -> workflow routing)

```
PR Lifecycle Events:
├── pull_request.opened
│   ├── → review-family workflows (label-based routing)
│   ├── → resolve-family workflows (auto-trigger for specific labels)
│   └── → utility/support workflows (context gathering)
├── pull_request.synchronize
│   ├── → review-family workflows (re-run on new commits)
│   ├── → resolve-family workflows (re-evaluate conditions)
│   └── → auto-fix family (incremental fixes)
├── pull_request.closed
│   └── → utility/support workflows (cleanup, metrics)
├── pull_request_review.submitted
│   └── → review-family workflows (react to review feedback)
├── issue_comment.created
│   ├── → resolve-family workflows (slash command parsing)
│   └── → utility/support workflows (comment analysis)
└── workflow_dispatch
    ├── → manual override paths
    └── → debugging/ad-hoc workflows
```

## 2.2 Workflow Family Grouping

### Review Family
- `review-code-quality.yml`: Static analysis, linting, style checks
- `review-security.yml`: Security scanning, dependency vuln checks
- `review-performance.yml`: Performance benchmarking, regression detection
- `review-documentation.yml`: Docstring validation, markdown linting

### Resolve Family
- `resolve-merge-conflicts.yml`: Automatic conflict resolution strategies
- `resolve-dependencies.yml`: Dependency version updates, lockfile maintenance
- `resolve-test-failures.yml`: Test analysis, flaky test detection
- `resolve-style-violations.yml`: Auto-formatting, style issue correction

### Auto-Fix Family
- `auto-fix-security.yml`: Security patch application, dependency bumping
- `auto-fix-tests.yml`: Test fix generation, mock updates
- `auto-fix-deps.yml`: Automated dependency updates with safety checks
- `auto-fix-docs.yml`: Documentation typo fixes, link validation

### Utility/Support
- `context-gatherer.yml`: Repository context collection, file indexing
- `session-manager.yml`: Workflow session lifecycle management
- `artifact-coordinator.yml`: Artifact sharing between workflows
- `telemetry-collector.yml`: Metrics gathering, performance tracking
- `error-handler.yml`: Centralized error handling, fallback routing

## 2.3 Data Flow Between Workflows

### Payload Passing
- JSON payloads passed via workflow outputs → inputs
- Standardized schema: `{ event, payload, metadata, timestamps }`
- Size limited to 1MB; larger data uses artifact sharing

### Session Reuse
- Session ID propagated through workflow chains
- Shared session context stored in workflow-run scoped storage
- TTL: 2 hours for active sessions, 24 hours for archived

### Artifact Sharing
- Upload/download via `actions/upload-artifact` and `download-artifact`
- Naming convention: `workflow-name-{session-id}-{timestamp}`
- Retention: 7 days for workflow artifacts, 90 days for release artifacts
- Types: test reports, coverage data, build outputs, analysis results

## 2.4 Concurrency Groups and Cancellation Behavior

| Workflow Family | Concurrency Group | Max Parallel | Cancellation Behavior |
|----------------|-------------------|--------------|-----------------------|
| Review Family | `review-${{ github.event.pull_request.number }}` | 3 | Cancel previous on new trigger |
| Resolve Family | `resolve-${{ github.event.pull_request.number }}` | 2 | Allow queueing, cancel oldest |
| Auto-Fix Family | `autofix-${{ github.event.pull_request.number }}` | 1 | Sequential only, no cancellation |
| Utility/Support | `utility-${{ github.run_id }}` | 5 | Independent, no cancellation |
| Manual Triggers | `manual-${{ github.actor }}` | 1 per actor | Cancel previous same actor |

## 2.5 Label/Command Flow Diagram (text diagram showing label->workflow mapping)

```
Label/Command → Workflow Mapping:
├── [review:priority] → review-code-quality.yml (high priority queue)
├── [review:security] → review-security.yml (immediate execution)
├── [resolve:conflicts] → resolve-merge-conflicts.yml (high priority)
├── [resolve:deps] → resolve-dependencies.yml (scheduled + trigger)
├── [autofix:security] → auto-fix-security.yml (bypass review for critical)
├── [autofix:tests] → auto-fix-tests.yml (requires test-failure label)
├── [skip:ci] → utility/support only (bypass all families)
├── [needs:rebase] → resolve-family (pre-merge validation)
├── /fix → auto-fix family (comment command routing)
├── /review → review family (comment command routing)
└── /resolve → resolve family (comment command routing)
```

## 2.6 Session Reuse Patterns (when workflows trigger other workflows)

### Trigger Patterns:
1. **Sequential Chaining**: Review → Resolve → Auto-Fix (linear progression)
2. **Fan-Out**: Single trigger → Multiple parallel workflows (context gathering)
3. **Fan-In**: Multiple workflows → Consolidation workflow (result aggregation)
4. **Recursive**: Workflow triggers same workflow with different parameters (iteration)
5. **Conditional**: Trigger based on previous workflow outputs/conclusions

### Session Lifecycle:
- Initiated by: `workflow_run` or `workflow_dispatch` with session ID
- Propagated via: Workflow inputs, environment variables, shared artifacts
- Terminated by: Explicit completion signal, timeout, or error threshold
- Reuse Criteria: Same PR, same actor, compatible workflow family

## 2.7 Error Handling and Fallback Paths

### Quota Exhaustion:
- GitHub Actions quota: Check `github.actions_quota` output
- Fallback: Queue workflows, execute during off-peak hours
- Notification: Comment on PR with estimated delay
- Escalation: After 3 retries, notify maintainers via email

### Failed Sessions:
- Retry Policy: Exponential backoff (1min, 2min, 4min, 10min)
- Max Retries: 3 attempts per workflow instance
- Failure Types:
  - Infrastructure: Automatic retry with different runner
  - Application: Route to error-handler workflow
  - Logic: Manual intervention required (label `needs:manual-review`)
- Fallback Chains:
  Primary → Secondary (different runner) → Tertiary (manual) → Abort

## 2.8 Cross-Workflow State Sharing

### Comment Markers:
- `<!-- workflow-session: {session-id} -->`: Session tracking in PR comments
- `<!-- workflow-result: {workflow-name}:{status} -->`: Result annotation
- `<!-- workflow-data: {key}:{value} -->`: Small data sharing (<1KB)
- Updated by: `gh api` calls or custom actions
- Read by: Workflow initialization steps

### Payload Files:
- Stored in: `.workflow/sessions/{session-id}/`
- Naming: `{workflow-name}-{timestamp}.json`
- Format: NDJSON for streaming, JSON for structured data
- Access: Shared via workspace persistence between jobs
- Cleanup: Automatic after session TTL expiration

## 2.9 Workflow Initiation Paths

### Manual Triggers:
- `workflow_dispatch` with inputs:
  - `session-id`: For continuing existing sessions
  - `force-run`: Bypass normal conditions
  - `debug-level`: Verbose logging
  - `target-files`: Specific file subset
- Access: Repository dispatch API, GitHub UI, CLI
- Permissions: Requires write access to repository

### Automatic Triggers:
- Event-based: PR events, issue comments, schedule
- Conditional: Based on labels, file paths, author permissions
- Chain-triggered: Completion of prerequisite workflows
- Time-based: cron schedules for maintenance workflows
- External: Webhook integrations (CI/CD, monitoring systems)

## 2.10 Timeout and Retry Behavior Summary

### Timeouts:
- Job-level: 60 minutes (configurable per workflow)
- Workflow-level: 6 hours (GitHub Actions limit)
- Session-level: 2 hours active, extendable by activity
- Step-level: Default 5 minutes, overrideable with `timeout-minutes`

### Retry Behavior:
- Automatic Retries: Infrastructure failures only (2 attempts)
- Manual Retry: Via `workflow_dispatch` with retry flag
- Conditional Retry: Based on error codes in workflow outputs
- Delay Strategy: Fixed 30s for rate limits, exponential for others
- Maximum Attempts: 5 total (including initial run)

## 2.11 Cross-Workflow Data Flow Summary (final consolidated diagram)

```
Data Flow Overview:
┌─────────────────┐    ┌────────────────────┐    ┌────────────────────┐
│   Event Trigger │───▶│   Session Manager  │───▶│ Context Gatherer   │
└─────────────────┘    └────────────────────┘    └────────────────────┘
                                  │                         │
                                  ▼                         ▼
                        ┌─────────────────┐         ┌────────────────────┐
                        │  Payload Router │         │   Artifact Store   │
                        └─────────────────┘         └────────────────────┘
                                  │                         │
        ┌─────────────────────────┼─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
┌─────────────────┐    ┌────────────────────┐    ┌────────────────────┐
│   Review Family │    │   Resolve Family   │    │   Auto-Fix Family  │
└─────────────────┘    └────────────────────┘    └────────────────────┘
        │                         │                         │
        └─────────────┬───────────┘─────────────┬───────────┘
                      ▼                         ▼
            ┌─────────────────────────────────────────┐
            │       Utility/Support & Telemetry       │
            └─────────────────────────────────────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │  Result Aggregator │
                        └────────────────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │   PR Commenter     │
                        └────────────────────┘
```

### Data Flow Principles:
1. **Immutability**: Payloads treated as immutable once created
2. **Atomicity**: Each workflow produces discrete, versioned outputs
3. **Traceability**: All data flows tagged with session ID and workflow run ID
4. **Efficiency**: Prefer references over duplication (artifact sharing vs payload passing)
5. **Resilience**: Fallback to comment markers when primary channels fail