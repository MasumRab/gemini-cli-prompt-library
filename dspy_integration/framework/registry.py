import os
import re
import tomllib
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Command:
    name: str
    category: str
    description: str
    prompt: str
    author: str = ""
    tags: Optional[List[str]] = field(default_factory=list)


def normalize_text(text: str) -> str:
    """Normalize text for matching/scoring (strip punctuation, lowercase)."""
    return re.sub(r"[^\w\s]", "", text).lower()


class CommandRegistry:
    def __init__(self, commands_dir="commands"):
        self.commands_dir = commands_dir
        self.commands = self._discover_commands()

    def _discover_commands(self):
        commands = {}
        for category in os.listdir(self.commands_dir):
            category_path = os.path.join(self.commands_dir, category)
            if os.path.isdir(category_path):
                for command_file in os.listdir(category_path):
                    if command_file.endswith(".toml"):
                        command_name = command_file[:-5]
                        try:
                            with open(
                                os.path.join(category_path, command_file), "rb"
                            ) as f:
                                data = tomllib.load(f)

                            prompt = data.get("prompt", "")
                            description = data.get("description", "")

                            # Fallback: extract first # line from prompt if description is missing
                            if not description and prompt:
                                prompt_lines = prompt.strip().split("\n")
                                for line in prompt_lines:
                                    cleaned_line = line.strip()
                                    if cleaned_line and cleaned_line.startswith("#"):
                                        description = cleaned_line.strip("# ").strip()
                                        if description:
                                            break

                            commands[command_name] = Command(
                                name=command_name,
                                category=category,
                                description=description,
                                prompt=prompt,
                                author=data.get("author", ""),
                                tags=data.get("tags", []),
                            )
                        except Exception as e:
                            print(f"Error loading command {command_name}: {e}")
        return commands

    def search(self, keyword):
        """
        Search for commands by keyword in name, description, or tags.
        """
        results = []
        for command in self.commands.values():
            if (
                keyword in command.name
                or keyword in command.description
                or (command.tags and keyword in command.tags)
            ):
                results.append(command)
        return results

    def list_by_category(self, category):
        """List all commands in a given category."""
        return [
            command
            for command in self.commands.values()
            if command.category == category
        ]

    def get_command(self, name):
        """Get a command by its name."""
        return self.commands.get(name)


def get_command(name):
    """Convenience function to get a command from the default registry."""
    # TODO [High Priority]: Implement singleton/caching for CommandRegistry
    # to avoid O(N) re-parsing.
    registry = CommandRegistry()
    return registry.get_command(name)


class IntelligentDispatcher:
    """
    Intelligent dispatcher that routes natural language requests to
    appropriate commands.
    """

    def __init__(self, registry: Optional[CommandRegistry] = None):
        self.registry = registry or CommandRegistry()

    def dispatch(self, user_input: str) -> Optional[Command]:
        """
        Dispatch user input to the best matching command.

        Args:
            user_input: Natural language request

        Returns:
            Best matching Command object
        """
        user_input_normalized = normalize_text(user_input)
        best_match = None
        max_score = 0

        for command in self.registry.commands.values():
            score = self._calculate_match_score(user_input_normalized, command)

            if score > max_score:
                max_score = score
                best_match = command

        return best_match if max_score > 0 else None

    def _calculate_match_score(self, user_input: str, command: Command) -> float:
        """
        Calculate how well a command matches the user input.
        """
        score = 0

        # Tokenize inputs
        user_tokens = set(user_input.split())
        normalized_name = normalize_text(command.name.replace("-", " "))
        normalized_description = normalize_text(command.description)

        name_tokens = set(normalized_name.split())
        desc_tokens = set(normalized_description.split())
        tag_tokens = set(command.tags or [])

        # Exact name match gets high score
        if normalized_name in user_input:
            score += 10

        # Count token overlaps
        name_overlap = len(name_tokens.intersection(user_tokens))
        desc_overlap = len(desc_tokens.intersection(user_tokens))
        tag_overlap = len(tag_tokens.intersection(user_tokens))

        score += (name_overlap * 5) + desc_overlap + (tag_overlap * 3)

        return score
