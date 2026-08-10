# Graphite-Agent V8 Progression Plan

> **Status:** Draft — 2025-07-13
> **Scope:** All work inside `/home/masum/github/remote/gemini-cli-prompt-library`
> **Prerequisite:** Resolve the stuck interactive rebase (7 conflicts) before any V8 implementation begins.

---

## 1. Current State Assessment

### 1.1 Version History

| Version | Layer                       | Status                | Key Artifacts                                                                                                                          |
| :------ | :-------------------------- | :-------------------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| V6.4    | Core analyser               | ✅ Working            | `lib/snapshot.py`, `lib/git_utils.py`, `lib/github_utils.py`, `lib/schemas.py` — produces `analysis_snapshot.json`                     |
| V7.1    | Diagnostic command layer    | ✅ Working            | 23 CLI tools, runbooks, workbooks, checklists, contracts, prompts                                                                      |
| V7.2    | Target intent + root health | ✅ Working            | `lib/targets.py`, `lib/roots.py`, `lib/stack_ordering.py`, target/root questions, stale-root handling                                  |
| V7.3    | Multi-root retrofit bundle  | ✅ Working            | Diff report, README, integration of V7.1+V7.2 into `agent_core.py`                                                                     |
| V7.4    | Replay risk scaffold        | ✅ Working (skeleton) | `discover_repo.py`, `replay_risk.py`, `validate_replay.py`, `write_report.py`, `build_command_plan.py`, config system, fixtures, tests |
| **V8**  | **Unification + execution** | **📋 Planned**        | **This document**                                                                                                                      |

### 1.2 Architecture: Two Disconnected Pipelines

The system currently has **two parallel pipelines** that do not share data or control flow:

```
Pipeline A (V6.4 → V7.3): "Analysis Pipeline"
  analyse.py → analysis_snapshot.json → agent_core.py → targets/roots/stack_order → execution_plan.json

Pipeline B (V7.4): "Replay Safety Pipeline"
  discover_repo.py → repo_inventory.json → replay_risk.py → validate_replay.py → write_report.py → build_command_plan.py
```

**V8's primary goal is to unify these into a single coherent pipeline.**

### 1.3 Blocked: Stuck Interactive Rebase

The repository is mid-interactive-rebase with 7 unresolved conflicts:

| File                                               | Status | Conflict Type     |
| :------------------------------------------------- | :----- | :---------------- |
| `.flake8`                                          | UD     | deleted_by_theirs |
| `commands/prompts/improve.toml`                    | UU     | both_modified     |
| `commands_manifest.json`                           | UU     | both_modified     |
| `dspy_integration/framework/optimizers/miro_v2.py` | UU     | both_modified     |
| `dspy_integration/framework/providers/base.py`     | UU     | both_modified     |
| `package.json`                                     | DU     | deleted_by_us     |
| `tests/test_active_context.py`                     | UU     | both_modified     |

The V7.4 replay risk tool correctly detects this state (`overall_risk: high`, `execution_allowed: false`).
**No V8 work should proceed until this rebase is resolved.**

### 1.4 Gap Analysis

| Gap                                                  | Source Spec   | Current State                                                                                  | V8 Priority |
| :--------------------------------------------------- | :------------ | :--------------------------------------------------------------------------------------------- | :---------- |
| No unified dispatcher (`main.py`)                    | Phase 8.2     | Missing entirely                                                                               | **P0**      |
| No `lib/git_core.py` shared library                  | Phase 8.1/9.4 | `lib/git_utils.py` exists but lacks `get_patch_id()`, `get_remote_refs()`, `get_pr_metadata()` | **P0**      |
| Target discovery scoring algorithm not implemented   | Phase 9.1     | `lib/targets.py` uses simple `root_branch` lookup, not weighted scoring                        | **P1**      |
| State projection (`rebuild_plan.py`) not implemented | Phase 9.3     | `rebuild_plan.py` exists but doesn't project `decision_log.jsonl` onto snapshot                | **P1**      |
| `build_command_plan.py` always emits empty commands  | V7.4          | `commands: []` even when validation passes                                                     | **P1**      |
| `execute_approved.py` is a stub                      | V7.1          | No actual Graphite command execution logic                                                     | **P2**      |
| No staleness/idempotency checking                    | Phase 8.5     | `checklist_report.json` doesn't store validation timestamp                                     | **P2**      |
| No patch equivalence detection                       | V7.2 report   | "Not yet implemented"                                                                          | **P3**      |
| No active `config/repo.yaml`                         | V7.4          | Only example configs exist                                                                     | **P2**      |
| Reports hardcode "V7.4 scaffold defers to V7.3"      | V7.4          | `lib/reports.py` line says topology is deferred                                                | **P1**      |
| Rebase recovery workflow missing                     | V8 (new)      | No tooling to help resolve the current stuck state                                             | **P0**      |

---

## 2. V8 Architecture: Unified Pipeline

### 2.1 Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    main.py (Unified Dispatcher)                   │
│  graphite-agent discover | analyse | triage | validate | execute  │
└──────────┬────────────────────────────────────────────────────────┘
           │
  ┌────────▼────────┐
  │  STAGE 1: DISCOVER  │
  │  discover_repo.py   │
  │  → repo_inventory   │
  │  → replay_risk      │
  │  → validate_replay  │
  └────────┬───────────┘
           │ (gate: replay validation must pass)
  ┌────────▼────────┐
  │  STAGE 2: ANALYSE   │
  │  analyse.py         │
  │  → analysis_snapshot│
  │  (Git + PR topology)│
  └────────┬───────────┘
           │
  ┌────────▼────────┐
  │  STAGE 3: TRIAGE    │
  │  agent_core.py      │
  │  → targets          │
  │  → root_health      │
  │  → stack_order      │
  │  → triage_packets   │
  │  → questions        │
  └────────┬───────────┘
           │ (gate: user decisions recorded)
  ┌────────▼────────┐
  │  STAGE 4: PLAN      │
  │  rebuild_plan.py    │
  │  (state projection) │
  │  → execution_plan   │
  │  build_command_plan │
  │  → command_plan     │
  └────────┬───────────┘
           │ (gate: all validations pass)
  ┌────────▼────────┐
  │  STAGE 5: VALIDATE  │
  │  validate_cache     │
  │  validate_targets   │
  │  validate_roots     │
  │  validate_stack     │
  │  validate_plan      │
  │  → checklist_report │
  └────────┬───────────┘
           │ (gate: user explicit approval)
  ┌────────▼────────┐
  │  STAGE 6: EXECUTE   │
  │  execute_approved   │
  │  (Graphite commands)│
  └────────────────────┘
```

### 2.2 Key Design Principles for V8

1. **Single entry point**: `main.py` dispatches all subcommands, enforces stage ordering and gates.
2. **Unified state model**: One `run_id` flows through all stages. Outputs land in `outputs/runs/<run_id>/`.
3. **Replay safety is the front gate**: No analysis proceeds until replay validation passes.
4. **Decision projection is the bridge**: `rebuild_plan.py` projects `decision_log.jsonl` onto `analysis_snapshot.json` to produce the dynamic `execution_plan.json`.
5. **Config-driven**: `config/repo.yaml` (not just examples) controls thresholds, roots, generated-file patterns.
6. **Idempotent re-runs**: All analysis tools can be re-run safely. Only `decision_log.jsonl` is append-only.
7. **Staleness detection**: `checklist_report.json` stores validation timestamp; if any input is newer, system blocks execution.

---

## 3. Implementation Phases

### Phase 0: Rebase Recovery (BLOCKER — must complete first)

**Goal:** Resolve the 7 unresolved conflicts and finish or abort the interactive rebase.

**Steps:**

1. Inspect each conflicted file and determine resolution strategy:
   - `.flake8` (UD — deleted upstream): Accept deletion, remove file.
   - `package.json` (DU — deleted by us): Confirm removal, accept theirs or drop.
   - `commands_manifest.json` (UU): Regenerate from source rather than manually merge.
   - `commands/prompts/improve.toml` (UU): Manual semantic merge.
   - `dspy_integration/framework/optimizers/miro_v2.py` (UU): Manual semantic merge.
   - `dspy_integration/framework/providers/base.py` (UU): Manual semantic merge.
   - `tests/test_active_context.py` (UU): Manual semantic merge.
2. After resolving: `git rebase --continue` or `git rebase --abort` if the rebase is not salvageable.
3. Verify clean state: `git status` shows no conflicts, no rebase-merge dir.
4. Run V7.4 tests to confirm: `python .graphite-agent/tests/run_tests.py`
5. Create a new V8 branch: `git checkout -b graphite-agent-v8`

**Deliverable:** Clean working tree on a V8 branch.

**Estimated effort:** 2-4 hours (manual conflict resolution)

---

### Phase 1: Unified Dispatcher + Git Core (P0)

**Goal:** Create `main.py` and consolidate git utilities into `lib/git_core.py`.

#### 1.1 `tools/lib/git_core.py`

Consolidate from `lib/git_utils.py` and add missing functions:

```python
# Required functions (from Phase 8.1/9.4 spec):
def get_patch_id(commit_hash: str) -> str: ...
def is_ancestor(ancestor: str, descendant: str) -> bool: ...
def get_merge_base(a: str, b: str) -> str | None: ...
def get_remote_refs() -> list[str]: ...
def get_pr_metadata(branch_name: str) -> dict | None: ...
def calculate_proximity(target: str, branch: str) -> int: ...
def get_merge_parents(commit_hash: str) -> list[str]: ...
```

**Migration:** Refactor `lib/snapshot.py` to use `git_core.py` instead of `lib/git_utils.py` directly. Keep `git_utils.py` as a thin compatibility shim or remove it.

#### 1.2 `tools/main.py` (Unified Dispatcher)

```python
# Command mapping:
# graphite-agent discover    → Stage 1 (discover_repo + replay_risk + validate_replay)
# graphite-agent analyse     → Stage 2 (analyse.py)
# graphite-agent triage      → Stage 3 (agent_core: targets, roots, stack, questions)
# graphite-agent decide      → Record decision (decide.py / target_decide.py / root_decide.py)
# graphite-agent plan        → Stage 4 (rebuild_plan + build_command_plan)
# graphite-agent validate    → Stage 5 (all validators)
# graphite-agent execute     → Stage 6 (execute_approved)
# graphite-agent status      → checklist.py
# graphite-agent report      → write_report.py
# graphite-agent run         → Full pipeline: discover → analyse → triage → plan → validate
```

**Safety checks in `main.py`:**

- Verify `.graphite-agent/` and `outputs/` exist
- Enforce stage ordering (can't `plan` before `analyse`, can't `execute` before `validate`)
- Check staleness before `execute`
- Require `--approve` flag for `execute`

**Deliverables:**

- `tools/main.py`
- `tools/lib/git_core.py`
- Updated imports in all tools that currently use `lib/git_utils.py`
- Tests for dispatcher stage gating

**Estimated effort:** 4-6 hours

---

### Phase 2: Pipeline Unification (P1)

**Goal:** Connect the V7.4 replay safety pipeline with the V6.4/V7.3 analysis pipeline.

#### 2.1 Unified Run Context

Create `tools/lib/run_context.py`:

```python
class RunContext:
    """Shared state object that flows through all pipeline stages."""
    run_id: str
    agent_dir: Path
    outputs_dir: Path
    run_dir: Path       # outputs/runs/<run_id>/
    latest_dir: Path    # outputs/latest/
    config: dict
    inventory: dict | None
    replay_risk: dict | None
    replay_validation: dict | None
    snapshot: dict | None
    decisions: dict | None
    execution_plan: dict | None
    command_plan: dict | None
    checklist: dict | None
```

#### 2.2 Integrate Replay Gate into Analysis

Modify `analyse.py` / `agent_core.py` to:

1. Check for `outputs/latest/validation/replay_validation.json`
2. If status is `blocked`, refuse to proceed (or warn in `--force` mode)
3. Include replay risk summary in `analysis_snapshot.json` metadata

#### 2.3 Integrate Analysis Results into Reports

Modify `lib/reports.py`:

- Replace "V7.4 scaffold defers full topology to existing V7.3 tools" with actual topology data from `analysis_snapshot.json`
- Include branch topology summary from `branch_graph.nodes`
- Include safe/blocked branches from the analysis pipeline
- Merge replay risk and analysis-based risk into a unified risk assessment

#### 2.4 Active Config File

Create `config/repo.yaml` (not just examples):

```yaml
repo:
  name: gemini-cli-prompt-library
  mode: local_only

roots:
  configured:
    - main
  discover: true

generated_files:
  patterns:
    - "dist/**"
    - "build/**"
    - "*.generated.*"
    - "*.lock"
    - "package-lock.json"
    - "commands_manifest.json"
  treat_as_replay_risk: true

execution:
  default_mode: analyzer_only
  require_explicit_approval: true
```

**Deliverables:**

- `tools/lib/run_context.py`
- Modified `analyse.py` with replay gate
- Modified `lib/reports.py` with unified reporting
- `config/repo.yaml` active config
- Tests for pipeline integration

**Estimated effort:** 6-8 hours

---

### Phase 3: Target Discovery Scoring (P1)

**Goal:** Implement the weighted scoring algorithm from Phase 9.1 spec.

#### 3.1 Rewrite `lib/targets.py`

Replace the simple `root_branch` lookup with the full scoring algorithm:

| Signal            | Weight                   | Implementation                                                  |
| :---------------- | :----------------------- | :-------------------------------------------------------------- |
| Origin HEAD       | 100                      | `inventory.origin_head()`                                       |
| PR Base Frequency | +15 per PR (max +60)     | Count `pr_metadata.items` where `baseRefName == candidate`      |
| Ancestry Depth    | +10 per branch (max +50) | Count branches where `is_ancestor(candidate, branch)`           |
| Semantic Match    | +30                      | Case-insensitive match for "main", "master", "develop", "trunk" |
| Proximity Score   | +20                      | `merge-base` < 5 commits from branch HEAD                       |
| Short-Lived Check | -80                      | Branch created < 48h ago with 0 descendants                     |

Confidence mapping: High ≥ 85, Medium 50-84, Low < 50.

#### 3.2 Enrich `target_candidates.json`

Include full scoring breakdown:

```json
{
  "candidates": {
    "main": {
      "target": "main",
      "score": 115,
      "confidence": "high",
      "signals": [
        { "signal": "origin_head", "weight": 100 },
        { "signal": "semantic_match", "weight": 30 },
        {
          "signal": "ancestry_depth",
          "weight": 20,
          "detail": "2 descendant branches"
        }
      ]
    }
  }
}
```

**Deliverables:**

- Rewritten `lib/targets.py` with scoring algorithm
- Updated `discover_targets.py` to use inventory data (not just snapshot nodes)
- Tests for scoring accuracy

**Estimated effort:** 3-4 hours

---

### Phase 4: State Projection (P1)

**Goal:** Implement the decision projection algorithm from Phase 9.3 spec.

#### 4.1 Rewrite `rebuild_plan.py`

Current `rebuild_plan.py` doesn't implement the projection algorithm. Replace it:

```python
def project_decisions(snapshot, decision_log):
    """
    Project append-only decision_log onto static analysis_snapshot
    to produce dynamic execution_plan.
    """
    active_decisions = {}
    # Step 1: Process log oldest to newest
    for entry in decision_log:
        subject = entry.get('branch') or entry.get('target_root')
        if entry.get('event_type') == 'decision_revoked':
            active_decisions.pop(subject, None)
        elif entry.get('event_type') in {'decision_recorded', 'decision_revised', 'root_refresh_policy'}:
            active_decisions[subject] = entry

    # Step 2: Apply overlay onto snapshot nodes
    nodes = copy.deepcopy(snapshot['branch_graph']['nodes'])
    for branch, node in nodes.items():
        if branch in active_decisions:
            decision = active_decisions[branch]
            node['status'] = 'safe'  # or needs_restack based on choice
            node['resolved_parent'] = extract_parent(decision['choice'])
            node['decision_provenance'] = decision['event_id']

    # Step 3: Recalculate stacks
    stack_order = generate_stack_order(nodes, root_health, EXECUTABLE)

    # Step 4: Build execution plan
    return {
        'execution_queue': [...],
        'manual_triage_queue': [...],
        'active_decisions': active_decisions,
        'generated_at_utc': now()
    }
```

#### 4.2 Implement `build_command_plan.py` Real Commands

When validation passes, generate actual Graphite commands:

```json
{
  "run_id": "2025-07-13T...",
  "mode": "dry_run",
  "execution_allowed": true,
  "blocked_by": [],
  "commands": [
    {
      "step": 1,
      "branch": "feature-x",
      "command": "gt track feature-x --parent main"
    },
    {
      "step": 2,
      "branch": "feature-y",
      "command": "gt track feature-y --parent feature-x"
    },
    { "step": 3, "branch": "feature-x", "command": "gt restack" }
  ]
}
```

In `--execute` mode (requires `--approve`), run commands via `subprocess` with safety checks.

**Deliverables:**

- Rewritten `rebuild_plan.py` with projection algorithm
- Rewritten `build_command_plan.py` with real command generation
- Tests for projection correctness

**Estimated effort:** 4-5 hours

---

### Phase 5: Execution Engine (P2)

**Goal:** Make `execute_approved.py` actually execute Graphite commands.

#### 5.1 Implement `execute_approved.py`

```python
def execute(plan_path, approve=False, dry_run=True):
    plan = load(plan_path)
    if not plan['execution_allowed']:
        raise SafetyError("Execution not allowed by validation")
    if not approve and not dry_run:
        raise SafetyError("Explicit --approve required for execution")

    results = []
    for cmd in plan['commands']:
        if dry_run:
            results.append({'command': cmd['command'], 'status': 'dry_run'})
        else:
            result = subprocess.run(cmd['command'], shell=True, ...)
            results.append({'command': cmd['command'], 'status': 'success' if result.returncode == 0 else 'failed', ...})
            if result.returncode != 0:
                break  # Stop on first failure

    return results
```

#### 5.2 Safety Guarantees

- **Pre-flight check**: Re-run `validate_replay` immediately before execution
- **Atomic tracking**: Record each command's result in `outputs/execution_log.jsonl`
- **Rollback capability**: If a command fails, record the state for manual recovery
- **No-force default**: Never use `--force` flags unless explicitly configured

**Deliverables:**

- Implemented `execute_approved.py`
- `outputs/execution_log.jsonl` format
- Tests for execution safety gates

**Estimated effort:** 3-4 hours

---

### Phase 6: Staleness Detection + Idempotency (P2)

**Goal:** Implement Phase 8.5 specs.

#### 6.1 Staleness Detection

Modify `checklist_report.json` to include:

```json
{
  "status": "pass",
  "validated_at_utc": "2025-07-13T...",
  "input_timestamps": {
    "analysis_snapshot.json": "2025-07-13T10:00:00Z",
    "target_matrix.json": "2025-07-13T10:01:00Z",
    "root_health.json": "2025-07-13T10:02:00Z",
    "stack_order.json": "2025-07-13T10:03:00Z"
  },
  "is_stale": false
}
```

If any input file is newer than `validated_at_utc`, `is_stale` becomes `true` and `execute_approved` blocks.

#### 6.2 Idempotency Verification

Add idempotency tests:

- Run `analyse.py` twice → same output (within timestamp tolerance)
- Run `target_analyse()` twice → same output
- Run `root_health()` twice → same output
- `decision_log.jsonl` is never modified by analysis tools

**Deliverables:**

- Staleness detection in validation
- Idempotency tests
- `execute_approved.py` staleness gate

**Estimated effort:** 2-3 hours

---

### Phase 7: Patch Equivalence Detection (P3)

**Goal:** Implement patch-id based equivalence detection (mentioned as "not yet implemented" in V7.2).

#### 7.1 Patch-ID Equivalence

Use `git patch-id` to detect:

- **Sibling overlap**: Two branches sharing the same patch-id (cherry-pick or duplicate work)
- **Already-merged**: A branch's patches are all present in the target (no-op merge)
- **Conflict forecast**: Predict textual conflicts by comparing changed file sets

#### 7.2 Integration with Replay Risk

Add patch equivalence checks to `lib/replay.py`:

```python
def patch_equivalence_risks(config, inventory):
    """Detect branches whose patches are already in target."""
    risks = []
    for branch in inventory['branches']['local']:
        for target in inventory['targets']['discovered']:
            overlap = git.patch_ids_between(target, branch) & git.patch_ids_between(target, target)
            if overlap:
                risks.append({
                    'branch': branch,
                    'target': target,
                    'overlap_count': len(overlap),
                    'recommendation': 'branch patches already in target — skip or create empty PR'
                })
    return risks
```

**Deliverables:**

- Patch equivalence detection in `lib/replay.py`
- Tests with fixture branches

**Estimated effort:** 3-4 hours

---

## 4. Testing Strategy

### 4.1 Test Pyramid

| Level       | Scope                    | Files                                                                |
| :---------- | :----------------------- | :------------------------------------------------------------------- |
| Unit        | Individual lib functions | `tests/test_v74_scaffold.py` (existing) + new `test_v8_*.py`         |
| Integration | Multi-stage pipeline     | `tests/test_v8_pipeline.py` — run full discover→execute in temp repo |
| Fixture     | Known conflict scenarios | `fixtures/` — add new fixtures for V8 scenarios                      |
| Contract    | JSON schema validation   | `contracts/` — enforce required fields on all outputs                |

### 4.2 New Fixtures Needed

| Fixture                    | Purpose                                                |
| :------------------------- | :----------------------------------------------------- |
| `fixtures/clean_repo/`     | Happy path: no conflicts, simple branch stack          |
| `fixtures/stale_root/`     | Multiple blocked branches from one root                |
| `fixtures/cross_root/`     | Branch with ancestry from two roots                    |
| `fixtures/merge_conflict/` | Branch with trunk-update merge                         |
| `fixtures/already_merged/` | Branch whose patches are in target (patch equivalence) |

### 4.3 Test Commands

```bash
# Run all tests
python .graphite-agent/tests/run_tests.py

# Run V8 tests only
python -m pytest .graphite-agent/tests/test_v8_*.py -v

# Integration test (creates temp repo, runs full pipeline)
python .graphite-agent/tests/test_v8_pipeline.py
```

---

## 5. File Manifest

### 5.1 New Files to Create

| File                          | Phase | Purpose                        |
| :---------------------------- | :---- | :----------------------------- |
| `tools/main.py`               | 1     | Unified dispatcher             |
| `tools/lib/git_core.py`       | 1     | Consolidated git utilities     |
| `tools/lib/run_context.py`    | 2     | Shared pipeline state          |
| `config/repo.yaml`            | 2     | Active repo config             |
| `tests/test_v8_dispatcher.py` | 1     | Dispatcher stage gating tests  |
| `tests/test_v8_pipeline.py`   | 2     | End-to-end integration tests   |
| `tests/test_v8_scoring.py`    | 3     | Target discovery scoring tests |
| `tests/test_v8_projection.py` | 4     | State projection tests         |
| `tests/test_v8_execution.py`  | 5     | Execution safety tests         |
| `tests/test_v8_staleness.py`  | 6     | Staleness detection tests      |
| `fixtures/clean_repo/`        | 4.2   | Happy-path fixture             |
| `fixtures/stale_root/`        | 4.2   | Stale root fixture             |
| `fixtures/cross_root/`        | 4.2   | Cross-root fixture             |
| `fixtures/already_merged/`    | 7     | Patch equivalence fixture      |

### 5.2 Files to Modify

| File                                           | Phase | Change                                            |
| :--------------------------------------------- | :---- | :------------------------------------------------ |
| `tools/lib/targets.py`                         | 3     | Rewrite with scoring algorithm                    |
| `tools/rebuild_plan.py`                        | 4     | Implement state projection                        |
| `tools/build_command_plan.py`                  | 4     | Generate real commands                            |
| `tools/execute_approved.py`                    | 5     | Implement execution engine                        |
| `tools/lib/replay.py`                          | 7     | Add patch equivalence                             |
| `tools/lib/reports.py`                         | 2     | Unified reporting (remove "defers to V7.3" lines) |
| `tools/analyse.py`                             | 2     | Add replay gate                                   |
| `tools/agent_core.py`                          | 2     | Integrate with run context                        |
| `tools/lib/snapshot.py`                        | 1     | Use `git_core.py` instead of `git_utils.py`       |
| `tools/validate_plan.py`                       | 6     | Add staleness check                               |
| `tools/checklist.py`                           | 6     | Store validation timestamp                        |
| `.graphite-agent/IMPLEMENTATION_REPORT_V72.md` | —     | Update with V8 status                             |
| `.graphite-agent/COMPATIBILITY.md`             | —     | Update for V8                                     |

### 5.3 Files to Deprecate

| File                     | Reason                                                    |
| :----------------------- | :-------------------------------------------------------- |
| `tools/lib/git_utils.py` | Replaced by `git_core.py` (keep as shim during migration) |
| `1_analyze_and_plan.py`  | Replaced by `main.py discover && main.py analyse`         |
| `2_strict_executor.py`   | Replaced by `main.py execute`                             |

---

## 6. Dependency Graph

```
Phase 0 (Rebase Recovery)
    │
    ▼
Phase 1 (Dispatcher + Git Core) ──── P0
    │
    ├──▶ Phase 2 (Pipeline Unification) ──── P1
    │       │
    │       ├──▶ Phase 3 (Target Scoring) ──── P1
    │       │       │
    │       │       └──▶ Phase 4 (State Projection) ──── P1
    │       │               │
    │       │               ├──▶ Phase 5 (Execution Engine) ──── P2
    │       │               │
    │       │               └──▶ Phase 6 (Staleness) ──── P2
    │       │
    │       └──▶ Phase 7 (Patch Equivalence) ──── P3
    │
    └──▶ (Phase 2 can start in parallel with Phase 3 once Phase 1 is done)
```

**Critical path:** Phase 0 → 1 → 2 → 4 → 5
**Parallelizable:** Phase 3 and Phase 2 can overlap. Phase 6 and 7 are independent.

---

## 7. Success Criteria

V8 is complete when:

1. **Single entry point**: `python .graphite-agent/tools/main.py run` executes the full pipeline end-to-end.
2. **Replay safety gate**: Pipeline refuses to proceed when rebase/merge/cherry-pick is active.
3. **Unified reporting**: `branch_stacking_report.md` includes both replay risk AND topology analysis (no "defers to V7.3" text).
4. **Target scoring**: `target_candidates.json` includes weighted scores with signal breakdowns.
5. **Decision projection**: `execution_plan.json` reflects user decisions projected onto the snapshot.
6. **Real command plan**: `command_plan.json` contains actual Graphite commands when validation passes.
7. **Safe execution**: `execute_approved.py` runs commands with pre-flight check, atomic logging, and rollback recording.
8. **Staleness detection**: Execution blocks if any input file is newer than the last validation.
9. **All tests pass**: `python .graphite-agent/tests/run_tests.py` exits 0.
10. **Config-driven**: `config/repo.yaml` is active and controls all thresholds.

---

## 8. Risk Register

| Risk                                               | Likelihood | Impact | Mitigation                                                        |
| :------------------------------------------------- | :--------- | :----- | :---------------------------------------------------------------- |
| Rebase conflicts reveal deeper repo issues         | Medium     | High   | Phase 0 includes full repo health check after resolution          |
| `gh` CLI not authenticated in target env           | High       | Medium | `discover_repo.py --local-only` mode already handles this         |
| Graphite CLI (`gt`) not installed                  | High       | High   | V8 execution engine checks for `gt` and provides install guidance |
| Large mixed commits make decomposition impractical | Medium     | Medium | V8 adds hunk-level decomposition tooling in Phase 4               |
| Patch-id stability across git versions             | Low        | Low    | Use `git patch-id` consistently; add version check                |
| PyYAML not installed for config parsing            | Medium     | Low    | `lib/config.py` already has fallback for missing PyYAML           |

---

## 9. Resuming Work

To resume V8 work after this plan is created:

```bash
# 1. Check rebase state
cd /home/masum/github/remote/gemini-cli-prompt-library
git status
ls .git/rebase-merge/  # if exists, rebase is still active

# 2. Resolve conflicts (Phase 0)
# ... manual resolution ...
git rebase --continue  # or --abort

# 3. Create V8 branch
git checkout -b graphite-agent-v8

# 4. Run existing tests to confirm baseline
python .graphite-agent/tests/run_tests.py

# 5. Start Phase 1: Create main.py and git_core.py
```

### 9.1 Quick Status Check Commands

```bash
# Is rebase still active?
test -d .git/rebase-merge && echo "REBASE ACTIVE" || echo "CLEAN"

# What conflicts remain?
git diff --name-only --diff-filter=U

# Do V7.4 tests pass?
python .graphite-agent/tests/run_tests.py 2>&1 | tail -5

# What's the current replay risk?
python .graphite-agent/tools/replay_risk.py --local-only 2>&1 | head -10
```

---

## 10. Appendix: Current Tool Inventory

### 10.1 CLI Tools (35 files in `tools/`)

| Tool                      | Pipeline   | Status                                          |
| :------------------------ | :--------- | :---------------------------------------------- |
| `analyse.py`              | Analysis   | ✅ Working (calls `agent_core.analyse_outputs`) |
| `discover_repo.py`        | Replay     | ✅ Working (V7.4)                               |
| `replay_risk.py`          | Replay     | ✅ Working (V7.4)                               |
| `validate_replay.py`      | Replay     | ✅ Working (V7.4)                               |
| `write_report.py`         | Replay     | ✅ Working (V7.4)                               |
| `build_command_plan.py`   | Replay     | ✅ Skeleton (empty commands)                    |
| `agent_core.py`           | Analysis   | ✅ Working (V7.3)                               |
| `discover_targets.py`     | Analysis   | ✅ Working                                      |
| `target_analyse.py`       | Analysis   | ✅ Working                                      |
| `target_matrix.py`        | Analysis   | ✅ Working                                      |
| `target_questions.py`     | Analysis   | ✅ Working                                      |
| `target_decide.py`        | Analysis   | ✅ Working                                      |
| `root_health.py`          | Analysis   | ✅ Working                                      |
| `root_questions.py`       | Analysis   | ✅ Working                                      |
| `root_decide.py`          | Analysis   | ✅ Working                                      |
| `stack_order.py`          | Analysis   | ✅ Working                                      |
| `decide.py`               | Analysis   | ✅ Working                                      |
| `revise_decision.py`      | Analysis   | ✅ Working                                      |
| `revoke_decision.py`      | Analysis   | ✅ Working                                      |
| `decision_history.py`     | Analysis   | ✅ Working                                      |
| `rework.py`               | Analysis   | ✅ Working                                      |
| `retarget_rework.py`      | Analysis   | ✅ Working                                      |
| `rebuild_plan.py`         | Analysis   | ⚠️ Stub (no projection)                         |
| `recommend.py`            | Analysis   | ✅ Working                                      |
| `execute_approved.py`     | Analysis   | ⚠️ Stub (no execution)                          |
| `query.py`                | Analysis   | ✅ Working                                      |
| `explain.py`              | Analysis   | ✅ Working                                      |
| `questions.py`            | Analysis   | ✅ Working                                      |
| `checklist.py`            | Analysis   | ✅ Working                                      |
| `validate_cache.py`       | Validation | ✅ Working                                      |
| `validate_targets.py`     | Validation | ✅ Working                                      |
| `validate_roots.py`       | Validation | ✅ Working                                      |
| `validate_stack_order.py` | Validation | ✅ Working                                      |
| `validate_plan.py`        | Validation | ✅ Working                                      |

### 10.2 Library Modules (15 files in `tools/lib/`)

| Module              | Purpose                             | Status                                       |
| :------------------ | :---------------------------------- | :------------------------------------------- |
| `config.py`         | Config loading with YAML support    | ✅ Working                                   |
| `io.py`             | JSON I/O, run directories           | ✅ Working                                   |
| `inventory.py`      | Git inventory collection            | ✅ Working                                   |
| `replay.py`         | Replay risk assessment              | ✅ Working                                   |
| `reports.py`        | Branch stacking report generation   | ⚠️ Hardcoded "defers to V7.3"                |
| `snapshot.py`       | V6.4 core analyser                  | ✅ Working                                   |
| `schemas.py`        | Dataclasses (PR, Edge, Audit, Node) | ✅ Working                                   |
| `git_utils.py`      | Git operations class                | ✅ Working (to be replaced by `git_core.py`) |
| `github_utils.py`   | GitHub PR fetching                  | ✅ Working                                   |
| `targets.py`        | Target discovery                    | ⚠️ Simple lookup, no scoring                 |
| `roots.py`          | Root health analysis                | ✅ Working                                   |
| `stack_ordering.py` | Stack order generation              | ✅ Working                                   |
| `relationships.py`  | Relationship graph builder          | ✅ Working                                   |
| `decisions.py`      | Decision log management             | ✅ Working                                   |
| `__init__.py`       | Package init                        | ✅ Working                                   |

### 10.3 Output Artifacts (30 files in `outputs/`)

All 19 V7.2 required outputs + 5 V7.4 run-scoped outputs + 6 legacy outputs = 30 total.
See `outputs/` directory listing for full inventory.

### 10.4 Contracts (11 files)

JSON schema contracts for: `analysis_summary`, `branch_stacking_report`, `decision_log`, `execution_plan`, `relationship_graph`, `replay_risk`, `repo_inventory`, `root_health`, `stack_order`, `target_candidates`, `target_matrix`, `target_questions`, `triage_packets`.

### 10.5 Test Coverage

| Test File                    | Tests                                           | Status     |
| :--------------------------- | :---------------------------------------------- | :--------- |
| `tests/test_v74_scaffold.py` | 4 tests (config, fixture risk, report, CLI run) | ✅ Passing |
| `tests/run_tests.py`         | Test runner                                     | ✅ Working |

V8 adds: `test_v8_dispatcher.py`, `test_v8_pipeline.py`, `test_v8_scoring.py`, `test_v8_projection.py`, `test_v8_execution.py`, `test_v8_staleness.py`.

---

## 11. Version Comparison Matrix

| Capability                      | V6.4 | V7.1 | V7.2 | V7.3 | V7.4 | **V8** |
| :------------------------------ | :--- | :--- | :--- | :--- | :--- | :----- |
| Git snapshot analysis           | ✅   | ✅   | ✅   | ✅   | ✅   | ✅     |
| PR metadata fetching            | ✅   | ✅   | ✅   | ✅   | ✅   | ✅     |
| Relationship graph              | ✅   | ✅   | ✅   | ✅   | ✅   | ✅     |
| Topology audit (cycles, Kahn)   | ✅   | ✅   | ✅   | ✅   | ✅   | ✅     |
| Branch classification           | ✅   | ✅   | ✅   | ✅   | ✅   | ✅     |
| Diagnostic commands (23)        | ❌   | ✅   | ✅   | ✅   | ✅   | ✅     |
| Target discovery                | ❌   | ❌   | ✅   | ✅   | ✅   | ✅+    |
| Target scoring algorithm        | ❌   | ❌   | ❌   | ❌   | ❌   | **✅** |
| Root health analysis            | ❌   | ❌   | ✅   | ✅   | ✅   | ✅     |
| Stack ordering                  | ❌   | ❌   | ✅   | ✅   | ✅   | ✅     |
| Decision tracking (append-only) | ❌   | ✅   | ✅   | ✅   | ✅   | ✅     |
| Replay risk detection           | ❌   | ❌   | ❌   | ❌   | ✅   | ✅     |
| Conflict marker detection       | ❌   | ❌   | ❌   | ❌   | ✅   | ✅     |
| Generated file risk             | ❌   | ❌   | ❌   | ❌   | ✅   | ✅     |
| Large commit risk               | ❌   | ❌   | ❌   | ❌   | ✅   | ✅     |
| Run-scoped outputs              | ❌   | ❌   | ❌   | ❌   | ✅   | ✅     |
| Config-driven thresholds        | ❌   | ❌   | ❌   | ❌   | ✅   | ✅+    |
| Unified dispatcher              | ❌   | ❌   | ❌   | ❌   | ❌   | **✅** |
| Unified pipeline                | ❌   | ❌   | ❌   | ❌   | ❌   | **✅** |
| State projection                | ❌   | ❌   | ❌   | ❌   | ❌   | **✅** |
| Real command plan               | ❌   | ❌   | ❌   | ❌   | ❌   | **✅** |
| Execution engine                | ❌   | ❌   | ❌   | ❌   | ❌   | **✅** |
| Staleness detection             | ❌   | ❌   | ❌   | ❌   | ❌   | **✅** |
| Patch equivalence               | ❌   | ❌   | ❌   | ❌   | ❌   | **✅** |
| Rebase recovery workflow        | ❌   | ❌   | ❌   | ❌   | ❌   | **✅** |

---

_End of V8 Progression Plan_
