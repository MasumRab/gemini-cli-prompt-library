# Traceability Matrix

**Objective:** Map exactly how a single, agent-neutral Capability cascades through the DSPy subsystems, is exposed via Plugins, fulfills Agent Architectures, and satisfies top-tier Benchmarks. Any break in this chain represents an incomplete integration.

## The Traceability Chain

`Capability` → `DSPy Component` → `Skill/Tool Definition` → `Plugin Exporter` → `Agent Architecture` → `Benchmark Requirement`

---

## Example 1: Security Code Review

| Layer | Implementation Mapping | Description |
| :--- | :--- | :--- |
| **Capability** | `cap_code_review_security` | The foundational ontology (Goal, Role, Workflow). |
| **DSPy Component** | `signatures/security.py` | Defines `Input[code]` → `Output[vulnerabilities]`. |
| **Skill Definition** | `skills/security_analysis.py` | Atomic Python function wrapping the DSPy pipeline. |
| **Plugin Exporter** | `plugins/mcp/tool_exporter.py` | Translates the Skill into an MCP-compatible JSON-RPC tool. |
| **Agent Architecture**| **Goose / Claude Desktop (MCP)** | Agent invokes the tool natively, passing file context. |
| **Benchmark Req** | **SWE-bench** | Satisfies requirement for agent to verify security implications before submitting patches. |

---

## Example 2: Recursive Task Breakdown (opencode-subtask)

| Layer | Implementation Mapping | Description |
| :--- | :--- | :--- |
| **Capability** | `cap_recursive_planning` | Workflow definition for decomposing large tasks. |
| **DSPy Component** | `modules/recursive_planner.py` | DSPy module handling branching tree logic. |
| **Skill Definition** | `workflows/investigate.yaml` | The hierarchical definition of the subtasks. |
| **Plugin Exporter** | `plugins/letta/workflow_generator.py`| Translates the task tree into Letta Core Memory injections. |
| **Agent Architecture**| **Letta / MemGPT (Stateful)** | Agent consumes subtasks progressively from memory loop. |
| **Benchmark Req** | **WebArena / OSWorld** | Satisfies requirement for long-horizon task retention across many turns. |

---

## Example 3: Mixture of Agents (MoA) Orchestration

| Layer | Implementation Mapping | Description |
| :--- | :--- | :--- |
| **Capability** | `cap_moa_orchestration` | Multi-persona requirement (Planner, Predictor, Critic). |
| **DSPy Component** | `critics/adversarial_reviewer.py` | DSPy module configured for cross-examination. |
| **Skill Definition** | `skills/moa_coordinator.py` | Python logic managing parallel async calls. |
| **Plugin Exporter** | `plugins/camel/society.py` | Instantiates CAMEL-AI role-playing agents. |
| **Agent Architecture**| **CAMEL-AI (Agent Society)** | Autonomous interaction between Reviewer and Predictor agents. |
| **Benchmark Req** | **AgentBench** | Satisfies complex reasoning evaluations requiring multi-perspective verification. |

---

## Example 4: Bash Environment Manipulation

| Layer | Implementation Mapping | Description |
| :--- | :--- | :--- |
| **Capability** | `cap_headless_execution` | Requirement to run strictly without TTY interference. |
| **DSPy Component** | `evaluators/shell_metric.py` | Validates generated shell commands for safety. |
| **Skill Definition** | `skills/bash_executor.py` | Wraps execution with strict `--json` formatting. |
| **Plugin Exporter** | `plugins/opencode/manifest.py` | Generates `AGENTS.md` exposing the JSON CLI tool. |
| **Agent Architecture**| **Amp / OpenCode (Headless)** | Background process calling the CLI directly. |
| **Benchmark Req** | **TerminalBench / TerminalBench 2**| Satisfies strict non-interactive shell manipulation requirements. |

---

## Gap Enforcement
If any new feature or prompt cannot be mapped continuously from `Capability` down to a `Benchmark Requirement`, it is considered **Level 1/2** and must be re-architected to align with the core DSPy/Plugin infrastructure.
