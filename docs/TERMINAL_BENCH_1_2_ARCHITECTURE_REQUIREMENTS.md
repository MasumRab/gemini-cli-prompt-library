# Terminal-Bench 1 & 2 Architecture Requirements

**Objective:** Map specific Benchmark Requirements to Architecture Features to ensure the plugin layer is capable of scoring highly on SOTA evaluations.

## 1. TerminalBench 1 & 2 Implications
- **Requirement: Shell command robustness.** Agents must execute arbitrary bash safely.
  - *Architecture Feature:* `Tool Wrapper + Critic`. The `hooks.py` must sanitize input and the `critic.py` must pre-evaluate commands for destructive intent (`rm -rf`).
- **Requirement: Non-interactive terminal execution.**
  - *Architecture Feature:* `No TTY dependency`. `headless_cli.py` absolutely must override `InquirerPy` or `rich` prompts, forcing strict `--json` output.
- **Requirement: Timeout avoidance.**
  - *Architecture Feature:* `Async execution`. DSPy optimizers must run detached. The plugin must return a Job ID polling mechanism rather than blocking the TCP connection.

## 2. SWE-Bench Implications
- **Requirement: Long horizon task execution.**
  - *Architecture Feature:* `Planner + Memory`. The plugin (e.g., `letta/memory_mapper.py`) must store the initial GitHub issue in long-term memory, preventing context window exhaustion during long debug sessions.
- **Requirement: Hidden test recovery.**
  - *Architecture Feature:* `Verification Loop`. The `critic.py` must run `pytest` in a sandbox, capture failures, and trigger a DSPy Teleprompter retry autonomously before yielding back to the main agent.

## 3. AgentBench Implications
- **Requirement: Multi-environment reasoning.**
  - *Architecture Feature:* `CAMEL Society`. Isolates DB reasoning to a DB-Agent and Shell reasoning to a Shell-Agent, preventing context pollution.
