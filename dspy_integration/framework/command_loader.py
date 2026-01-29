"""
Unified command loader to eliminate duplicate command discovery implementations.

This module consolidates the duplicate command discovery logic found in
registry.py and manifest.py into a single, consistent implementation.
"""

import os
import tomli
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path


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
    
    Addresses the duplication between:
    - dspy_integration/framework/registry.py (_discover_commands method)
    - dspy_integration/framework/manifest.py (get_commands function)
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
            data = tomli.load(f)
        
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
    
    def search_commands(self, keyword: str) -> List[Command]:
        """
        Search for commands by keyword in name, description, or tags.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching Command objects
        """
        keyword_lower = keyword.lower()
        results = []
        
        for command in self.load_all_commands().values():
            if (
                keyword_lower in command.name.lower() or
                keyword_lower in command.description.lower() or
                (command.tags and keyword_lower in [tag.lower() for tag in command.tags])
            ):
                results.append(command)
        
        return results
    
    def list_commands_by_category(self, category: str) -> List[Command]:
        """
        List all commands in a given category.
        
        Args:
            category: Category name
            
        Returns:
            List of Command objects in the category
        """
        return [
            command
            for command in self.load_all_commands().values()
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
        commands = self.load_all_commands()
        return commands.get(name)


# Backwards compatibility functions for existing code
def get_command(name: str) -> Optional[Command]:
    """
    Convenience function to get a command from the default loader.
    
    Args:
        name: Command name
        
    Returns:
        Command object if found, None otherwise
    """
    loader = UnifiedCommandLoader()
    return loader.get_command(name)


def get_commands() -> List[Dict[str, Any]]:
    """
    Legacy function to return commands in the old format for compatibility.
    
    Returns:
        List of command dictionaries in the old format
    """
    loader = UnifiedCommandLoader()
    commands = loader.load_all_commands()
    
    return [
        {
            "name": cmd.name,
            "category": cmd.category,
            "description": cmd.description,
            "examples": cmd.examples or []
        }
        for cmd in commands.values()
    ]


class CommandRegistry:
    """
    Updated CommandRegistry that uses the unified loader.
    
    This addresses the duplication and improves the original implementation
    in registry.py by using the consolidated loading logic.
    """
    
    def __init__(self, commands_dir: str = "commands"):
        self.loader = UnifiedCommandLoader(commands_dir)
        self.commands = self.loader.load_all_commands()
    
    def search(self, keyword: str) -> List[Command]:
        """Search for commands by keyword."""
        return self.loader.search_commands(keyword)
    
    def list_by_category(self, category: str) -> List[Command]:
        """List all commands in a given category."""
        return self.loader.list_commands_by_category(category)
    
    def get_command(self, name: str) -> Optional[Command]:
        """Get a command by its name."""
        return self.loader.get_command(name)


class IntelligentDispatcher:
    """
    Intelligent dispatcher that routes natural language requests to appropriate commands.
    
    Updated to use the unified command loader for consistency.
    """
    
    def __init__(self, loader: Optional[UnifiedCommandLoader] = None):
        self.loader = loader or UnifiedCommandLoader()
        self.commands = self.loader.load_all_commands()

    def dispatch(self, user_input: str) -> Optional[Command]:
        """
        Dispatch user input to the best matching command.

        Args:
            user_input: Natural language request

        Returns:
            Best matching Command object
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

        # Tokenize inputs
        user_tokens = set(user_input.split())
        name_tokens = set(command.name.lower().replace("-", " ").split())
        desc_tokens = set(command.description.lower().split())
        tag_tokens = set([tag.lower() for tag in (command.tags or [])])

        # Exact name match gets high score
        if command.name.replace("-", " ") in user_input:
            score += 10

        # Count token overlaps
        name_overlap = len(name_tokens.intersection(user_tokens))
        desc_overlap = len(desc_tokens.intersection(user_tokens))
        tag_overlap = len(tag_tokens.intersection(user_tokens))

        score += (name_overlap * 5) + desc_overlap + (tag_overlap * 3)

        return score