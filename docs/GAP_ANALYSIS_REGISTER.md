# Gap Analysis Register

**Date:** 2026-01-18
**Objective:** Halt premature completion of investigation steps and establish a rigorous baseline for architectural completeness (Level 1-5).

## 1. Investigation Status

### Fully Investigated (Level 1-2: Basic Mapping)
- **Legacy Baseline:** Understanding of `CommandRegistry` and TOML prompts.
- **Headless Execution:** Awareness of TTY failure modes (`InquirerPy` vs `--json`).
- **Basic Target Mapping:** General awareness of Letta, Goose (MCP), and Amp requirements.

### Partially Investigated (Level 3-4: DSPy & Basic Hooks)
- **DSPy Integration:** Conceptual mapping of Signatures/Optimizers to targets.
- **Critic Architecture:** Conceptual understanding of pre/post hooks.
- **Mixture-of-Agents (MoA):** High-level orchestrator concept (Prediction/Review/Evaluation).
- **Benchmark Driven Requirements:** Awareness of SWE-Bench/TerminalBench importance.
- **Recursive Prompting:** Awareness of the `opencode-subtask` gap.

### Not Investigated / Missing (Level 5: Comprehensive Architecture)
- **Capability Ontology:** No formal data model isolating Goal, Role, Workflow, Constraints, etc., from the execution medium.
- **Traceability Matrix:** No formal mapping linking a generic capability down to a specific benchmark requirement across all agent targets.
- **CAMEL Society Design:** Completely unmodeled.
- **Strict Failure Recovery:** No definitions for timeout, hallucination, invalid tool, or recursion limit handling.
- **Hook Lifecycle Specification:** Missing concrete data flow definitions for hooks.
- **Comprehensive Reference Implementations (Mocks):** Previous mocks lacked lifecycle, data flow, failure handling, and migration paths.

---

## 2. Completeness Levels Definition

To prevent false "Completed" signals, components must be evaluated against this scale:

- **Level 1 (Basic Support):** The tool can technically interface with the target (e.g., outputs JSON).
- **Level 2 (Plugin Support):** The tool exposes a specific target plugin (e.g., MCP server wrapper).
- **Level 3 (DSPy Integration):** The plugin successfully proxies DSPy signatures, metrics, and optimization pipelines.
- **Level 4 (Critic Hooks):** The integration includes active interception, self-review, and on-the-fly optimization before returning to the agent.
- **Level 5 (SOTA Architecture):** The implementation supports MCP, DSPy, Critics, MoA orchestration, Recursive workflows, strict Failure Recovery, and is driven entirely by an Agent-Neutral Capability Graph evaluated against Top Tier Benchmarks (SWE-Bench, TerminalBench 2).

*Currently, the codebase sits between Level 1 and Level 2. The investigation aims to architect the leap to Level 5.*
