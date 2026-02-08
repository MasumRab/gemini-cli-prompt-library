"""
Updated manifest module that uses the unified command loader.

This addresses the duplication between registry.py and manifest.py by using
the unified command loader implementation.
"""

# TODO [Low Priority]: Deprecate this module in favor of registry.py.
# Reason: manifest.py is now a simple wrapper around command_loader.py.

from .command_loader import get_commands as unified_get_commands


def get_commands():
    """
    Get commands using the unified loader for consistency.

    This replaces the duplicate implementation with the unified approach.
    """
    return unified_get_commands()


if __name__ == "__main__":
    commands = get_commands()
    print(len(commands))
