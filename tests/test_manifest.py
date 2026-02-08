import unittest
from dspy_integration.framework.manifest import get_commands


class TestManifest(unittest.TestCase):
    def test_get_commands(self):
        commands = get_commands()
        self.assertGreaterEqual(len(commands), 46)

        command_names = [cmd['name'] for cmd in commands]
        self.assertIn("scheduled-codebase-audit", command_names)
        self.assertIn("security", command_names) # Verify standard command


if __name__ == "__main__":
    unittest.main()
