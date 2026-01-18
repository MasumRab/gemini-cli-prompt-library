import pytest
import os
import shutil
import toml
from dspy_integration.framework.registry import CommandRegistry

@pytest.fixture
def commands_dir(tmp_path):
    """Create a temporary commands directory for testing."""
    commands_dir = tmp_path / "commands"
    commands_dir.mkdir()

    # Create category directories
    (commands_dir / "category1").mkdir()
    (commands_dir / "category2").mkdir()

    # Create dummy command files
    command1_data = {
        "description": "This is the first command.",
        "prompt": "Do something.",
        "author": "tester",
        "tags": ["test", "one"]
    }
    with open(commands_dir / "category1" / "command1.toml", "w") as f:
        toml.dump(command1_data, f)

    command2_data = {
        "description": "This is the second command.",
        "prompt": "Do something else.",
        "tags": ["test", "two"]
    }
    with open(commands_dir / "category1" / "command2.toml", "w") as f:
        toml.dump(command2_data, f)

    command3_data = {
        "description": "A different kind of command.",
        "prompt": "A different prompt.",
        "tags": ["another", "three"]
    }
    with open(commands_dir / "category2" / "command3.toml", "w") as f:
        toml.dump(command3_data, f)

    return str(commands_dir)

def test_command_discovery(commands_dir):
    """Test that the registry correctly discovers commands."""
    registry = CommandRegistry(commands_dir=commands_dir)
    assert len(registry.commands) == 3

def test_get_command(commands_dir):
    """Test retrieving a command by name."""
    registry = CommandRegistry(commands_dir=commands_dir)
    command = registry.get_command("command1")
    assert command is not None
    assert command.name == "command1"
    assert command.category == "category1"
    assert "first command" in command.description

    non_existent = registry.get_command("non_existent")
    assert non_existent is None

def test_search_commands(commands_dir):
    """Test searching for commands."""
    registry = CommandRegistry(commands_dir=commands_dir)

    # Search by name
    results = registry.search("command1")
    assert len(results) == 1
    assert results[0].name == "command1"

    # Search by description
    results = registry.search("second")
    assert len(results) == 1
    assert results[0].name == "command2"

    # Search by tag
    results = registry.search("three")
    assert len(results) == 1
    assert results[0].name == "command3"

    # Search with no results
    results = registry.search("non_existent_keyword")
    assert len(results) == 0

def test_list_by_category(commands_dir):
    """Test listing commands by category."""
    registry = CommandRegistry(commands_dir=commands_dir)

    category1_commands = registry.list_by_category("category1")
    assert len(category1_commands) == 2

    category2_commands = registry.list_by_category("category2")
    assert len(category2_commands) == 1

    non_existent_category = registry.list_by_category("non_existent_category")
    assert len(non_existent_category) == 0
