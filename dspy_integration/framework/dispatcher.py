"""
Intelligent Dispatcher for routing user requests to commands.

This module provides the logic to interpret natural language user requests
and dispatch them to the most appropriate command in the registry.
"""

from typing import Optional, Set
from .registry import CommandRegistry, Command, get_command


class IntelligentDispatcher:
    """
    Intelligent dispatcher that routes natural language requests to appropriate commands.
    """

    def __init__(self, registry: Optional[CommandRegistry] = None):
        self.registry = registry or CommandRegistry()
        # Use cached commands from registry
        self.commands = self.registry.commands

    def dispatch(self, user_input: str) -> Optional[Command]:
        """
        Dispatch user input to the best matching command.

        Args:
            user_input: Natural language request

        Returns:
            Best matching Command object or None
        """
        user_input = user_input.lower()
        best_match = None
        max_score = 0

        for command in self.commands.values():
            score = self._calculate_match_score(user_input, command)

            if score > max_score:
                max_score = score
                best_match = command

        return best_match if max_score > 0 else None

    def _calculate_match_score(self, user_input: str, command: Command) -> float:
        """Calculate how well a command matches the user input."""
        score = 0

        # Normalize inputs
        user_tokens = set(user_input.split())

        # Helper to get tokens
        def get_tokens(text: str) -> Set[str]:
            return set(text.lower().replace("-", " ").split())

        name_tokens = get_tokens(command.name)
        desc_tokens = get_tokens(command.description)
        tag_tokens = set()
        if command.tags:
            for tag in command.tags:
                tag_tokens.update(get_tokens(tag))

        # 1. Exact Name Match (Highest Priority)
        # Check if the command name appears in the input (handling hyphens as spaces)
        normalized_name = command.name.replace("-", " ")
        if normalized_name in user_input:
            score += 20  # Very strong signal

        # 2. Token Overlap
        name_overlap = len(name_tokens.intersection(user_tokens))
        desc_overlap = len(desc_tokens.intersection(user_tokens))
        tag_overlap = len(tag_tokens.intersection(user_tokens))

        score += (name_overlap * 5)      # Name words are important
        score += (tag_overlap * 3)       # Tags are significant
        score += (desc_overlap * 1)      # Description is supporting

        return score


def dispatch(user_input: str) -> Optional[Command]:
    """
    Convenience function to dispatch a request using the default dispatcher.

    Args:
        user_input: Natural language request

    Returns:
        Best matching Command object or None
    """
    dispatcher = IntelligentDispatcher()
    return dispatcher.dispatch(user_input)
