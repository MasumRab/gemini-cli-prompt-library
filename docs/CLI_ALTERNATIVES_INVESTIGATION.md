
## 7. Extensible Frameworks: Bridging the Gap (ohmyagent / ohmypi)

While Letta and Amp represent specific architectural paradigms (stateful vs. headless), ecosystem frameworks like **ohmyagent** or **ohmypi** (drawing inspiration from `ohmyzsh` for the terminal) offer a compelling hybrid approach. These tools act as generalized plugin managers and wrappers for AI agents, allowing capabilities to cross boundaries.

### How they bridge Gemini and non-Gemini behaviors:
1. **Plugin Ecosystem (The "ohmyzsh" model):**
   - Instead of rewriting our `.toml` prompts for every specific agent architecture, we can package `dspy_integration/framework/registry.py` as an `ohmyagent` plugin.
   - The framework handles the translation layer. If the user invokes it manually via terminal (Legacy Gemini style), the framework renders the rich TTY UI. If an autonomous agent (like Amp) invokes the framework, the plugin manager automatically suppresses the TTY and returns raw JSON or MCP standard tool formats.
2. **Unified State & Context Management:**
   - These frameworks often maintain a global configuration (similar to `~/.dspy_tuning/config.yaml`). They can seamlessly transition between a stateless slash command (`/testing:generate-unit-tests`) and injecting that same prompt into a stateful Letta agent's context window.
3. **Extended Capabilities:**
   - **Cross-Agent Chaining:** An `ohmyagent` workflow could use a headless agent (OpenCode) to scrape the workspace context, pass that context to our DSPy framework for optimization, and then pipe the result to a conversational agent for human review.
   - **Universal Tool Access:** By wrapping our prompts in this layer, we bypass the "Possible vs Impossible" hard limits. The framework acts as a hypervisor, exposing our prompts as CLI commands to humans, as MCP tools to Goose, and as native Python functions to Lettacode.

### Conclusion on Extensible Frameworks
Adopting or building toward an `ohmyagent/ohmypi` standard is the most robust path forward. It preserves the rapid, slash-command execution style of the Gemini CLI while simultaneously unlocking our prompt library for the next generation of headless and stateful autonomous agents.

---

## 8. Advanced Terminal Benchmarking & Highly Divergent SOTA Agents

To fully assess our prompt library's compatibility across the ecosystem, we must expand our evaluation beyond standard headless agents to include robust terminal benchmarking setups, Gemini fork targets, and highly divergent state-of-the-art (SOTA) coding agents.

### A. Terminal Benchmark Variants
Migrating away from TTY-locked CLI behavior unlocks the ability to test our prompts against major terminal benchmark environments:
1. **SWE-Bench (Software Engineering Benchmark):**
   - *Architecture:* Provisions a sandboxed Docker container with a specific GitHub issue and target repository. The agent must resolve the issue autonomously using terminal commands.
   - *Integration:* By flattening our `CommandRegistry` into MCP tools or headless commands, our DSPy optimization prompts (e.g., `/workflows:smart-refactor`) can be evaluated directly on SWE-Bench metrics.
2. **WebArena / OSWorld (Multi-Turn State Evals):**
   - *Architecture:* Evaluates agents on complex, multi-step tasks requiring interaction with web and OS interfaces over long horizons.
   - *Integration:* Legacy Gemini CLI was fundamentally incapable of this due to single-turn stateless dispatch. Stateful agents (Letta) executing our restructured prompts can now be evaluated on their ability to retain context across 50+ turns.
3. **Local Execution Jails (Sandbox Evals):**
   - *Architecture:* Systems like `Aider` or `OpenDevin` run in tightly controlled local sandboxes to prevent destructive terminal commands.
   - *Integration:* Our prompts must be restructured to explicitly define safe vs. unsafe execution boundaries if deployed via these agents.

### B. Gemini Fork Targets (Qwen, llxprt)
Several projects aim to directly replicate or expand upon the legacy Gemini CLI experience while utilizing different underlying models.
1. **Qwen (CLI variants):**
   - As noted in `docs/SESSION_ANALYSIS.md`, Qwen is an active target. Qwen CLI variants often maintain a similar terminal-first approach but introduce different token limits and reasoning constraints.
   - *Transferability:* High. Since the interaction model (slash commands in a terminal) remains largely the same, our TOML prompts and text-processing pipelines can port over with minimal structural changes, provided the specific `Provider` (e.g., `dspy_integration/framework/providers/qwen.py`) is optimized for Qwen's specific prompt templates.
2. **llxprt (and similar TUI/CLI forks):**
   - These tools attempt to wrap LLM capabilities in advanced Terminal User Interfaces (TUIs).
   - *Transferability:* Medium-High. While they preserve the terminal environment, they often expect prompts to be formatted for their specific semantic routing or syntax highlighting engines. We can transfer our fundamental goals, but the UI rendering logic in our legacy CLI (`rich`, `InquirerPy`) will likely conflict with their native TUI rendering.

### C. Highly Divergent SOTA Terminal Agents (OpenDevin, Aider, Sweep)
These represent the bleeding edge of AI coding and operate entirely differently from standard slash commands.

1. **Aider (Pair Programming CLI):**
   - *Architecture:* Aider tracks git history, reads the AST of the codebase, and maintains a continuous chat session *in the terminal* while directly applying diffs to files.
   - *Transferability (Impossible 1:1):* Aider does not use static `/command` dispatch. To inject our DSPy prompts into Aider, we would need to pass them as "Architectural Guidelines" or `.aider.conf.yml` conventions, rather than executing them as discrete tasks.
2. **OpenDevin / Devin-clones:**
   - *Architecture:* Full autonomous workspace agents with access to a browser, terminal, and editor. They plan and execute multi-step workflows.
   - *Transferability:* Our atomic commands (e.g., `/testing:generate-unit-tests`) must be converted into **Tools/Skills** that OpenDevin can call when its internal planner decides testing is necessary. We cannot force OpenDevin to run a specific workflow sequentially via the CLI; we can only equip it with the best prompt strategies for when it decides to do so.
3. **Sweep (GitHub App / Agent):**
   - *Architecture:* Operates entirely asynchronously via GitHub Issues and Pull Requests. No local terminal is involved.
   - *Transferability:* Requires full inversion of control. Our prompt library would need to be hosted as a backend service or GitHub Action that Sweep queries when drafting its PRs, entirely bypassing local CLI execution.

### Conclusion on Benchmarks and SOTA Agents
The ecosystem is rapidly bifurcating into two distinct paths:
1. **The Interactive Terminal (Qwen, ohmyagent, Legacy Gemini):** Where human-in-the-loop `/slash` commands and TUIs dominate.
2. **The Autonomous Sandbox (OpenDevin, Aider, SWE-Bench):** Where headless execution, MCP toolkits, and dynamic planning replace static command execution.

To survive this bifurcation, our prompt infrastructure *must* abstract the core instruction (the DSPy logic) away from the execution mechanism (the terminal). By standardizing our library into MCP-compatible schemas, we can satisfy both the interactive CLI tools (via `ohmyagent` plugins) and the highly divergent SOTA agents (via tool integrations) while enabling rigorous SWE-Bench evaluations.

---

## 9. Plugin Infrastructure Specifications for Divergent Targets

To bridge the gap between our legacy `.toml` command registry and the highly divergent targets, we must map out the exact plugin infrastructure and schema requirements for the major agentic platforms. This mapping dictates how our `dspy_integration` framework must expose its capabilities.

### A. Letta (Stateful, Tiered-Memory)
Letta agents expand capabilities via native Python functions injected into their event loop.
- **Plugin Format:** Python functions with strict docstrings (used for LLM instruction) and type hints.
- **Infrastructure Requirement:** We must build a compiler (`scripts/compile_to_letta.py`) that reads a `.toml` command and generates a Letta Tool.
- **Example Schema:**
  ```python
  def generate_unit_tests(target_file: str) -> str:
      """
      Executes the DSPy enhanced unit test generation prompt on a given file.
      Args:
          target_file: The path to the file to test.
      """
      # Internally calls our dspy_integration framework
      return run_dspy_pipeline("/testing:generate-unit-tests", target_file)
  ```

### B. Amp / OpenCode (Headless Workspace Agents)
These agents typically rely on local configuration files (like `AGENTS.md` or `.amp.yaml`) to discover workspace-specific tools, often executing them via standard shell commands but expecting JSON stdout.
- **Plugin Format:** Shell command definitions exposed in a project manifest, accompanied by strict instructions not to block on TTY.
- **Infrastructure Requirement:**
  1. A `dspy-helm plugin generate-opencode` command that appends our command list to the repository's `AGENTS.md`.
  2. Aggressive enforcement of the `--json` output flag within `cli.py`.
- **Example Schema (`.amp.yaml` or `AGENTS.md` snippet):**
  ```yaml
  tools:
    - name: dspy_unit_test
      description: "Generates DSPy unit tests for a file"
      command: "python -m dspy_integration.cli --json /testing:generate-unit-tests {file}"
  ```

### C. Hermes / Function Calling Models (OpenRouter / Native API)
Models like Hermes 2 Pro are explicitly trained on JSON Schema tool calling. They do not run local shells; they expect tools to be provided in the OpenAI tool format during the API request.
- **Plugin Format:** JSON Schema (OpenAI format).
- **Infrastructure Requirement:** Our `CommandRegistry` must feature an `export_to_openai_schema()` method.
- **Example Schema:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "dspy_unit_test",
      "description": "Generates DSPy unit tests for a file",
      "parameters": {
        "type": "object",
        "properties": {
          "target_file": {
            "type": "string",
            "description": "The file path to analyze"
          }
        },
        "required": ["target_file"]
      }
    }
  }
  ```

### D. Model Context Protocol (MCP) (Goose, Claude Desktop)
MCP is the emerging standard for connecting AI agents to local context and tools. Goose and Claude use this heavily.
- **Plugin Format:** An active local MCP Server (Node or Python) that advertises tools via JSON-RPC.
- **Infrastructure Requirement:** We need a standalone MCP server (`dspy_integration/mcp_server.py`) using the `mcp` Python SDK. The server wraps our `CommandRegistry` and responds to `tools/list` and `tools/call` RPC requests.
- **Example Schema (MCP Tool Object):**
  ```json
  {
    "name": "dspy_prompt_library",
    "description": "Access the DSPy prompt engineering library",
    "inputSchema": {
      "type": "object",
      "properties": {
        "command": {
          "type": "string",
          "enum": ["/testing:generate-unit-tests", "/code-review:security"]
        },
        "arguments": { "type": "string" }
      },
      "required": ["command", "arguments"]
    }
  }
  ```

### E. Pi / ohmypi (Ecosystem Wrappers)
Wrappers expect a standardized manifest to import plugins globally across the user's system, not just a single workspace.
- **Plugin Format:** A centralized manifest (e.g., `manifest.json`) distributed via pip or npm.
- **Infrastructure Requirement:** A build step that packages our `.toml` files into a globally discoverable `ohmypi` registry format.

### Summary of Infrastructure Needs
To support all divergent targets, the `dspy_integration` framework must implement a **Polyglot Exporter**. Instead of just parsing `.toml` files for local CLI use, the framework must be able to export those definitions into:
1. Letta Python Tool definitions.
2. OpenCode/Amp Shell Manifests.
3. Hermes/OpenAI JSON Schemas.
4. An active Model Context Protocol (MCP) server.

---

## 10. DSPy Feature Mapping to Plugin Infrastructure

A critical requirement of this migration is preserving the advanced capabilities of the DSPy framework (Signatures, Optimizers, Modules) when exposing them to highly divergent agent targets. We cannot merely pass static text strings; we must map DSPy's programmable pipelines into the plugin schemas.

### A. DSPy Signatures -> Target Schemas
DSPy `Signatures` (`InputField`, `OutputField`) define the strict typing and expected structure of a prompt.
- **Hermes / OpenAI Schema Mapping:** A DSPy Signature translates 1:1 to an OpenAI function calling schema. `InputFields` become the `properties` required by the function, and `OutputFields` dictate the expected JSON schema response.
- **MCP Server Mapping:** The MCP `inputSchema` for a tool can be dynamically generated by inspecting the `__annotations__` and fields of a loaded DSPy Signature class.

### B. DSPy Optimizers (Teleprompters) -> Stateful Execution
DSPy optimizers (like `BootstrapFewShot` or `MIPROv2`) require multiple LLM calls, dataset parsing, and feedback loops.
- **Letta (Stateful) Mapping:** Letta is uniquely suited for this. We map a DSPy Optimizer as a long-running Letta Task (via a Python block). Letta can pause execution, store intermediate optimizer traces in its Archival Memory, and resume the optimization pipeline over multiple event loops without blocking.
- **Headless CLI (Amp/OpenCode) Mapping:** Because Amp expects synchronous tool execution, long-running DSPy optimization must be handled as background jobs. The CLI plugin must execute the optimizer (e.g., `python -m dspy_integration.optimize --detach`), returning a Job ID to Amp. Amp can then poll the tool for the compiled DSPy module once optimization is complete.

### C. DSPy Metrics -> Agent Context Validation
DSPy relies on metric functions (e.g., "does this code compile?", "is this secure?") to score prompt generations.
- **Goose / OpenDevin Mapping:** SOTA autonomous agents have native capabilities to run tests (e.g., executing `pytest` in a sandbox). We can map DSPy's internal metric evaluation to the agent's native sandbox tools. Instead of DSPy executing the code internally, the MCP tool returns a "proposed solution," and delegates the actual metric validation to the target agent's sandboxed terminal.

### D. Dynamically Compiled Modules
When DSPy finishes optimization, it produces a compiled program (with tailored few-shot examples and tuned instructions).
- **Extensible Frameworks (ohmyagent) Mapping:** The `ohmypi` plugin infrastructure can dynamically register newly compiled DSPy modules as *newly available tools* in the global registry. If an agent runs an optimizer tool, the framework updates its own manifest to expose the newly optimized module as a dedicated command (e.g., `/custom:optimized-unit-tester`) for future calls.

### Summary of DSPy Mapping Strategy
To retain the power of DSPy:
1. Extract schemas dynamically from `dspy.Signature` classes rather than writing manual JSON schemas.
2. Delegate metric validation to the target agent's sandbox when possible (MCP/Goose).
3. Handle heavy optimizers via async polling in headless environments (Amp) or native memory states in tiered agents (Letta).

---

## 11. Critic Module & Interception Hooks Strategy

When executing DSPy capabilities via rigid external agents, there is a risk of silent failures or suboptimal output if the target agent lacks the nuance to self-correct. To manage this across divergent architectures, we must implement an internal **Critic Module** supported by **Execution Hooks**.

### The Need for a Critic Module
Legacy Gemini CLI users could manually intervene if a prompt generated poor output. In a headless (Amp) or stateless tool-calling (Hermes) environment, this human-in-the-loop validation is gone. A "Critic" module acts as an automated judge that:
1. Evaluates the LLM output against the initial DSPy Signature constraints.
2. Determines if the output is acceptable, or if a DSPy Optimizer (Teleprompter) must be triggered to tune the prompt before returning the final result to the agent.

### Architecture of the Interception Hooks
To seamlessly integrate the Critic without altering the target agent's code, our `CommandRegistry` (or the MCP/ohmypi wrapper) must implement an event-driven hook system:

1. **`pre_invoke(command, context)`:**
   - *Action:* Intercepts the raw tool call from the agent (e.g., Goose requesting `/testing:generate-unit-tests`).
   - *Role:* Injects workspace context or determines if a previously optimized (compiled) DSPy module already exists for this task.
2. **`post_invoke(response, metric_fn)` -> Critic Evaluation:**
   - *Action:* Captures the raw output from the underlying LLM provider before it is returned to the calling agent.
   - *Role:* The Critic evaluates the `response`. If the metric score falls below a threshold (e.g., `< 0.8`), it raises an `OptimizationRequired` event.
3. **`on_optimization_required(dataset)`:**
   - *Action:* Halts the return payload to the agent.
   - *Role:* Silently spins up a DSPy Teleprompter (e.g., `BootstrapFewShot`), optimizes the prompt, re-runs the inference, and then returns the improved output to the calling agent.

### Mapping Hooks to Plugin Infrastructure
- **MCP (Goose/Claude):** Hooks act as middleware inside the MCP Server. A standard tool call might take longer (due to silent optimization loops), so the MCP server must support asynchronous progress updates to prevent agent timeout.
- **Letta (Stateful):** Letta's native event-driven architecture handles this elegantly. Our hooks can emit Letta system events (e.g., `SystemEvent.CRITIC_FAILED`), prompting the Letta agent to autonomously switch from "execution mode" to "optimization mode" and retrieve additional training data from its Archival Memory.
- **Amp/OpenCode (Headless):** Because shell commands are synchronous and prone to timeout, the Critic hook must immediately exit with a specific JSON payload (e.g., `{"status": "needs_optimization", "job_id": 123}`). The Amp agent's `AGENTS.md` instructions must be updated to understand this payload and poll the background optimization job.

### Conclusion on Critic Interception
By implementing a standard hook-based Critic module, our DSPy integration becomes **self-healing**. It abstracts the complexity of prompt optimization away from the target agents (Amp, Goose, Hermes), allowing them to consume high-quality outputs as simple tools, while our internal hooks handle the rigorous DSPy metric evaluations and tuning loops securely in the background.

---

## 12. Mixture-of-Agents (MoA) & Parallel Orchestration

Moving beyond single-agent architectures (like the legacy Gemini CLI) opens the door to State-of-the-Art (SOTA) **Mixture-of-Agents (MoA)** and parallel orchestration frameworks. Rather than relying on a single prompt or a single monolithic agent to execute a task, evaluate it, and correct it, MoA distributes these responsibilities across a swarm of specialized, parallel agents.

### The Swarm Architecture
In an MoA setup, our `dspy_integration` framework does not just feed a prompt to an execution engine. Instead, it acts as the orchestrator for three distinct agentic roles running in parallel:

1. **The Prediction / Execution Agent:**
   - *Role:* Takes the initial user query and the DSPy Signature, and predicts the best possible implementation or answer.
   - *Behavior:* It runs fast, often utilizing a smaller, highly optimized model (e.g., Llama-3-8B).
2. **The Review Agent:**
   - *Role:* Receives the output from the Prediction Agent asynchronously. It acts as a static analyzer, checking for logical flaws, security vulnerabilities, or schema violations.
   - *Behavior:* It uses a distinct prompt (e.g., our `/code-review:security` or `/code-review:best-practices` TOML commands) to specifically target weaknesses in the prediction.
3. **The Evaluation (Critic) Agent:**
   - *Role:* Executes the code or validates the output in a sandboxed terminal environment. It runs the DSPy Metric functions.
   - *Behavior:* If the metric fails, it synthesizes the feedback from the Review Agent and the execution trace, passing a highly detailed failure report back to the orchestrator to trigger a DSPy Teleprompter optimization loop.

### Integration with Target Platforms
- **Goose / OpenDevin:** These SOTA targets increasingly support sub-agent spawning. An MCP tool call to our framework (e.g., `run_dspy_pipeline`) can internally fan out to multiple API calls, gathering parallel predictions from Groq, Gemini, and Claude simultaneously, using a final LLM to synthesize the best response (classic MoA routing).
- **Extensible Frameworks (ohmypi/ohmyagent):** These plugins can natively define multi-agent workflows. A single `/workflows:smart-refactor` command from the user will trigger the ohmypi orchestrator to spawn the Execution, Review, and Evaluation agents in the background, only returning control to the CLI once consensus is reached.

### Advantages over Legacy Gemini CLI
- **Latency Masking:** Instead of waiting for a massive chain-of-thought to finish sequentially, parallel prediction and review agents operate simultaneously, drastically reducing the time-to-first-token of the final optimized output.
- **Hallucination Mitigation:** By forcing a dedicated Review Agent to actively try to break the Prediction Agent's output (an adversarial setup), the resulting DSPy optimization data is significantly higher quality.
- **Model Diversity:** An MoA setup allows us to use cheap, fast models for initial predictions (Groq/Llama) and heavy, expensive models (Gemini 1.5 Pro / Claude 3.5 Sonnet) exclusively for the final evaluation synthesis.

By designing our plugin infrastructure (via MCP and Hooks) to support asynchronous, parallel swarm execution, we future-proof the prompt library against the rapidly evolving landscape of multi-agent coding systems.

---

## 13. Target-to-Architecture Mapping & Codebase Integration

To implement these varied plugin infrastructures without breaking our legacy Gemini CLI compatibility, we must map specific targets to specific plugin outputs and structure the codebase cleanly.

### Target to Plugin Architecture Mapping

| Target Agent | Required Plugin Architecture | Primary Mechanism |
| :--- | :--- | :--- |
| **Goose, Claude Code, Cline** | **MCP (Model Context Protocol)** | Active local JSON-RPC server wrapping `CommandRegistry`. |
| **Letta, Lettacode** | **Python Function Blocks** | Compiled Python files with strict docstrings and type hints. |
| **OpenCode, Amp** | **Headless Shell Manifests** | `AGENTS.md` / `.amp.yaml` generation pointing to `--json` CLI args. |
| **Hermes, OpenRouter Native** | **OpenAI JSON Schema** | Static JSON export of DSPy Signatures. |
| **Pi / ohmyagent** | **Unified Plugin Manifest** | Global `manifest.json` for ecosystem discovery. |
| **Aider, Sweep, OpenDevin** | **MCP + System Context** | Cannot use CLI. Must consume via MCP tools or global `.aider.conf` injection. |

### Coexistence in the Current Codebase

To ensure these new plugin interfaces exist peacefully alongside the current codebase (`dspy_integration`), we will implement a "Hub and Spoke" integration model. The core `CommandRegistry` and `.toml` prompts remain the single source of truth (the Hub), while the plugin exporters (the Spokes) live in a new dedicated directory.

#### Proposed Directory Structure

```text
dspy_integration/
├── framework/
│   ├── registry.py        # (Existing) The Hub: parses .toml
│   ├── dispatcher.py      # (Existing)
│   └── plugins/           # (NEW) The Spokes: Exporter modules
│       ├── __init__.py
│       ├── mcp_server.py  # Runs the active MCP server for Goose/Claude
│       ├── to_letta.py    # Compiles .toml to Python blocks
│       ├── to_schema.py   # Exports to OpenAI JSON Schema
│       └── to_amp.py      # Generates headless shell manifests
├── cli.py                 # (Existing) Legacy interactive CLI
└── optimize.py            # (Existing) Background async optimizations
```

#### Integration Rules (Avoiding Regression)
1. **No Mutations to Core Registry:** The `plugins/` modules must act strictly as *consumers* of the `CommandRegistry`. They read the `.toml` configurations and translate them. They do not alter the way `registry.py` functions for the legacy CLI.
2. **Opt-In Execution:** The MCP server (`mcp_server.py`) will not run by default. It will be launched via a dedicated command (e.g., `python -m dspy_integration.plugins.mcp_server`) or defined in a Goose extension config, ensuring zero overhead for legacy CLI users.
3. **Headless Safety Checks:** The legacy `cli.py` must aggressively import and utilize the `is_agentic()` checks from `docs/AGENTIC_COMPATIBILITY.md` to ensure that if an agent *does* attempt to run the CLI directly (Amp/OpenCode), it automatically shifts into headless JSON mode without hanging.

By isolating the translation layer into `dspy_integration/framework/plugins/`, we preserve the rapid prototyping capability of the Gemini-style CLI while fully unlocking the library for SOTA autonomous agents via MCP and Letta function blocks.

---

## 14. Prompt Mapping: Missing Prompts & Recursive Templates

While the Command Registry currently maps many DSPy testing and code-review capabilities, a critical missing piece identified in previous `opencode-subtask` workflows is the **Recursive Prompt Template Construction**.

### The Missing "opencode-subtask" Mapping
Earlier agentic workflows (like OpenCode) attempted to break down massive tasks using a subtask delegation loop. A single prompt could not encompass large feature development.
- **The Concept:** A parent prompt (`opencode-task`) generates child prompts (`opencode-subtask`), which in turn execute recursively until the task is complete.
- **The Missing Link:** The current `.toml` structure is rigid and flat. It interpolates `{{args}}` but does not support yielding or spawning child `.toml` executions dynamically from within a prompt.

### Implementing Recursive Templates for Divergent Targets
To fix this missing prompt architecture, we must introduce a **Recursive Delegation Schema**:

1. **For MCP / Goose Targets:**
   - The `/architecture:design-subtasks` prompt must be mapped. When invoked, its DSPy OutputField should require a JSON array of specific *new MCP tool calls*.
   - This allows Goose to call the parent prompt, receive the sub-task JSON, and autonomously loop through calling the child prompts.
2. **For Letta (Stateful) Targets:**
   - We map the recursive template to a Letta Core Block update. The parent prompt updates Letta's Persona with the subtasks. As Letta completes each subtask, it pops it from memory, naturally executing a recursive loop without external orchestration.
3. **For Amp / OpenCode (Headless CLI):**
   - We must introduce a new command, `/workflows:recursive-opencode-subtask`.
   - The hook infrastructure (described in Section 11) intercepts the output. Instead of returning text to Amp, the hook parses the subtasks, generates temporary `AGENTS.md` sub-instructions, and executes nested CLI calls autonomously.

By adding recursive template support to the plugin exporters, we bridge the gap between static Gemini slash commands and the dynamic planning required by SOTA coding agents.

---

## 15. Top Terminal Benchmarks (Tier 1 & 2): Architecture and Design Evaluation

To validate our prompt infrastructure against the highest standards of autonomous coding, we must evaluate its design against Tier 1 and Tier 2 terminal benchmarks.

### Tier 1 Benchmarks (SWE-bench & WebArena)
These represent the gold standard for agentic capability, requiring deep reasoning, multi-file context, and autonomous terminal execution.
- **SWE-bench (Software Engineering):** Agents must resolve real-world GitHub issues.
  - *Architecture Implication:* Our prompts cannot be single-turn scripts. They must be modular. The `opencode-subtask` recursive structure is mandatory here. The target agent (e.g., OpenDevin running our MCP tools) will use our `/architecture:system-design` prompt to plan, and then our `/testing:generate-unit-tests` prompt to verify its own patches before submitting them to SWE-bench.
- **WebArena / OSWorld:** Evaluates long-horizon tasks across OS environments.
  - *Architecture Implication:* Tests the statefulness of our agents. The Letta (MemGPT) tiered-memory mapping is critical here, allowing the agent to remember instructions from `/prompts:best-practices` across 100+ terminal interactions.

### Tier 2 Benchmarks (TerminalBench & AgentBench)
These benchmarks focus heavily on specific tool use, bash scripting, and constrained execution environments.
- **TerminalBench:** Focuses on bash proficiency and environment manipulation.
  - *Architecture Implication:* Emphasizes the need for headless execution (OpenCode/Amp schema). If our prompts try to render `rich` TUI progress bars, the TerminalBench regex evaluators will fail. Strict `--json` output enforcement is required.
- **AgentBench (LLM-as-Agent):** Evaluates reasoning across diverse environments (DB, Web, Shell).
  - *Architecture Implication:* Validates our "Mixture-of-Agents" (MoA) orchestration. A monolithic agent often fails AgentBench due to context pollution. By routing the prompt generation through an isolated Execution Agent and scoring it via a Sandboxed Critic Agent (Section 11), we maximize AgentBench scores.

---

## 16. Architecture Design Mocks & Skill Analysis

To visualize the integration, 5 architecture mocks have been created in `docs/mocks/`:
1. `01_letta_stateful_mock.py`: Python function blocks for Letta's memory tier.
2. `02_mcp_goose_mock.py`: A `FastMCP` server for Goose/Claude.
3. `03_amp_headless_mock.yaml`: A shell manifest enforcing `--json` for Amp.
4. `04_hermes_openai_schema_mock.json`: Native JSON schema for Hermes API calling.
5. `05_moa_orchestrator_mock.py`: Parallel swarm orchestration for MoA environments.

### Skill vs. Complex Pipeline Analysis
Not all prompts are created equal. When exposing them to divergent targets, we must classify them:
- **Simple Skills (Atomic Functions):**
  - *Examples:* `/prompts:list`, `/learning:explain-concept`.
  - *Implementation:* These can be executed synchronously. They require zero DSPy optimization and return immediately. In MCP, they are standard tools. In Amp, they are basic shell scripts.
- **Complex Pipelines (DSPy Optimizations):**
  - *Examples:* `/testing:generate-unit-tests`, `/code-review:security`, recursive `opencode-subtask`.
  - *Implementation:* These require the **Critic Hooks** and **MoA Swarm** logic. Because they may spin up a DSPy Teleprompter (which takes time and multiple LLM calls), they must be implemented asynchronously in Letta/MCP, or via detached job-polling in headless shell agents.

---
