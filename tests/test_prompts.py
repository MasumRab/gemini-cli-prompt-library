"""
Tests for the Prompt Abstraction Layer (TOML-DSPy integration).
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestTOMLPrompt:
    """Test TOML prompt parsing and rendering."""

    def test_extract_variables(self):
        """Test extracting variables from prompt template."""
        from dspy_integration.prompts import TOMLPrompt

        prompt = TOMLPrompt(
            name="test_prompt",
            path=Path("/test/test.toml"),
            content={"prompt": "Analyze this code: {{code}}\n\nResult: {{output}}"},
        )

        assert "code" in prompt.variables
        assert "output" in prompt.variables

    def test_extract_variables_complex(self):
        """Test extracting variables with different patterns."""
        from dspy_integration.prompts import TOMLPrompt

        prompt = TOMLPrompt(
            name="test_prompt",
            path=Path("/test/test.toml"),
            content={"prompt": "{{args}}\n{{function}}\n{{expected}}"},
        )

        assert len(prompt.variables) == 3
        assert "args" in prompt.variables
        assert "function" in prompt.variables
        assert "expected" in prompt.variables

    def test_render_template(self):
        """Test rendering prompt template with variables."""
        from dspy_integration.prompts import TOMLPrompt

        prompt = TOMLPrompt(
            name="test_prompt",
            path=Path("/test/test.toml"),
            content={"prompt": "Hello {{name}}, your score is {{score}}"},
        )

        rendered = prompt.render(name="Alice", score="100")
        assert "Hello Alice" in rendered
        assert "100" in rendered

    def test_render_missing_variable(self):
        """Test rendering with missing variable (should leave placeholder)."""
        from dspy_integration.prompts import TOMLPrompt

        prompt = TOMLPrompt(
            name="test_prompt",
            path=Path("/test/test.toml"),
            content={"prompt": "Hello {{name}}, {{missing}}"},
        )

        rendered = prompt.render(name="Bob")
        assert "Hello Bob" in rendered
        assert "{{missing}}" in rendered

    def test_prompt_category(self):
        """Test prompt category extraction from path."""
        from dspy_integration.prompts import TOMLPrompt

        prompt = TOMLPrompt(
            name="security",
            path=Path("/commands/code-review/security.toml"),
            content={"prompt": "Review this: {{code}}"},
        )

        assert prompt.category == "code-review"

    def test_repr(self):
        """Test string representation."""
        from dspy_integration.prompts import TOMLPrompt

        prompt = TOMLPrompt(
            name="security_review",
            path=Path("/commands/code-review/security.toml"),
            content={"prompt": "{{code}}"},
        )

        repr_str = repr(prompt)
        assert "security_review" in repr_str
        assert "code-review" in repr_str


class TestPromptRegistry:
    """Test prompt registry."""

    def test_register_and_get(self):
        """Test registering and retrieving a prompt."""
        from dspy_integration.prompts import PromptRegistry, TOMLPrompt

        PromptRegistry.clear()

        prompt = TOMLPrompt(
            name="test_prompt",
            path=Path("/test/test.toml"),
            content={"prompt": "Test: {{input}}"},
        )
        PromptRegistry._prompts["test/category"] = prompt

        retrieved = PromptRegistry.get("test/category")
        assert retrieved is prompt
        assert retrieved.name == "test_prompt"

    def test_list_prompts(self):
        """Test listing all prompts."""
        from dspy_integration.prompts import PromptRegistry, TOMLPrompt

        PromptRegistry.clear()

        PromptRegistry._prompts["test/prompt1"] = TOMLPrompt(
            "p1", Path("/test/1.toml"), {"prompt": "{{a}}"}
        )
        PromptRegistry._prompts["test/prompt2"] = TOMLPrompt(
            "p2", Path("/test/2.toml"), {"prompt": "{{b}}"}
        )

        prompts = PromptRegistry.list()
        assert len(prompts) == 2
        assert "test/prompt1" in prompts
        assert "test/prompt2" in prompts

    def test_list_by_category(self):
        """Test listing prompts by category."""
        from dspy_integration.prompts import PromptRegistry, TOMLPrompt

        PromptRegistry.clear()

        PromptRegistry._prompts["code-review/security"] = TOMLPrompt(
            "security", Path("/test.toml"), {"prompt": "{{code}}"}
        )
        PromptRegistry._prompts["code-review/performance"] = TOMLPrompt(
            "performance", Path("/test.toml"), {"prompt": "{{code}}"}
        )
        PromptRegistry._prompts["testing/unit-test"] = TOMLPrompt(
            "unit-test", Path("/test.toml"), {"prompt": "{{function}}"}
        )

        code_review = PromptRegistry.list_by_category("code-review")
        assert len(code_review) == 2
        assert "code-review/security" in code_review

        testing = PromptRegistry.list_by_category("testing")
        assert len(testing) == 1
        assert "testing/unit-test" in testing

    def test_register_dspy_mapping(self):
        """Test registering TOML to DSPy mapping."""
        from dspy_integration.prompts import PromptRegistry

        PromptRegistry.clear()

        PromptRegistry.register_dspy_mapping("code-review/security", "security_review")
        PromptRegistry.register_dspy_mapping("testing/unit-test", "unit_test")

        assert (
            PromptRegistry.get_dspy_module("code-review/security") == "security_review"
        )
        assert PromptRegistry.get_dspy_module("testing/unit-test") == "unit_test"
        assert PromptRegistry.get_dspy_module("unknown") is None

    def test_clear_registry(self):
        """Test clearing the registry."""
        from dspy_integration.prompts import PromptRegistry, TOMLPrompt

        PromptRegistry._prompts["test/prompt"] = TOMLPrompt(
            "prompt", Path("/test.toml"), {"prompt": "{{x}}"}
        )
        PromptRegistry._toml_to_dspy["test"] = "module"

        PromptRegistry.clear()

        assert len(PromptRegistry._prompts) == 0
        assert len(PromptRegistry._toml_to_dspy) == 0


class TestTOMLToDSPyConverter:
    """Test TOML to DSPy conversion."""

    def test_convert_basic(self):
        """Test basic conversion."""
        from dspy_integration.prompts import TOMLPrompt, TOMLToDSPyConverter

        prompt = TOMLPrompt(
            name="test_prompt",
            path=Path("/test/test.toml"),
            content={"prompt": "Analyze: {{code}}\nOutput: {{output}}"},
        )

        config = TOMLToDSPyConverter.convert(prompt)

        assert "signature" in config
        assert "input_fields" in config
        assert "output_fields" in config
        assert "prompt_template" in config

        assert "code" in config["input_fields"]
        assert "output" in config["output_fields"]

    @pytest.mark.skip(
        reason="Requires real dspy module - skipped in mocked test environment"
    )
    def test_create_module(self):
        """Test creating a DSPy module from TOML prompt.

        Note: This test requires real dspy module and may not work with mocked dspy.
        """
        import dspy
        from dspy_integration.prompts import TOMLPrompt, TOMLToDSPyConverter

        prompt = TOMLPrompt(
            name="security_review",
            path=Path("/test/test.toml"),
            content={"prompt": "Find vulnerabilities in: {{code}}\nResult: {{review}}"},
        )

        ModuleClass = TOMLToDSPyConverter.create_module(prompt, "SecurityReviewModule")

        assert ModuleClass.__name__ == "SecurityReviewModule"
        # Check it's a proper class with forward method
        assert isinstance(ModuleClass, type)
        assert hasattr(ModuleClass, "forward")

    def test_create_module_default_name(self):
        """Test creating module with auto-generated name."""
        from dspy_integration.prompts import TOMLPrompt, TOMLToDSPyConverter

        prompt = TOMLPrompt(
            name="my_test_prompt",
            path=Path("/test/test.toml"),
            content={"prompt": "{{input}}"},
        )

        ModuleClass = TOMLToDSPyConverter.create_module(prompt)

        assert (
            "MyTestPrompt" in ModuleClass.__name__ or "Module" in ModuleClass.__name__
        )


class TestLoadPrompts:
    """Test loading prompts from directory."""

    def test_load_from_directory(self, tmp_path):
        """Test loading prompts from a directory."""
        from dspy_integration.prompts import PromptRegistry, load_commands_prompts

        # Create test TOML files
        (tmp_path / "category1").mkdir()
        with open(tmp_path / "category1" / "test1.toml", "w") as f:
            f.write('prompt = "Test 1: {{input}}"')
        with open(tmp_path / "category1" / "test2.toml", "w") as f:
            f.write('prompt = "Test 2: {{code}}"')

        PromptRegistry.clear()
        load_commands_prompts(tmp_path)

        prompts = PromptRegistry.list()
        assert len(prompts) == 2
        assert "category1/test1" in prompts
        assert "category1/test2" in prompts

    def test_load_ignores_invalid_files(self, tmp_path):
        """Test that invalid files are ignored."""
        from dspy_integration.prompts import PromptRegistry, load_commands_prompts

        # Create a file that's not valid TOML
        (tmp_path / "invalid.toml").write_text("not valid toml {")

        PromptRegistry.clear()
        load_commands_prompts(tmp_path)

        # Should not crash, just skip the invalid file
        assert len(PromptRegistry.list()) == 0


class TestDefaultMappings:
    """Test default TOML to scenario mappings."""

    def test_default_mappings_defined(self):
        """Test that default mappings are defined."""
        from dspy_integration.prompts import DEFAULT_MAPPINGS

        assert "code-review/security" in DEFAULT_MAPPINGS
        assert "testing/generate-unit-tests" in DEFAULT_MAPPINGS
        assert "docs/write-readme" in DEFAULT_MAPPINGS
        assert "architecture/design-api" in DEFAULT_MAPPINGS

    def test_default_mappings_point_to_scenarios(self):
        """Test that default mappings point to valid scenarios."""
        from dspy_integration.prompts import DEFAULT_MAPPINGS
        from dspy_integration.scenarios import ScenarioRegistry

        for toml_name, scenario_name in DEFAULT_MAPPINGS.items():
            assert scenario_name in ScenarioRegistry.list(), (
                f"Mapping {toml_name} -> {scenario_name} but {scenario_name} is not registered"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
