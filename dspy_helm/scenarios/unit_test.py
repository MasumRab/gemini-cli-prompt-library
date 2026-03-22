"""
Unit Test Generation Scenario.

Maps to: commands/testing/generate-unit-tests.toml
Category: Testing
"""

import dspy

from typing import List, Dict, Any
from .base import BaseScenario, ScenarioRegistry


@ScenarioRegistry.register("unit_test")
class UnitTestScenario(BaseScenario):
    """Scenario for evaluating unit test generation prompts."""

    INPUT_FIELDS = ["function"]
    OUTPUT_FIELDS = ["tests"]

    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """Load unit test generation test cases."""
        import json
        from pathlib import Path

        data_path = Path(__file__).parent.parent / "data" / "unit_test.jsonl"
        if data_path.exists():
            with open(data_path, "r") as f:
                data = [json.loads(line) for line in f if line.strip()]
                if data and "input" in data[0] and "expected_output" in data[0]:
                    return [
                        {"function": item["input"], "tests": item["expected_output"]}
                        for item in data
                    ]
                return data

        return [
            {
                "function": "function add(a, b) { return a + b; }",
                "tests": "Basic, edge, negative, decimals",
            },
            {
                "function": "function validateEmail(email) { return email.includes('@'); }",
                "tests": "Valid, invalid, empty",
            },
            {
                "function": "async function fetchUser(id) { return await db.get(id); }",
                "tests": "Success, not found, error",
            },
            {
                "function": "function factorial(n) { if (n <= 1) return 1; return n * factorial(n - 1); }",
                "tests": "Base, recursive, negative",
            },
            {
                "function": "function sortArray(arr) { return arr.sort(); }",
                "tests": "Numbers, strings, empty",
            },
            {
                "function": "class BankAccount { constructor(balance) { this.balance = balance; } }",
                "tests": "Initial, deposit, negative",
            },
            {
                "function": "function parseJSON(str) { return JSON.parse(str); }",
                "tests": "Valid, invalid, empty",
            },
            {
                "function": "function debounce(fn, delay) { }",
                "tests": "Once, multiple, delay",
            },
            {
                "function": "function binarySearch(arr, target) { }",
                "tests": "Found, not found, empty",
            },
            {
                "function": "function formatCurrency(amount) { return '$' + amount.toFixed(2); }",
                "tests": "Whole, decimal, zero",
            },
            {
                "function": "function isPalindrome(str) { return str === str.reverse(); }",
                "tests": "Palindrome, not, empty",
            },
            {
                "function": "function capitalize(str) { return str[0].toUpperCase() + str.slice(1); }",
                "tests": "Normal, empty, single",
            },
            {
                "function": "function chunkArray(arr, size) { }",
                "tests": "Exact, not exact, empty",
            },
            {
                "function": "function throttle(fn, delay) { }",
                "tests": "First, trailing, rapid",
            },
            {
                "function": "function deepClone(obj) { return JSON.parse(JSON.stringify(obj)); }",
                "tests": "Nested, circular",
            },
            {
                "function": "function groupBy(arr, key) { }",
                "tests": "Multiple groups, empty",
            },
            {
                "function": "function unique(arr) { return [...new Set(arr)]; }",
                "tests": "Duplicates, empty",
            },
            {
                "function": "function sum(arr) { return arr.reduce((a, b) => a + b, 0); }",
                "tests": "Empty, single, negative",
            },
            {
                "function": "function retry(fn, maxAttempts) { }",
                "tests": "Success first, retries, fail",
            },
            {
                "function": "function shuffle(arr) { return arr.sort(() => Math.random() - 0.5); }",
                "tests": "Distribution, empty",
            },
        ]

    def make_prompt(self, row: Dict[str, Any]) -> str:
        """Create prompt for unit test generation."""
        return f"""# Unit Test Generation

Generate comprehensive unit tests for:

```
{row["function"]}
```

## Test Requirements

### 1. Test Categories

#### Happy Path
- Valid inputs with expected outputs

#### Edge Cases
- Empty inputs (null, undefined, empty string/array)
- Zero, negative, maximum values
- Single element collections

#### Error Cases
- Invalid inputs
- Type mismatches
- Out of range values

#### Boundary Conditions
- First/last elements
- Off-by-one scenarios
- Limits and thresholds

### 2. Framework

Use Jest for JavaScript/TypeScript, pytest for Python.

### 3. Structure (AAA Pattern)
- **Arrange**: Set up test data
- **Act**: Execute function
- **Assert**: Verify results

### 4. Output Format

Provide production-ready test code with:
- Framework declaration
- All test cases with descriptions
- Clear assertions
- Edge case coverage comments
"""

    def metric(
        self, example: "dspy.Example", pred: "dspy.Prediction", trace=None
    ) -> float:
        """Evaluate unit test generation quality."""
        expected = example.tests.lower()
        pred_text = str(pred.tests).lower()
        if expected in pred_text:
            return 1.0
        return 0.0
