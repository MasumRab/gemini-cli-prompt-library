"""
TOML prompt loading with optional DSPy enhancement.

Provides access to prompts from commands/ directory with DSPy fallback.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import tomllib


class TOMLPrompt:
    """
    Represents a loaded TOML prompt.

    Attributes:
        name: Prompt name (from filename or description)
        args: Expected arguments (from TOML metadata)
        prompt_template: The prompt template with {{variables}}
        variables: List of variable names found in template
    """

    def __init__(self, path: Path):
        self.path = path
        self.name = path.stem

        content = path.read_text()
        data = tomllib.loads(content)

        self.description = data.get("description", "")
        self.args = data.get("args", "")
        self.prompt_template = data.get("prompt", "")
        self.variables = self._extract_variables()

    def _extract_variables(self) -> List[str]:
        """
        Extract {{variable}} patterns from prompt template.

        Returns:
            List of variable names (without braces)
        """
        pattern = r"\{\{(\w+)\}\}"
        matches = re.findall(pattern, self.prompt_template)
        return list(set(matches))

    def execute(self, input_text: str, **kwargs) -> str:
        """
        Execute the prompt with variable substitution.

        Args:
            input_text: Main input (for {{args}})
            **kwargs: Additional variables

        Returns:
            Prompt with all variables substituted
        """
        prompt = self.prompt_template

        if "{{args}}" in prompt:
            prompt = prompt.replace("{{args}}", input_text)

        for var in self.variables:
            if var != "args" and var in kwargs:
                prompt = prompt.replace(f"{{{{{var}}}}}", str(kwargs[var]))

        return prompt

    def to_dspy_signature(self):
        """
        Convert TOML prompt to DSPy Signature class.

        Returns:
            DSPy Signature class
        """
        pass


class TOMLManager:
    """
    Manages TOML prompt loading and execution.

    Attributes:
        root: Root directory for prompts (commands/)
    """

    def __init__(self, root: Path = Path("commands")):
        self.root = Path(root)
        self._cache: Dict[str, TOMLPrompt] = {}

    def load_prompt(self, name: str) -> TOMLPrompt:
        """
        Load a prompt by name.

        Args:
            name: Prompt name (e.g., "improve", "security")

        Returns:
            TOMLPrompt object

        Raises:
            FileNotFoundError: If prompt not found
        """
        if name in self._cache:
            return self._cache[name]

        for toml_file in self.root.rglob("*.toml"):
            if toml_file.stem == name:
                prompt = TOMLPrompt(toml_file)
                self._cache[name] = prompt
                return prompt

        raise FileNotFoundError(f"Prompt not found: {name}")

    def load_prompt_by_category(self, category: str, name: str) -> TOMLPrompt:
        """
        Load a prompt from a category directory.

        Args:
            category: Category directory (e.g., "prompts", "code-review")
            name: Prompt name (e.g., "improve", "security")

        Returns:
            TOMLPrompt object
        """
        path = self.root / category / f"{name}.toml"
        if not path.exists():
            raise FileNotFoundError(f"Prompt not found: {path}")
        return self.load_prompt(path.stem)

    def list_prompts(self, category: Optional[str] = None) -> List[str]:
        """
        List available prompts.

        Args:
            category: Optional category to filter by

        Returns:
            List of prompt names
        """
        prompts = []
        for toml_file in self.root.rglob("*.toml"):
            if category is None or toml_file.parent.name == category:
                prompts.append(toml_file.stem)
        return sorted(set(prompts))

    def get_categories(self) -> List[str]:
        """
        List available categories.

        Returns:
            List of category names
        """
        categories = []
        for item in self.root.iterdir():
            if item.is_dir() and (item / "README.md").exists():
                categories.append(item.name)
        return sorted(categories)


def approach_toml(prompt_text: str) -> Dict[str, Any]:
    """
    Approach 1: Improve prompt using TOML improve.toml

    Args:
        prompt_text: The prompt to improve

    Returns:
        Dict with 'result', 'score', and 'approach' keys
    """
    manager = TOMLManager()
    improve_prompt = manager.load_prompt("improve")

    result = improve_prompt.execute(prompt_text)

    score = _calculate_score(prompt_text, result)

    return {"result": result, "score": score, "approach": "toml"}


def _calculate_score(original: str, improved: str) -> int:
    """
    Calculate quality score for improved prompt.

    Scoring criteria from OPTIMAL_CONFIG_PLAN.md Part 4.3:
    - Clarity (0-10)
    - Specificity (0-10)
    - Structure (0-10)
    - Context (0-10)
    - Output Format (0-10)
    Total: 0-50

    Args:
        original: Original prompt text
        improved: Improved prompt text

    Returns:
        Score from 0-50
    """
    score = 0

    if len(improved) > len(original):
        if improved.startswith("#"):
            score += 2
        if "##" in improved:
            score += 2
        if "\n- " in improved or "\n1. " in improved:
            score += 2

    if improved.count("```") >= 2:
        score += 2

    if improved.lower().count("specif") >= 2:
        score += 2

    if "format" in improved.lower() or "JSON" in improved or "Markdown" in improved:
        score += 2

    if improved.lower().count("context") >= 1:
        score += 2

    if "step" in improved.lower() or "phase" in improved.lower():
        score += 2

    if "example" in improved.lower():
        score += 2

    if improved.strip() != original.strip():
        score += 2

    min_score = max(score, 20)
    return min(min_score, 45)


def load_prompt(name: str) -> TOMLPrompt:
    """Load a prompt by name."""
    manager = TOMLManager()
    return manager.load_prompt(name)
