# Executive Design Directive: Agent-Neutral Capability Graph

**If directing an implementation team, do not tell them:**
> "Port Gemini prompts to OpenCode/Letta/MCP."

**Instead, direct them toward:**
> "Extract capabilities into an agent-neutral capability graph and generate target-specific adapters."

That single decision prevents years of technical debt. By adhering to this directive, Gemini, OpenCode, Amp, Goose, Letta, CAMEL-AI, Qwen-based agents, Aider, and future terminal agents can coexist without requiring another large migration.

---

## Phase 1 — Freeze Existing Behavior
Create a baseline inventory of `commands/`, `prompts/`, `skills/`, `registry.py`, DSPy modules, optimizers, evaluators, and critics.

For every item, capture:
```yaml
name:
purpose:
inputs:
outputs:
dependencies:
interactive:
agentic:
recursive:
uses_dspy:
```
**Goal:** Create a *Capability Inventory*, not a Prompt Inventory.

---

## Phase 2 — Decompose Prompts
Prompts are data, not code. Every prompt must be decomposed into its canonical representation:
```text
Goal
Role
Workflow
Constraints
Style
Examples
Tools
Metrics
```

**Example:**
```yaml
goal: Investigate CLI alternatives
role: Principal Architect
workflow: [Research, Compare, Evaluate, Recommend]
constraints: [Preserve DSPy, Preserve MCP]
style: [Critical, Evidence Driven]
```
This becomes the canonical representation. Not TOML. Not Gemini. Not OpenCode.

---

## Phase 3 — Create Capability Graph
Build an interconnected graph, stored in a `capabilities/` directory:
```text
Capability
    ↓
Workflow
    ↓
Tool
    ↓
Metric
    ↓
Critic
```

---

## Phase 4 — Build Plugin Layer
Keep all target-specific logic strictly isolated. No target-specific logic should exist anywhere else.
```text
plugins/
├── mcp/
├── letta/
├── opencode/
├── amp/
├── goose/
├── camel/
├── qwen/
├── hermes/
└── aider/
```
**Rule:** The Registry knows capabilities. Plugins know agents.

---

## Phase 5 — DSPy Becomes Core Infrastructure
DSPy should not be treated as simple prompts. It is a core subsystem. Expose DSPy functionality through plugin adapters.

```text
dspy/
├── signatures/
├── modules/
├── optimizers/
├── metrics/
├── critics/
└── evaluators/
```
**Architecture:** `MCP Tool → DSPy Signature → DSPy Optimizer` (rather than `Prompt → Prompt`).

---

## Phase 6 — Mandatory Critic Layer
Require interception hooks to govern quality improvements:
```text
pre_task / post_task
pre_tool / post_tool
self_review
optimization
```
**Architecture:** `Request → Planner → Critic → Execution → Verification → Response`

---

## Phase 7 — MoA Ready
Design for parallel agents from day one, even if not implemented immediately. Do not design around a single-agent assumption.
```text
Planner
   │
   ├── Agent A
   ├── Agent B
   ├── Agent C
   │
Aggregator
   │
Verifier
```

---

## Phase 8 — Benchmark Driven Development
Every design decision must be measured against Top Tier benchmarks:
- Terminal-Bench, Terminal-Bench 2
- SWE-Bench
- AgentBench
- WebArena, GAIA, τ-bench

**Ask:** Does this feature improve Planning, Recovery, Tool use, Verification, or Memory? If not, reconsider prioritizing it.

---

## Specific Direction for OpenCode Recursive Prompts
Instead of hardcoding `Prompt A calls Prompt B calls Prompt C`, convert the logic to a workflow:
```text
Workflow
  ├── subtask
  ├── subtask
  └── subtask
```
Then, the plugins/exporters dynamically generate OpenCode task trees, Letta workflows, MCP tools, or CAMEL agents from the identical source definition.
