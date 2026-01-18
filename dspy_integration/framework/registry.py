import os
import toml
from dataclasses import dataclass

@dataclass
class Command:
    name: str
    category: str
    description: str
    prompt: str
    author: str = ""
    tags: list = None

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
                            with open(os.path.join(category_path, command_file), "r") as f:
                                data = toml.load(f)
                                commands[command_name] = Command(
                                    name=command_name,
                                    category=category,
                                    description=data.get("description", ""),
                                    prompt=data.get("prompt", ""),
                                    author=data.get("author", ""),
                                    tags=data.get("tags", [])
                                )
                        except Exception as e:
                            print(f"Error loading command {command_name}: {e}")
        return commands

    def search(self, keyword):
        """Search for commands by keyword in name, description, or tags."""
        results = []
        for command in self.commands.values():
            if (keyword in command.name or
                keyword in command.description or
                (command.tags and keyword in command.tags)):
                results.append(command)
        return results

    def list_by_category(self, category):
        """List all commands in a given category."""
        return [command for command in self.commands.values() if command.category == category]

    def get_command(self, name):
        """Get a command by its name."""
        return self.commands.get(name)

def get_command(name):
    """Convenience function to get a command from the default registry."""
    registry = CommandRegistry()
    return registry.get_command(name)
