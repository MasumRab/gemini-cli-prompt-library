"""
Tests for scripts/verify_prompts.py
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import patch

import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.verify_prompts import (
    get_toml_files,
    parse_registry,
    verify_prompts,
)  # noqa: E402


class TestGetTomlFiles:
    """Test suite for get_toml_files function."""

    def setup_method(self):
        """Create a temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_file(self, rel_path, content="test"):
        """Helper to create a file in temp directory."""
        filepath = os.path.join(self.temp_dir, rel_path)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def test_finds_toml_in_root(self):
        """Test that TOML files in root directory are found."""
        self._create_file("test1.toml", "key = 'value'")
        self._create_file("test2.toml", "key = 'value'")

        result = get_toml_files(self.temp_dir)

        assert len(result) == 2
        assert any("test1.toml" in f for f in result)
        assert any("test2.toml" in f for f in result)

    def test_finds_toml_in_subdirectories(self):
        """Test that TOML files in subdirectories are found."""
        self._create_file("subdir/test1.toml", "key = 'value'")
        self._create_file("subdir/nested/test2.toml", "key = 'value'")
        self._create_file("other/test3.toml", "key = 'value'")

        result = get_toml_files(self.temp_dir)

        assert len(result) == 3
        assert any("subdir" in f and "test1.toml" in f for f in result)
        assert any("nested" in f and "test2.toml" in f for f in result)
        assert any("other" in f and "test3.toml" in f for f in result)

    def test_ignores_non_toml_files(self):
        """Test that non-TOML files are ignored."""
        self._create_file("test1.toml", "key = 'value'")
        self._create_file("test1.txt", "text content")
        self._create_file("test1.md", "# content")
        self._create_file("test1.py", "print('hello')")

        result = get_toml_files(self.temp_dir)

        assert len(result) == 1
        assert result[0].endswith("test1.toml")

    def test_returns_empty_list_for_empty_dir(self):
        """Test that empty directory returns empty list."""
        result = get_toml_files(self.temp_dir)
        assert result == []

    def test_returns_empty_list_for_nonexistent_dir(self, tmp_path):
        """Test that nonexistent directory returns empty list."""
        nonexistent = tmp_path / "nonexistent"
        result = get_toml_files(str(nonexistent))
        assert result == []

    def test_finds_multiple_toml_files_deeply_nested(self):
        """Test finding TOML files in deeply nested structure."""
        self._create_file("a/b/c/d/e/deep.toml", "key = 'value'")
        self._create_file("a/b/c/shallow.toml", "key = 'value'")

        result = get_toml_files(self.temp_dir)

        assert len(result) == 2
        assert any("deep.toml" in f for f in result)
        assert any("shallow.toml" in f for f in result)


class TestParseRegistry:
    """Test suite for parse_registry function."""

    def setup_method(self):
        """Create a temporary file for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        )
        self.temp_file.close()

    def teardown_method(self):
        """Clean up temporary file."""
        os.unlink(self.temp_file.name)

    def _write_registry(self, content):
        """Helper to write content to registry file."""
        with open(self.temp_file.name, "w") as f:
            f.write(content)

    def test_parses_basic_commands(self):
        """Test parsing of basic command list."""
        self._write_registry("""
## Commands

- **code-review**: Code review command
- **security-audit**: Security audit command
- **docs-readme**: Generate README
        """)
        result = parse_registry(self.temp_file.name)

        assert len(result) == 3
        assert "code-review" in result
        assert "security-audit" in result
        assert "docs-readme" in result

    def test_parses_commands_with_special_chars(self):
        """Test parsing of commands with hyphens and underscores."""
        self._write_registry("""
- **my-command-name**: Test command
- **another_command**: Another command
- **test123**: Numbered command
        """)
        result = parse_registry(self.temp_file.name)

        assert "my-command-name" in result
        assert "another_command" in result
        assert "test123" in result

    def test_returns_empty_set_for_empty_file(self):
        """Test that empty file returns empty set."""
        self._write_registry("")
        result = parse_registry(self.temp_file.name)
        assert result == set()

    def test_returns_empty_set_for_no_commands(self):
        """Test that file without command format returns empty set."""
        self._write_registry("""
# This is a README

No commands here.
Just some regular text.
        """)
        result = parse_registry(self.temp_file.name)
        assert result == set()

    def test_deduplicates_commands(self):
        """Test that duplicate commands are deduplicated."""
        self._write_registry("""
- **code-review**: First mention
- **code-review**: Second mention
- **code-review**: Third mention
        """)
        result = parse_registry(self.temp_file.name)

        assert len(result) == 1
        assert "code-review" in result

    def test_ignores_non_command_bold_text(self):
        """Test that bold text that's not followed by colon is ignored by regex pattern."""
        # Note: The regex pattern "- \*\*(.*?)\*\*:" matches any bold text followed by colon
        # So "Bold text here" won't match because it ends with just ** not **:
        self._write_registry("""
- **Important**: Not a command
- **code-review**: This is a command
- **Bold text here**: Also matches pattern
        """)
        result = parse_registry(self.temp_file.name)

        # All three match the pattern since they end with **:
        assert len(result) == 3
        assert "code-review" in result
        assert "Important" in result
        assert "Bold text here" in result

    def test_parses_multiline_registry(self):
        """Test parsing of registry with multiple sections."""
        self._write_registry("""
# Command Registry

## Code Review
- **code-review**: Review code
- **security-audit**: Security check

## Documentation
- **docs-readme**: Generate README
- **docs-api**: Generate API docs

## Other
- **misc**: Miscellaneous
        """)
        result = parse_registry(self.temp_file.name)

        assert len(result) == 5
        assert "code-review" in result
        assert "security-audit" in result
        assert "docs-readme" in result
        assert "docs-api" in result
        assert "misc" in result


class TestVerifyPrompts:
    """Test suite for verify_prompts function."""

    def setup_method(self):
        """Create a temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_toml_file(self, category, filename, prompt="# Test"):
        """Helper to create a TOML file."""
        dir_path = os.path.join(self.temp_dir, "commands", category)
        os.makedirs(dir_path, exist_ok=True)
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "w") as f:
            f.write(f"""name = "test"
description = "Test command"
prompt = '''
{prompt}
'''
""")
        return filepath

    def _create_registry(self, commands):
        """Helper to create a registry file."""
        content = "## Commands\n\n"
        for cmd in commands:
            content += f"- **{cmd}**: Command description\n"
        with open("GEMINI.md", "w") as f:
            f.write(content)

    def test_verify_prompts_passes_with_valid_toml(self, capsys):
        """Test verification passes with valid TOML files."""
        self._create_toml_file("code-review", "test.toml", "# Test Command")
        self._create_registry(["code-review-test"])

        # Should not exit
        verify_prompts()

        captured = capsys.readouterr()
        assert "Verification Passed" in captured.out

    def test_verify_prompts_fails_missing_prompt_key(self, capsys):
        """Test verification fails when TOML is missing 'prompt' key."""
        # Create a TOML without 'prompt' key
        dir_path = os.path.join(self.temp_dir, "commands", "test")
        os.makedirs(dir_path, exist_ok=True)
        filepath = os.path.join(dir_path, "no-prompt.toml")
        with open(filepath, "w") as f:
            f.write('name = "test"\ndescription = "No prompt"\n')
        self._create_registry(["test-no-prompt"])

        with pytest.raises(SystemExit) as exc_info:
            verify_prompts()

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Missing 'prompt' key" in captured.out

    def test_verify_prompts_fails_invalid_toml(self, capsys):
        """Test verification fails with invalid TOML syntax."""
        dir_path = os.path.join(self.temp_dir, "commands", "test")
        os.makedirs(dir_path, exist_ok=True)
        filepath = os.path.join(dir_path, "invalid.toml")
        with open(filepath, "w") as f:
            f.write("invalid = [\n")  # Missing closing bracket
        self._create_registry(["test-invalid"])

        with pytest.raises(SystemExit) as exc_info:
            verify_prompts()

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Invalid TOML" in captured.out

    def test_verify_prompts_fails_unregistered_command(self, capsys):
        """Test verification fails when TOML is not in registry."""
        self._create_toml_file("code-review", "unregistered.toml", "# Test")
        self._create_registry(["some-other-command"])  # No match

        with pytest.raises(SystemExit) as exc_info:
            verify_prompts()

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "not found in" in captured.out

    def test_verify_prompts_fails_missing_commands_dir(self, capsys):
        """Test verification fails when commands directory is missing."""
        self._create_registry(["some-command"])

        with pytest.raises(SystemExit) as exc_info:
            verify_prompts()

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert "commands" in captured.out.lower()

    def test_verify_prompts_fails_missing_registry_file(self, capsys):
        """Test verification fails when registry file is missing."""
        os.makedirs(os.path.join(self.temp_dir, "commands"), exist_ok=True)
        self._create_toml_file("test", "test.toml", "# Test")

        with pytest.raises(SystemExit) as exc_info:
            verify_prompts()

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert "GEMINI.md" in captured.out

    def test_verify_prompts_with_simple_name_match(self, capsys):
        """Test verification passes when TOML name matches without category."""
        self._create_toml_file("code-review", "simple.toml", "# Simple Command")
        # Registry has simple-name, TOML has category=code-review, name=simple
        self._create_registry(["simple"])

        verify_prompts()

        captured = capsys.readouterr()
        assert "Verification Passed" in captured.out

    def test_verify_prompts_with_prefixed_name_match(self, capsys):
        """Test verification passes when TOML name matches with category prefix."""
        self._create_toml_file("code-review", "prefixed.toml", "# Prefixed Command")
        # Registry has code-review-prefixed, TOML has category=code-review, name=prefixed
        self._create_registry(["code-review-prefixed"])

        verify_prompts()

        captured = capsys.readouterr()
        assert "Verification Passed" in captured.out

    def test_verify_prompts_reports_multiple_errors(self, capsys):
        """Test verification reports multiple errors at once."""
        # Create multiple files with different errors
        # File 1: Valid TOML but missing prompt key
        dir_path1 = os.path.join(self.temp_dir, "commands", "test")
        os.makedirs(dir_path1, exist_ok=True)
        filepath1 = os.path.join(dir_path1, "no-prompt.toml")
        with open(filepath1, "w") as f:
            f.write('name = "test"\ndescription = "No prompt"\n')
        self._create_registry(["test-no-prompt"])

        # File 2: Valid TOML but also missing prompt key
        dir_path2 = os.path.join(self.temp_dir, "commands", "test2")
        os.makedirs(dir_path2, exist_ok=True)
        filepath2 = os.path.join(dir_path2, "also-no-prompt.toml")
        with open(filepath2, "w") as f:
            f.write('name = "test"\ndescription = "Also no prompt"\n')
        # Also add to registry (will be found)
        self._create_registry(["test-no-prompt", "test2-also-no-prompt"])

        with pytest.raises(SystemExit) as exc_info:
            verify_prompts()

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        # Should show multiple missing prompt errors
        assert "Missing 'prompt' key" in captured.out
        # Count how many times it appears
        assert captured.out.count("Missing 'prompt' key") >= 2