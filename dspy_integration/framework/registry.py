import os
import tomllib
import threading
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
                            commands[command_name] = Command(
                                name=command_name,
                                category=category,
                                description=data.get("description", ""),
                                prompt=data.get("prompt", ""),
                                author=data.get("author", ""),
                                tags=data.get("tags", []),
                            )
                        except Exception as e:
                            print(f"Error loading command {command_name}: {e}")
        return commands

    def search(self, keyword):
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
        return [
            command
            for command in self.commands.values()
            if command.category == category
        ]

    def get_command(self, name):
        return self.commands.get(name)


# Singleton registry instance
_registry_instance: Optional[CommandRegistry] = None
_registry_lock = threading.Lock()


def _get_registry_instance() -> CommandRegistry:
    """Get or create a singleton registry instance."""
    global _registry_instance
    with _registry_lock:
        if _registry_instance is None:
            _registry_instance = CommandRegistry()
        return _registry_instance


def reset_registry() -> None:
    """Reset the singleton registry (for testing)."""
    global _registry_instance
    with _registry_lock:
        _registry_instance = None


def set_registry(registry: CommandRegistry) -> None:
    """Set a custom registry instance (for testing or custom configs)."""
    global _registry_instance
    with _registry_lock:
        _registry_instance = registry


def get_command(name: str) -> Command:
    """Convenience function to get a command from the default registry."""
    registry = _get_registry_instance()
    return registry.get_command(name)


class IntelligentDispatcher:
    def __init__(self, registry: Optional[CommandRegistry] = None):
        self.registry = registry or CommandRegistry()

    def dispatch(self, user_input: str) -> Optional[Command]:
        user_input = user_input.lower()
        best_match = None
        max_score = 0

        for command in self.registry.commands.values():
            score = self._calculate_match_score(user_input, command)
            if score > max_score:
                max_score = score
                best_match = command

        return best_match if max_score > 0 else None

    def _calculate_match_score(self, user_input: str, command: Command) -> float:
        score = 0
        user_tokens = set(user_input.split())
        name_tokens = set(command.name.lower().replace("-", " ").split())
        desc_tokens = set(command.description.lower().split())
        tag_tokens = set(command.tags or [])

        if command.name.replace("-", " ") in user_input:
            score += 10

        name_overlap = len(name_tokens.intersection(user_tokens))
        desc_overlap = len(desc_tokens.intersection(user_tokens))
        tag_overlap = len(tag_tokens.intersection(user_tokens))

        score += (name_overlap * 5) + desc_overlap + (tag_overlap * 3)
        return score
