"""
Test coverage analysis for DSPy-HELM.

Updated Coverage Matrix (after adding new tests):
| Component               | Tests File         | Status   |
|-------------------------|--------------------|----------|
| Providers               |                    |          |
|   BaseProvider          | test_providers.py  | ✅ Good  |
|   ProviderChain         | test_providers.py  | ✅ Good  |
|   OpenCodeZenProvider   | test_providers.py  | ✅ Good  |
|   OpenRouterProvider    | test_providers.py  | Partial  |
|   GeminiProvider        | test_providers.py  | Partial  |
| Scenarios               |                    |          |
|   ScenarioRegistry      | test_scenarios.py  | ✅ Good  |
|   SecurityReviewScenario| test_scenarios.py  | ✅ Good  |
|   UnitTestScenario      | test_scenarios.py  | ✅ Good  |
|   DocumentationScenario | test_scenarios.py  | ✅ Good  |
|   APIDesignScenario     | test_scenarios.py  | ✅ Good  |
| Optimizers              |                    |          |
|   BaseOptimizer         | test_optimizers.py | ✅ Good  |
|   MIPROv2Optimizer      | test_optimizers.py | ✅ Good  |
|   BootstrapFewShot      | test_optimizers.py | ✅ Good  |
| Evaluation              |                    |          |
|   Evaluator             | test_evaluator.py  | ✅ Good  |
| Prompts                 |                    |          |
|   TOMLPrompt            | test_prompts.py    | ✅ Good  |
|   PromptRegistry        | test_prompts.py    | ✅ Good  |
|   TOMLToDSPyConverter   | test_prompts.py    | ✅ Good  |
| CLI                     |                    |          |
|   CLI main              | test_cli.py        | ✅ Good  |
| DSPy Modules            |                    |          |
|   All modules           | test_modules.py    | ✅ Good  |
| Integration             |                    |          |
|   Full pipeline         | test_integration.py| ✅ Good  |
| Edge Cases              |                    |          |
|   Error handling        | test_edge_cases.py | ✅ Good  |

Test Files:
- test_scenarios.py     : Scenario and registry tests
- test_providers.py     : Provider and chain tests
- test_cli.py           : CLI interface tests
- test_prompts.py       : TOML prompt abstraction tests
- test_optimizers.py    : Optimizer tests
- test_evaluator.py     : Evaluator tests
- test_modules.py       : DSPy integration module tests
- test_integration.py   : End-to-end integration tests
- test_edge_cases.py    : Error handling and edge cases
- conftest.py           : Pytest fixtures and configuration
- TEST_COVERAGE.md      : This file

Running Tests:
    pytest tests/ -v

Running Specific Tests:
    pytest tests/test_optimizers.py -v
    pytest tests/test_integration.py -v
    pytest tests/test_edge_cases.py -v

Adding New Tests:
1. Place test file in tests/ directory
2. Name file test_<component>.py
3. Create test classes with Test* naming
4. Use pytest fixtures from conftest.py
5. Follow existing test patterns
"""
