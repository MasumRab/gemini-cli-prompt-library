"""
Tests for scripts/generate_manifest.py
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.generate_manifest import generate_manifest  # noqa: E402


class TestGenerateManifest:
    """Test suite for manifest generation functionality."""

    def setup_method(self):
        """Create a temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_toml_file(self, category, filename, name, description, prompt="# Test prompt"):
        """Helper to create a TOML file in the commands directory."""
        commands_dir = os.path.join(self.temp_dir, "commands", category)
        os.makedirs(commands_dir, exist_ok=True)
        filepath = os.path.join(commands_dir, filename)
        with open(filepath, "w") as f:
            f.write(f"""name = "{name}"
description = "Test command"
prompt = '''
{prompt}
'''
schedule = "manual"
""")
        return filepath

    def _create_template(self):
        """Helper to create the improve.toml template file."""
        template_dir = os.path.join(self.temp_dir, "commands", "prompts")
        os.makedirs(template_dir, exist_ok=True)
        template_path = os.path.join(template_dir, "improve.toml.template")
        with open(template_path, "w") as f:
            f.write("Commands:\n{{COMMAND_MANIFEST}}")
        return template_path

    def test_generate_manifest_basic(self, capsys):
        """Test basic manifest generation with valid TOML files."""
        # Create test command structure
        self._create_toml_file("code-review", "security-audit.toml", "security-audit", "Security audit command", "# Security Review\nThis performs security analysis.")
        self._create_toml_file("code-review", "code-review.toml", "code-review", "Code review command", "# Code Review\nThis reviews code.")
        self._create_toml_file("docs", "readme-gen.toml", "readme-gen", "README generator", "# README Generation\nGenerates README files.")
        # Create template file (required by script)
        self._create_template()

        # Run the generator
        generate_manifest()

        # Check that manifest file was created
        manifest_path = os.path.join(self.temp_dir, "commands_manifest.json")
        assert os.path.exists(manifest_path), "Manifest file should be created"

        # Load and verify manifest content
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        assert "/code-review:security-audit" in manifest
        assert "/code-review:code-review" in manifest
        assert "/docs:readme-gen" in manifest
        assert manifest["/code-review:security-audit"] == "Security Review"
        assert manifest["/code-review:code-review"] == "Code Review"
        assert manifest["/docs:readme-gen"] == "README Generation"

    def test_generate_manifest_missing_commands_dir(self, capsys):
        """Test behavior when commands directory doesn't exist."""
        # Don't create commands directory
        generate_manifest()

        # Check output mentions the error
        captured = capsys.readouterr()
        assert "Error" in captured.out or "not found" in captured.out.lower()

    def test_generate_manifest_empty_commands_dir(self, capsys):
        """Test behavior when commands directory is empty."""
        # Create empty commands directory
        os.makedirs(os.path.join(self.temp_dir, "commands"), exist_ok=True)
        # Create template file (required by script)
        self._create_template()

        generate_manifest()

        # Manifest should be created but empty
        manifest_path = os.path.join(self.temp_dir, "commands_manifest.json")
        assert os.path.exists(manifest_path)

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        assert manifest == {}

        # Should show warning about empty manifest
        captured = capsys.readouterr()
        assert "Warning" in captured.out or "empty" in captured.out.lower()

    def test_generate_manifest_invalid_toml(self, capsys):
        """Test handling of invalid TOML files."""
        # Create a valid command
        self._create_toml_file("code-review", "valid.toml", "valid", "Valid command", "# Valid Command")
        # Create template file (required by script)
        self._create_template()

        # Create invalid TOML file
        commands_dir = os.path.join(self.temp_dir, "commands", "invalid")
        os.makedirs(commands_dir, exist_ok=True)
        invalid_toml = os.path.join(commands_dir, "broken.toml")
        with open(invalid_toml, "w") as f:
            f.write("invalid toml = [broken\n")  # Syntax error

        generate_manifest()

        # Should still create manifest with valid entries
        manifest_path = os.path.join(self.temp_dir, "commands_manifest.json")
        assert os.path.exists(manifest_path)

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        assert "/code-review:valid" in manifest

        # Should have printed error message
        captured = capsys.readouterr()
        assert "Error" in captured.out or "decoding" in captured.out.lower()

    def test_generate_manifest_no_header_in_prompt(self, capsys):
        """Test TOML file where prompt doesn't start with a comment."""
        self._create_toml_file("test", "no-header.toml", "no-header", "No header test", "This has no header comment.\n# But has one later")
        # Create template file (required by script)
        self._create_template()

        generate_manifest()

        manifest_path = os.path.join(self.temp_dir, "commands_manifest.json")
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Should use default description when no header found at start
        assert "/test:no-header" in manifest

    def test_generate_manifest_multiple_categories(self, capsys):
        """Test handling of multiple command categories."""
        categories = ["code-review", "docs", "testing", "debugging", "learning", "writing", "architecture", "prompts", "workflows"]
        for i, category in enumerate(categories):
            self._create_toml_file(category, f"cmd{i}.toml", f"cmd{i}", f"Command {i}", f"# Command {i}")
        # Create template file (required by script)
        self._create_template()

        generate_manifest()

        manifest_path = os.path.join(self.temp_dir, "commands_manifest.json")
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        assert len(manifest) == len(categories)
        for i, category in enumerate(categories):
            assert f"/{category}:cmd{i}" in manifest

    def test_manifest_json_format(self, capsys):
        """Test that manifest is valid JSON with correct formatting."""
        self._create_toml_file("test", "format.toml", "format", "Format test", "# Format Test")
        # Create template file (required by script)
        self._create_template()

        generate_manifest()

        manifest_path = os.path.join(self.temp_dir, "commands_manifest.json")

        # Should be valid JSON (json.load should not raise)
        with open(manifest_path, "r") as f:
            content = f.read()
            manifest = json.loads(content)

        assert isinstance(manifest, dict)
        assert "/test:format" in manifest

    def test_command_name_extraction(self, capsys):
        """Test that command names are correctly extracted from filenames."""
        self._create_toml_file("category", "my-command-name.toml", "my-command", "Test", "# Test Command")
        # Create template file (required by script)
        self._create_template()

        generate_manifest()

        manifest_path = os.path.join(self.temp_dir, "commands_manifest.json")
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Should match pattern: /category:filename_without_extension
        assert "/category:my-command-name" in manifest

    def test_improve_toml_template_update(self, capsys):
        """Test that improve.toml is updated from template if template exists."""
        # Create template file
        template_path = self._create_template()

        # Create valid TOML
        self._create_toml_file("test", "test.toml", "test", "Test", "# Test")

        generate_manifest()

        # Check output file was created
        output_path = os.path.join(self.temp_dir, "commands", "prompts", "improve.toml")
        assert os.path.exists(output_path), "improve.toml should be created from template"

        with open(output_path, "r") as f:
            content = f.read()

        # Should have replaced the placeholder
        assert "{{COMMAND_MANIFEST}}" not in content
        assert "/test:test" in content

    def test_improve_toml_update_skipped_without_template(self, capsys):
        """Test behavior when template file doesn't exist.

        Note: This test documents current behavior - the script does NOT gracefully
        handle missing template files (raises FileNotFoundError).
        This is a potential bug that could be fixed in the future.
        """
        # Create valid TOML but NOT the template file
        self._create_toml_file("test", "test.toml", "test", "Test", "# Test")
        # Note: NOT creating template file

        # Current behavior: script raises FileNotFoundError when template is missing
        # This test documents this behavior - if script is fixed to handle it gracefully,
        # update this test to check manifest is still created
        with pytest.raises(FileNotFoundError, match="improve.toml.template"):
            generate_manifest()

        # The manifest should have been created before the error occurred
        manifest_path = os.path.join(self.temp_dir, "commands_manifest.json")
        assert os.path.exists(manifest_path), "Manifest should be created before template error"

        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        assert "/test:test" in manifest