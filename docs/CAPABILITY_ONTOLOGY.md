# Capability Ontology

This ontology decouples "Prompts" (which are execution mechanisms) from "Capabilities" (which are fundamental intents).
By mapping capabilities through this ontology, we can dynamically generate target-specific adapters (Letta workflows, MCP tools, CAMEL societies) from a single source of truth.

## The Core Ontology Model

```yaml
Capability:
  # The fundamental identity of the capability
  id: string
  name: string
  category: string

  # The Intent Level
  goal: string           # What is trying to be achieved (e.g., "Find security flaws")
  role: string           # The persona executing the capability (e.g., "Principal Security Architect")
  style: list[string]    # Tone and interaction directives (e.g., ["Critical", "Evidence Driven"])

  # The Operational Level
  workflow: list[string] # Ordered sub-tasks (e.g., ["Static Analysis", "Taint Tracking", "Report Generation"])
  constraints: list[string] # Hard boundaries (e.g., "Do not execute arbitrary code")
  examples: list[dict]   # Few-shot examples for LLM context tuning

  # The Subsystem & Tool Level
  tools: list[string]    # Required external capabilities (e.g., "file_reader", "bash_executor")
  dspy_signature: string # Reference to the formal DSPy Signature mapping Inputs -> Outputs
  dspy_optimizer: string # The specific Teleprompter required if metrics fail

  # The Validation Level
  metrics: list[string]  # Functions evaluating success (e.g., "compiles_successfully", "no_cves_found")
  critic: string         # Reference to the Critic Hook pipeline governing retry logic
  benchmark: string      # The Tier 1/2 Benchmark driving this capability's design (e.g., "SWE-Bench")
```

## Example: Code Review Security Capability

Instead of a flat `commands/code-review/security.toml`, the capability is defined as:

```yaml
id: cap_code_review_security
name: "Deep Security Review"
category: "Code Review"

goal: "Identify and exploit conceptual security vulnerabilities in source code."
role: "Senior Application Security Engineer"
style:
  - "Adversarial"
  - "Precise"
  - "CWE-Referencing"

workflow:
  - "Deconstruct architecture"
  - "Trace untrusted inputs"
  - "Identify logic flaws"
  - "Draft exploit vectors"
  - "Recommend mitigations"

constraints:
  - "Output must conform to SARIF format"
  - "Do not hallucinate CVEs"

tools:
  - "read_file"
  - "list_directory"

dspy_signature: "SecurityReviewSignature"
dspy_optimizer: "MIPROv2"

metrics:
  - "valid_json"
  - "cwe_accuracy"

critic: "strict_security_critic"
benchmark: "SWE-bench"
```

## How the Ontology Drives the Architecture

1. **For MCP (Goose/Claude):** The `id`, `name`, `goal`, and `tools` generate the `mcp.tool()` JSON-RPC definition.
2. **For Letta (Stateful):** The `role`, `style`, and `constraints` inject into the Letta agent's `Persona` core memory block.
3. **For CAMEL-AI (Society):** The `workflow` triggers the Orchestrator to spawn specialized agents for each step (e.g., a "Taint Tracking Agent" and a "Mitigation Agent").
4. **For Headless CLI (Amp):** The entire capability compiles down to a `--json` driven headless command wrapper.

This ontology ensures we are building an **Agent-Neutral Capability Graph**, eradicating the technical debt of porting prompts to specific targets.
