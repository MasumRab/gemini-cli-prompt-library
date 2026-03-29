#!/usr/bin/env python3
"""
Test framework registry module.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_registry():
    """Test the command registry."""
    from dspy_integration.framework.registry import CommandRegistry

    registry = CommandRegistry()
    commands = registry.commands
    assert len(commands) > 0, "Registry should have commands"
    print(f"✅ Registry loaded: {len(commands)} commands")

    # Test getting a command
    improve_cmd = registry.get_command("improve")
    assert improve_cmd is not None, "'improve' command should be found"
    assert hasattr(improve_cmd, 'category'), "'improve' command should have category attribute"
    print(f"✅ Found 'improve' command: {improve_cmd.category}")

    # Test search
    results = registry.search("test")
    assert isinstance(results, list), "Search should return a list"
    print(f"✅ Search 'test' found {len(results)} results")


if __name__ == "__main__":
    test_registry()
    print("All tests passed!")
