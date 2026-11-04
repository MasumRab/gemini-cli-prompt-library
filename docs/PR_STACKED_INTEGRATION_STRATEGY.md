# PR Stacked Integration Strategy: Non-Graphite Components

## Repository Structure (Non-Graphite Components)

```
gemini-cli-prompt-library/
├── dspy_helm/                    # DSPy-HELM integration (CLI, providers, scenarios, data)
│   ├── cli.py
│   ├── providers/                # base.py, gemini.py, groq.py, opencode.py, etc.
│   ├── scenarios/                # api_design.py, base.py, documentation.py, etc.
│   └── data/                     # *.jsonl training/test data
├── scripts/                      # Automation tools
│   ├── update_active_context.py
│   ├── generate_manifest.py
│   └── perform_audit.py
├── docs/                         # Documentation
├── .github/
│   └── workflows/               # CI/CD workflows
├── .mergify.yml                # Merge automation config
└── pyproject.toml             # Python package config
```

## Stacked History Path (Non-Graphite Only)

### Layer 1: Core Infrastructure ⚙️
- `dspy_helm/cli.py` - Main CLI entry point
- Root configuration files

### Layer 2: Provider System 🧩
- `dspy_helm/providers/base.py` - Base provider class
- Provider implementations

### Layer 3: Scenarios & Data 📊
- `dspy_helm/scenarios/*.py` (api_design.py, base.py, documentation.py, security_review.py, unit_test.py)
- `dspy_helm/data/*.jsonl` - Training/test data (line-delimited JSON)

### Layer 4: Automation Scripts 🤖
- `scripts/update_active_context.py`
- `scripts/generate_manifest.py`
- `scripts/perform_audit.py`

### Layer 5: Documentation & Workflows 📝
- `.github/workflows/*.yml`
- `docs/*.md`
- `.mergify.yml`

## Safe Cherry-Pick Strategy

### For PR Series A (Core → Providers):
```bash
git worktree add -B impl-core-providers ../impl-core-providers origin/main
git cherry-pick <base_provider_commit>
git cherry-pick <gemini_provider_commit>
python -c "from dspy_helm.providers.base import BaseProvider; print('OK')"
```

> **Note:** To bring only specific provider files from another branch (without a full cherry-pick of a commit), use:
> ```bash
> git checkout <branch> -- dspy_helm/providers/gemini.py
> # or
> git restore --source=<branch> dspy_helm/providers/gemini.py
> ```

### For PR Series B (Scenarios + Data):
```bash
git worktree add -B impl-scenarios ../impl-scenarios impl-core-providers
git cherry-pick <scenario_config_commit>
python -c "from dspy_helm.scenarios import load_scenarios"
```

### For PR Series C (Scripts):
```bash
git worktree add -B impl-scripts ../impl-scripts impl-scenarios
git cherry-pick <update_context_script_commit>
python scripts/update_active_context.py --help   # or invoke the script's actual CLI
```

### For PR Series D (Docs + Workflows):
```bash
git worktree add -B impl-docs ../impl-docs origin/main
git cherry-pick <docs_update_commit>
yamllint .github/workflows/*.yml
```

## 🚨 Regression & Architectural Shift Identification Points

### Critical Dependency Chains
```
scripts/ → dspy_helm/ → providers/ → scenarios/ → data/
 ↑
docs/ ← workflows/
```

### Points Requiring Regression Testing

1. **CLI Entry Point Changes** (`dspy_helm/cli.py`)
   - Test: `python -c "from dspy_helm.cli import main"`

2. **Provider Interface Modifications** (`providers/base.py`)
   - Test: All provider instantiations

3. **Scenario Configuration Updates** (`dspy_helm/scenarios/*.py`)
   - Test: `dspy-helm evaluate --list`

4. **Script Signature Changes** (`scripts/*.py`)
   - Test: CLI argument parsing

5. **Workflow File Modifications** (`.github/workflows/*.yml`)
   - Test: YAML validation

6. **Data Format Changes** (`data/*.jsonl`)
   - Test: Schema/line-structure validation

### Architectural Shifts to Monitor

#### Interface Contract Changes
```python
# CURRENT: BaseProvider.call(self, prompt: str, **kwargs) -> ProviderResponse
# RISK:  Adding *positional* params or changing the return type breaks all providers
#        (e.g. forcing `call(prompt, model=...)` and removing **kwargs)
```

#### Pipeline Flow Modifications
```python
# OLD: cli() → eval() → provider.call()
# NEW: cli() → validate() → eval() → provider.call()
```

#### Module Restructuring
```python
# OLD: dspy_helm/scenarios/
# NEW: dspy_helm/suite/ and dspy_helm/benchmarks/
```

## Validation Checklist Matrix

| Change Type | Layer | Regression Risk | Validation |
|-------------|-------|----------------|------------|
| CLI interface | 1 | High | `python -c "from dspy_helm.cli import main"` |
| Provider base | 2 | High | `from dspy_helm.providers import BaseProvider` |
| Provider implementations | 2 | Medium | Instantiate each provider |
| Scenario configs | 3 | Medium | `dspy-helm evaluate --list` |
| Training data | 3 | High | Data schema/line validation |
| Scripts | 4 | Medium | CLI invocation tests |
| Workflows | 5 | High | YAML lint + dry run |
| Documentation | 5 | Low | Link checking |