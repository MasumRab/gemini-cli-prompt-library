"""
Command Registry for prompt library.

This module handles command discovery, loading from TOML files, and provides
access to command metadata. It serves as the single source of truth for
available commands in the system.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


@dataclass
class Command:
    """Unified command representation."""

    name: str
    category: str
    description: str
    prompt: str
    author: str = ""
    tags: Optional[List[str]] = field(default_factory=list)
    examples: Optional[List[str]] = field(default_factory=list)


class UnifiedCommandLoader:
    """
    Unified command loader that consolidates duplicate discovery logic.
    """

    def __init__(self, commands_dir: str = "commands"):
        self.commands_dir = Path(commands_dir)
        if not self.commands_dir.exists():
            # Try relative to this file
            self.commands_dir = Path(__file__).parent.parent.parent / "commands"

        if not self.commands_dir.exists():
            raise FileNotFoundError(f"Commands directory not found: {self.commands_dir}")

    def load_all_commands(self) -> Dict[str, Command]:
        """
        Load all commands from the commands directory.

        Returns:
            Dictionary mapping command names to Command objects
        """
        commands = {}

        for category_path in self.commands_dir.iterdir():
            if category_path.is_dir():
                category = category_path.name

                for command_file in category_path.glob("*.toml"):
                    command_name = command_file.stem

                    try:
                        command = self._load_command_from_file(
                            command_file, category
                        )
                        commands[command_name] = command
                    except Exception as e:
                        logging.warning(
                            f"Error loading command {command_name} from {command_file}: {e}"
                        )

        return commands

    def _load_command_from_file(self, file_path: Path, category: str) -> Command:
        """
        Load a single command from a TOML file.

        Args:
            file_path: Path to the TOML file
            category: Category name derived from directory

        Returns:
            Command object
        """
        with open(file_path, "rb") as f:
            data = tomllib.load(f)

        # Extract description from prompt if not provided in TOML
        description = data.get("description", "")
        if not description:
            # Try to extract from prompt comments
            prompt = data.get("prompt", "")
            description = self._extract_description_from_prompt(prompt)

        return Command(
            name=file_path.stem,
            category=category,
            description=description,
            prompt=data.get("prompt", ""),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            examples=data.get("examples", [])
        )

    def _extract_description_from_prompt(self, prompt: str) -> str:
        """
        Extract description from prompt comments.

        Args:
            prompt: The prompt string

        Returns:
            Extracted description
        """
        lines = prompt.strip().split('\n')
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line and cleaned_line.startswith('#'):
                description = cleaned_line.strip('# ').strip()
                if description:
                    return description

        return ""


class CommandRegistry:
    """
    Registry for managing and accessing commands.

    Uses UnifiedCommandLoader to load commands from files.
    """

    def __init__(self, commands_dir: str = "commands"):
        self.loader = UnifiedCommandLoader(commands_dir)
        # Cache commands on init
        self.commands = self.loader.load_all_commands()

    def search(self, keyword: str) -> List[Command]:
        """
        Search for commands by keyword in name, description, or tags.

        Args:
            keyword: Keyword to search for

        Returns:
            List of matching Command objects
        """
        keyword_lower = keyword.lower()
        results = []

        for command in self.commands.values():
            if (
                keyword_lower in command.name.lower() or
                keyword_lower in command.description.lower() or
                (command.tags and keyword_lower in [tag.lower() for tag in command.tags])
            ):
                results.append(command)

        return results

    def list_by_category(self, category: str) -> List[Command]:
        """
        List all commands in a given category.

        Args:
            category: Category name

        Returns:
            List of Command objects in the category
        """
        return [
            command
            for command in self.commands.values()
            if command.category.lower() == category.lower()
        ]

    def get_command(self, name: str) -> Optional[Command]:
        """
        Get a command by its name.

        Args:
            name: Command name

        Returns:
            Command object if found, None otherwise
        """
        return self.commands.get(name)


def get_command(name: str) -> Optional[Command]:
    """
    Convenience function to get a command from the default registry.

    Args:
        name: Command name

    Returns:
        Command object if found, None otherwise
    """
    # TODO [High Priority]: Implement singleton pattern or caching for CommandRegistry to avoid re-parsing TOML files on every call.
    # Reason: Current implementation re-instantiates CommandRegistry on every call, leading to O(N) file reads.
    registry = CommandRegistry()
    return registry.get_command(name)
