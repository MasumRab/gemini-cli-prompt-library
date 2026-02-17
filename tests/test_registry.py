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
    try:
        from dspy_integration.framework.registry import CommandRegistry

        registry = CommandRegistry()
        commands = registry._commands
        print(f"✅ Registry loaded: {len(commands)} commands")

        # Test getting a command
        improve_cmd = registry.get_command("improve")
        if improve_cmd:
            print(f"✅ Found 'improve' command: {improve_cmd['category']}")
        else:
            print("❌ 'improve' command not found")

        # Test search
        results = registry.search("test")
        print(f"✅ Search 'test' found {len(results)} results")

        return True

    except Exception as e:
        print(f"❌ Registry test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_registry()
    sys.exit(0 if success else 1)
