# OpenCode Recursive Subtask Design

**Objective:** Resolve the critical missing `opencode-subtask` recursive prompt template construction that legacy static TOML cannot handle.

## The Architectural Gap
In legacy systems: `Prompt A calls Prompt B calls Prompt C`.
This fails in headless autonomous environments because static text cannot orchestrate execution loops.

## The Level 5 Design
We convert recursive prompts into a **Workflow Task Tree**. The exporter plugins generate OpenCode task trees, Letta workflows, or MCP tools dynamically from the same source definition.

### Architecture Components
1. **`workflow_compiler.py`:** Parses the Capability Ontology. Identifies the `subtasks` array.
2. **`subtask_generator.py`:** Generates distinct, atomic tasks. For OpenCode, it writes nested `AGENTS.md` sub-instructions.
3. **`recursion_manager.py`:** Enforces depth limits (e.g., `MAX_DEPTH=3`) to prevent infinite AI loops.
4. **`aggregation_strategy.py`:** Defines how the outputs of the subtasks are stitched back together (e.g., map-reduce).

### Execution Flow
```text
Planner (OpenCode)
 ↓
workflow_compiler.py (Reads Capability)
 ↓
task_tree_schema.yaml (Generated)
 ├── Research (Subtask)
 ├── Architecture (Subtask)
 └── Recommendation (Subtask)
 ↓
Parallel/Sequential Agents (Amp/OpenCode workers)
 ↓
aggregation_strategy.py (Stitches results)
 ↓
Critic (Validates final stitched output)
 ↓
Final Report
```
