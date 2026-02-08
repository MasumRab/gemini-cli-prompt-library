"""
Updated CommandRegistry that uses the unified command loader.

This addresses the duplication between registry.py and manifest.py by using
the unified command loader implementation.
"""

# TODO [Low Priority]: Review for deprecation.
# Reason: This file primarily wraps command_loader.py. Once the refactor is stable,
# consider removing this wrapper if no longer needed by external scripts.

from typing import List, Optional
from .command_loader import (
    UnifiedCommandLoader,
    Command,
    IntelligentDispatcher as UnifiedIntelligentDispatcher
)


class CommandRegistry:
    """
    Updated CommandRegistry that uses the unified command loader.

    This addresses the duplication and improves the original implementation
    by using the consolidated loading logic from command_loader.py.
    """

    def __init__(self, commands_dir="commands"):
        self.loader = UnifiedCommandLoader(commands_dir)
        self.commands = self.loader.load_all_commands()

    def search(self, keyword: str):
        """Search for commands by keyword in name, description, or tags."""
        return self.loader.search_commands(keyword)

    def list_by_category(self, category: str):
        """List all commands in a given category."""
        return self.loader.list_commands_by_category(category)

    def get_command(self, name: str):
        """Get a command by its name."""
        return self.loader.get_command(name)


def get_command(name: str):
    """Convenience function to get a command from the default registry."""
    from .command_loader import get_command as loader_get_command
    return loader_get_command(name)


# Use the unified IntelligentDispatcher from command_loader
IntelligentDispatcher = UnifiedIntelligentDispatcher
