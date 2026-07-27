# Reference Implementation: OpenCode/Amp (Headless & Recursive)

## 1. Folder Structure
```text
plugins/opencode/
├── __init__.py
├── manifest_generator.py   # Generates AGENTS.md / .amp.yaml
├── headless_cli.py         # Subclasses CLI to enforce --json
├── task_tree_compiler.py   # Unrolls Recursive Capabilities
└── failure_recovery.py     # Handles Timeout & Invalid JSON
```

## 2. Runtime Lifecycle
```text
Workflow Execution (Amp)
 ↓
headless_cli.py (Forces strict JSON output)
 ↓
task_tree_compiler.py (Spawns subtasks if recursive workflow detected)
 ↓
DSPy Execution
 ↓
failure_recovery.py (Catches exceptions, returns JSON error payload)
 ↓
Stdout (JSON captured by Amp)
```

## 3. Data Model
Maps `CAPABILITY_ONTOLOGY.md` directly to shell commands, discarding `Style` and `Role` as irrelevant for headless execution.

## 4. Plugin Model
Static exporter. Runs once to generate `AGENTS.md` and then relies on `headless_cli.py` for execution.

## 5. Hook Model
Hooks operate at the `sys.stdout` level, catching any errant `rich` TTY prints and forcing them into JSON structures.

## 6. DSPy Mapping
`DSPy Optimizers` must be run with `--detach`, returning a Job ID in JSON to prevent the headless agent from timing out.

## 7. MoA Mapping
Amp manages its own swarms. The CLI tool exposes atomic skills, relying on Amp's orchestrator rather than internal MoA.

## 8. Memory Model
Entirely stateless. Context must be passed via CLI arguments `{file_path}`.

## 9. Benchmark Model
**TerminalBench 2:** Relies heavily on this architecture to ensure zero TTY hang-ups and strict JSON parsing.

## 10. Migration Strategy
Generates a parallel entrypoint (`python -m dspy_integration.headless_cli`) strictly for CI and Amp agents.
