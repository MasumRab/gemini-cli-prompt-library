"""
Command manifest and registry for intelligent dispatcher.

Automatically discovers all commands from commands/ directory.
Provides metadata for dispatcher to select appropriate commands.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import tomllib


class CommandRegistry:
    """
    Registry of all available commands.

    Auto-discovers commands from commands/ directory and provides
    lookup and search functionality for the intelligent dispatcher.
    """

    def __init__(self, root: Path = Path("commands")):
        self.root = Path(root)
        self._commands: Dict[str, Dict] = {}
        self._load_all()

    def _load_all(self):
        """Load metadata from all TOML files."""
        for toml_file in self.root.rglob("*.toml"):
            try:
                metadata = self._load_metadata(toml_file)
                self._commands[metadata["name"]] = metadata
            except Exception as e:
                print(f"Warning: Failed to load {toml_file}: {e}", file=sys.stderr)
                continue

    def _load_metadata(self, path: Path) -> Dict:
        """Load command metadata from TOML file."""
        try:
            content = path.read_text()
            data = tomllib.loads(content)

            # Extract metadata
            name = path.stem
            category = path.parent.name
            description = data.get("description", "")
            args = data.get("args", "")

            # Extract examples from prompt if available
            examples = []
            prompt = data.get("prompt", "")
            if "example" in prompt.lower():
                # Simple extraction - can be improved
                examples = ["Basic usage"]

            return {
                "name": name,
                "category": category,
                "path": str(path),
                "description": description,
                "args": args,
                "examples": examples,
            }
        except Exception as e:
            raise ValueError(f"Failed to parse {path}: {e}")

    def get_command(self, name: str) -> Optional[Dict]:
        """Get command metadata by name."""
        return self._commands.get(name)

    def list_by_category(self, category: str) -> List[str]:
        """List command names in a category."""
        return [
            name for name, cmd in self._commands.items() if cmd["category"] == category
        ]

    def search(self, query: str) -> List[Dict]:
        """Search commands by keyword in description."""
        query_lower = query.lower()
        results = []

        for name, cmd in self._commands.items():
            if query_lower in cmd["description"].lower() or query_lower in name.lower():
                results.append(cmd)

        return results

    def get_all_commands(self) -> List[Dict]:
        """Get all commands."""
        return list(self._commands.values())

    def get_categories(self) -> List[str]:
        """Get all categories."""
        return list(set(cmd["category"] for cmd in self._commands.values()))


def get_commands() -> List[Dict]:
    """Get all commands (convenience function)."""
    registry = CommandRegistry()
    return registry.get_all_commands()
