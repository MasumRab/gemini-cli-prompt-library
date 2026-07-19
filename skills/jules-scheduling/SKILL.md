---
name: jules-scheduling
description: Jules task scheduling and orchestration — multi-task workflows, parallel execution, phase dependencies, and coordination. Use when planning multi-step Jules projects, creating task schedules, or managing complex Jules workflows. Trigger keywords: jules schedule, jules orchestration, jules tasks, jules parallel.
---

# Jules Task Scheduling

Orchestrate complex multi-task Jules workflows.

---

## Schedule Schema

### JSON Structure

```json
{
  "schedule_metadata": {
    "version": "1.0",
    "project": "ProjectName",
    "total_tasks": 11,
    "parallel_execution": true,
    "estimated_duration_days": "16-25"
  },
  "task_schedule": [
    {
      "task_id": "task_1",
      "title": "Task Title",
      "phase": "foundation",
      "priority": "high",
      "dependencies": [],
      "parallel_capable": false,
      "estimated_duration": "2-3 days",
      "branch": "scientific",
      "status": "completed",
      "jules_prompt": "Execute Task 1: ...",
      "context": {
        "objective": "...",
        "validation_criteria": [],
        "success_indicators": []
      },
      "execution_steps": []
    }
  ],
  "execution_rules": {
    "phase_dependencies": {},
    "parallel_execution": {},
    "branch_requirements": {},
    "quality_gates": {}
  }
}
```

---

## Execution Rules

### Phase Dependencies

```json
{
  "phase_dependencies": {
    "foundation": [],
    "core_enhancement": ["foundation"],
    "performance": ["foundation"],
    "integration": ["core_enhancement"]
  }
}
```

### Parallel Execution

```json
{
  "jules_coordination": {
    "coordinator_mode": "parallel_with_dependencies",
    "max_concurrent_tasks": 3,
    "error_handling": "fail_fast_with_rollback"
  }
}
```

---

## Quality Gates

```json
{
  "quality_gates": {
    "test_coverage_minimum": 90,
    "security_scan_required": true,
    "performance_benchmarks_required": true,
    "documentation_required": true
  }
}
```

---

## Task Template

```json
{
  "task_id": "task_N",
  "title": "Task Title",
  "phase": "phase_name",
  "priority": "high|medium|low",
  "dependencies": ["task_X"],
  "parallel_capable": true,
  "estimated_duration": "2-3 days",
  "branch": "target_branch",
  "status": "pending|running|completed|failed",
  "jules_prompt": "Full prompt for Jules...",
  "context": {
    "objective": "What to accomplish",
    "validation_criteria": [
      "Check 1",
      "Check 2"
    ],
    "success_indicators": [
      "Indicator 1",
      "Indicator 2"
    ],
    "risks": [
      "Risk 1",
      "Risk 2"
    ]
  },
  "execution_steps": [
    "Step 1",
    "Step 2"
  ]
}
```

---

## Example: EmailIntelligence Schedule

See `jules_sessions/task_schedule.json` for full example with 11 tasks:

| Phase | Tasks | Parallel |
|-------|-------|----------|
| Foundation | 1-2 | No |
| Core Enhancement | 11.1-11.5 | Yes |
| Performance | 11.6-11.9 | Yes |

**Key Settings:**
- Max concurrent: 3 tasks
- Fail mode: `fail_fast_with_rollback`
- Primary branch: `scientific`

---

## Creating a Schedule

### Step 1: Define Tasks

```bash
# Break project into tasks
# Each task needs:
# - Clear objective
# - Validation criteria
# - Execution steps
# - Dependencies
```

### Step 2: Set Execution Rules

```json
{
  "parallel_execution": {
    "foundation": false,
    "core_enhancement": true
  },
  "branch_requirements": {
    "primary_execution_branch": "scientific",
    "reference_branch": "main"
  }
}
```

### Step 3: Create Prompts

Each task needs a complete `jules_prompt`:

```
Execute Task N: Task Title. 
Work in {branch} branch which contains {context}.
{objective}.
{execution steps}.
```

### Step 4: Validate

```bash
# Check schema
jq '.' jules_sessions/task_schedule.json

# Count tasks by phase
jq '[.task_schedule[].phase] | group_by(.) | map({phase: .[0], count: length})' \
  jules_sessions/task_schedule.json

# Find dependencies
jq '.task_schedule[] | select(.dependencies | length > 0) | {task_id, dependencies}' \
  jules_sessions/task_schedule.json
```

---

## Monitoring Progress

### Track Status

```bash
# All task statuses
jq '.task_schedule[] | {task_id, status, title}' jules_sessions/task_schedule.json

# Pending tasks
jq '.task_schedule[] | select(.status == "pending") | .title' jules_sessions/task_schedule.json

# Completed count
jq '[.task_schedule[] | select(.status == "completed")] | length' jules_sessions/task_schedule.json
```

### Update Status

```bash
# Mark task complete
jq '(.task_schedule[] | select(.task_id == "task_1") | .status) = "completed"' \
  jules_sessions/task_schedule.json > tmp.json && mv tmp.json jules_sessions/task_schedule.json
```

---

## Parallel Execution Patterns

### Pattern 1: Independent Tasks

```json
{
  "tasks": ["task_a", "task_b", "task_c"],
  "parallel_capable": true,
  "max_concurrent": 3,
  "dependencies": []
}
```

### Pattern 2: Sequential with Parallel Middle

```json
{
  "foundation": { "parallel": false, "tasks": ["task_1", "task_2"] },
  "core": { "parallel": true, "tasks": ["task_3", "task_4", "task_5"] },
  "integration": { "parallel": false, "tasks": ["task_6"] }
}
```

### Pattern 3: Dependency Chain

```json
{
  "task_1": { "dependencies": [] },
  "task_2": { "dependencies": ["task_1"] },
  "task_3": { "dependencies": ["task_2"] }
}
```

---

## References

- CLI: [[jules-cli]] for creating sessions
- API: [[jules-api]] for programmatic control
- Workflows: [[jules-workflows]] for patterns
- Sessions: [[jules-sessions]] for session analysis
- Example: `jules_sessions/task_schedule.json`
