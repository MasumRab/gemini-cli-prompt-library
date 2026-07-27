# Reference Implementation: CAMEL-AI (Agent Society)

## 1. Folder Structure
```text
plugins/camel/
├── __init__.py
├── society.py              # Orchestrator for multiple agents
├── agent_factory.py        # Spawns Predictor, Reviewer, Critic
├── role_library.py         # Maps Ontology Roles to CAMEL Roles
├── critic_society.py       # Specialized adversarial swarm
└── workflow_generation.py  # Unrolls Capabilities into Society tasks
```

## 2. Runtime Lifecycle
```text
Capability Invocation
 ↓
society.py (Instantiates Agent Factory)
 ↓
Parallel Execution (Predictor Agent vs Reviewer Agent)
 ↓
critic_society.py (Adversarial synthesis)
 ↓
Final output consensus
```

## 3. Data Model
Maps `Role` from `CAPABILITY_ONTOLOGY.md` strictly to `camel.agents.RolePlaying`. `Goal` becomes the `task_prompt`.

## 4. Plugin Model
Native Python integration mapping internal Capabilities to the `camel` pip library.

## 5. Hook Model
Hooks operate at the Inter-Agent communication level (intercepting messages before they reach the next agent).

## 6. DSPy Mapping
Each CAMEL Agent wraps a specific `DSPy Module`. The Society replaces traditional monolithic `DSPy Optimizers`.

## 7. MoA Mapping
This *is* the definitive MoA implementation.

## 8. Memory Model
Uses CAMEL's internal memory window management for conversation history between specialized agents.

## 9. Benchmark Model
**AgentBench:** Excels here due to distributed reasoning preventing context-pollution in complex tasks.

## 10. Migration Strategy
Experimental module requiring `camel-ai` dependency. Deployed as a distinct execution path (`--society` flag).
