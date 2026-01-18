#!/usr/bin/env python3
"""
Quick test to verify framework imports work.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_framework_imports():
    """Test that framework imports work."""
    try:
        from dspy_integration.framework.registry import CommandRegistry
        from dspy_integration.framework import get_commands

        print("✅ Framework imports successful")

        # Test registry
        registry = CommandRegistry()
        commands = registry.get_all_commands()
        print(f"✅ Registry loaded: {len(commands)} commands")

        # Test get_commands function
        cmds = get_commands()
        print(f"✅ get_commands() returned: {len(cmds)} commands")

        return True

    except Exception as e:
        print(f"❌ Framework import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_framework_imports()
    sys.exit(0 if success else 1)
