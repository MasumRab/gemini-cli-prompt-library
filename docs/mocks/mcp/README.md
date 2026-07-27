# Reference Implementation: MCP Server (Goose / Claude)

## 1. Folder Structure
```text
plugins/mcp/
├── __init__.py
├── server.py               # Active FastMCP server process
├── registry_adapter.py     # Bridges Capability Ontology to MCP standard
├── tool_exporter.py        # Translates Skills into JSON-RPC Tools
├── memory_adapter.py       # Exposes MCP Context/Resources
├── hooks_middleware.py     # Injects Pre/Post Critic logic
└── benchmark_adapter.py    # Ensures SWE-bench output formatting
```

## 2. Runtime Lifecycle
```text
Request (Goose)
 ↓
server.py (JSON-RPC listener)
 ↓
registry_adapter.py (Looks up Capability)
 ↓
hooks_middleware.py (pre_task)
 ↓
DSPy Signature / Execution
 ↓
hooks_middleware.py (post_task & Critic evaluation)
 ↓
Response (Returned to Goose via JSON-RPC)
```

## 3. Data Model
Consumes `CAPABILITY_ONTOLOGY.md`. `Goal`, `Role`, and `Tools` map to `mcp.tool()`.

## 4. Plugin Model
Operates as an active daemon (`python -m dspy_integration.plugins.mcp.server`). Goose connects to it over stdio or SSE.

## 5. Hook Model
Hooks intercept execution at the `mcp.tool()` wrapper level. If `self_review` fails, the hook triggers a DSPy Optimizer transparently before yielding to the MCP client.

## 6. DSPy Mapping
`DSPy Signatures` define the JSON schema for `mcp.tool()` inputs/outputs.

## 7. MoA Mapping
Sub-agents can be spawned synchronously within a tool execution. The MCP server holds the connection open while the MoA orchestrator resolves.

## 8. Memory Model
Exposes Letta-like memory via MCP `Resources` and `Prompts`, allowing the agent to read context before calling tools.

## 9. Benchmark Model
**SWE-Bench:** Exposes tools for AST parsing and test generation natively to the sandboxed agent.

## 10. Migration Strategy
Legacy CLI users continue using `cli.py`. Autonomous agents configure Goose to launch `mcp.server.py`. Zero conflicts.
