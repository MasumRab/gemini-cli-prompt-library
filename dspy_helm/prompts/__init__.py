"""
Prompt Abstraction Layer for TOML-DSPy Integration.

This module provides:
- TOML prompt loading and parsing
- Conversion from TOML to DSPy Signatures
- Registry connecting TOML prompts to DSPy modules
- Bidirectional sync between TOML and DSPy
"""

from typing import Dict, Type, Optional, Any, List, TYPE_CHECKING
from pathlib import Path
import re
import toml

if TYPE_CHECKING:
    import dspy


class TOMLPrompt:
    """Represents a TOML prompt template."""

    def __init__(self, name: str, path: Path, content: Dict[str, Any]):
        self.name = name
        self.path = path
        self.prompt_template = content.get("prompt", "")
        self.variables = self._extract_variables()
        self.category = path.parent.name

    def _extract_variables(self) -> List[str]:
        """Extract variables from prompt template (e.g., {{args}})."""
        pattern = r"\{\{(\w+)\}\}"
        matches = re.findall(pattern, self.prompt_template)
        return list(set(matches))

    def render(self, **kwargs) -> str:
        """Render the prompt template with provided variables."""
        result = self.prompt_template
        for key, value in kwargs.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def to_dspy_signature(self) -> type:
        """Convert TOML prompt to DSPy Signature class."""
        import dspy

        input_fields = {}
        output_fields = {}

        for var in self.variables:
            if var in ["args", "code", "input", "requirements", "project"]:
                input_fields[var] = dspy.InputField(desc=f"Input: {var}")
            else:
                input_fields[var] = dspy.InputField(desc=f"Input parameter: {var}")

        # Add default output field
        output_fields["output"] = dspy.OutputField(desc="Generated output")

        signature_name = "".join(word.capitalize() for word in self.name.split("_"))
        signature_name = f"{signature_name}Signature"

        return type(signature_name, (), {**input_fields, **output_fields})

    def __repr__(self) -> str:
        return f"TOMLPrompt(name={self.name}, category={self.category}, vars={self.variables})"


class PromptRegistry:
    """Registry for TOML prompts with DSPy module mapping."""

    _prompts: Dict[str, TOMLPrompt] = {}
    _toml_to_dspy: Dict[str, str] = {}  # TOML name -> DSPy module name

    @classmethod
    def load_prompts(cls, commands_dir: Path) -> None:
        """Load all TOML prompts from commands directory."""
        for toml_file in commands_dir.glob("**/*.toml"):
            try:
                content = toml.load(toml_file)
                if "prompt" in content:
                    name = toml_file.stem
                    category = toml_file.parent.name
                    prompt = TOMLPrompt(name, toml_file, content)
                    cls._prompts[f"{category}/{name}"] = prompt
            except Exception as e:
                print(f"Warning: Could not load {toml_file}: {e}")

    @classmethod
    def get(cls, name: str) -> Optional[TOMLPrompt]:
        """Get a prompt by name (e.g., 'code-review/security')."""
        return cls._prompts.get(name)

    @classmethod
    def list(cls) -> List[str]:
        """List all registered prompts."""
        return list(cls._prompts.keys())

    @classmethod
    def list_by_category(cls, category: str) -> List[str]:
        """List prompts in a specific category."""
        return [name for name in cls._prompts.keys() if name.startswith(f"{category}/")]

    @classmethod
    def register_dspy_mapping(cls, toml_name: str, module_name: str) -> None:
        """Register a mapping from TOML prompt to DSPy module."""
        cls._toml_to_dspy[toml_name] = module_name

    @classmethod
    def get_dspy_module(cls, toml_name: str) -> Optional[str]:
        """Get the DSPy module name for a TOML prompt."""
        return cls._toml_to_dspy.get(toml_name)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered prompts."""
        cls._prompts.clear()
        cls._toml_to_dspy.clear()


class TOMLToDSPyConverter:
    """Converter from TOML prompts to DSPy modules."""

    @staticmethod
    def convert(toml_prompt: TOMLPrompt) -> Dict[str, Any]:
        """Convert a TOML prompt to DSPy module configuration."""
        signature = toml_prompt.to_dspy_signature()

        return {
            "signature": signature,
            "input_fields": toml_prompt.variables,
            "output_fields": ["output"],
            "prompt_template": toml_prompt.prompt_template,
        }

    @staticmethod
    def create_module(toml_prompt: TOMLPrompt, module_class_name: Optional[str] = None):
        """Create a DSPy module from a TOML prompt."""
        import dspy

        config = TOMLToDSPyConverter.convert(toml_prompt)
        signature = config["signature"]

        name = module_class_name or "".join(
            word.capitalize() for word in toml_prompt.name.split("_")
        )

        class GeneratedModule(dspy.Module):
            def __init__(self):
                super().__init__()
                self.generate = dspy.ChainOfThought(signature)

            def forward(self, **inputs):
                return self.generate(**inputs)

        GeneratedModule.__name__ = name
        return GeneratedModule


def load_commands_prompts(commands_path=None) -> None:
    """Load prompts from the commands directory."""
    if commands_path is None:
        commands_path = Path(__file__).parent.parent / "commands"

    if isinstance(commands_path, str):
        commands_path = Path(commands_path)

    if commands_path.exists():
        PromptRegistry.load_prompts(commands_path)


# Default mappings from TOML prompts to DSPy scenarios
DEFAULT_MAPPINGS = {
    "code-review/security": "security_review",
    "testing/generate-unit-tests": "unit_test",
    "docs/write-readme": "documentation",
    "architecture/design-api": "api_design",
}


def initialize_prompt_registry(commands_path=None):
    """Initialize the prompt registry with default mappings."""
    load_commands_prompts(commands_path)

    # Register default mappings
    for toml_name, scenario_name in DEFAULT_MAPPINGS.items():
        PromptRegistry.register_dspy_mapping(toml_name, scenario_name)

    return PromptRegistry


__all__ = [
    "TOMLPrompt",
    "PromptRegistry",
    "TOMLToDSPyConverter",
    "load_commands_prompts",
    "initialize_prompt_registry",
]
