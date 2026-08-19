# Skill Extraction Matrix

**Objective:** Classify legacy Gemini `.toml` prompts to determine their execution complexity. Not all prompts require DSPy optimization or Agent Societies. Many can be extracted as simple, atomic skills.

| Prompt / Capability ID | Classification | Justification | Target Plugins (Best Fit) | Impossible Targets | Required Hooks |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `list-commands` | **Simple Skill** | No LLM required. Just a directory read and JSON return. | All Targets | None | `None` |
| `explain-concept` | **Simple Skill** | Single-turn, stateless LLM call. No optimization needed. | All Targets | None | `failure_recovery` |
| `smart-refactor` | **Workflow** | Requires reading files, generating diffs, and applying changes sequentially. | Letta, OpenCode, Goose | Hermes (Raw) | `pre_execute` |
| `opencode-subtask` | **Recursive Workflow** | Must spawn child tasks dynamically based on parent output. | OpenCode, CAMEL, Goose | Amp (Strict) | `recursion_manager` |
| `generate-unit-tests` | **DSPy Module** | Requires `Signature` constraints and `MIPROv2` optimization loops if tests fail. | MCP, Letta | OpenCode (Sync) | `critic`, `retry` |
| `security-review` | **Agent Society** | Best evaluated via adversarial Predictor vs Reviewer setup. | CAMEL, MoA | Hermes, Pi | `consensus_engine` |
| `benchmark-eval` | **Benchmark Task** | Must adhere to strict `TerminalBench` environment constraints (no TTY). | OpenCode, MCP | Legacy Gemini | `benchmark_adapter` |

---
