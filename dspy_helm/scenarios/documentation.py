"""
Documentation Generation Scenario.

Maps to: commands/docs/write-readme.toml
Category: Documentation
"""

from typing import List, Dict, Any
from .base import BaseScenario, ScenarioRegistry


@ScenarioRegistry.register("documentation")
class DocumentationScenario(BaseScenario):
    """Scenario for evaluating documentation generation prompts."""

    INPUT_FIELDS = ["project"]
    OUTPUT_FIELDS = ["readme"]

    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """Load documentation generation test cases."""
        import json
        from pathlib import Path

        data_path = Path(__file__).parent.parent / "data" / "documentation.jsonl"
        if data_path.exists():
            with open(data_path, "r") as f:
                data = [json.loads(line) for line in f if line.strip()]
                if data and "input" in data[0] and "expected_output" in data[0]:
                    return [
                        {"project": item["input"], "readme": item["expected_output"]}
                        for item in data
                    ]
                return data

        return [
            {
                "project": "A CLI tool for file processing that converts images to PNG",
                "readme": "installation, usage, examples",
            },
            {
                "project": "REST API for blog posts with users and comments",
                "readme": "endpoints, authentication, models",
            },
            {
                "project": "Python library for HTTP requests with caching",
                "readme": "installation, quick start, api",
            },
            {
                "project": "Node.js authentication service with JWT",
                "readme": "setup, usage, configuration",
            },
            {
                "project": "Database migration tool for PostgreSQL",
                "readme": "requirements, installation, commands",
            },
            {
                "project": "React component library for data visualization",
                "readme": "getting started, components",
            },
            {
                "project": "Go microservice template with Docker",
                "readme": "structure, building, deployment",
            },
            {
                "project": "Machine learning pipeline for text classification",
                "readme": "requirements, training, inference",
            },
            {
                "project": "Chrome extension for tab management",
                "readme": "installation, usage, permissions",
            },
            {
                "project": "Static site generator with markdown support",
                "readme": "quick start, configuration",
            },
            {
                "project": "GraphQL API server with authentication",
                "readme": "schema, resolvers, auth",
            },
            {
                "project": "Redis caching layer for Node.js",
                "readme": "installation, usage, patterns",
            },
            {
                "project": "Kubernetes operator for database management",
                "readme": "architecture, custom resources",
            },
            {
                "project": "Desktop app for API testing with Vue 3",
                "readme": "architecture, features",
            },
            {
                "project": "CI/CD pipeline generator for GitHub Actions",
                "readme": "templates, customization",
            },
            {
                "project": "Real-time collaboration library with WebSockets",
                "readme": "architecture, events",
            },
            {
                "project": "Payment processing SDK with Stripe integration",
                "readme": "setup, webhooks, errors",
            },
            {
                "project": "Code search tool with regex support",
                "readme": "installation, usage, patterns",
            },
            {
                "project": "Config management system with validation",
                "readme": "schema, validation, migration",
            },
            {
                "project": "Event sourcing library for domain-driven design",
                "readme": "concepts, commands, queries",
            },
        ]

    def make_prompt(self, row: Dict[str, Any]) -> str:
        """Create prompt for documentation generation."""
        return f"""# README Generation

Create a comprehensive README.md for:

```
{row["project"]}
```

## Required Sections

### 1. Project Title & Badges
- Clear, descriptive title
- Build status, version, license badges

### 2. Description
- What the project does
- Why it exists (problem solved)
- Key features (3-5 bullet points)

### 3. Installation
- Prerequisites
- Step-by-step instructions
- Platform-specific notes

### 4. Quick Start
- Minimal working example
- Common use cases

### 5. Usage
- Detailed examples
- Configuration options

### 6. API Documentation (if applicable)
- Key functions/methods
- Parameters and return values

### 7. Contributing
- How to contribute
- Code of conduct

### 8. License
- License type and copyright

## Output Format

Generate complete, production-ready README.md in Markdown format.
"""

    def metric(
        self, example: "dspy.Example", pred: "dspy.Prediction", trace=None
    ) -> float:
        """Evaluate documentation quality."""
        expected = example.readme.lower()
        pred_text = str(pred.readme).lower()
        if expected in pred_text:
            return 1.0
        return 0.0
