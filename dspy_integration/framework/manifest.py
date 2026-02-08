"""
Updated manifest module that uses the command registry.

This addresses the duplication between registry.py and manifest.py by using
the unified command registry implementation.
"""

# TODO [Low Priority]: Deprecate this module in favor of registry.py.
# Reason: manifest.py is now a simple wrapper around registry.py.

from .registry import CommandRegistry



def get_commands():
    """
    Get commands using the registry for consistency.

    This replaces the duplicate implementation with the unified approach.
    Returns a list of dicts for backward compatibility.
    """
    registry = CommandRegistry()
    return [
        {
            "name": cmd.name,
            "category": cmd.category,
            "description": cmd.description,
            "examples": cmd.examples or []
        }
        for cmd in registry.commands.values()
    ]


if __name__ == "__main__":
    commands = get_commands()
    print(len(commands))
