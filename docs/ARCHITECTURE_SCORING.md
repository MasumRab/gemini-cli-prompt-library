# Architecture Scoring & Evaluation

To determine the definitive primary architecture for the migration from Gemini CLI, we evaluate the 6 Reference Implementations against a weighted criteria matrix.

## Criteria & Weighting

| Criteria | Weight | Description |
| :--- | :--- | :--- |
| **MCP Compatibility** | High (3) | Universal standard for Goose, Claude, OpenDevin. |
| **DSPy Compatibility** | High (3) | Native support for Signatures, Teleprompters, Metrics. |
| **MoA / CAMEL Support**| High (3) | Supports distributed swarms and parallel execution. |
| **Terminal Bench Perf**| High (3) | Strict adherence to JSON/Headless rules (zero TTY). |
| **Recursive Workflows**| High (3) | Dynamic unrolling of task trees (opencode-subtask). |
| **Memory Support** | Medium (2)| Integration with long-term memory (Letta/Archival). |
| **Future Adaptability**| High (3) | Ability to absorb unknown future SOTA agents. |

---

## Scoring Matrix (1-5 Scale)

| Architecture | MCP (3) | DSPy (3) | MoA (3) | TerminalBench (3) | Recursion (3) | Memory (2) | Future (3) | **Total Score** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Letta (Stateful)** | 2 (6) | 5 (15) | 2 (6) | 3 (9) | 5 (15) | 5 (10) | 4 (12) | **73 / 100** |
| **2. MCP Server** | 5 (15) | 5 (15) | 4 (12) | 5 (15) | 4 (12) | 4 (8) | 5 (15) | **92 / 100** |
| **3. OpenCode/Amp** | 1 (3) | 3 (9) | 1 (3) | 5 (15) | 5 (15) | 1 (2) | 2 (6) | **53 / 100** |
| **4. Hermes (Schema)**| 1 (3) | 4 (12) | 1 (3) | 1 (3) | 1 (3) | 1 (2) | 2 (6) | **32 / 100** |
| **5. MoA Orchestrator**| 3 (9) | 5 (15) | 5 (15) | 3 (9) | 4 (12) | 3 (6) | 4 (12) | **78 / 100** |
| **6. CAMEL Society** | 3 (9) | 5 (15) | 5 (15) | 3 (9) | 4 (12) | 4 (8) | 4 (12) | **80 / 100** |

---

## Winner: The MCP Server + Capability Ontology Core

The **MCP Server Architecture (Score: 92)** definitively wins.

However, it only wins because it acts as a *Transport Layer* for the **Agent-Neutral Capability Ontology**.
- It naturally supports **DSPy** execution behind the `mcp.tool()` wrapper.
- It easily delegates complex reasoning to the **CAMEL Society (MoA)** internally.
- It completely resolves the **TerminalBench** TTY issue by operating exclusively via JSON-RPC.
- By exposing `Capabilities` rather than `Prompts`, it allows Goose or Claude to unroll **Recursive Workflows** dynamically.

### Strategic Conclusion
Do not build 6 different architectures. Build **Phase 3 (Capability Graph)** and expose it primarily through the **MCP Plugin Layer**, utilizing **DSPy + Critic Hooks** internally. This composite approach secures the highest possible evaluation score and future-proofs the library against any SOTA shifts.
